/**
 * Users API - Track and list @phonologic.ca users
 * 
 * Endpoints:
 * - GET /api/users - List all users (requires auth)
 * - GET /api/users?action=me - Get current user with admin status
 * - POST /api/users?action=set-admin - Set admin status (requires admin)
 * 
 * @module api/users
 */

const { getRedis, REDIS_KEYS } = require('../../lib/redis');
const { getSessionFromRequest } = require('../auth/google');

/**
 * Default admin emails - fallback if Redis admins not set
 * Can be overridden by ADMIN_EMAILS env var (comma-separated)
 */
const DEFAULT_ADMINS = (process.env.ADMIN_EMAILS || 'joey@phonologic.ca').split(',').map(e => e.trim().toLowerCase());

/**
 * Main API handler
 * @param {import('http').IncomingMessage} req 
 * @param {import('http').ServerResponse} res 
 */
module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
  
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }

  // Require authentication for all endpoints
  const session = getSessionFromRequest(req);
  if (!session) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  const action = req.query.action;

  try {
    switch (action) {
      case 'me':
        return handleGetMe(req, res, session);
      case 'set-admin':
        return handleSetAdmin(req, res, session);
      default:
        return handleListUsers(req, res, session);
    }
  } catch (error) {
    console.error('[USERS API] Unhandled error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * Get current user info with admin status
 */
async function handleGetMe(req, res, session) {
  const isAdmin = await checkIsAdmin(session.email);
  
  return res.json({
    email: session.email,
    name: session.name,
    picture: session.picture,
    isAdmin
  });
}

/**
 * List users with pagination and optimized admin lookup
 * Query params: limit (default 50), offset (default 0)
 */
async function handleListUsers(req, res, session) {
  const redis = getRedis();
  
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  const limit = Math.min(parseInt(req.query.limit) || 50, 100); // Max 100
  const offset = parseInt(req.query.offset) || 0;

  // Add cache headers
  res.setHeader('Cache-Control', 'private, max-age=60');

  try {
    // Fetch users and admins in parallel (O(2) instead of O(n))
    const [usersData, adminEmails] = await Promise.all([
      redis.hgetall(REDIS_KEYS.USERS),
      redis.smembers(REDIS_KEYS.ADMINS)
    ]);
    
    if (!usersData || Object.keys(usersData).length === 0) {
      return res.json({ users: [], total: 0, limit, offset });
    }

    // Create admin set for O(1) lookup
    const adminSet = new Set([
      ...DEFAULT_ADMINS,
      ...(adminEmails || []).map(e => e.toLowerCase())
    ]);

    // Parse and format users with error handling for corrupted data
    const users = [];
    for (const [email, data] of Object.entries(usersData)) {
      try {
        const userData = parseUserData(data);
        
        users.push({
          email,
          name: userData.name || email.split('@')[0],
          picture: userData.picture || null,
          lastLogin: userData.lastLogin,
          loginCount: userData.loginCount || 1,
          isAdmin: adminSet.has(email.toLowerCase())
        });
      } catch (parseError) {
        console.warn(`[USERS API] Failed to parse user data for ${email}:`, parseError.message);
      }
    }

    // Sort by last login (most recent first)
    users.sort((a, b) => new Date(b.lastLogin) - new Date(a.lastLogin));

    const total = users.length;
    const paginatedUsers = users.slice(offset, offset + limit);

    return res.json({ 
      users: paginatedUsers,
      total,
      limit,
      offset,
      hasMore: offset + limit < total
    });
  } catch (error) {
    console.error('[USERS API] Failed to list users:', error);
    return res.status(500).json({ error: 'Failed to fetch users' });
  }
}

/**
 * Set admin status for a user (requires admin privileges)
 * SECURITY: Prevents self-demotion to avoid no-admin state
 */
async function handleSetAdmin(req, res, session) {
  // Check if requester is admin
  const isRequesterAdmin = await checkIsAdmin(session.email);
  if (!isRequesterAdmin) {
    return res.status(403).json({ error: 'Admin privileges required' });
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, isAdmin } = req.body || {};
  
  if (!email || typeof isAdmin !== 'boolean') {
    return res.status(400).json({ error: 'Email and isAdmin (boolean) required' });
  }

  // SECURITY: Prevent admin from removing their own admin status
  if (!isAdmin && email.toLowerCase() === session.email.toLowerCase()) {
    return res.status(400).json({ 
      error: 'Cannot remove your own admin status',
      message: 'Ask another admin to remove your privileges'
    });
  }

  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    if (isAdmin) {
      await redis.sadd(REDIS_KEYS.ADMINS, email.toLowerCase());
      console.log(`[USERS API] Admin granted to ${email} by ${session.email}`);
    } else {
      await redis.srem(REDIS_KEYS.ADMINS, email.toLowerCase());
      console.log(`[USERS API] Admin revoked from ${email} by ${session.email}`);
    }

    return res.json({ success: true, email, isAdmin });
  } catch (error) {
    console.error('[USERS API] Failed to set admin:', error);
    return res.status(500).json({ error: 'Failed to update admin status' });
  }
}

/**
 * Check if an email has admin privileges
 * Checks Redis admins set first, falls back to env var / defaults
 * 
 * @param {string} email - Email to check
 * @returns {Promise<boolean>} True if user is admin
 */
async function checkIsAdmin(email) {
  const normalizedEmail = email.toLowerCase();
  
  // Check default admins first (env var or hardcoded)
  if (DEFAULT_ADMINS.includes(normalizedEmail)) {
    return true;
  }

  // Check Redis admins set
  const redis = getRedis();
  if (redis) {
    try {
      const isRedisAdmin = await redis.sismember(REDIS_KEYS.ADMINS, normalizedEmail);
      return Boolean(isRedisAdmin);
    } catch (error) {
      console.warn('[USERS API] Failed to check Redis admin status:', error.message);
    }
  }

  return false;
}

/**
 * Safely parse user data from Redis (handles string or object)
 * 
 * @param {string|object} data - Raw data from Redis
 * @returns {object} Parsed user data
 * @throws {Error} If data cannot be parsed
 */
function parseUserData(data) {
  if (typeof data === 'object' && data !== null) {
    return data;
  }
  if (typeof data === 'string') {
    return JSON.parse(data);
  }
  throw new Error('Invalid user data format');
}

/**
 * Record a user login - called from auth callback
 * Updates last login time and increments login count
 * 
 * @param {object} user - User info from Google
 * @param {string} user.email - User email
 * @param {string} user.name - User display name
 * @param {string} user.picture - Profile picture URL
 * @returns {Promise<void>}
 */
async function recordUserLogin(user) {
  const redis = getRedis();
  
  if (!redis) {
    console.warn('[USERS API] Cannot record login - Redis unavailable');
    return;
  }

  const maxRetries = 2;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // Get existing data
      const existing = await redis.hget(REDIS_KEYS.USERS, user.email);
      const existingData = existing ? parseUserData(existing) : null;
      
      const userData = {
        name: user.name,
        picture: user.picture,
        lastLogin: new Date().toISOString(),
        loginCount: (existingData?.loginCount || 0) + 1,
        firstLogin: existingData?.firstLogin || new Date().toISOString()
      };

      await redis.hset(REDIS_KEYS.USERS, { [user.email]: JSON.stringify(userData) });
      console.log(`[USERS API] Recorded login for ${user.email} (count: ${userData.loginCount})`);
      return;
    } catch (error) {
      console.error(`[USERS API] Failed to record login (attempt ${attempt}/${maxRetries}):`, error.message);
      if (attempt === maxRetries) {
        // Don't throw - login should succeed even if tracking fails
        console.error('[USERS API] All retry attempts exhausted for login recording');
      }
    }
  }
}

module.exports.recordUserLogin = recordUserLogin;
module.exports.checkIsAdmin = checkIsAdmin;
