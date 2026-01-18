/**
 * Agent Orchestrator for Phonologic AI Operations Hub
 * Manages AI agents and their collaborative workflows
 */

const { ClaudeClient } = require('./claude-client');
const { MemoryIndex, WorkflowStore, OpsLogger } = require('./firestore-db');

// Agent role definitions
const AGENT_ROLES = {
  TEAM_SYNC: {
    name: 'Remote Team Sync Specialist',
    role: 'Remote Team Sync Specialist',
    goal: 'Monitor GitHub and ClickUp to provide comprehensive summaries of Philippines dev team progress',
    backstory: `You are a dedicated project coordinator specializing in remote team management. 
    You excel at analyzing development progress, identifying blockers, and communicating status updates 
    to stakeholders. You have deep expertise in GitHub workflows and ClickUp project management.`
  },
  KNOWLEDGE: {
    name: 'Knowledge Management Specialist',
    role: 'Knowledge Management Specialist',
    goal: 'Convert strategy documents and knowledge assets into actionable project plans',
    backstory: `You are an expert knowledge manager who bridges the gap between strategy and execution. 
    You excel at analyzing complex documents, extracting key requirements, and transforming them into 
    structured project plans that teams can execute immediately.`
  },
  MARKETING: {
    name: 'B2C Marketing Strategist',
    role: 'B2C Marketing Strategist',
    goal: 'Research Philippine market data and create localized B2C campaigns while maintaining brand voice',
    backstory: `You are a marketing strategist with deep expertise in the Philippine market. 
    You understand local consumer behavior, cultural nuances, and effective marketing channels. 
    You create compelling campaigns that resonate with local audiences while maintaining brand consistency.`
  },
  PROJECT_MANAGER: {
    name: 'Project Manager',
    role: 'Project Manager',
    goal: 'Coordinate agent workflows and ensure project deliverables are met on time',
    backstory: `You are an experienced project manager who excels at coordinating complex projects 
    with multiple stakeholders. You ensure tasks are completed on schedule, resources are allocated 
    effectively, and communication flows smoothly between all team members.`
  },
  COMMUNICATION: {
    name: 'Communication Specialist',
    role: 'Communication Specialist',
    goal: 'Draft and manage all internal and external communications',
    backstory: `You are a skilled communicator who creates clear, concise, and effective messages 
    for different audiences. You excel at drafting emails, reports, and documentation that keep 
    stakeholders informed and aligned.`
  }
};

class AgentOrchestrator {
  constructor() {
    this.claude = new ClaudeClient();
    this.memory = new MemoryIndex();
    this.workflows = new WorkflowStore();
    this.logger = new OpsLogger();
  }

  /**
   * Execute a single agent task
   */
  async executeAgentTask(agentRole, task, context = null) {
    const agent = AGENT_ROLES[agentRole];
    if (!agent) {
      throw new Error(`Unknown agent role: ${agentRole}`);
    }

    await this.logger.info(`Agent ${agent.name} starting task`, { task: task.substring(0, 100) });

    const result = await this.claude.executeAgentTask({
      role: agent.role,
      goal: agent.goal,
      context: context || agent.backstory,
      task
    });

    await this.logger.info(`Agent ${agent.name} completed task`, { 
      contentLength: result.content.length 
    });

    return result;
  }

  /**
   * Run Team Sync workflow
   */
  async runTeamSyncWorkflow({ githubData, clickupData }) {
    const workflow = await this.workflows.createWorkflow({
      type: 'team_sync',
      inputs: { githubData: !!githubData, clickupData: !!clickupData },
      createdBy: 'system'
    });

    try {
      await this.workflows.updateWorkflow(workflow.id, { status: 'running' });

      // Step 1: Analyze GitHub activity
      const githubAnalysis = await this.executeAgentTask(
        'TEAM_SYNC',
        `Analyze this GitHub activity data and identify key development progress, commits, PRs, and any blockers:\n\n${JSON.stringify(githubData, null, 2)}`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'github_analysis',
        result: githubAnalysis.content
      });

      // Step 2: Analyze ClickUp tasks
      const clickupAnalysis = await this.executeAgentTask(
        'TEAM_SYNC',
        `Analyze this ClickUp task data and identify task progress, completed items, and upcoming deadlines:\n\n${JSON.stringify(clickupData, null, 2)}`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'clickup_analysis',
        result: clickupAnalysis.content
      });

