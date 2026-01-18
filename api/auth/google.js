/**
 * Google OAuth Authentication for PhonoLogic Operations Portal
 * 
 * SECURITY: Access restricted to @phonologic.ca email domain only.
 * 
 * Endpoints:
 * - GET /api/auth/google?action=login - Redirect to Google OAuth
 * - GET /api/auth/google?action=callback - Handle OAuth callback
 * - GET /api/auth/google?action=verify - Check session validity
 * - GET /api/auth/google?action=logout - Clear session
 * 
 * @module api/auth/google
 */

const crypto = require('crypto');
const { OAuth2Client } = require('google-auth-library');
const { getRedis, REDIS_KEYS } = require('../../lib/redis');
const { recordUserLogin } = require('../users/index.js');

/** @constant {string[]} Allowed email domains for authentication */
const ALLOWED_EMAIL_DOMAINS = ['phonologic.ca'];

/** @constant {number} Session duration in seconds (7 days) */
const SESSION_DURATION_SECONDS = 86400 * 7;

function getRedirectUri(req) {
  const host = req.headers.host || 'ops.phonologic.cloud';
  const protocol = host.includes('localhost') ? 'http' : 'https';
  return `${protocol}://${host}/api/auth/google?action=callback`;
}

function getOAuth2Client(req) {
  return new OAuth2Client(
    process.env.GOOGLE_OAUTH_CLIENT_ID,
    process.env.GOOGLE_OAUTH_CLIENT_SECRET,
    getRedirectUri(req)
  );
}

/**
 * Get session secret - throws if not configured
 * @returns {string} Session secret
 * @throws {Error} If SESSION_SECRET env var is missing
 */
function getSessionSecret() {
  const secret = process.env.SESSION_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error('SESSION_SECRET must be set and at least 32 characters');
  }
  return secret;
}

/**
 * Create signed session token
 * @param {object} userData - User data to encode
 * @returns {string} Signed session token
 */
function createSessionToken(userData) {
  const payload = {
    ...userData,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + SESSION_DURATION_SECONDS
  };
  const data = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const signature = crypto.createHmac('sha256', getSessionSecret()).update(data).digest('base64url');
  return `${data}.${signature}`;
}

/**
 * Verify and decode session token
 * @param {string} token - Session token to verify
 * @returns {object|null} Decoded payload or null if invalid
 */
function verifySessionToken(token) {
  if (!token) return null;
  try {
    const [data, signature] = token.split('.');
    if (!data || !signature) return null;
    
    const expectedSig = crypto.createHmac('sha256', getSessionSecret()).update(data).digest('base64url');
    if (signature !== expectedSig) return null;
    
    const payload = JSON.parse(Buffer.from(data, 'base64url').toString());
    if (payload.exp < Math.floor(Date.now() / 1000)) return null;
    return payload;
  } catch {
    return null;
  }
}

module.exports = async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const action = req.query.action;

  try {
    switch (action) {
      case 'login':
        return handleLogin(req, res);
      case 'callback':
        return handleCallback(req, res);
      case 'verify':
        return handleVerify(req, res);
      case 'logout':
        return handleLogout(req, res);
      default:
        return res.status(400).json({ error: 'Invalid action' });
    }
  } catch (error) {
    console.error('[AUTH] Error:', error);
    return res.status(500).json({ error: 'Authentication failed' });
  }
};

/**
 * Redirect user to Google OAuth consent screen
 */
async function handleLogin(req, res) {
  const redis = getRedis();
  if (!redis) {
    return res.status(500).json({ error: 'Auth service unavailable' });
  }

  const state = crypto.randomBytes(32).toString('hex');
  await redis.set(`${REDIS_KEYS.OAUTH_STATE}${state}`, 'valid', { ex: 600 }); // 10 min TTL

  const oauth2Client = getOAuth2Client(req);
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: [
      'https://www.googleapis.com/auth/userinfo.email',
      'https://www.googleapis.com/auth/userinfo.profile',
      'openid'
    ],
    prompt: 'select_account',
    state
  });

  return res.redirect(302, authUrl);
}

