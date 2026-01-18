/**
 * Shared Redis Client Singleton
 * 
 * Provides a single Upstash Redis connection for all API endpoints.
 * Prevents multiple connection instances and ensures consistent configuration.
 * 
 * @module lib/redis
 */

const { Redis } = require('@upstash/redis');

/** @type {Redis|null} Singleton Redis instance */
let redis = null;

/** @type {boolean} Tracks if connection has been attempted */
let connectionAttempted = false;

/**
 * Redis key constants - centralized to prevent typos and enable easy changes
 * ALL Redis keys should be defined here - do not hardcode keys in API files
 */
const REDIS_KEYS = {
  /** Hash storing all user login data */
  USERS: 'phonologic:users',
  /** Set of admin email addresses */
  ADMINS: 'phonologic:admins',
  /** Hash storing all wiki pages */
  WIKI: 'phonologic:wiki',
  /** Hash storing all announcements */
  ANNOUNCEMENTS: 'phonologic:announcements',
  /** Hash storing announcement comments (separate from announcements for scalability) */
  COMMENTS: 'phonologic:comments',
  /** Hash storing goals/OKRs */
  GOALS: 'phonologic:goals',
  /** Prefix for OAuth state tokens */
  OAUTH_STATE: 'oauth_state:',
  /** Prefix for rate limiting */
  RATE_LIMIT: 'rate_limit:'
};

/**
 * Get the shared Redis client instance.
 * Creates the connection on first call, returns cached instance thereafter.
 * 
 * @returns {Redis|null} Redis client or null if connection failed
 * @example
 * const { getRedis, REDIS_KEYS } = require('../lib/redis');
 * const redis = getRedis();
 * if (redis) {
 *   await redis.hget(REDIS_KEYS.USERS, 'user@example.com');
 * }
 */
function getRedis() {
  if (redis) return redis;
  if (connectionAttempted) return null;
  
  connectionAttempted = true;
  
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  
  if (!url || !token) {
    console.error('[REDIS] Missing UPSTASH_REDIS_REST_URL or UPSTASH_REDIS_REST_TOKEN');
    return null;
  }
  
  try {
    redis = new Redis({ url, token });
    console.log('[REDIS] Client initialized successfully');
    return redis;
  } catch (error) {
    console.error('[REDIS] Failed to initialize client:', error.message);
    return null;
  }
}

/**
 * Check if Redis is available and connected.
 * 
 * @returns {boolean} True if Redis client exists
 */
function isRedisAvailable() {
  return getRedis() !== null;
}

module.exports = {
  getRedis,
  isRedisAvailable,
  REDIS_KEYS
};
