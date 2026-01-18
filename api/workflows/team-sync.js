/**
 * Team Sync Workflow API
 * Monitors GitHub and ClickUp to summarize Philippines dev team progress
 * Protected by @phonologic.ca Google SSO
 */

const { AgentOrchestrator } = require('../../lib/agent-orchestrator');
const { GitHubClient } = require('../../lib/github-client');
const { ClickUpClient } = require('../../lib/clickup-client');
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
  const rateLimit = await checkRateLimit(`team-sync:${session.email}`, 10, 60);
  if (!rateLimit.allowed) {
    return res.status(429).json({ error: 'Too many requests', retryAfter: 60 });
  }

  try {
    if (req.method === 'POST') {
      const { githubRepoUrl, clickupWorkspaceId, sinceDays = 7 } = req.body;

      // Gather data from GitHub
      let githubData = null;
      if (githubRepoUrl) {
        try {
          const github = new GitHubClient();
          const { owner, repo } = GitHubClient.parseRepoUrl(githubRepoUrl);
          githubData = await github.getRepoSummary(owner, repo, sinceDays);
        } catch (error) {
          console.error('GitHub fetch error:', error);
          githubData = { error: error.message };
        }
      }

      // Gather data from ClickUp
      let clickupData = null;
      if (clickupWorkspaceId) {
        try {
          const clickup = new ClickUpClient();
          clickupData = await clickup.getWorkspaceSummary(clickupWorkspaceId);
        } catch (error) {
          console.error('ClickUp fetch error:', error);
          clickupData = { error: error.message };
        }
      }

      // Run the orchestrator workflow
      const orchestrator = new AgentOrchestrator();
      const result = await orchestrator.runTeamSyncWorkflow({
        githubData,
        clickupData
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
        workflows: workflows.filter(w => w.type === 'team_sync')
      });
    }

    return res.status(405).json({ error: 'Method not allowed' });

  } catch (error) {
    console.error('Team sync workflow error:', error);
    return res.status(500).json({ 
      error: 'Workflow execution failed',
      message: error.message 
    });
  }
};
