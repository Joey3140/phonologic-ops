/**
 * Firestore database utilities for Phonologic Ops Hub
 * Shared connection and helpers matching main PhonoLogic app
 */

const { Firestore } = require('@google-cloud/firestore');

let firestoreInstance = null;

/**
 * Get Firestore instance (singleton)
 */
function getFirestore() {
  if (!firestoreInstance) {
    firestoreInstance = new Firestore({
      projectId: process.env.GCP_PROJECT_ID,
      credentials: JSON.parse(process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON || '{}')
    });
  }
  return firestoreInstance;
}

// Collection names for ops hub
const COLLECTIONS = {
  AGENTS: 'ops_agents',
  WORKFLOWS: 'ops_workflows',
  TASKS: 'ops_tasks',
  MEMORY: 'ops_memory',
  DOCUMENTS: 'ops_documents',
  LOGS: 'ops_logs'
};

/**
 * Memory Index - stores indexed documents for agent retrieval
 */
class MemoryIndex {
  constructor() {
    this.db = getFirestore();
    this.memoryCollection = this.db.collection(COLLECTIONS.MEMORY);
    this.docsCollection = this.db.collection(COLLECTIONS.DOCUMENTS);
  }

  /**
   * Index a document for agent retrieval
   */
  async indexDocument({ id, content, metadata, source, embedding = null }) {
    const doc = {
      id,
      content,
      metadata: metadata || {},
      source: source || 'manual',
      embedding,
      indexedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    await this.docsCollection.doc(id).set(doc, { merge: true });
    return doc;
  }

  /**
   * Query documents by keyword search (simple implementation)
   * For production, consider using Firestore full-text search or Algolia
   */
  async queryDocuments(query, limit = 10) {
    const snapshot = await this.docsCollection.limit(limit * 3).get();
    const results = [];
    
    const queryLower = query.toLowerCase();
    const queryTerms = queryLower.split(/\s+/);

    snapshot.forEach(doc => {
      const data = doc.data();
      const contentLower = (data.content || '').toLowerCase();
      
      // Simple relevance scoring
      let score = 0;
      queryTerms.forEach(term => {
        if (contentLower.includes(term)) {
          score += 1;
        }
      });

      if (score > 0) {
        results.push({
          id: doc.id,
          content: data.content,
          metadata: data.metadata,
          source: data.source,
          score
        });
      }
    });

    // Sort by score and return top results
    return results
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }

  /**
   * Get document by ID
   */
  async getDocument(id) {
    const doc = await this.docsCollection.doc(id).get();
    return doc.exists ? doc.data() : null;
  }

  /**
   * Search by metadata
   */
  async searchByMetadata(filters, limit = 10) {
    let query = this.docsCollection;
    
    Object.entries(filters).forEach(([key, value]) => {
      query = query.where(`metadata.${key}`, '==', value);
    });

    const snapshot = await query.limit(limit).get();
    const results = [];
    
    snapshot.forEach(doc => {
      results.push({ id: doc.id, ...doc.data() });
    });

    return results;
  }

  /**
   * Get index statistics
   */
  async getStats() {
    const snapshot = await this.docsCollection.get();
    const sources = new Set();
    
    snapshot.forEach(doc => {
      sources.add(doc.data().source || 'unknown');
    });

    return {
      totalDocuments: snapshot.size,
      sources: Array.from(sources)
    };
  }
}

/**
 * Workflow storage for tracking agent workflows
 */
class WorkflowStore {
  constructor() {
    this.db = getFirestore();
    this.collection = this.db.collection(COLLECTIONS.WORKFLOWS);
  }

  /**
   * Create a new workflow run
   */
  async createWorkflow({ type, inputs, createdBy }) {
    const id = `wf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const workflow = {
      id,
      type,
      inputs,
      status: 'pending',
      steps: [],
      createdBy,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    await this.collection.doc(id).set(workflow);
    return workflow;
  }

  /**
   * Update workflow status
   */
  async updateWorkflow(id, updates) {
    await this.collection.doc(id).update({
      ...updates,
      updatedAt: new Date().toISOString()
    });
  }

  /**
   * Add step to workflow
   */
  async addWorkflowStep(id, step) {
    const doc = await this.collection.doc(id).get();
    const data = doc.data();
    
    const steps = data.steps || [];
    steps.push({
      ...step,
      timestamp: new Date().toISOString()
    });

    await this.collection.doc(id).update({
      steps,
      updatedAt: new Date().toISOString()
    });
  }

  /**
   * Get workflow by ID
   */
  async getWorkflow(id) {
    const doc = await this.collection.doc(id).get();
    return doc.exists ? doc.data() : null;
  }

  /**
   * Get recent workflows
   */
  async getRecentWorkflows(limit = 20) {
    const snapshot = await this.collection
      .orderBy('createdAt', 'desc')
      .limit(limit)
      .get();

    const results = [];
    snapshot.forEach(doc => {
      results.push(doc.data());
    });

    return results;
  }
}

/**
 * Ops logging
 */
class OpsLogger {
  constructor() {
    this.db = getFirestore();
    this.collection = this.db.collection(COLLECTIONS.LOGS);
  }

  async log(level, message, data = {}) {
    const entry = {
      level,
      message,
      data,
      timestamp: new Date().toISOString()
    };

    await this.collection.add(entry);
    return entry;
  }

  info(message, data) { return this.log('info', message, data); }
  warn(message, data) { return this.log('warn', message, data); }
  error(message, data) { return this.log('error', message, data); }
}

module.exports = {
  getFirestore,
  COLLECTIONS,
  MemoryIndex,
  WorkflowStore,
  OpsLogger
};
