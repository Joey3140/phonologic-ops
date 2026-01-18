/**
 * Announcements API - Company news and updates with comments
 * 
 * Endpoints:
 * - GET /api/announcements - List all announcements
 * - GET /api/announcements?id=xxx - Get single announcement with comments
 * - GET /api/announcements?action=latest - Get latest announcement only
 * - POST /api/announcements - Create announcement (admin only)
 * - POST /api/announcements?action=comment&id=xxx - Add comment to announcement
 * - DELETE /api/announcements?id=xxx - Delete announcement (admin only)
 * - DELETE /api/announcements?id=xxx&commentId=yyy - Delete comment (admin or author)
 * 
 * @module api/announcements
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

  const { action, id, commentId } = req.query;

  try {
    switch (req.method) {
      case 'GET':
        if (action === 'latest') return handleLatest(req, res);
        if (id) return handleGetOne(req, res, id);
        return handleList(req, res);
      case 'POST':
        if (action === 'comment' && id) return handleAddComment(req, res, session, id);
        return handleCreate(req, res, session);
      case 'DELETE':
        if (commentId && id) return handleDeleteComment(req, res, session, id, commentId);
        return handleDelete(req, res, session);
      default:
        return res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    console.error('[ANNOUNCEMENTS API] Error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * List announcements with pagination (newest first)
 * Query params: limit (default 20), offset (default 0)
 */
async function handleList(req, res) {
  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  const limit = Math.min(parseInt(req.query.limit) || 20, 50); // Max 50
  const offset = parseInt(req.query.offset) || 0;

  // Add cache headers
  res.setHeader('Cache-Control', 'private, max-age=30');

  try {
    const data = await redis.hgetall(REDIS_KEYS.ANNOUNCEMENTS);
    
    if (!data || Object.keys(data).length === 0) {
      return res.json({ announcements: [], total: 0, limit, offset });
    }

    const announcements = Object.entries(data).map(([id, item]) => {
      const parsed = typeof item === 'string' ? JSON.parse(item) : item;
      return { id, ...parsed };
    });

    // Sort by date (newest first)
    announcements.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

    const total = announcements.length;
    const paginatedAnnouncements = announcements.slice(offset, offset + limit);

    return res.json({ 
      announcements: paginatedAnnouncements,
      total,
      limit,
      offset,
      hasMore: offset + limit < total
    });
  } catch (error) {
    console.error('[ANNOUNCEMENTS API] List error:', error);
    return res.status(500).json({ error: 'Failed to fetch announcements' });
  }
}

/**
 * Create a new announcement (admin only)
 */
