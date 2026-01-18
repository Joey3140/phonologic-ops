/**
 * GitHub Integration for Phonologic Ops Hub
 * Monitors repositories for team sync workflows
 */

const fetch = require('node-fetch');

const GITHUB_API_BASE = 'https://api.github.com';

class GitHubClient {
  constructor(token = process.env.GITHUB_TOKEN) {
    this.token = token;
  }

  /**
   * Make authenticated request to GitHub API
   */
  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${GITHUB_API_BASE}${endpoint}`;
    
    const headers = {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Phonologic-Ops-Hub',
      ...options.headers
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`GitHub API error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // ========== REPOSITORY ==========

  /**
   * Get repository info
   */
  async getRepository(owner, repo) {
    return this.request(`/repos/${owner}/${repo}`);
  }

  /**
   * Get repository branches
   */
  async getBranches(owner, repo) {
    return this.request(`/repos/${owner}/${repo}/branches`);
  }

  // ========== COMMITS ==========

  /**
   * Get recent commits
   */
  async getCommits(owner, repo, options = {}) {
    const params = new URLSearchParams({
      per_page: options.perPage || 30,
      ...(options.since && { since: options.since }),
      ...(options.sha && { sha: options.sha })
    });

    return this.request(`/repos/${owner}/${repo}/commits?${params}`);
  }

  /**
   * Get commit details
   */
  async getCommit(owner, repo, sha) {
    return this.request(`/repos/${owner}/${repo}/commits/${sha}`);
  }

  // ========== PULL REQUESTS ==========

  /**
   * Get pull requests
   */
  async getPullRequests(owner, repo, state = 'all') {
    return this.request(`/repos/${owner}/${repo}/pulls?state=${state}&per_page=30`);
  }

  /**
   * Get pull request details
   */
  async getPullRequest(owner, repo, number) {
    return this.request(`/repos/${owner}/${repo}/pulls/${number}`);
  }

  /**
   * Get pull request reviews
   */
  async getPullRequestReviews(owner, repo, number) {
    return this.request(`/repos/${owner}/${repo}/pulls/${number}/reviews`);
  }

  // ========== ISSUES ==========

  /**
   * Get issues
   */
  async getIssues(owner, repo, state = 'open') {
    return this.request(`/repos/${owner}/${repo}/issues?state=${state}&per_page=30`);
  }

  /**
   * Get issue details
   */
  async getIssue(owner, repo, number) {
    return this.request(`/repos/${owner}/${repo}/issues/${number}`);
  }

  // ========== CONTRIBUTORS ==========

  /**
   * Get repository contributors
   */
  async getContributors(owner, repo) {
    return this.request(`/repos/${owner}/${repo}/contributors`);
  }

  // ========== TEAM SYNC HELPERS ==========

  /**
   * Get comprehensive repo summary for team sync
   */
  async getRepoSummary(owner, repo, sinceDays = 7) {
    const since = new Date(Date.now() - sinceDays * 24 * 60 * 60 * 1000).toISOString();

    const [repoInfo, commits, pullRequests, issues] = await Promise.all([
      this.getRepository(owner, repo),
      this.getCommits(owner, repo, { since }),
      this.getPullRequests(owner, repo, 'all'),
      this.getIssues(owner, repo, 'all')
    ]);

    // Filter recent PRs and issues
    const sinceDate = new Date(since);
    const recentPRs = pullRequests.filter(pr => new Date(pr.updated_at) >= sinceDate);
    const recentIssues = issues.filter(issue => 
      !issue.pull_request && new Date(issue.updated_at) >= sinceDate
    );

    // Group commits by author
    const commitsByAuthor = {};
    commits.forEach(commit => {
      const author = commit.author?.login || commit.commit.author?.name || 'unknown';
      if (!commitsByAuthor[author]) {
        commitsByAuthor[author] = [];
      }
      commitsByAuthor[author].push({
        sha: commit.sha.substring(0, 7),
        message: commit.commit.message.split('\n')[0],
        date: commit.commit.author.date
      });
    });

    return {
      repository: {
        name: repoInfo.full_name,
        description: repoInfo.description,
        defaultBranch: repoInfo.default_branch,
        openIssues: repoInfo.open_issues_count
      },
      period: {
        since: since,
        days: sinceDays
      },
      commits: {
        total: commits.length,
        byAuthor: commitsByAuthor
      },
      pullRequests: {
        total: recentPRs.length,
        open: recentPRs.filter(pr => pr.state === 'open').length,
        merged: recentPRs.filter(pr => pr.merged_at).length,
        items: recentPRs.map(pr => ({
          number: pr.number,
          title: pr.title,
          author: pr.user?.login,
          state: pr.state,
          merged: !!pr.merged_at,
          updatedAt: pr.updated_at
        }))
      },
      issues: {
        total: recentIssues.length,
        open: recentIssues.filter(i => i.state === 'open').length,
        closed: recentIssues.filter(i => i.state === 'closed').length,
        items: recentIssues.map(issue => ({
          number: issue.number,
          title: issue.title,
          author: issue.user?.login,
          state: issue.state,
          labels: issue.labels.map(l => l.name),
          updatedAt: issue.updated_at
        }))
      }
    };
  }

  /**
   * Parse GitHub URL to extract owner and repo
   */
  static parseRepoUrl(url) {
    const match = url.match(/github\.com[\/:]([^\/]+)\/([^\/\.]+)/);
    if (!match) {
      throw new Error('Invalid GitHub repository URL');
    }
    return { owner: match[1], repo: match[2] };
  }
}

module.exports = { GitHubClient };
