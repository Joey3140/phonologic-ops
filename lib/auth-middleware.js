/**
 * Auth & Security Middleware for API routes
 * 
 * Provides:
 * - Authentication (requires @phonologic.ca Google SSO)
 * - CORS handling (restricted origins)
 * - Rate limiting
 * - Admin checks
 * 
 * @module lib/auth-middleware
 */

const { getSessionFromRequest } = require('../api/auth/google');
const { getRedis, REDIS_KEYS } = require('./redis');

/** Allowed CORS origins - no wildcards */
const ALLOWED_ORIGINS = [
  'https://ops.phonologic.cloud',
  'https://phonologic.cloud',
  'http://localhost:3000',
  'http://localhost:5000'
];

/** Rate limit config per endpoint type */
const RATE_LIMITS = {
  default: { requests: 60, windowSec: 60 },
  write: { requests: 20, windowSec: 60 },
  auth: { requests: 10, windowSec: 60 }
};

/**
 * Set secure CORS headers - NO wildcard fallback
 * @param {object} req - Request object
 * @param {object} res - Response object
 * @returns {boolean} True if origin is allowed
 */
function setCorsHeaders(req, res) {
  const origin = req.headers.origin;
  
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  } else if (!origin) {
    // Same-origin request (no Origin header) - allow
    res.setHeader('Access-Control-Allow-Origin', 'https://ops.phonologic.cloud');
  } else {
    // Unknown origin - don't set CORS header (browser will block)
    return false;
  }
  
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  return true;
}

/**
 * Handle OPTIONS preflight requests
 * @param {object} req - Request object
 * @param {object} res - Response object
 * @returns {boolean} True if this was an OPTIONS request (handled)
 */
function handlePreflight(req, res) {
  if (req.method === 'OPTIONS') {
    setCorsHeaders(req, res);
    res.status(200).end();
    return true;
  }
  return false;
}

/**
 * Check rate limit for an IP/endpoint
 * @param {string} ip - Client IP
 * @param {string} endpoint - Endpoint name
 * @param {string} limitType - 'default', 'write', or 'auth'
 * @returns {Promise<{allowed: boolean, remaining: number}>}
 */
async function checkRateLimit(ip, endpoint, limitType = 'default') {
  const redis = getRedis();
  if (!redis) return { allowed: true, remaining: 999 }; // Fail open if Redis down
  
  const config = RATE_LIMITS[limitType] || RATE_LIMITS.default;
  const key = `${REDIS_KEYS.RATE_LIMIT}${endpoint}:${ip}`;
  
  try {
    const current = await redis.incr(key);
    if (current === 1) {
      await redis.expire(key, config.windowSec);
    }
    
    const remaining = Math.max(0, config.requests - current);
    return { allowed: current <= config.requests, remaining };
  } catch (error) {
    console.warn('[RATE LIMIT] Check failed:', error.message);
    return { allowed: true, remaining: 999 }; // Fail open
  }
}

/**
 * Get client IP from request
 * @param {object} req - Request object
 * @returns {string} Client IP
 */
function getClientIp(req) {
  return req.headers['x-forwarded-for']?.split(',')[0]?.trim() || 
         req.headers['x-real-ip'] || 
         req.socket?.remoteAddress || 
         'unknown';
}

/**
 * Require authentication - returns session or sends 401
 * @param {object} req - Request object
 * @param {object} res - Response object
 * @returns {object|null} Session object or null (401 sent)
 */
function requireAuth(req, res) {
  const session = getSessionFromRequest(req);
  
  if (!session) {
    res.status(401).json({ 
      error: 'Unauthorized',
      message: 'Please sign in with your @phonologic.ca Google account'
    });
    return null;
  }
  
  return session;
}

/**
 * Optional auth - returns session or null (doesn't block)
 * @param {object} req - Request object
 * @returns {object|null} Session object or null
 */
function optionalAuth(req) {
  return getSessionFromRequest(req);
}

/**
 * Wrapper for protected API handlers with full security
 * Handles: CORS, preflight, rate limiting, authentication
 * 
 * @param {Function} handler - API handler function
 * @param {object} options - Configuration options
 * @param {string} options.rateLimit - Rate limit type: 'default', 'write', 'auth'
 * @param {boolean} options.requireAuth - Whether auth is required (default: true)
 * @returns {Function} Wrapped handler
 */
function withAuth(handler, options = {}) {
  const { rateLimit = 'default', requireAuth: authRequired = true } = options;
  
  return async (req, res) => {
    // 1. Handle CORS
    const corsAllowed = setCorsHeaders(req, res);
    if (!corsAllowed) {
      return res.status(403).json({ error: 'Origin not allowed' });
    }
    
    // 2. Handle preflight
    if (handlePreflight(req, res)) return;
    
    // 3. Rate limiting
    const ip = getClientIp(req);
    const endpoint = req.url?.split('?')[0] || '/api';
    const { allowed, remaining } = await checkRateLimit(ip, endpoint, rateLimit);
    
    res.setHeader('X-RateLimit-Remaining', remaining);
    if (!allowed) {
      return res.status(429).json({ 
        error: 'Too many requests',
        message: 'Please wait before trying again'
      });
    }
    
    // 4. Authentication
    if (authRequired) {
      const session = getSessionFromRequest(req);
      if (!session) {
        return res.status(401).json({ 
          error: 'Unauthorized',
          message: 'Please sign in with your @phonologic.ca Google account'
        });
      }
      req.session = session;
    } else {
      req.session = getSessionFromRequest(req);
    }
    
    // 5. Call handler
    try {
      return await handler(req, res);
    } catch (error) {
      console.error(`[API ERROR] ${endpoint}:`, error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  };
}

module.exports = { 
  requireAuth, 
  optionalAuth, 
  withAuth, 
  getSessionFromRequest,
  setCorsHeaders,
  handlePreflight,
  checkRateLimit,
  getClientIp,
  ALLOWED_ORIGINS
};
