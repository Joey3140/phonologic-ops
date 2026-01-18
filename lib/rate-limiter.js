/**
 * Rate limiter using Upstash Redis (matching main PhonoLogic app)
 */

const { Redis } = require('@upstash/redis');

let redis = null;

function getRedis() {
  if (!redis) {
    redis = new Redis({
      url: process.env.UPSTASH_REDIS_REST_URL,
      token: process.env.UPSTASH_REDIS_REST_TOKEN
    });
  }
  return redis;
}

/**
 * Rate limit check for API endpoints
 */
async function checkRateLimit(identifier, limit = 100, windowSeconds = 60) {
  const redis = getRedis();
  const key = `ops_ratelimit:${identifier}`;
  
  const current = await redis.incr(key);
  
  if (current === 1) {
    await redis.expire(key, windowSeconds);
  }
  
  return {
    allowed: current <= limit,
    current,
    limit,
    remaining: Math.max(0, limit - current)
  };
}

/**
 * Rate limiter middleware for API routes
 */
function rateLimiter(options = {}) {
  const { limit = 100, windowSeconds = 60, keyGenerator } = options;

  return async (req, res, next) => {
    const identifier = keyGenerator 
      ? keyGenerator(req) 
      : req.headers['x-forwarded-for'] || req.socket?.remoteAddress || 'unknown';

    const result = await checkRateLimit(identifier, limit, windowSeconds);

    res.setHeader('X-RateLimit-Limit', result.limit);
    res.setHeader('X-RateLimit-Remaining', result.remaining);

    if (!result.allowed) {
      return res.status(429).json({
        error: 'Too many requests',
        retryAfter: windowSeconds
      });
    }

    if (next) next();
    return result;
  };
}

module.exports = { checkRateLimit, rateLimiter, getRedis };
