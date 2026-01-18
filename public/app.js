/**
 * Phonologic Operations Portal - Frontend Application
 * 
 * Authentication: Restricted to @phonologic.ca Google SSO
 * Admin System: Admins can manage other users' admin status
 * 
 * @module public/app
 */

const app = {
  /** @type {object|null} Current user info */
  user: null,
  /** @type {boolean} Whether user is authenticated */
  isAuthenticated: false,
  /** @type {boolean} Whether current user has admin privileges */
  isAdmin: false,

  /**
   * Initialize the application
   * Checks auth status and sets up the UI
   */
  async init() {
    // Check for auth errors/success in URL
    this.handleAuthRedirect();
    
    // Check authentication status
    await this.checkAuth();
  },

  /**
   * Check authentication status and admin privileges
   */
  async checkAuth() {
    try {
      const res = await fetch('/api/auth/google?action=verify', {
        credentials: 'include'
      });
      const data = await res.json();
      
      if (data.authenticated) {
        this.isAuthenticated = true;
        this.user = data.user;
        
        // Check admin status
        await this.checkAdminStatus();
        
        this.showMainApp();
      } else {
        this.isAuthenticated = false;
        this.showLoginScreen();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      this.showLoginScreen();
    }
  },

  /**
   * Check if current user has admin privileges
   */
  async checkAdminStatus() {
    try {
      const res = await fetch('/api/users?action=me', { credentials: 'include' });
      const data = await res.json();
      this.isAdmin = data.isAdmin || false;
    } catch (error) {
      console.error('Admin check failed:', error);
      this.isAdmin = false;
    }
  },

  // Handle auth redirect params
  handleAuthRedirect() {
    const params = new URLSearchParams(window.location.search);
    const authError = params.get('auth_error');
    const authSuccess = params.get('auth_success');
    
    if (authError) {
      this.showAuthError(decodeURIComponent(authError));
      window.history.replaceState({}, '', '/');
    }
    
    if (authSuccess) {
      window.history.replaceState({}, '', '/');
    }
  },

  // Show login screen
  showLoginScreen() {
    document.getElementById('loginScreen').style.display = 'flex';
    document.getElementById('mainApp').style.display = 'none';
  },

  // Show main app
  showMainApp() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('mainApp').style.display = 'flex';
    
    // Update user info in header
    if (this.user) {
      const avatar = document.getElementById('userAvatar');
      const email = document.getElementById('userEmail');
      if (avatar) avatar.src = this.user.picture || '';
      if (email) email.textContent = this.user.email;
    }

    // Setup form handlers
    this.setupForms();
  },

  // Show access denied screen (full page, hides everything else)
  showAuthError(message) {
    document.getElementById('authErrorMessage').textContent = message;
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('mainApp').style.display = 'none';
    document.getElementById('accessDeniedScreen').style.display = 'flex';
  },

  // Close access denied screen and return to login
  closeAuthError() {
    document.getElementById('accessDeniedScreen').style.display = 'none';
    this.showLoginScreen();
  },

  // Logout
  async logout() {
    try {
      await fetch('/api/auth/google?action=logout', {
        credentials: 'include'
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
    this.isAuthenticated = false;
    this.user = null;
    this.showLoginScreen();
  },

  // Page navigation
  showPage(pageId) {
    // Update nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.classList.toggle('active', tab.dataset.page === pageId);
    });

    // Show/hide pages
    document.querySelectorAll('.portal-main').forEach(page => {
      page.style.display = page.id === `page-${pageId}` ? 'block' : 'none';
    });

    // Load page-specific content
    switch (pageId) {
      case 'home':
        this.loadLatestAnnouncement();
        break;
      case 'team':
        this.loadUsers();
        break;
      case 'announcements':
        this.loadAnnouncements();
        break;
      case 'wiki':
        this.loadWiki();
        break;
      case 'goals':
        this.loadGoals();
        break;
      case 'metrics':
        this.loadMetrics();
        break;
      case 'aihub':
        this.refreshOrchestratorStatus();
        break;
    }
  },

  async loadLatestAnnouncement() {
    try {
      const res = await fetch('/api/announcements?action=latest', { credentials: 'include' });
      const data = await res.json();
      
      const section = document.getElementById('latest-announcement-section');
      if (!data.announcement) {
        section.style.display = 'none';
        return;
      }

      const ann = data.announcement;
      document.getElementById('latest-announcement-title').textContent = ann.title;
      document.getElementById('latest-announcement-content').textContent = ann.content;
      document.getElementById('latest-announcement-meta').textContent = `${ann.author} • ${this.formatDate(ann.createdAt)}`;
      section.style.display = 'block';
    } catch (error) {
      console.error('Failed to load latest announcement:', error);
    }
  },

  /**
   * Load users for org chart page
   * Shows admin controls if current user is admin
   */
  async loadUsers() {
    const container = document.getElementById('users-list');
    if (!container) return;

    try {
      const res = await fetch('/api/users', { credentials: 'include' });
      const data = await res.json();

      if (!data.users || data.users.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <p>No team members have logged in yet.</p>
            <p class="text-secondary">Users will appear here after they sign in.</p>
          </div>
        `;
        return;
      }

      container.innerHTML = data.users.map(user => `
        <div class="user-card ${user.isAdmin ? 'is-admin' : ''}">
          <img class="user-card-avatar" src="${user.picture || ''}" alt="${user.name}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23334155%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2255%22 font-size=%2240%22 text-anchor=%22middle%22 fill=%22%23fff%22>${user.name.charAt(0).toUpperCase()}</text></svg>'">
          <div class="user-card-info">
            <h4>
              ${user.name}
              ${user.isAdmin ? '<span class="admin-badge">Admin</span>' : ''}
            </h4>
            <p class="user-card-email">${user.email}</p>
            <p class="user-card-meta">
              Last login: ${new Date(user.lastLogin).toLocaleDateString('en-US', { 
                month: 'short', day: 'numeric', year: 'numeric', 
                hour: 'numeric', minute: '2-digit' 
              })}
              ${user.loginCount > 1 ? ` • ${user.loginCount} logins` : ''}
            </p>
          </div>
          ${this.isAdmin && user.email !== this.user.email ? `
            <button class="btn btn-sm ${user.isAdmin ? 'btn-secondary' : 'btn-primary'}" 
                    onclick="app.toggleAdmin('${user.email}', ${!user.isAdmin})">
              ${user.isAdmin ? 'Remove Admin' : 'Make Admin'}
            </button>
          ` : ''}
        </div>
      `).join('');
    } catch (error) {
      console.error('Failed to load users:', error);
      container.innerHTML = '<p class="error">Failed to load team members</p>';
    }
  },

  /**
   * Toggle admin status for a user (admin only)
   */
  async toggleAdmin(email, makeAdmin) {
    try {
      const res = await fetch('/api/users?action=set-admin', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, isAdmin: makeAdmin })
      });
      const data = await res.json();
      if (data.success) {
        await this.loadUsers();
      } else {
        alert('Failed to update admin status: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to toggle admin:', error);
      alert('Failed to update admin status');
    }
  },

  // ==================== ANNOUNCEMENTS ====================
  
  async loadAnnouncements() {
    const container = document.getElementById('announcements-list');
    if (!container) return;

    // Show admin form if admin
    if (this.isAdmin) {
      document.getElementById('announcement-form-section').style.display = 'block';
    }

    try {
      const res = await fetch('/api/announcements', { credentials: 'include' });
      const data = await res.json();

      if (!data.announcements || data.announcements.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <p>No announcements yet.</p>
            ${this.isAdmin ? '<p class="text-secondary">Post the first announcement above!</p>' : ''}
          </div>
        `;
        return;
      }

      container.innerHTML = data.announcements.map(ann => {
        const comments = ann.comments || [];
        const commentsHtml = comments.length > 0 
          ? comments.map(c => `
              <div class="comment-item">
                <div class="comment-header">
                  <span class="comment-author">${c.author}</span>
                  <span class="comment-date">${this.formatDate(c.createdAt)}</span>
                </div>
                <div class="comment-content">${c.content}</div>
                ${this.isAdmin || c.authorEmail === this.user?.email ? `
                  <div class="comment-actions">
                    <button class="btn btn-sm btn-danger" onclick="app.deleteComment('${ann.id}', '${c.id}')">Delete</button>
                  </div>
                ` : ''}
              </div>
            `).join('')
          : '<p class="no-comments">No comments yet</p>';

        return `
          <div class="announcement-card type-${ann.type}">
            <div class="announcement-header">
              <h4>${ann.title}</h4>
              <span class="announcement-meta">${ann.author} • ${this.formatDate(ann.createdAt)}</span>
            </div>
            <div class="announcement-content">${ann.content}</div>
            ${this.isAdmin ? `
              <div class="announcement-actions">
                <button class="btn btn-sm btn-danger" onclick="app.deleteAnnouncement('${ann.id}')">Delete</button>
              </div>
            ` : ''}
            <div class="comments-section">
              <div class="comments-header">
                <h5>Comments (${comments.length})</h5>
              </div>
              <div class="comments-list">${commentsHtml}</div>
              <form class="comment-form" onsubmit="app.addComment(event, '${ann.id}')">
                <input type="text" placeholder="Add a comment..." id="comment-input-${ann.id}" required>
                <button type="submit" class="btn btn-sm btn-primary">Post</button>
              </form>
            </div>
          </div>
        `;
      }).join('');
    } catch (error) {
      console.error('Failed to load announcements:', error);
      container.innerHTML = '<p class="error">Failed to load announcements</p>';
    }
  },

  async postAnnouncement(e) {
    e.preventDefault();
    const title = document.getElementById('announcement-title').value;
    const content = document.getElementById('announcement-content').value;
    const type = document.getElementById('announcement-type').value;

    try {
      const res = await fetch('/api/announcements', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, type })
      });
      const data = await res.json();
      if (data.success) {
        document.getElementById('announcement-form').reset();
        await this.loadAnnouncements();
      } else {
        alert('Failed to post: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to post announcement:', error);
      alert('Failed to post announcement');
    }
  },

  async deleteAnnouncement(id) {
    if (!confirm('Delete this announcement?')) return;
    try {
      await fetch(`/api/announcements?id=${id}`, { method: 'DELETE', credentials: 'include' });
      await this.loadAnnouncements();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  },

  async addComment(e, announcementId) {
    e.preventDefault();
    const input = document.getElementById(`comment-input-${announcementId}`);
    const content = input.value.trim();
    if (!content) return;

    try {
      const res = await fetch(`/api/announcements?action=comment&id=${announcementId}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });
      const data = await res.json();
      if (data.success) {
        input.value = '';
        await this.loadAnnouncements();
      } else {
        alert('Failed to add comment: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
      alert('Failed to add comment');
    }
  },

  async deleteComment(announcementId, commentId) {
    if (!confirm('Delete this comment?')) return;
    try {
      await fetch(`/api/announcements?id=${announcementId}&commentId=${commentId}`, { 
        method: 'DELETE', 
        credentials: 'include' 
      });
      await this.loadAnnouncements();
    } catch (error) {
      console.error('Failed to delete comment:', error);
    }
  },

  // ==================== WIKI ====================
  
  wikiPages: [],
  currentWikiPage: null,
  wikiFilter: 'all',

  async loadWiki() {
    // Show admin controls
    if (this.isAdmin) {
      document.getElementById('wiki-new-btn').style.display = 'block';
    }
    await this.loadWikiPages();
  },

  async loadWikiPages() {
    const container = document.getElementById('wiki-pages-list');
    try {
      const res = await fetch('/api/wiki', { credentials: 'include' });
      const data = await res.json();
      this.wikiPages = data.pages || [];
      this.renderWikiList();
    } catch (error) {
      console.error('Failed to load wiki:', error);
      container.innerHTML = '<p class="error">Failed to load wiki pages</p>';
    }
  },

  renderWikiList() {
    const container = document.getElementById('wiki-pages-list');
    const filtered = this.wikiFilter === 'all' 
      ? this.wikiPages 
      : this.wikiPages.filter(p => p.category === this.wikiFilter);

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>No wiki pages yet.</p>
          ${this.isAdmin ? '<p class="text-secondary">Create the first page!</p>' : ''}
        </div>
      `;
      return;
    }

    const catMeta = {
      'getting-started': { name: 'Getting Started', desc: 'Essential info for new team members', order: 1 },
      'development': { name: 'Development', desc: 'Technical docs and engineering', order: 2 },
      'product': { name: 'Product', desc: 'Features, curriculum, and roadmap', order: 3 },
      'operations': { name: 'Operations', desc: 'Deployment and business ops', order: 4 },
      'analytics': { name: 'Analytics', desc: 'Data and reporting', order: 5 },
      'policies': { name: 'Policies', desc: 'HR and company guidelines', order: 6 }
    };

    // If showing all, group by department
    if (this.wikiFilter === 'all') {
      const grouped = {};
      filtered.forEach(page => {
        const cat = page.category || 'other';
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(page);
      });

      const sortedCats = Object.keys(grouped).sort((a, b) => 
        (catMeta[a]?.order || 99) - (catMeta[b]?.order || 99)
      );

      container.innerHTML = sortedCats.map(cat => {
        const meta = catMeta[cat] || { name: cat, desc: '' };
        const pages = grouped[cat].sort((a, b) => a.title.localeCompare(b.title));
        return `
          <div class="wiki-department-section">
            <div class="wiki-department-header">
              <h3>${meta.name}</h3>
              <span class="wiki-department-desc">${meta.desc}</span>
            </div>
            <div class="wiki-department-pages">
              ${pages.map(page => `
                <div class="wiki-page-item" onclick="app.viewWikiPage('${page.id}')">
                  <h4>${page.title}</h4>
                  <span class="tool-arrow">→</span>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }).join('');
    } else {
      // Single category view
      const meta = catMeta[this.wikiFilter] || { name: this.wikiFilter };
      container.innerHTML = filtered.sort((a, b) => a.title.localeCompare(b.title)).map(page => `
        <div class="wiki-page-item" onclick="app.viewWikiPage('${page.id}')">
          <h4>${page.title}</h4>
          <span class="tool-arrow">→</span>
        </div>
      `).join('');
    }
  },

  filterWiki(category) {
    this.wikiFilter = category;
    document.querySelectorAll('.wiki-cat-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.category === category);
    });
    document.getElementById('wiki-pages-list').style.display = 'flex';
    document.getElementById('wiki-page-view').style.display = 'none';
    document.getElementById('wiki-editor').style.display = 'none';
    this.renderWikiList();
  },

  async viewWikiPage(id) {
    try {
      const res = await fetch(`/api/wiki?id=${id}`, { credentials: 'include' });
      const data = await res.json();
      this.currentWikiPage = data.page;

      document.getElementById('wiki-pages-list').style.display = 'none';
      document.getElementById('wiki-editor').style.display = 'none';
      document.getElementById('wiki-page-view').style.display = 'block';

      document.getElementById('wiki-view-title').textContent = data.page.title;
      document.getElementById('wiki-view-category').textContent = data.page.category;
      document.getElementById('wiki-view-updated').textContent = 'Updated ' + this.formatDate(data.page.updatedAt);
      document.getElementById('wiki-view-content').innerHTML = this.renderMarkdown(data.page.content);

      if (this.isAdmin) {
        document.getElementById('wiki-page-actions').style.display = 'flex';
      }
    } catch (error) {
      console.error('Failed to load page:', error);
    }
  },

  showWikiEditor(page = null) {
    document.getElementById('wiki-pages-list').style.display = 'none';
    document.getElementById('wiki-page-view').style.display = 'none';
    document.getElementById('wiki-editor').style.display = 'block';

    if (page) {
      document.getElementById('wiki-page-id').value = page.id;
      document.getElementById('wiki-page-title').value = page.title;
      document.getElementById('wiki-page-category').value = page.category;
      document.getElementById('wiki-page-content').value = page.content;
    } else {
      document.getElementById('wiki-form').reset();
      document.getElementById('wiki-page-id').value = '';
    }
  },

  editWikiPage() {
    if (this.currentWikiPage) {
      this.showWikiEditor(this.currentWikiPage);
    }
  },

  cancelWikiEdit() {
    document.getElementById('wiki-editor').style.display = 'none';
    document.getElementById('wiki-pages-list').style.display = 'flex';
    this.currentWikiPage = null;
  },

  async saveWikiPage(e) {
    e.preventDefault();
    const id = document.getElementById('wiki-page-id').value || undefined;
    const title = document.getElementById('wiki-page-title').value;
    const category = document.getElementById('wiki-page-category').value;
    const content = document.getElementById('wiki-page-content').value;

    try {
      const res = await fetch('/api/wiki', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, title, category, content })
      });
      const data = await res.json();
      if (data.success) {
        this.cancelWikiEdit();
        await this.loadWikiPages();
      } else {
        alert('Failed to save: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to save wiki page:', error);
      alert('Failed to save page');
    }
  },

  async deleteWikiPage() {
    if (!this.currentWikiPage || !confirm('Delete this wiki page?')) return;
    try {
      await fetch(`/api/wiki?id=${this.currentWikiPage.id}`, { method: 'DELETE', credentials: 'include' });
      this.currentWikiPage = null;
      document.getElementById('wiki-page-view').style.display = 'none';
      document.getElementById('wiki-pages-list').style.display = 'flex';
      await this.loadWikiPages();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  },

  // ==================== GOALS ====================
  
  currentGoal: null,

  async loadGoals() {
    const container = document.getElementById('goals-list');
    if (this.isAdmin) {
      document.getElementById('goals-add-btn').style.display = 'inline-block';
    }

    try {
      const res = await fetch('/api/goals', { credentials: 'include' });
      const data = await res.json();

      if (!data.goals || data.goals.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <p>No goals defined yet.</p>
            ${this.isAdmin ? '<p class="text-secondary">Add your first company goal!</p>' : ''}
          </div>
        `;
        return;
      }

      const statusLabels = { 'on-track': 'On Track', 'at-risk': 'At Risk', 'behind': 'Behind', 'completed': 'Completed' };
      container.innerHTML = data.goals.map(goal => `
        <div class="goal-card">
          <div class="goal-header">
            <h4>${goal.title}</h4>
            <span class="goal-status ${goal.status}">${statusLabels[goal.status] || goal.status}</span>
          </div>
          ${goal.description ? `<p class="goal-description">${goal.description}</p>` : ''}
          <div class="goal-progress">
            <div class="goal-progress-bar">
              <div class="goal-progress-fill" style="width: ${goal.progress}%"></div>
            </div>
          </div>
          <div class="goal-meta">
            <span>${goal.quarter} • ${goal.progress}% complete</span>
            <div class="goal-actions">
              ${goal.clickupLink ? `<a href="${goal.clickupLink}" target="_blank" class="btn btn-sm btn-secondary">ClickUp →</a>` : ''}
              ${this.isAdmin ? `
                <button class="btn btn-sm btn-secondary" onclick="app.editGoal('${goal.id}')">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="app.deleteGoal('${goal.id}')">Delete</button>
              ` : ''}
            </div>
          </div>
        </div>
      `).join('');
    } catch (error) {
      console.error('Failed to load goals:', error);
      container.innerHTML = '<p class="error">Failed to load goals</p>';
    }
  },

  showGoalForm(goal = null) {
    document.getElementById('goal-form-section').style.display = 'block';
    if (goal) {
      document.getElementById('goal-id').value = goal.id;
      document.getElementById('goal-title').value = goal.title;
      document.getElementById('goal-description').value = goal.description || '';
      document.getElementById('goal-quarter').value = goal.quarter;
      document.getElementById('goal-status').value = goal.status;
      document.getElementById('goal-progress').value = goal.progress;
      document.getElementById('goal-clickup-link').value = goal.clickupLink || '';
    } else {
      document.getElementById('goal-form').reset();
      document.getElementById('goal-id').value = '';
    }
  },

  async editGoal(id) {
    try {
      const res = await fetch('/api/goals', { credentials: 'include' });
      const data = await res.json();
      const goal = data.goals.find(g => g.id === id);
      if (goal) this.showGoalForm(goal);
    } catch (error) {
      console.error('Failed to load goal:', error);
    }
  },

  cancelGoalEdit() {
    document.getElementById('goal-form-section').style.display = 'none';
    document.getElementById('goal-form').reset();
  },

  async saveGoal(e) {
    e.preventDefault();
    const goal = {
      id: document.getElementById('goal-id').value || undefined,
      title: document.getElementById('goal-title').value,
      description: document.getElementById('goal-description').value,
      quarter: document.getElementById('goal-quarter').value,
      status: document.getElementById('goal-status').value,
      progress: document.getElementById('goal-progress').value,
      clickupLink: document.getElementById('goal-clickup-link').value
    };

    try {
      const res = await fetch('/api/goals', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(goal)
      });
      const data = await res.json();
      if (data.success) {
        this.cancelGoalEdit();
        await this.loadGoals();
      } else {
        alert('Failed to save: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to save goal:', error);
      alert('Failed to save goal');
    }
  },

  async deleteGoal(id) {
    if (!confirm('Delete this goal?')) return;
    try {
      await fetch(`/api/goals?id=${id}`, { method: 'DELETE', credentials: 'include' });
      await this.loadGoals();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  },

  // ==================== METRICS ====================
  
  async loadMetrics() {
    try {
      // Load stats from various endpoints
      const [usersRes, wikiRes, goalsRes, annRes] = await Promise.all([
        fetch('/api/users', { credentials: 'include' }),
        fetch('/api/wiki', { credentials: 'include' }),
        fetch('/api/goals?action=stats', { credentials: 'include' }),
        fetch('/api/announcements', { credentials: 'include' })
      ]);

      const [users, wiki, goals, ann] = await Promise.all([
        usersRes.json(), wikiRes.json(), goalsRes.json(), annRes.json()
      ]);

      document.getElementById('stat-team-size').textContent = users.users?.length || 0;
      document.getElementById('stat-wiki-pages').textContent = wiki.pages?.length || 0;
      document.getElementById('stat-goals-complete').textContent = goals.stats?.completed || 0;
      document.getElementById('stat-announcements').textContent = ann.announcements?.length || 0;
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  },

  // ==================== UTILITIES ====================
  
  formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  },

  /**
   * Render markdown to HTML with XSS protection
   * SECURITY: Escapes HTML entities before processing markdown
   * @param {string} text - Raw markdown text
   * @returns {string} Safe HTML
   */
  renderMarkdown(text) {
    if (!text) return '';
    
    // SECURITY: Escape HTML entities first to prevent XSS
    const escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
    
    // Then apply markdown formatting
    return escaped
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/^### (.*$)/gm, '<h4>$1</h4>')
      .replace(/^## (.*$)/gm, '<h3>$1</h3>')
      .replace(/^# (.*$)/gm, '<h2>$1</h2>')
      .replace(/^\- (.*$)/gm, '<li>$1</li>')
      .replace(/\n/g, '<br>');
  },

  closeConfirm() {
    document.getElementById('confirmModal').classList.add('hidden');
  },

  // Setup form handlers
  setupForms() {
    document.getElementById('announcement-form')?.addEventListener('submit', (e) => this.postAnnouncement(e));
    document.getElementById('wiki-form')?.addEventListener('submit', (e) => this.saveWikiPage(e));
    document.getElementById('goal-form')?.addEventListener('submit', (e) => this.saveGoal(e));
  },

  // ==================== AI HUB ====================
  
  orchestratorBaseUrl: '/api/orchestrator',

  async refreshOrchestratorStatus() {
    const healthEl = document.getElementById('orchestrator-health');
    const statusEl = document.getElementById('orchestrator-status-text');
    const uptimeEl = document.getElementById('orchestrator-uptime');
    
    try {
      const res = await fetch(`${this.orchestratorBaseUrl}/status`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        healthEl.className = 'status-indicator healthy';
        statusEl.textContent = 'Operational';
        
        const uptime = Math.floor(data.uptime_seconds || 0);
        const hours = Math.floor(uptime / 3600);
        const mins = Math.floor((uptime % 3600) / 60);
        uptimeEl.textContent = `${hours}h ${mins}m`;
        
        document.getElementById('orchestrator-teams').textContent = data.teams?.length || 3;
        const totalAgents = data.teams?.reduce((sum, t) => sum + (t.agents?.length || 0), 0) || 9;
        document.getElementById('orchestrator-agents').textContent = totalAgents;
      } else {
        throw new Error('Not available');
      }
    } catch (error) {
      healthEl.className = 'status-indicator unhealthy';
      statusEl.textContent = 'Offline';
      uptimeEl.textContent = '--';
    }
  },

  async queryBrain() {
    const query = document.getElementById('brain-query-input').value;
    const category = document.getElementById('brain-category-select').value;
    
    if (!query.trim()) {
      alert('Please enter a search query');
      return;
    }
    
    try {
      const res = await fetch(`${this.orchestratorBaseUrl}/brain/query`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, category: category || null })
      });
      
      if (res.ok) {
        const data = await res.json();
        document.getElementById('brain-results').style.display = 'block';
        document.getElementById('brain-results-content').textContent = JSON.stringify(data.results, null, 2);
      } else {
        throw new Error('Query failed');
      }
    } catch (error) {
      console.error('Brain query error:', error);
      document.getElementById('brain-results').style.display = 'block';
      document.getElementById('brain-results-content').textContent = 'Error: Orchestrator not available. Ensure the orchestrator service is running.';
    }
  },

  async getBrainInfo(type) {
    try {
      const res = await fetch(`${this.orchestratorBaseUrl}/brain/${type}`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        document.getElementById('brain-results').style.display = 'block';
        document.getElementById('brain-results-content').textContent = data.content || JSON.stringify(data, null, 2);
      } else {
        throw new Error('Failed to fetch');
      }
    } catch (error) {
      document.getElementById('brain-results').style.display = 'block';
      document.getElementById('brain-results-content').textContent = 'Error: Orchestrator not available';
    }
  },

  showMarketingForm() {
    const panel = document.getElementById('aihub-task-panel');
    const title = document.getElementById('aihub-task-title');
    const form = document.getElementById('aihub-task-form');
    
    title.textContent = 'Run Marketing Campaign';
    form.innerHTML = `
      <div class="form-group">
        <label>Product Concept *</label>
        <textarea id="task-product-concept" placeholder="Describe your product or service..." required></textarea>
      </div>
      <div class="form-group">
        <label>Target Market</label>
        <input type="text" id="task-target-market" value="Global" placeholder="e.g., Philippines, North America">
      </div>
      <div class="form-group">
        <label>Brand Guidelines</label>
        <textarea id="task-brand-guidelines" placeholder="Optional: Paste brand guidelines or key messaging..."></textarea>
      </div>
      <div class="form-group">
        <label>Campaign Goals (comma-separated)</label>
        <input type="text" id="task-campaign-goals" placeholder="e.g., Brand awareness, Lead generation">
      </div>
      <button class="btn btn-primary" onclick="app.runMarketingCampaign()">Run Campaign</button>
    `;
    
    panel.style.display = 'block';
    document.getElementById('aihub-task-result').style.display = 'none';
  },

  async runMarketingCampaign() {
    const payload = {
      product_concept: document.getElementById('task-product-concept').value,
      target_market: document.getElementById('task-target-market').value || 'Global',
      brand_guidelines: document.getElementById('task-brand-guidelines').value || null,
      campaign_goals: document.getElementById('task-campaign-goals').value.split(',').map(g => g.trim()).filter(Boolean)
    };
    
    if (!payload.product_concept) {
      alert('Product concept is required');
      return;
    }
    
    try {
      document.getElementById('aihub-task-result').style.display = 'block';
      document.getElementById('aihub-task-result-content').textContent = 'Running campaign... This may take a few minutes.';
      
      const res = await fetch(`${this.orchestratorBaseUrl}/marketing/campaign`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      document.getElementById('aihub-task-result-content').textContent = JSON.stringify(data, null, 2);
    } catch (error) {
      document.getElementById('aihub-task-result-content').textContent = 'Error: ' + error.message;
    }
  },

  showOnboardingForm() {
    const panel = document.getElementById('aihub-task-panel');
    const title = document.getElementById('aihub-task-title');
    const form = document.getElementById('aihub-task-form');
    
    title.textContent = 'Run Onboarding';
    form.innerHTML = `
      <div class="form-group">
        <label>Type *</label>
        <select id="task-entity-type">
          <option value="employee">Employee</option>
          <option value="client">Client</option>
        </select>
      </div>
      <div class="form-group">
        <label>Name *</label>
        <input type="text" id="task-name" placeholder="Full name" required>
      </div>
      <div class="form-group">
        <label>Email *</label>
        <input type="email" id="task-email" placeholder="email@example.com" required>
      </div>
      <div class="form-group">
        <label>Role</label>
        <input type="text" id="task-role" placeholder="e.g., Software Engineer">
      </div>
      <div class="form-group">
        <label>Department</label>
        <input type="text" id="task-department" placeholder="e.g., Engineering">
      </div>
      <button class="btn btn-primary" onclick="app.runOnboarding()">Run Onboarding</button>
    `;
    
    panel.style.display = 'block';
    document.getElementById('aihub-task-result').style.display = 'none';
  },

  async runOnboarding() {
    const payload = {
      entity_type: document.getElementById('task-entity-type').value,
      name: document.getElementById('task-name').value,
      email: document.getElementById('task-email').value,
      role: document.getElementById('task-role').value || null,
      department: document.getElementById('task-department').value || null
    };
    
    if (!payload.name || !payload.email) {
      alert('Name and email are required');
      return;
    }
    
    try {
      document.getElementById('aihub-task-result').style.display = 'block';
      document.getElementById('aihub-task-result-content').textContent = 'Running onboarding workflow...';
      
      const res = await fetch(`${this.orchestratorBaseUrl}/pm/onboard`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      document.getElementById('aihub-task-result-content').textContent = JSON.stringify(data, null, 2);
    } catch (error) {
      document.getElementById('aihub-task-result-content').textContent = 'Error: ' + error.message;
    }
  },

  showProgressReportForm() {
    const panel = document.getElementById('aihub-task-panel');
    const title = document.getElementById('aihub-task-title');
    const form = document.getElementById('aihub-task-form');
    
    title.textContent = 'Send Progress Report';
    form.innerHTML = `
      <div class="form-group">
        <label>Project Name *</label>
        <input type="text" id="task-project-name" placeholder="e.g., PhonoLogic App Development" required>
      </div>
      <div class="form-group">
        <label>Recipient Name *</label>
        <input type="text" id="task-recipient-name" placeholder="Full name" required>
      </div>
      <div class="form-group">
        <label>Recipient Email *</label>
        <input type="email" id="task-recipient-email" placeholder="email@example.com" required>
      </div>
      <button class="btn btn-primary" onclick="app.sendProgressReport()">Send Report</button>
    `;
    
    panel.style.display = 'block';
    document.getElementById('aihub-task-result').style.display = 'none';
  },

  async sendProgressReport() {
    const payload = {
      project_name: document.getElementById('task-project-name').value,
      recipient_name: document.getElementById('task-recipient-name').value,
      recipient_email: document.getElementById('task-recipient-email').value
    };
    
    if (!payload.project_name || !payload.recipient_email) {
      alert('Project name and recipient email are required');
      return;
    }
    
    try {
      document.getElementById('aihub-task-result').style.display = 'block';
      document.getElementById('aihub-task-result-content').textContent = 'Generating and sending report...';
      
      const res = await fetch(`${this.orchestratorBaseUrl}/pm/progress-report`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      document.getElementById('aihub-task-result-content').textContent = JSON.stringify(data, null, 2);
    } catch (error) {
      document.getElementById('aihub-task-result-content').textContent = 'Error: ' + error.message;
    }
  },

  showBrowserAnalyzeForm() {
    const panel = document.getElementById('aihub-task-panel');
    const title = document.getElementById('aihub-task-title');
    const form = document.getElementById('aihub-task-form');
    
    title.textContent = 'Analyze Slides';
    form.innerHTML = `
      <div class="form-group">
        <label>Presentation URL *</label>
        <input type="url" id="task-slide-url" placeholder="https://docs.google.com/presentation/... or https://app.pitch.com/..." required>
      </div>
      <div class="form-group">
        <label>
          <input type="checkbox" id="task-brand-check" checked>
          Check brand compliance
        </label>
      </div>
      <button class="btn btn-primary" onclick="app.analyzeSlides()">Analyze</button>
    `;
    
    panel.style.display = 'block';
    document.getElementById('aihub-task-result').style.display = 'none';
  },

  async analyzeSlides() {
    const payload = {
      url: document.getElementById('task-slide-url').value,
      check_brand_compliance: document.getElementById('task-brand-check').checked
    };
    
    if (!payload.url) {
      alert('Presentation URL is required');
      return;
    }
    
    try {
      document.getElementById('aihub-task-result').style.display = 'block';
      document.getElementById('aihub-task-result-content').textContent = 'Analyzing slides... This may take a moment.';
      
      const res = await fetch(`${this.orchestratorBaseUrl}/browser/analyze`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      document.getElementById('aihub-task-result-content').textContent = JSON.stringify(data, null, 2);
    } catch (error) {
      document.getElementById('aihub-task-result-content').textContent = 'Error: ' + error.message;
    }
  },

  closeTaskPanel() {
    document.getElementById('aihub-task-panel').style.display = 'none';
  }
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => app.init());