async function handleCreate(req, res, session) {
  const isAdmin = await checkIsAdmin(session.email);
  if (!isAdmin) {
    return res.status(403).json({ error: 'Admin privileges required' });
  }

  const { title, content, type = 'info' } = req.body || {};
  
  if (!title || !content) {
    return res.status(400).json({ error: 'Title and content required' });
  }

  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const id = `ann_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const announcement = {
      title,
      content,
      type,
      author: session.name,
      authorEmail: session.email,
      createdAt: new Date().toISOString()
    };

    await redis.hset(REDIS_KEYS.ANNOUNCEMENTS, { [id]: JSON.stringify(announcement) });
    console.log(`[ANNOUNCEMENTS API] Created: ${title} by ${session.email}`);

    return res.json({ success: true, id, announcement });
  } catch (error) {
    console.error('[ANNOUNCEMENTS API] Create error:', error);
    return res.status(500).json({ error: 'Failed to create announcement' });
  }
}

/**
 * Delete an announcement (admin only)
 */
async function handleDelete(req, res, session) {
  const isAdmin = await checkIsAdmin(session.email);
  if (!isAdmin) {
    return res.status(403).json({ error: 'Admin privileges required' });
  }

  const { id } = req.query;
  if (!id) {
    return res.status(400).json({ error: 'Announcement ID required' });
  }

  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    await redis.hdel(REDIS_KEYS.ANNOUNCEMENTS, id);
    console.log(`[ANNOUNCEMENTS API] Deleted: ${id} by ${session.email}`);

    return res.json({ success: true });
  } catch (error) {
    console.error('[ANNOUNCEMENTS API] Delete error:', error);
    return res.status(500).json({ error: 'Failed to delete announcement' });
  }
}

/**
 * Get latest announcement only
 */
async function handleLatest(req, res) {
  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const data = await redis.hgetall(REDIS_KEYS.ANNOUNCEMENTS);
    
    if (!data || Object.keys(data).length === 0) {
      return res.json({ announcement: null });
    }

    const announcements = Object.entries(data).map(([id, item]) => {
      const parsed = typeof item === 'string' ? JSON.parse(item) : item;
      return { id, ...parsed };
    });

    announcements.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    
    return res.json({ announcement: announcements[0] || null });
  } catch (error) {
    console.error('[ANNOUNCEMENTS API] Latest error:', error);
    return res.status(500).json({ error: 'Failed to fetch latest announcement' });
  }
}

/**
 * Get single announcement with comments
 */
async function handleGetOne(req, res, id) {
  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const item = await redis.hget(REDIS_KEYS.ANNOUNCEMENTS, id);
    if (!item) {
      return res.status(404).json({ error: 'Announcement not found' });
    }

    const parsed = typeof item === 'string' ? JSON.parse(item) : item;
    return res.json({ announcement: { id, ...parsed } });
  } catch (error) {
    console.error('[ANNOUNCEMENTS API] GetOne error:', error);
    return res.status(500).json({ error: 'Failed to fetch announcement' });
  }
}

/**
 * Add comment to announcement
 */
async function handleAddComment(req, res, session, announcementId) {
  const { content } = req.body || {};
  
  if (!content || content.trim().length === 0) {
    return res.status(400).json({ error: 'Comment content required' });
  }

  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const item = await redis.hget(REDIS_KEYS.ANNOUNCEMENTS, announcementId);
    if (!item) {
      return res.status(404).json({ error: 'Announcement not found' });
    }

    const announcement = typeof item === 'string' ? JSON.parse(item) : item;
    
    const commentId = `cmt_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
    const comment = {
      id: commentId,
      content: content.trim(),
      author: session.name,
      authorEmail: session.email,
      createdAt: new Date().toISOString()
    };

    announcement.comments = announcement.comments || [];
    announcement.comments.push(comment);

    await redis.hset(REDIS_KEYS.ANNOUNCEMENTS, { [announcementId]: JSON.stringify(announcement) });
    console.log(`[ANNOUNCEMENTS API] Comment added to ${announcementId} by ${session.email}`);

    return res.json({ success: true, comment });
  } catch (error) {
    console.error('[ANNOUNCEMENTS API] AddComment error:', error);
    return res.status(500).json({ error: 'Failed to add comment' });
  }
}

/**
 * Delete comment (admin or comment author)
 */
async function handleDeleteComment(req, res, session, announcementId, commentId) {
  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  try {
    const item = await redis.hget(REDIS_KEYS.ANNOUNCEMENTS, announcementId);
    if (!item) {
      return res.status(404).json({ error: 'Announcement not found' });
    }

    const announcement = typeof item === 'string' ? JSON.parse(item) : item;
    const commentIndex = (announcement.comments || []).findIndex(c => c.id === commentId);
    
    if (commentIndex === -1) {
      return res.status(404).json({ error: 'Comment not found' });
    }

    const comment = announcement.comments[commentIndex];
    const isAdmin = await checkIsAdmin(session.email);
    
    if (!isAdmin && comment.authorEmail !== session.email) {
      return res.status(403).json({ error: 'Cannot delete this comment' });
    }

    announcement.comments.splice(commentIndex, 1);
    await redis.hset(REDIS_KEYS.ANNOUNCEMENTS, { [announcementId]: JSON.stringify(announcement) });
    console.log(`[ANNOUNCEMENTS API] Comment ${commentId} deleted by ${session.email}`);

    return res.json({ success: true });
  } catch (error) {
    console.error('[ANNOUNCEMENTS API] DeleteComment error:', error);
    return res.status(500).json({ error: 'Failed to delete comment' });
  }
}
