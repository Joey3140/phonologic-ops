/**
 * ClickUp API Integration for Phonologic Ops Hub
 * Manages tasks, projects, and workspace data
 */

const fetch = require('node-fetch');

const CLICKUP_API_BASE = 'https://api.clickup.com/api/v2';

class ClickUpClient {
  constructor(apiToken = process.env.CLICKUP_API_TOKEN) {
    if (!apiToken) {
      throw new Error('CLICKUP_API_TOKEN environment variable must be set');
    }
    this.apiToken = apiToken;
  }

  /**
   * Make authenticated request to ClickUp API
   */
  async request(endpoint, options = {}) {
    const url = `${CLICKUP_API_BASE}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': this.apiToken,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`ClickUp API error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // ========== WORKSPACE & TEAMS ==========

  /**
   * Get authorized teams/workspaces
   */
  async getTeams() {
    return this.request('/team');
  }

  /**
   * Get spaces in a team
   */
  async getSpaces(teamId) {
    return this.request(`/team/${teamId}/space`);
  }

  /**
   * Get folders in a space
   */
  async getFolders(spaceId) {
    return this.request(`/space/${spaceId}/folder`);
  }

  /**
   * Get lists in a folder
   */
  async getLists(folderId) {
    return this.request(`/folder/${folderId}/list`);
  }

  /**
   * Get folderless lists in a space
   */
  async getFolderlessLists(spaceId) {
    return this.request(`/space/${spaceId}/list`);
  }

  // ========== TASKS ==========

  /**
   * Get tasks from a list
   */
  async getTasks(listId, options = {}) {
    const params = new URLSearchParams({
      archived: 'false',
      subtasks: 'true',
      include_closed: 'false',
      ...options
    });
    
    return this.request(`/list/${listId}/task?${params}`);
  }

  /**
   * Get a single task by ID
   */
  async getTask(taskId) {
    return this.request(`/task/${taskId}`);
  }

  /**
   * Create a new task
   */
  async createTask(listId, taskData) {
    return this.request(`/list/${listId}/task`, {
      method: 'POST',
      body: JSON.stringify(taskData)
    });
  }

  /**
   * Update a task
   */
  async updateTask(taskId, updates) {
    return this.request(`/task/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  /**
   * Delete a task
   */
  async deleteTask(taskId) {
    return this.request(`/task/${taskId}`, {
      method: 'DELETE'
    });
  }

  /**
   * Add comment to a task
   */
  async addTaskComment(taskId, commentText) {
    return this.request(`/task/${taskId}/comment`, {
      method: 'POST',
      body: JSON.stringify({
        comment_text: commentText
      })
    });
  }

  /**
   * Get task comments
   */
  async getTaskComments(taskId) {
    return this.request(`/task/${taskId}/comment`);
  }

  // ========== BULK OPERATIONS ==========

  /**
   * Create multiple tasks from a project plan
   */
  async createTasksFromPlan(listId, tasks) {
    const results = [];
    
    for (const task of tasks) {
      try {
        const taskData = {
          name: task.name || task.title,
          description: task.description || '',
          priority: this.mapPriority(task.priority),
          tags: task.tags || [],
          due_date: task.due_date_offset_days 
            ? Date.now() + (task.due_date_offset_days * 24 * 60 * 60 * 1000)
            : null
        };

        const created = await this.createTask(listId, taskData);
        results.push({ success: true, task: created });
      } catch (error) {
        results.push({ success: false, task: task.name, error: error.message });
      }
    }

    return results;
  }

  /**
   * Map priority string to ClickUp priority number
   */
  mapPriority(priority) {
    const map = {
      'urgent': 1,
      'high': 2,
      'normal': 3,
      'medium': 3,
      'low': 4
    };
    return map[priority?.toLowerCase()] || 3;
  }

  // ========== REPORTING ==========

  /**
   * Get workspace summary for team sync
   */
  async getWorkspaceSummary(teamId) {
    const spaces = await this.getSpaces(teamId);
    const summary = {
      teamId,
      spaces: [],
      totalTasks: 0,
      tasksByStatus: {}
    };

    for (const space of spaces.spaces || []) {
      const spaceData = {
        id: space.id,
        name: space.name,
        lists: [],
        taskCount: 0
      };

      // Get folderless lists
      const lists = await this.getFolderlessLists(space.id);
      
      for (const list of lists.lists || []) {
        const tasks = await this.getTasks(list.id);
        const taskList = tasks.tasks || [];
        
        spaceData.lists.push({
          id: list.id,
          name: list.name,
          taskCount: taskList.length
        });

        spaceData.taskCount += taskList.length;
        summary.totalTasks += taskList.length;

        // Count by status
        taskList.forEach(task => {
          const status = task.status?.status || 'unknown';
          summary.tasksByStatus[status] = (summary.tasksByStatus[status] || 0) + 1;
        });
      }

      summary.spaces.push(spaceData);
    }

    return summary;
  }

  /**
   * Get recent activity for a list
   */
  async getRecentTasks(listId, days = 7) {
    const since = Date.now() - (days * 24 * 60 * 60 * 1000);
    
    const tasks = await this.getTasks(listId, {
      date_updated_gt: since,
      order_by: 'updated',
      reverse: true
    });

    return tasks.tasks || [];
  }

  /**
   * Get tasks by assignee
   */
  async getTasksByAssignee(listId, assigneeId) {
    const tasks = await this.getTasks(listId, {
      assignees: [assigneeId]
    });

    return tasks.tasks || [];
  }

  /**
   * Get overdue tasks
   */
  async getOverdueTasks(listId) {
    const now = Date.now();
    const tasks = await this.getTasks(listId);
    
    return (tasks.tasks || []).filter(task => {
      return task.due_date && parseInt(task.due_date) < now && task.status?.type !== 'closed';
    });
  }
}

module.exports = { ClickUpClient };
