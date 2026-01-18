/**
 * Wiki API - Company knowledge base
 * 
 * Endpoints:
 * - GET /api/wiki - List all wiki pages
 * - GET /api/wiki?id=xxx - Get single page
 * - POST /api/wiki - Create/update page (admin only)
 * - DELETE /api/wiki?id=xxx - Delete page (admin only)
 * 
 * @module api/wiki
 */

const { getRedis, REDIS_KEYS } = require('../../lib/redis');
const { getSessionFromRequest } = require('../auth/google');
const { checkIsAdmin } = require('../users/index');

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
        return req.query.id ? handleGet(req, res) : handleList(req, res);
      case 'POST':
        return handleSave(req, res, session);
      case 'DELETE':
        return handleDelete(req, res, session);
      default:
        return res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    console.error('[WIKI API] Error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * List wiki pages with optional pagination
 * Query params: limit (default 50), offset (default 0), category (optional filter)
 */
async function handleList(req, res) {
  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  const limit = Math.min(parseInt(req.query.limit) || 50, 100); // Max 100
  const offset = parseInt(req.query.offset) || 0;
  const categoryFilter = req.query.category;

  // Add cache headers for list requests
  res.setHeader('Cache-Control', 'private, max-age=60');

  try {
    const data = await redis.hgetall(REDIS_KEYS.WIKI);
    
    if (!data || Object.keys(data).length === 0) {
      return res.json({ pages: [], total: 0, limit, offset });
    }

    let pages = Object.entries(data).map(([id, item]) => {
      const parsed = typeof item === 'string' ? JSON.parse(item) : item;
      return {
        id,
        title: parsed.title,
        category: parsed.category,
        updatedAt: parsed.updatedAt,
        author: parsed.author
      };
    });

    // Filter by category if specified
    if (categoryFilter) {
      pages = pages.filter(p => p.category === categoryFilter);
    }

    // Sort by title
    pages.sort((a, b) => a.title.localeCompare(b.title));

    const total = pages.length;
    const paginatedPages = pages.slice(offset, offset + limit);

    return res.json({ 
      pages: paginatedPages, 
      total, 
      limit, 
      offset,
      hasMore: offset + limit < total
    });
  } catch (error) {
    console.error('[WIKI API] List error:', error);
    return res.status(500).json({ error: 'Failed to fetch wiki pages' });
  }
}

/**
 * Get a single wiki page with full content
 */
async function handleGet(req, res) {
  const { id } = req.query;
  
  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const data = await redis.hget(REDIS_KEYS.WIKI, id);
    
    if (!data) {
      return res.status(404).json({ error: 'Page not found' });
    }

    const page = typeof data === 'string' ? JSON.parse(data) : data;
    return res.json({ page: { id, ...page } });
  } catch (error) {
    console.error('[WIKI API] Get error:', error);
    return res.status(500).json({ error: 'Failed to fetch page' });
  }
}

/**
 * Create or update a wiki page (admin only)
 */
async function handleSave(req, res, session) {
  const isAdmin = await checkIsAdmin(session.email);
  if (!isAdmin) {
    return res.status(403).json({ error: 'Admin privileges required' });
  }

  const { id, title, content, category = 'policies' } = req.body || {};
  
  if (!title || !content) {
    return res.status(400).json({ error: 'Title and content required' });
  }

  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const pageId = id || `wiki_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const isNew = !id;

    // Get existing page for createdAt preservation
    let existingPage = null;
    if (!isNew) {
      const existing = await redis.hget(REDIS_KEYS.WIKI, pageId);
      existingPage = existing ? (typeof existing === 'string' ? JSON.parse(existing) : existing) : null;
    }

    const page = {
      title,
      content,
      category,
      author: session.name,
      authorEmail: session.email,
      createdAt: existingPage?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    await redis.hset(REDIS_KEYS.WIKI, { [pageId]: JSON.stringify(page) });
    console.log(`[WIKI API] ${isNew ? 'Created' : 'Updated'}: ${title} by ${session.email}`);

    return res.json({ success: true, id: pageId, page });
  } catch (error) {
    console.error('[WIKI API] Save error:', error);
    return res.status(500).json({ error: 'Failed to save page' });
  }
}

/**
 * Delete a wiki page (admin only)
 */
async function handleDelete(req, res, session) {
  const isAdmin = await checkIsAdmin(session.email);
  if (!isAdmin) {
    return res.status(403).json({ error: 'Admin privileges required' });
  }

  const { id } = req.query;
  if (!id) {
    return res.status(400).json({ error: 'Page ID required' });
  }

  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    await redis.hdel(REDIS_KEYS.WIKI, id);
    console.log(`[WIKI API] Deleted: ${id} by ${session.email}`);

    return res.json({ success: true });
  } catch (error) {
    console.error('[WIKI API] Delete error:', error);
    return res.status(500).json({ error: 'Failed to delete page' });
  }
}
