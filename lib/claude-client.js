/**
 * Claude 3.5 Sonnet client for Phonologic AI Operations Hub
 */

const Anthropic = require('@anthropic-ai/sdk');

class ClaudeClient {
  constructor(apiKey = process.env.ANTHROPIC_API_KEY) {
    if (!apiKey) {
      throw new Error('ANTHROPIC_API_KEY environment variable must be set');
    }
    
    this.client = new Anthropic({ apiKey });
    this.model = 'claude-3-5-sonnet-20241022';
  }

  /**
   * Generate a response from Claude
   */
  async generateResponse({
    prompt,
    systemPrompt = null,
    maxTokens = 4000,
    temperature = 0.7,
    includeReasoning = false
  }) {
    try {
      const messages = [{ role: 'user', content: prompt }];
      
      const params = {
        model: this.model,
        max_tokens: maxTokens,
        temperature,
        messages
      };
      
      if (systemPrompt) {
        params.system = systemPrompt;
      }
      
      const response = await this.client.messages.create(params);
      let content = response.content[0]?.text || '';
      
      // Parse reasoning if requested
      let reasoning = null;
      if (includeReasoning && content.includes('<reasoning>')) {
        const match = content.match(/<reasoning>([\s\S]*?)<\/reasoning>/);
        if (match) {
          reasoning = match[1].trim();
          content = content.replace(/<reasoning>[\s\S]*?<\/reasoning>/, '').trim();
        }
      }
      
      return {
        content,
        reasoning,
        confidence: 0.8,
        metadata: {
          model: this.model,
          usage: response.usage
        }
      };
    } catch (error) {
      console.error('Error generating Claude response:', error);
      throw error;
    }
  }

  /**
   * Analyze code with Claude
   */
  async analyzeCode(code, context = null) {
    const systemPrompt = `You are a senior software engineer analyzing code for the Phonologic AI Operations Hub.
    Provide clear, actionable insights about code quality, potential issues, and improvement suggestions.`;
    
    let prompt = `Analyze the following code:\n\n${code}\n\n`;
    if (context) {
      prompt += `Context: ${context}\n\n`;
    }
    prompt += 'Provide analysis covering: code quality, potential bugs, performance issues, and improvements.';
    
    return this.generateResponse({ prompt, systemPrompt, includeReasoning: true });
  }

  /**
   * Generate a project plan from requirements
   */
  async generateProjectPlan(requirements, constraints = null) {
    const systemPrompt = `You are a project manager for the Phonologic AI Operations Hub.
    Create detailed, actionable project plans with clear tasks, timelines, and dependencies.
    Output in JSON format with structure: { tasks: [{ title, description, priority, estimatedHours, dependencies }] }`;
    
    let prompt = `Create a project plan for the following requirements:\n\n${requirements}\n\n`;
    if (constraints) {
      prompt += `Constraints: ${constraints}\n\n`;
    }
    prompt += 'Include: tasks, priorities, estimated time, dependencies, and success criteria.';
    
    return this.generateResponse({ prompt, systemPrompt });
  }

  /**
   * Summarize data
   */
  async summarizeData(data, summaryType = 'general') {
    const systemPrompt = `You are a data analyst for the Phonologic AI Operations Hub.
    Create concise, actionable summaries of ${summaryType} data.`;
    
    const prompt = `Summarize the following ${summaryType} data:\n\n${data}\n\nFocus on key insights, trends, and action items.`;
    
    return this.generateResponse({ prompt, systemPrompt });
  }

  /**
   * Draft communications (emails, reports, etc.)
   */
  async draftCommunication({ purpose, audience, keyPoints, tone = 'professional' }) {
    const systemPrompt = `You are a communication specialist for Phonologic.
    Draft ${tone} communications that are clear, concise, and effective.`;
    
    let prompt = `Draft a ${purpose} for ${audience}.\n\nKey points to include:\n`;
    keyPoints.forEach((point, i) => {
      prompt += `${i + 1}. ${point}\n`;
    });
    
    return this.generateResponse({ prompt, systemPrompt });
  }

  /**
   * Execute agent task with specific role
   */
  async executeAgentTask({ role, goal, context, task }) {
    const systemPrompt = `You are a ${role} for Phonologic AI Operations Hub.
    Your goal: ${goal}
    
    Execute tasks thoroughly and provide structured, actionable outputs.
    Always include your reasoning and confidence level in your response.`;
    
    let prompt = task;
    if (context) {
      prompt = `Context:\n${context}\n\nTask:\n${task}`;
    }
    
    return this.generateResponse({ prompt, systemPrompt, includeReasoning: true });
  }
}

module.exports = { ClaudeClient };