/**
 * Handle OAuth callback from Google
 * Validates state, exchanges code for tokens, verifies domain, creates session
 */
async function handleCallback(req, res) {
  const { code, error: oauthError, state } = req.query;
  const host = req.headers.host || 'ops.phonologic.cloud';
  const protocol = host.includes('localhost') ? 'http' : 'https';
  const baseUrl = `${protocol}://${host}`;

  if (oauthError || !code) {
    return res.redirect(`${baseUrl}/?auth_error=login_failed`);
  }

  // Verify CSRF state using shared Redis client
  const redis = getRedis();
  if (redis && state) {
    const stateKey = `${REDIS_KEYS.OAUTH_STATE}${state}`;
    const storedState = await redis.get(stateKey);
    if (storedState !== 'valid') {
      return res.redirect(`${baseUrl}/?auth_error=invalid_state`);
    }
    await redis.del(stateKey);
  }

  try {
    const oauth2Client = getOAuth2Client(req);
    const { tokens } = await oauth2Client.getToken(code);

    // Get user info
    const userInfoRes = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: { Authorization: `Bearer ${tokens.access_token}` }
    });
    const userInfo = await userInfoRes.json();

    // ⚠️ DOMAIN RESTRICTION - Only @phonologic.ca
    const emailDomain = userInfo.email.split('@')[1]?.toLowerCase();
    if (!ALLOWED_EMAIL_DOMAINS.includes(emailDomain)) {
      console.warn(`[AUTH] ❌ Rejected: ${userInfo.email} - not @phonologic.ca`);
      return res.redirect(`${baseUrl}/?auth_error=${encodeURIComponent('Access restricted to @phonologic.ca accounts only')}`);
    }

    console.log(`[AUTH] ✅ Approved: ${userInfo.email}`);

    // Record user login for org chart
    await recordUserLogin({
      email: userInfo.email,
      name: userInfo.name,
      picture: userInfo.picture
    });

    // Create session token
    const sessionToken = createSessionToken({
      email: userInfo.email,
      name: userInfo.name,
      picture: userInfo.picture,
      googleId: userInfo.id
    });

    // Set HTTP-only secure cookie
    const isSecure = protocol === 'https';
    const cookieOptions = [
      `ops_auth_token=${encodeURIComponent(sessionToken)}`,
      'Path=/',
      'HttpOnly',
      `Max-Age=${SESSION_DURATION_SECONDS}`,
      'SameSite=Lax'
    ];
    if (isSecure) cookieOptions.push('Secure');
    
    res.setHeader('Set-Cookie', cookieOptions.join('; '));
    return res.redirect(`${baseUrl}/?auth_success=true`);

  } catch (error) {
    console.error('[AUTH] Callback error:', error);
    return res.redirect(`${baseUrl}/?auth_error=login_failed`);
  }
}

// Verify current session (for frontend to check auth status)
async function handleVerify(req, res) {
  const cookies = req.headers.cookie || '';
  const tokenMatch = cookies.match(/ops_auth_token=([^;]+)/);
  const token = tokenMatch ? decodeURIComponent(tokenMatch[1]) : null;

  const session = verifySessionToken(token);
  if (!session) {
    return res.status(401).json({ authenticated: false });
  }

  return res.json({
    authenticated: true,
    user: {
      email: session.email,
      name: session.name,
      picture: session.picture
    }
  });
}

// Logout - clear cookie
async function handleLogout(req, res) {
  res.setHeader('Set-Cookie', 'ops_auth_token=; Path=/; HttpOnly; Max-Age=0');
  return res.json({ success: true });
}

// Export verify function for other API routes to use
module.exports.verifySessionToken = verifySessionToken;
module.exports.getSessionFromRequest = (req) => {
  const cookies = req.headers.cookie || '';
  const tokenMatch = cookies.match(/ops_auth_token=([^;]+)/);
  const token = tokenMatch ? decodeURIComponent(tokenMatch[1]) : null;
  return verifySessionToken(token);
};
