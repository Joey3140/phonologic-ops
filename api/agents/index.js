/**
 * Agents API - Execute individual agent tasks
 * Protected by @phonologic.ca Google SSO
 */

const { AgentOrchestrator, AGENT_ROLES } = require('../../lib/agent-orchestrator');
const { checkRateLimit } = require('../../lib/rate-limiter');
const { getSessionFromRequest } = require('../auth/google');

module.exports = async (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin || 'https://ops.phonologic.cloud');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Auth check - require @phonologic.ca SSO
  const session = getSessionFromRequest(req);
  if (!session) {
    return res.status(401).json({ error: 'Unauthorized', message: 'Please sign in with @phonologic.ca' });
  }

  // Rate limiting by user email
  const rateLimit = await checkRateLimit(`agents:${session.email}`, 30, 60);
  if (!rateLimit.allowed) {
    return res.status(429).json({ error: 'Too many requests', retryAfter: 60 });
  }

  try {
    // GET - list available agents
    if (req.method === 'GET') {
      const orchestrator = new AgentOrchestrator();
      const agents = orchestrator.getAgents();
      
      return res.status(200).json({
        agents,
        availableRoles: Object.keys(AGENT_ROLES)
      });
    }

    // POST - execute agent task
    if (req.method === 'POST') {
      const { agentRole, task, context } = req.body;

      if (!agentRole || !task) {
        return res.status(400).json({ 
          error: 'agentRole and task are required',
          availableRoles: Object.keys(AGENT_ROLES)
        });
      }

      if (!AGENT_ROLES[agentRole]) {
        return res.status(400).json({ 
          error: `Unknown agent role: ${agentRole}`,
          availableRoles: Object.keys(AGENT_ROLES)
        });
      }

      const orchestrator = new AgentOrchestrator();
      const result = await orchestrator.executeAgentTask(agentRole, task, context);

      return res.status(200).json({
        success: true,
        agentRole,
        result
      });
    }

    return res.status(405).json({ error: 'Method not allowed' });

  } catch (error) {
    console.error('Agent execution error:', error);
    return res.status(500).json({ 
      error: 'Agent execution failed',
      message: error.message 
    });
  }
};
