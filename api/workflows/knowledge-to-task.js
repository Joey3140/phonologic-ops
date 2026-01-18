/**
 * Knowledge-to-Task Workflow API
 * Reads strategy docs and converts them to ClickUp project plans
 * Protected by @phonologic.ca Google SSO
 */

const { AgentOrchestrator } = require('../../lib/agent-orchestrator');
const { GoogleWorkspace } = require('../../lib/google-workspace');
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
  const rateLimit = await checkRateLimit(`knowledge-task:${session.email}`, 10, 60);
  if (!rateLimit.allowed) {
    return res.status(429).json({ error: 'Too many requests', retryAfter: 60 });
  }

  try {
    if (req.method === 'POST') {
      const { 
        documentId,          // Google Drive document ID
        documentContent,     // Or provide content directly
        projectName,
        clickupListId,       // Optional: create tasks in ClickUp
        googleTokens         // OAuth tokens for Google access
      } = req.body;

      let content = documentContent;

      // Fetch from Google Drive if document ID provided
      if (documentId && googleTokens) {
        try {
          const google = new GoogleWorkspace();
          await google.initialize(googleTokens);
          const doc = await google.getFileContent(documentId);
          content = doc.content;
        } catch (error) {
          console.error('Google Drive fetch error:', error);
          return res.status(400).json({ 
            error: 'Failed to fetch document from Google Drive',
            message: error.message 
          });
        }
      }

      if (!content) {
        return res.status(400).json({ 
          error: 'Either documentId with googleTokens or documentContent is required' 
        });
      }

      // Run the orchestrator workflow
      const orchestrator = new AgentOrchestrator();
      const result = await orchestrator.runKnowledgeToTaskWorkflow({
        documentContent: content,
        projectName: projectName || 'New Project'
      });

      // Optionally create tasks in ClickUp
      let clickupResult = null;
      if (clickupListId && result.clickupTasks) {
        try {
          const clickup = new ClickUpClient();
          // Parse tasks from Claude's response
          let tasks;
          try {
            tasks = JSON.parse(result.clickupTasks);
          } catch {
            // Try to extract JSON from the response
            const match = result.clickupTasks.match(/\[[\s\S]*\]/);
            if (match) {
              tasks = JSON.parse(match[0]);
            }
          }

          if (tasks && Array.isArray(tasks)) {
            clickupResult = await clickup.createTasksFromPlan(clickupListId, tasks);
          }
        } catch (error) {
          console.error('ClickUp task creation error:', error);
          clickupResult = { error: error.message };
        }
      }

      return res.status(200).json({
        success: true,
        ...result,
        clickupResult
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
        workflows: workflows.filter(w => w.type === 'knowledge_to_task')
      });
    }

    return res.status(405).json({ error: 'Method not allowed' });

  } catch (error) {
    console.error('Knowledge-to-task workflow error:', error);
    return res.status(500).json({ 
      error: 'Workflow execution failed',
      message: error.message 
    });
  }
};
