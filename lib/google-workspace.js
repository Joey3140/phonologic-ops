/**
 * Google Workspace Integration for Phonologic Ops Hub
 * Provides access to Drive, Gmail, and Sheets
 */

const { google } = require('googleapis');

class GoogleWorkspace {
  constructor() {
    this.auth = null;
    this.drive = null;
    this.gmail = null;
    this.sheets = null;
  }

  /**
   * Initialize OAuth2 client
   */
  async initialize(tokens = null) {
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_REDIRECT_URI || 'https://ops.phonologic.cloud/api/auth/google/callback'
    );

    if (tokens) {
      oauth2Client.setCredentials(tokens);
    }

    this.auth = oauth2Client;
    this.drive = google.drive({ version: 'v3', auth: oauth2Client });
    this.gmail = google.gmail({ version: 'v1', auth: oauth2Client });
    this.sheets = google.sheets({ version: 'v4', auth: oauth2Client });

    return this;
  }

  /**
   * Get OAuth URL for user authorization
   */
  getAuthUrl() {
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_REDIRECT_URI || 'https://ops.phonologic.cloud/api/auth/google/callback'
    );

    const scopes = [
      'https://www.googleapis.com/auth/drive.readonly',
      'https://www.googleapis.com/auth/gmail.send',
      'https://www.googleapis.com/auth/spreadsheets'
    ];

    return oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: scopes
    });
  }

  /**
   * Exchange authorization code for tokens
   */
  async getTokensFromCode(code) {
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_REDIRECT_URI || 'https://ops.phonologic.cloud/api/auth/google/callback'
    );

    const { tokens } = await oauth2Client.getToken(code);
    return tokens;
  }

  // ========== DRIVE OPERATIONS ==========

  /**
   * List files in Drive
   */
  async listFiles({ folderId = null, query = null, pageSize = 20 }) {
    let q = "trashed = false";
    
    if (folderId) {
      q += ` and '${folderId}' in parents`;
    }
    if (query) {
      q += ` and name contains '${query}'`;
    }

    const response = await this.drive.files.list({
      q,
      pageSize,
      fields: 'files(id, name, mimeType, modifiedTime, webViewLink)'
    });

    return response.data.files;
  }

  /**
   * Get file content from Drive
   */
  async getFileContent(fileId) {
    // Get file metadata first
    const metadata = await this.drive.files.get({
      fileId,
      fields: 'id, name, mimeType'
    });

    const mimeType = metadata.data.mimeType;

    // Handle Google Docs
    if (mimeType === 'application/vnd.google-apps.document') {
      const response = await this.drive.files.export({
        fileId,
        mimeType: 'text/plain'
      });
      return {
        id: fileId,
        name: metadata.data.name,
        mimeType,
        content: response.data
      };
    }

    // Handle Google Sheets
    if (mimeType === 'application/vnd.google-apps.spreadsheet') {
      const response = await this.drive.files.export({
        fileId,
        mimeType: 'text/csv'
      });
      return {
        id: fileId,
        name: metadata.data.name,
        mimeType,
        content: response.data
      };
    }

    // Handle regular files
    const response = await this.drive.files.get({
      fileId,
      alt: 'media'
    });

    return {
      id: fileId,
      name: metadata.data.name,
      mimeType,
      content: response.data
    };
  }

  /**
   * Search Drive files
   */
  async searchFiles(searchQuery, pageSize = 10) {
    const response = await this.drive.files.list({
      q: `fullText contains '${searchQuery}' and trashed = false`,
      pageSize,
      fields: 'files(id, name, mimeType, modifiedTime, webViewLink)'
    });

    return response.data.files;
  }

  // ========== GMAIL OPERATIONS ==========

  /**
   * Send email via Gmail
   */
  async sendEmail({ to, subject, body, html = false }) {
    const utf8Subject = `=?utf-8?B?${Buffer.from(subject).toString('base64')}?=`;
    
    const messageParts = [
      `To: ${to}`,
      `Subject: ${utf8Subject}`,
      `MIME-Version: 1.0`,
      `Content-Type: ${html ? 'text/html' : 'text/plain'}; charset=utf-8`,
      '',
      body
    ];
    
    const message = messageParts.join('\n');
    const encodedMessage = Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');

    const response = await this.gmail.users.messages.send({
      userId: 'me',
      requestBody: {
        raw: encodedMessage
      }
    });

    return response.data;
  }

  /**
   * Create email draft
   */
  async createDraft({ to, subject, body, html = false }) {
    const utf8Subject = `=?utf-8?B?${Buffer.from(subject).toString('base64')}?=`;
    
    const messageParts = [
      `To: ${to}`,
      `Subject: ${utf8Subject}`,
      `MIME-Version: 1.0`,
      `Content-Type: ${html ? 'text/html' : 'text/plain'}; charset=utf-8`,
      '',
      body
    ];
    
    const message = messageParts.join('\n');
    const encodedMessage = Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');

    const response = await this.gmail.users.drafts.create({
      userId: 'me',
      requestBody: {
        message: {
          raw: encodedMessage
        }
      }
    });

    return response.data;
  }

  // ========== SHEETS OPERATIONS ==========

  /**
   * Read data from Google Sheets
   */
  async readSheet(spreadsheetId, range) {
    const response = await this.sheets.spreadsheets.values.get({
      spreadsheetId,
      range
    });

    return response.data.values;
  }

  /**
   * Write data to Google Sheets
   */
  async writeSheet(spreadsheetId, range, values) {
    const response = await this.sheets.spreadsheets.values.update({
      spreadsheetId,
      range,
      valueInputOption: 'USER_ENTERED',
      requestBody: {
        values
      }
    });

    return response.data;
  }

  /**
   * Append data to Google Sheets
   */
  async appendToSheet(spreadsheetId, range, values) {
    const response = await this.sheets.spreadsheets.values.append({
      spreadsheetId,
      range,
      valueInputOption: 'USER_ENTERED',
      requestBody: {
        values
      }
    });

    return response.data;
  }

  /**
   * Create new spreadsheet
   */
  async createSpreadsheet(title) {
    const response = await this.sheets.spreadsheets.create({
      requestBody: {
        properties: {
          title
        }
      }
    });

    return {
      id: response.data.spreadsheetId,
      url: response.data.spreadsheetUrl
    };
  }
}

module.exports = { GoogleWorkspace };
