/**
 * Goals API - Company OKRs and objectives
 * 
 * Endpoints:
 * - GET /api/goals - List all goals
 * - GET /api/goals?action=stats - Get goal statistics
 * - POST /api/goals - Create/update goal (admin only)
 * - DELETE /api/goals?id=xxx - Delete goal (admin only)
 * 
 * @module api/goals
 */

const { getRedis } = require('../../lib/redis');
const { getSessionFromRequest } = require('../auth/google');
const { checkIsAdmin } = require('../users/index');

/** Redis key for goals */
const GOALS_KEY = 'phonologic:goals';

/**
 * Main API handler
 */
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
  
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }

  // Require authentication
  const session = getSessionFromRequest(req);
  if (!session) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  try {
    switch (req.method) {
      case 'GET':
        return req.query.action === 'stats' ? handleStats(req, res) : handleList(req, res);
      case 'POST':
        return handleSave(req, res, session);
      case 'DELETE':
        return handleDelete(req, res, session);
      default:
        return res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    console.error('[GOALS API] Error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * List all goals
 */
async function handleList(req, res) {
  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const data = await redis.hgetall(GOALS_KEY);
    
    if (!data || Object.keys(data).length === 0) {
      return res.json({ goals: [] });
    }

    const goals = Object.entries(data).map(([id, item]) => {
      const parsed = typeof item === 'string' ? JSON.parse(item) : item;
      return { id, ...parsed };
    });

    // Sort by quarter then by status
    const statusOrder = { 'on-track': 0, 'at-risk': 1, 'behind': 2, 'completed': 3 };
    goals.sort((a, b) => {
      if (a.quarter !== b.quarter) return a.quarter.localeCompare(b.quarter);
      return (statusOrder[a.status] || 0) - (statusOrder[b.status] || 0);
    });

    return res.json({ goals });
  } catch (error) {
    console.error('[GOALS API] List error:', error);
    return res.status(500).json({ error: 'Failed to fetch goals' });
  }
}

/**
 * Get goal statistics
 */
async function handleStats(req, res) {
  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const data = await redis.hgetall(GOALS_KEY);
    
    let total = 0;
    let completed = 0;
    let onTrack = 0;
    let atRisk = 0;
    let behind = 0;

    if (data) {
      Object.values(data).forEach(item => {
        const goal = typeof item === 'string' ? JSON.parse(item) : item;
        total++;
        switch (goal.status) {
          case 'completed': completed++; break;
          case 'on-track': onTrack++; break;
          case 'at-risk': atRisk++; break;
          case 'behind': behind++; break;
        }
      });
    }

    return res.json({ stats: { total, completed, onTrack, atRisk, behind } });
  } catch (error) {
    console.error('[GOALS API] Stats error:', error);
    return res.status(500).json({ error: 'Failed to fetch stats' });
  }
}

/**
 * Create or update a goal (admin only)
 */
async function handleSave(req, res, session) {
  const isAdmin = await checkIsAdmin(session.email);
  if (!isAdmin) {
    return res.status(403).json({ error: 'Admin privileges required' });
  }

  const { id, title, description, quarter, status, progress, clickupLink } = req.body || {};
  
  if (!title) {
    return res.status(400).json({ error: 'Title required' });
  }

  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const goalId = id || `goal_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const isNew = !id;

    const goal = {
      title,
      description: description || '',
      quarter: quarter || 'Q1 2026',
      status: status || 'on-track',
      progress: parseInt(progress) || 0,
      clickupLink: clickupLink || '',
      author: session.name,
      authorEmail: session.email,
      createdAt: isNew ? new Date().toISOString() : undefined,
      updatedAt: new Date().toISOString()
    };

    // Preserve createdAt on update
    if (!isNew) {
      const existing = await redis.hget(GOALS_KEY, goalId);
      if (existing) {
        const existingGoal = typeof existing === 'string' ? JSON.parse(existing) : existing;
        goal.createdAt = existingGoal.createdAt;
      }
    }

    await redis.hset(GOALS_KEY, { [goalId]: JSON.stringify(goal) });
    console.log(`[GOALS API] ${isNew ? 'Created' : 'Updated'}: ${title} by ${session.email}`);

    return res.json({ success: true, id: goalId, goal });
  } catch (error) {
    console.error('[GOALS API] Save error:', error);
    return res.status(500).json({ error: 'Failed to save goal' });
  }
}

/**
 * Delete a goal (admin only)
 */
async function handleDelete(req, res, session) {
  const isAdmin = await checkIsAdmin(session.email);
  if (!isAdmin) {
    return res.status(403).json({ error: 'Admin privileges required' });
  }

  const { id } = req.query;
  if (!id) {
    return res.status(400).json({ error: 'Goal ID required' });
  }

  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    await redis.hdel(GOALS_KEY, id);
    console.log(`[GOALS API] Deleted: ${id} by ${session.email}`);

    return res.json({ success: true });
  } catch (error) {
    console.error('[GOALS API] Delete error:', error);
    return res.status(500).json({ error: 'Failed to delete goal' });
  }
}
