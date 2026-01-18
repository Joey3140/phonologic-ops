/**
 * B2C Marketing Campaign Workflow API
 * Research Canada/USA market data and draft localized campaigns
 * Protected by @phonologic.ca Google SSO
 */

const { AgentOrchestrator } = require('../../lib/agent-orchestrator');
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
  const rateLimit = await checkRateLimit(`marketing:${session.email}`, 5, 60);
  if (!rateLimit.allowed) {
    return res.status(429).json({ error: 'Too many requests', retryAfter: 60 });
  }

  try {
    if (req.method === 'POST') {
      const { 
        campaignBrief,
        targetMarket = 'Canada',
        brandGuidelines = ''
      } = req.body;

      if (!campaignBrief) {
        return res.status(400).json({ error: 'campaignBrief is required' });
      }

      // Run the orchestrator workflow
      const orchestrator = new AgentOrchestrator();
      const result = await orchestrator.runMarketingCampaignWorkflow({
        campaignBrief,
        targetMarket,
        brandGuidelines
      });

      return res.status(200).json({
        success: true,
        ...result
      });
    }

    // GET - return workflow status
    if (req.method === 'GET') {
      const { workflowId } = req.query;
      
      if (workflowId) {
        const orchestrator = new AgentOrchestrator();
        const workflow = await orchestrator.workflows.getWorkflow(workflowId);
        return res.status(200).json({ workflow });
      }

      // Return recent workflows
      const orchestrator = new AgentOrchestrator();
      const workflows = await orchestrator.workflows.getRecentWorkflows(10);
      return res.status(200).json({ 
        workflows: workflows.filter(w => w.type === 'marketing_campaign')
      });
    }

    return res.status(405).json({ error: 'Method not allowed' });

  } catch (error) {
    console.error('Marketing campaign workflow error:', error);
    return res.status(500).json({ 
      error: 'Workflow execution failed',
      message: error.message 
    });
  }
};