      // Step 3: Generate summary report
      const summaryReport = await this.executeAgentTask(
        'COMMUNICATION',
        `Create a comprehensive daily progress report combining these analyses:
        
GitHub Analysis:
${githubAnalysis.content}

ClickUp Analysis:
${clickupAnalysis.content}

Format as a clear, actionable report with: Executive Summary, Key Achievements, Current Blockers, and Next Steps.`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'summary_report',
        result: summaryReport.content
      });

      await this.workflows.updateWorkflow(workflow.id, { 
        status: 'completed',
        result: summaryReport.content
      });

      return {
        workflowId: workflow.id,
        status: 'completed',
        report: summaryReport.content,
        analyses: {
          github: githubAnalysis.content,
          clickup: clickupAnalysis.content
        }
      };

    } catch (error) {
      await this.workflows.updateWorkflow(workflow.id, { 
        status: 'failed',
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Run Knowledge-to-Task workflow
   */
  async runKnowledgeToTaskWorkflow({ documentContent, projectName }) {
    const workflow = await this.workflows.createWorkflow({
      type: 'knowledge_to_task',
      inputs: { projectName, documentLength: documentContent?.length },
      createdBy: 'system'
    });

    try {
      await this.workflows.updateWorkflow(workflow.id, { status: 'running' });

      // Step 1: Extract requirements from document
      const requirements = await this.executeAgentTask(
        'KNOWLEDGE',
        `Analyze this strategy document and extract all actionable requirements, objectives, and constraints:

Document:
${documentContent}

Output as structured JSON with: { objectives: [], requirements: [], constraints: [], successCriteria: [] }`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'extract_requirements',
        result: requirements.content
      });

      // Step 2: Generate project plan
      const projectPlan = await this.executeAgentTask(
        'PROJECT_MANAGER',
        `Create a detailed project plan for "${projectName}" based on these requirements:

${requirements.content}

Output as structured JSON with tasks array: { tasks: [{ title, description, priority (high/medium/low), estimatedHours, dependencies: [], assignee: null }] }`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'generate_plan',
        result: projectPlan.content
      });

      // Step 3: Format for ClickUp
      const clickupTasks = await this.executeAgentTask(
        'PROJECT_MANAGER',
        `Format this project plan for ClickUp task creation:

${projectPlan.content}

Output as JSON array ready for ClickUp API: [{ name, description, priority (1-4), due_date_offset_days, tags: [] }]`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'format_clickup',
        result: clickupTasks.content
      });

      await this.workflows.updateWorkflow(workflow.id, { 
        status: 'completed',
        result: clickupTasks.content
      });

      return {
        workflowId: workflow.id,
        status: 'completed',
        requirements: requirements.content,
        projectPlan: projectPlan.content,
        clickupTasks: clickupTasks.content
      };

    } catch (error) {
      await this.workflows.updateWorkflow(workflow.id, { 
        status: 'failed',
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Run B2C Marketing Campaign workflow
   */
  async runMarketingCampaignWorkflow({ campaignBrief, targetMarket = 'Philippines', brandGuidelines = '' }) {
    const workflow = await this.workflows.createWorkflow({
      type: 'marketing_campaign',
      inputs: { targetMarket, briefLength: campaignBrief?.length },
      createdBy: 'system'
    });

    try {
      await this.workflows.updateWorkflow(workflow.id, { status: 'running' });

      // Step 1: Market research
      const marketResearch = await this.executeAgentTask(
        'MARKETING',
        `Conduct market research for a B2C campaign in ${targetMarket}:

Campaign Brief:
${campaignBrief}

Analyze: target demographics, consumer behavior, preferred channels, cultural considerations, and competitor landscape.
Output as structured analysis.`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'market_research',
        result: marketResearch.content
      });

      // Step 2: Campaign concepts
      const campaignConcepts = await this.executeAgentTask(
        'MARKETING',
        `Create 3 localized B2C campaign concepts for ${targetMarket} based on:

Market Research:
${marketResearch.content}

Brand Guidelines:
${brandGuidelines || 'Maintain professional, innovative, and approachable brand voice.'}

For each concept include: theme, key messaging, visual direction, channel strategy, and expected outcomes.`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'campaign_concepts',
        result: campaignConcepts.content
      });

      // Step 3: Execution plan
      const executionPlan = await this.executeAgentTask(
        'PROJECT_MANAGER',
        `Create a detailed execution plan for these marketing campaign concepts:

${campaignConcepts.content}

Include: timeline, budget allocation, team responsibilities, KPIs, and milestones.
Output as actionable project plan.`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'execution_plan',
        result: executionPlan.content
      });

      // Step 4: Stakeholder presentation
      const presentation = await this.executeAgentTask(
        'COMMUNICATION',
        `Create an executive presentation summarizing:

Market Research:
${marketResearch.content}

Campaign Concepts:
${campaignConcepts.content}

Execution Plan:
${executionPlan.content}

Format as a clear presentation outline with key talking points for each section.`
      );
      await this.workflows.addWorkflowStep(workflow.id, {
        step: 'presentation',
        result: presentation.content
      });

      await this.workflows.updateWorkflow(workflow.id, { 
        status: 'completed',
        result: presentation.content
      });

      return {
        workflowId: workflow.id,
        status: 'completed',
        marketResearch: marketResearch.content,
        campaignConcepts: campaignConcepts.content,
        executionPlan: executionPlan.content,
        presentation: presentation.content
      };

    } catch (error) {
      await this.workflows.updateWorkflow(workflow.id, { 
        status: 'failed',
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Get available agents
   */
  getAgents() {
    return Object.entries(AGENT_ROLES).map(([key, agent]) => ({
      id: key,
      ...agent
    }));
  }
}

module.exports = { AgentOrchestrator, AGENT_ROLES };
