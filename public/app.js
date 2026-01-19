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
    
    // Initialize Brain mode toggle (enable contribute for admins)
    this.initBrainModeToggle();
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
        this.initBrainModeToggle();
        // Show brain viewer for admins
        if (this.isAdmin) {
          document.getElementById('brain-viewer-section').style.display = 'block';
        }
        break;
    }
  },

  async loadLatestAnnouncement() {
    const section = document.getElementById('latest-announcement-section');
    if (!section) {
      console.error('[ANNOUNCEMENT] Section element not found');
      return;
    }
    
    try {
      const res = await fetch('/api/announcements?action=latest', { credentials: 'include' });
      const data = await res.json();
      
      console.log('[ANNOUNCEMENT] API response:', data);
      
      if (!data.announcement) {
        console.log('[ANNOUNCEMENT] No announcement in response, hiding section');
        section.style.display = 'none';
        return;
      }

      const ann = data.announcement;
      console.log('[ANNOUNCEMENT] Showing announcement:', ann.title);
      
      document.getElementById('latest-announcement-title').textContent = ann.title;
      document.getElementById('latest-announcement-content').textContent = ann.content;
      document.getElementById('latest-announcement-meta').textContent = `${ann.author} • ${this.formatDate(ann.createdAt)}`;
      section.style.display = 'block';
    } catch (error) {
      console.error('[ANNOUNCEMENT] Failed to load:', error);
      section.style.display = 'none';
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
      'getting-started': { name: 'Getting Started', desc: 'Essential info for new team members', icon: '🚀', order: 1 },
      'development': { name: 'Development', desc: 'Technical docs and engineering', icon: '💻', order: 2 },
      'product': { name: 'Product', desc: 'Features, pricing, and roadmap', icon: '📦', order: 3 },
      'operations': { name: 'Operations', desc: 'Workflows and business processes', icon: '⚙️', order: 4 },
      'analytics': { name: 'Analytics', desc: 'Metrics and reporting', icon: '📊', order: 5 },
      'policies': { name: 'Policies', desc: 'Security and compliance guidelines', icon: '📋', order: 6 }
    };

    // Update sidebar category counts
    this.updateCategoryCounts();

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
        const meta = catMeta[cat] || { name: cat, desc: '', icon: '📄' };
        const pages = grouped[cat].sort((a, b) => a.title.localeCompare(b.title));
        return `
          <div class="wiki-category-group">
            <div class="wiki-category-group-header">
              <span class="wiki-category-group-icon">${meta.icon}</span>
              <div class="wiki-category-group-info">
                <h3>${meta.name}</h3>
                <span>${meta.desc}</span>
              </div>
            </div>
            <div class="wiki-category-group-pages">
              ${pages.map(page => `
                <div class="wiki-page-item" onclick="app.viewWikiPage('${page.id}')">
                  <div class="wiki-page-item-content">
                    <h4>${page.title}</h4>
                  </div>
                  <span class="wiki-page-arrow">→</span>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }).join('');
    } else {
      // Single category view
      container.innerHTML = filtered.sort((a, b) => a.title.localeCompare(b.title)).map(page => `
        <div class="wiki-page-item" onclick="app.viewWikiPage('${page.id}')">
          <div class="wiki-page-item-content">
            <h4>${page.title}</h4>
          </div>
          <span class="wiki-page-arrow">→</span>
        </div>
      `).join('');
    }
  },

  updateCategoryCounts() {
    const counts = {
      'getting-started': 0,
      'development': 0,
      'product': 0,
      'operations': 0,
      'analytics': 0,
      'policies': 0
    };
    
    this.wikiPages.forEach(page => {
      if (counts.hasOwnProperty(page.category)) {
        counts[page.category]++;
      }
    });
    
    Object.keys(counts).forEach(cat => {
      const el = document.getElementById(`count-${cat}`);
      if (el) el.textContent = counts[cat];
    });
  },

  filterWiki(category) {
    this.wikiFilter = category;
    
    // Update sidebar navigation
    document.querySelectorAll('.wiki-nav-item').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.category === category);
    });
    
    // Update section header
    const catMeta = {
      'all': { name: 'All Pages', desc: 'Browse all documentation' },
      'getting-started': { name: 'Getting Started', desc: 'Essential info for new team members' },
      'development': { name: 'Development', desc: 'Technical docs and engineering' },
      'product': { name: 'Product', desc: 'Features, pricing, and roadmap' },
      'operations': { name: 'Operations', desc: 'Workflows and business processes' },
      'analytics': { name: 'Analytics', desc: 'Metrics and reporting' },
      'policies': { name: 'Policies', desc: 'Security and compliance guidelines' }
    };
    
    const meta = catMeta[category] || { name: category, desc: '' };
    document.getElementById('wiki-section-title').textContent = meta.name;
    document.getElementById('wiki-section-desc').textContent = meta.desc;
    
    // Show/hide UI elements
    document.getElementById('wiki-front-door').style.display = 'block';
    document.getElementById('wiki-page-view').style.display = 'none';
    document.getElementById('wiki-editor').style.display = 'none';
    
    this.renderWikiList();
  },

  searchWiki(query) {
    // Ensure wiki pages are loaded
    if (!this.wikiPages || this.wikiPages.length === 0) {
      console.log('[WIKI] No pages loaded yet, loading now...');
      this.loadWikiPages().then(() => this.searchWiki(query));
      return;
    }
    
    if (!query.trim()) {
      this.filterWiki(this.wikiFilter || 'all');
      return;
    }
    
    const q = query.toLowerCase();
    const filtered = this.wikiPages.filter(page => 
      page.title.toLowerCase().includes(q) || 
      (page.content && page.content.toLowerCase().includes(q)) ||
      (page.category && page.category.toLowerCase().includes(q))
    );
    
    document.getElementById('wiki-section-title').textContent = `Search: "${query}"`;
    document.getElementById('wiki-section-desc').textContent = `${filtered.length} result${filtered.length !== 1 ? 's' : ''} found`;
    
    const container = document.getElementById('wiki-pages-list');
    if (filtered.length === 0) {
      container.innerHTML = `<div class="empty-state"><p>No pages match "${query}"</p></div>`;
      return;
    }
    
    container.innerHTML = filtered.map(page => `
      <div class="wiki-page-item" onclick="app.viewWikiPage('${page.id}')">
        <div class="wiki-page-item-content">
          <h4>${page.title}</h4>
          <span class="wiki-page-cat">${this.getCategoryName(page.category)}</span>
        </div>
        <span class="wiki-page-arrow">→</span>
      </div>
    `).join('');
  },

  getCategoryName(cat) {
    const names = {
      'getting-started': '🚀 Getting Started',
      'development': '💻 Development',
      'product': '📦 Product',
      'operations': '⚙️ Operations',
      'analytics': '📊 Analytics',
      'policies': '📋 Policies'
    };
    return names[cat] || cat;
  },

  backToWikiList() {
    document.getElementById('wiki-page-view').style.display = 'none';
    document.getElementById('wiki-front-door').style.display = 'block';
    this.currentWikiPage = null;
  },

  async viewWikiPage(id) {
    try {
      const res = await fetch(`/api/wiki?id=${id}`, { credentials: 'include' });
      const data = await res.json();
      this.currentWikiPage = data.page;

      // Hide front door, show page view
      document.getElementById('wiki-front-door').style.display = 'none';
      document.getElementById('wiki-editor').style.display = 'none';
      document.getElementById('wiki-page-view').style.display = 'block';

      document.getElementById('wiki-view-title').textContent = data.page.title;
      document.getElementById('wiki-view-category').textContent = this.getCategoryName(data.page.category);
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
    document.getElementById('wiki-front-door').style.display = 'none';
    document.getElementById('wiki-page-view').style.display = 'none';
    document.getElementById('wiki-editor').style.display = 'block';

    const headerEl = document.querySelector('.wiki-editor-header h2');
    if (page) {
      headerEl.textContent = 'Edit Page';
      document.getElementById('wiki-page-id').value = page.id;
      document.getElementById('wiki-page-title').value = page.title;
      document.getElementById('wiki-page-category').value = page.category;
      document.getElementById('wiki-page-content').value = page.content;
    } else {
      headerEl.textContent = 'Create New Page';
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
    document.getElementById('wiki-front-door').style.display = 'block';
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
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
    
    // Process markdown tables to HTML tables
    html = this.renderTables(html);
    
    // Process lists (must be done before line breaks)
    html = this.renderLists(html);
    
    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr class="wiki-hr">');
    
    // Headings
    html = html.replace(/^### (.*$)/gm, '<h4 class="wiki-h4">$1</h4>');
    html = html.replace(/^## (.*$)/gm, '<h3 class="wiki-h3">$1</h3>');
    html = html.replace(/^# (.*$)/gm, '<h2 class="wiki-h2">$1</h2>');
    
    // Inline formatting
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/`(.*?)`/g, '<code class="wiki-code">$1</code>');
    
    // Links [text](url)
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="wiki-link">$1</a>');
    
    // Checkboxes
    html = html.replace(/- \[x\] (.*$)/gm, '<div class="wiki-checkbox checked">✓ $1</div>');
    html = html.replace(/- \[ \] (.*$)/gm, '<div class="wiki-checkbox">○ $1</div>');
    
    // Paragraphs - convert double newlines to paragraph breaks
    html = html.replace(/\n\n/g, '</p><p class="wiki-p">');
    
    // Single newlines to line breaks (but not inside tables/lists which are already processed)
    html = html.replace(/\n/g, '<br>');
    
    // Wrap in paragraph
    html = '<p class="wiki-p">' + html + '</p>';
    
    // Clean up empty paragraphs and extra breaks
    html = html.replace(/<p class="wiki-p"><\/p>/g, '');
    html = html.replace(/<p class="wiki-p"><br>/g, '<p class="wiki-p">');
    html = html.replace(/<br><\/p>/g, '</p>');
    html = html.replace(/<p class="wiki-p">(<h[234])/g, '$1');
    html = html.replace(/(<\/h[234]>)<\/p>/g, '$1');
    html = html.replace(/<p class="wiki-p">(<table)/g, '$1');
    html = html.replace(/(<\/table>)<\/p>/g, '$1');
    html = html.replace(/<p class="wiki-p">(<ul)/g, '$1');
    html = html.replace(/(<\/ul>)<\/p>/g, '$1');
    html = html.replace(/<p class="wiki-p">(<hr)/g, '$1');
    html = html.replace(/(wiki-hr">)<\/p>/g, '$1');
    
    return html;
  },

  renderTables(text) {
    const lines = text.split('\n');
    let result = [];
    let inTable = false;
    let tableRows = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Check if this is a table row (starts and ends with |)
      if (line.startsWith('|') && line.endsWith('|')) {
        // Skip separator rows (|---|---|)
        if (line.match(/^\|[\s\-:]+\|$/)) {
          continue;
        }
        
        if (!inTable) {
          inTable = true;
          tableRows = [];
        }
        
        // Parse cells
        const cells = line.slice(1, -1).split('|').map(c => c.trim());
        tableRows.push(cells);
      } else {
        // End of table
        if (inTable) {
          result.push(this.buildTable(tableRows));
          inTable = false;
          tableRows = [];
        }
        result.push(lines[i]);
      }
    }
    
    // Handle table at end of text
    if (inTable) {
      result.push(this.buildTable(tableRows));
    }
    
    return result.join('\n');
  },

  buildTable(rows) {
    if (rows.length === 0) return '';
    
    // Filter out separator rows (cells that are just dashes like "--------")
    const isSeparatorRow = (cells) => cells.every(cell => /^[-:\s]+$/.test(cell) || cell === '');
    const filteredRows = rows.filter(row => !isSeparatorRow(row));
    
    if (filteredRows.length === 0) return '';
    
    let html = '<table class="wiki-table"><thead><tr>';
    
    // First row is header
    filteredRows[0].forEach(cell => {
      html += `<th>${cell}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    // Rest are body rows
    for (let i = 1; i < filteredRows.length; i++) {
      html += '<tr>';
      filteredRows[i].forEach(cell => {
        html += `<td>${cell}</td>`;
      });
      html += '</tr>';
    }
    
    html += '</tbody></table>';
    return html;
  },

  renderLists(text) {
    const lines = text.split('\n');
    let result = [];
    let inList = false;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const listMatch = line.match(/^(\s*)[-*] (.+)$/);
      
      if (listMatch && !line.includes('[x]') && !line.includes('[ ]')) {
        if (!inList) {
          result.push('<ul class="wiki-list">');
          inList = true;
        }
        result.push(`<li>${listMatch[2]}</li>`);
      } else {
        if (inList) {
          result.push('</ul>');
          inList = false;
        }
        result.push(line);
      }
    }
    
    if (inList) {
      result.push('</ul>');
    }
    
    return result.join('\n');
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
      alert('Please enter a question');
      return;
    }
    
    // Show loading state
    const resultsEl = document.getElementById('brain-results');
    const contentEl = document.getElementById('brain-results-content');
    resultsEl.style.display = 'block';
    contentEl.innerHTML = '<div class="brain-loading">🤔 Thinking...</div>';
    
    try {
      // Use chat endpoint for natural language responses
      const res = await fetch(`${this.orchestratorBaseUrl}/brain/chat`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, category: category || null })
      });
      
      if (res.ok) {
        const data = await res.json();
        // Render markdown-style answer
        contentEl.innerHTML = this.renderBrainAnswer(data);
      } else {
        throw new Error('Query failed');
      }
    } catch (error) {
      console.error('Brain query error:', error);
      contentEl.innerHTML = `<div class="brain-error">
        <strong>Could not get an answer.</strong><br>
        The orchestrator service may be offline. Try asking about pricing, team, mission, or product features.
      </div>`;
    }
  },

  renderBrainAnswer(data) {
    let html = '<div class="brain-answer">';
    
    // Main answer with markdown-style rendering
    if (data.answer) {
      let answer = data.answer
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/^• /gm, '<span class="brain-bullet">•</span> ')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
      html += `<p>${answer}</p>`;
    }
    
    // Show sources if available
    if (data.sources?.length > 0) {
      html += `<div class="brain-sources">Sources: ${data.sources.join(', ')}</div>`;
    }
    
    html += '</div>';
    return html;
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

  // Brain Data Viewer (Admin Only)
  brainData: null,
  
  async loadBrainData() {
    if (!this.isAdmin) {
      alert('Admin access required');
      return;
    }
    
    try {
      const res = await fetch(`${this.orchestratorBaseUrl}/brain/full`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to load brain data');
      
      const data = await res.json();
      this.brainData = data;
      
      // Show the content section
      document.getElementById('brain-viewer-content').style.display = 'block';
      
      // Populate each section
      document.getElementById('brain-company-data').textContent = JSON.stringify({
        company_name: data.company_name,
        tagline: data.tagline,
        mission: data.mission,
        vision: data.vision,
        founded_year: data.founded_year,
        headquarters: data.headquarters,
        website: data.website
      }, null, 2);
      
      document.getElementById('brain-timeline-data').textContent = JSON.stringify(data.launch_timeline || {}, null, 2);
      document.getElementById('brain-milestones-data').textContent = JSON.stringify(data.milestones || [], null, 2);
      document.getElementById('brain-team-data').textContent = JSON.stringify(data.team || [], null, 2);
      document.getElementById('brain-products-data').textContent = JSON.stringify(data.products || [], null, 2);
      document.getElementById('brain-pricing-data').textContent = JSON.stringify(data.pricing || {}, null, 2);
      document.getElementById('brain-metrics-data').textContent = JSON.stringify(data.key_metrics || {}, null, 2);
      document.getElementById('brain-redis-data').textContent = JSON.stringify(data.redis_updates || {}, null, 2);
      
    } catch (error) {
      console.error('Failed to load brain data:', error);
      alert('Failed to load brain data. Orchestrator may be offline.');
    }
  },
  
  exportBrainData() {
    if (!this.brainData) {
      alert('Load brain data first');
      return;
    }
    
    const blob = new Blob([JSON.stringify(this.brainData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `phonologic-brain-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  },

  // Brain Curator Chat Functions
  brainMode: 'query',  // Default to query mode
  
  setBrainMode(mode) {
    // Check if user is admin for contribute mode
    if (mode === 'contribute' && !this.isAdmin) {
      alert('Only admins can add information to the Brain.');
      return;
    }
    
    this.brainMode = mode;
    
    // Update UI
    document.getElementById('mode-query').classList.toggle('active', mode === 'query');
    document.getElementById('mode-contribute').classList.toggle('active', mode === 'contribute');
    
    // Update placeholder
    const input = document.getElementById('brain-chat-input');
    input.placeholder = mode === 'query' 
      ? 'Ask anything about PhonoLogic...'
      : 'Add new information (e.g., "Update: we now have 5 pilot schools")...';
  },
  
  initBrainModeToggle() {
    // Enable contribute button for admins
    const contributeBtn = document.getElementById('mode-contribute');
    if (contributeBtn && this.isAdmin) {
      contributeBtn.classList.add('enabled');
    }
  },
  
  async sendBrainChat() {
    const input = document.getElementById('brain-chat-input');
    const mode = this.brainMode;  // Use explicit mode from toggle
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat with mode indicator
    const modeLabel = mode === 'contribute' ? ' [Adding Info]' : '';
    this.addChatMessage(message + modeLabel, 'user');
    input.value = '';
    
    // Show loading
    const loadingId = this.addChatMessage('Thinking...', 'system', true);
    
    try {
      const res = await fetch(`${this.orchestratorBaseUrl}/brain/chat`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, mode })  // Explicit mode, no auto-detect
      });
      
      // Remove loading message
      document.getElementById(loadingId)?.remove();
      
      if (res.ok) {
        const data = await res.json();
        
        // Add response to chat - convert markdown to HTML
        let responseHtml = this.markdownToHtml(data.response);
        
        // If there are conflicts, add action buttons
        if (data.conflicts && data.conflicts.length > 0 && data.contribution_id) {
          responseHtml += `
            <div class="conflict-actions" data-contribution-id="${data.contribution_id}">
              <button class="btn btn-sm btn-primary" onclick="app.resolveBrainConflict('${data.contribution_id}', 'update')">Update Brain</button>
              <button class="btn btn-sm btn-secondary" onclick="app.resolveBrainConflict('${data.contribution_id}', 'keep')">Keep Existing</button>
              <button class="btn btn-sm btn-secondary" onclick="app.resolveBrainConflict('${data.contribution_id}', 'add_note')">Add as Note</button>
            </div>
          `;
        }
        
        this.addChatMessage(responseHtml, 'assistant', false, true);
        
        // Refresh pending if needed
        if (data.contribution_id) {
          this.refreshBrainPending();
        }
      } else {
        throw new Error('Chat request failed');
      }
    } catch (error) {
      document.getElementById(loadingId)?.remove();
      this.addChatMessage('Error: Could not reach the Brain Curator. Make sure the orchestrator is running.', 'error');
    }
  },
  
  /**
   * Convert markdown to HTML for proper rendering
   */
  markdownToHtml(text) {
    if (!text) return '';
    
    let html = text;
    
    // Handle markdown tables first (before other processing)
    html = html.replace(/\|(.+)\|\n\|[-:\| ]+\|\n((?:\|.+\|\n?)+)/g, (match, headerRow, bodyRows) => {
      const headers = headerRow.split('|').map(h => h.trim()).filter(h => h);
      const rows = bodyRows.trim().split('\n').map(row => 
        row.split('|').map(cell => cell.trim()).filter(cell => cell)
      );
      
      let table = '<table class="brain-table"><thead><tr>';
      headers.forEach(h => table += `<th>${h}</th>`);
      table += '</tr></thead><tbody>';
      rows.forEach(row => {
        table += '<tr>';
        row.forEach(cell => table += `<td>${cell}</td>`);
        table += '</tr>';
      });
      table += '</tbody></table>';
      return table;
    });
    
    html = html
      // Headers
      .replace(/^### (.+)$/gm, '<h4>$1</h4>')
      .replace(/^## (.+)$/gm, '<h3>$1</h3>')
      .replace(/^# (.+)$/gm, '<h2>$1</h2>')
      // Bold
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      // Italic  
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      // Code blocks
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      // Inline code
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      // Bullet lists
      .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
      // Numbered lists
      .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
      // Wrap consecutive <li> in <ul>
      .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
      // Paragraphs
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');
    
    // Wrap in paragraph
    html = '<p>' + html + '</p>';
    
    // Clean up - remove paragraph tags around block elements
    html = html
      .replace(/<p><\/p>/g, '')
      .replace(/<p>(<h[234]>)/g, '$1')
      .replace(/(<\/h[234]>)<\/p>/g, '$1')
      .replace(/<p>(<ul>)/g, '$1')
      .replace(/(<\/ul>)<\/p>/g, '$1')
      .replace(/<p>(<pre>)/g, '$1')
      .replace(/(<\/pre>)<\/p>/g, '$1')
      .replace(/<p>(<table)/g, '$1')
      .replace(/(<\/table>)<\/p>/g, '$1');
    
    return html;
  },

  addChatMessage(content, type, isLoading = false, isHtml = false) {
    const container = document.getElementById('brain-chat-messages');
    const id = 'msg-' + Date.now();
    
    const msgDiv = document.createElement('div');
    msgDiv.id = id;
    msgDiv.className = `chat-message ${type}-message${isLoading ? ' loading' : ''}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isHtml) {
      contentDiv.innerHTML = content;
    } else {
      contentDiv.textContent = content;
    }
    
    msgDiv.appendChild(contentDiv);
    container.appendChild(msgDiv);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
    
    return id;
  },
  
  async resolveBrainConflict(contributionId, action) {
    try {
      const res = await fetch(`${this.orchestratorBaseUrl}/brain/resolve`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contribution_id: contributionId, action })
      });
      
      if (res.ok) {
        const data = await res.json();
        this.addChatMessage(data.message, 'assistant');
        
        // Remove the action buttons
        document.querySelector(`[data-contribution-id="${contributionId}"]`)?.remove();
        
        // Refresh pending
        this.refreshBrainPending();
      }
    } catch (error) {
      this.addChatMessage('Error resolving contribution', 'error');
    }
  },
  
  async refreshBrainPending() {
    try {
      const res = await fetch(`${this.orchestratorBaseUrl}/brain/pending`, { credentials: 'include' });
      
      if (res.ok) {
        const data = await res.json();
        const section = document.getElementById('brain-pending-section');
        const list = document.getElementById('brain-pending-list');
        
        if (data.count > 0) {
          section.style.display = 'block';
          list.innerHTML = data.contributions.map(c => `
            <div class="pending-item">
              <span class="pending-status ${c.status}">${c.status}</span>
              <span class="pending-text">${c.raw_input}</span>
              ${c.conflicts_count > 0 ? `<span class="pending-conflicts">⚠️ ${c.conflicts_count} conflicts</span>` : ''}
            </div>
          `).join('');
        } else {
          section.style.display = 'none';
        }
      }
    } catch (error) {
      console.error('Failed to refresh pending:', error);
    }
  },

  showMarketingForm() {
    const panel = document.getElementById('aihub-task-panel');
    const title = document.getElementById('aihub-task-title');
    const form = document.getElementById('aihub-task-form');
    
    title.textContent = 'Marketing Campaign';
    form.innerHTML = `
      <p class="form-hint">I'll pull PhonoLogic's brand guidelines, product info, and target market from the Brain automatically.</p>
      <div class="form-group">
        <label>What do you need?</label>
        <textarea id="task-prompt" placeholder="e.g., Create a social media campaign for our private beta launch targeting K-4 teachers..." required></textarea>
      </div>
      <div class="form-group">
        <label>Attach files (optional)</label>
        <input type="file" id="task-files" multiple accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg">
      </div>
      <button class="btn btn-primary" onclick="app.runMarketingCampaign()">Generate</button>
    `;
    
    panel.style.display = 'block';
    document.getElementById('aihub-task-result').style.display = 'none';
  },

  async runMarketingCampaign() {
    const prompt = document.getElementById('task-prompt').value;
    
    if (!prompt.trim()) {
      alert('Please describe what you need');
      return;
    }
    
    try {
      document.getElementById('aihub-task-result').style.display = 'block';
      document.getElementById('aihub-task-result-content').innerHTML = '<div class="loading">Fetching Brain context and generating campaign...</div>';
      
      // The orchestrator will automatically fetch brain context
      const res = await fetch(`${this.orchestratorBaseUrl}/marketing/prompt`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt,
          use_brain_context: true  // Tell orchestrator to fetch brain data
        })
      });
      
      const data = await res.json();
      document.getElementById('aihub-task-result-content').innerHTML = this.markdownToHtml(data.result || JSON.stringify(data, null, 2));
    } catch (error) {
      document.getElementById('aihub-task-result-content').textContent = 'Error: ' + error.message;
    }
  },

  showOnboardingForm() {
    const panel = document.getElementById('aihub-task-panel');
    const title = document.getElementById('aihub-task-title');
    const form = document.getElementById('aihub-task-form');
    
    title.textContent = 'Project Management';
    form.innerHTML = `
      <p class="form-hint">I'll use PhonoLogic's team info and project context from the Brain.</p>
      <div class="form-group">
        <label>What do you need?</label>
        <textarea id="task-prompt" placeholder="e.g., Create onboarding tasks for a new engineer, Draft a project status update for investors..." required></textarea>
      </div>
      <div class="form-group">
        <label>Attach files (optional)</label>
        <input type="file" id="task-files" multiple accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg">
      </div>
      <button class="btn btn-primary" onclick="app.runProjectTask()">Generate</button>
    `;
    
    panel.style.display = 'block';
    document.getElementById('aihub-task-result').style.display = 'none';
  },

  async runProjectTask() {
    const prompt = document.getElementById('task-prompt').value;
    
    if (!prompt.trim()) {
      alert('Please describe what you need');
      return;
    }
    
    try {
      document.getElementById('aihub-task-result').style.display = 'block';
      document.getElementById('aihub-task-result-content').innerHTML = '<div class="loading">Fetching Brain context and generating...</div>';
      
      const res = await fetch(`${this.orchestratorBaseUrl}/pm/task`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt,
          use_brain_context: true
        })
      });
      
      const data = await res.json();
      document.getElementById('aihub-task-result-content').innerHTML = this.markdownToHtml(data.result || JSON.stringify(data, null, 2));
    } catch (error) {
      document.getElementById('aihub-task-result-content').textContent = 'Error: ' + error.message;
    }
  },

  showProgressReportForm() {
    const panel = document.getElementById('aihub-task-panel');
    const title = document.getElementById('aihub-task-title');
    const form = document.getElementById('aihub-task-form');
    
    title.textContent = 'Reports & Communications';
    form.innerHTML = `
      <p class="form-hint">I'll pull PhonoLogic's metrics, milestones, and team info from the Brain.</p>
      <div class="form-group">
        <label>What do you need?</label>
        <textarea id="task-prompt" placeholder="e.g., Draft an investor update email, Create a weekly team summary, Generate pilot school report..." required></textarea>
      </div>
      <div class="form-group">
        <label>Attach files (optional)</label>
        <input type="file" id="task-files" multiple accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg">
      </div>
      <button class="btn btn-primary" onclick="app.runReportTask()">Generate</button>
    `;
    
    panel.style.display = 'block';
    document.getElementById('aihub-task-result').style.display = 'none';
  },

  async runReportTask() {
    const prompt = document.getElementById('task-prompt').value;
    
    if (!prompt.trim()) {
      alert('Please describe what you need');
      return;
    }
    
    try {
      document.getElementById('aihub-task-result').style.display = 'block';
      document.getElementById('aihub-task-result-content').innerHTML = '<div class="loading">Fetching Brain context and generating report...</div>';
      
      const res = await fetch(`${this.orchestratorBaseUrl}/pm/report`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt,
          use_brain_context: true
        })
      });
      
      const data = await res.json();
      document.getElementById('aihub-task-result-content').innerHTML = this.markdownToHtml(data.result || JSON.stringify(data, null, 2));
    } catch (error) {
      document.getElementById('aihub-task-result-content').textContent = 'Error: ' + error.message;
    }
  },

  showBrowserAnalyzeForm() {
    const panel = document.getElementById('aihub-task-panel');
    const title = document.getElementById('aihub-task-title');
    const form = document.getElementById('aihub-task-form');
    
    title.textContent = 'Content Analysis';
    form.innerHTML = `
      <p class="form-hint">I'll check against PhonoLogic's brand guidelines from the Brain.</p>
      <div class="form-group">
        <label>What do you need?</label>
        <textarea id="task-prompt" placeholder="e.g., Review this pitch deck for brand compliance, Analyze competitor landing page, Check our website copy..." required></textarea>
      </div>
      <div class="form-group">
        <label>URL to analyze (optional)</label>
        <input type="url" id="task-url" placeholder="https://...">
      </div>
      <div class="form-group">
        <label>Attach files (optional)</label>
        <input type="file" id="task-files" multiple accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.pptx">
      </div>
      <button class="btn btn-primary" onclick="app.runAnalysisTask()">Analyze</button>
    `;
    
    panel.style.display = 'block';
    document.getElementById('aihub-task-result').style.display = 'none';
  },

  async runAnalysisTask() {
    const prompt = document.getElementById('task-prompt').value;
    const url = document.getElementById('task-url').value;
    
    if (!prompt.trim()) {
      alert('Please describe what you need');
      return;
    }
    
    try {
      document.getElementById('aihub-task-result').style.display = 'block';
      document.getElementById('aihub-task-result-content').innerHTML = '<div class="loading">Fetching Brain context and analyzing...</div>';
      
      const res = await fetch(`${this.orchestratorBaseUrl}/browser/prompt`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt,
          url: url || null,
          use_brain_context: true
        })
      });
      
      const data = await res.json();
      document.getElementById('aihub-task-result-content').innerHTML = this.markdownToHtml(data.result || JSON.stringify(data, null, 2));
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
