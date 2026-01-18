/**
 * Wiki Reorganization Script - Updates categories to department-based structure
 * 
 * New Categories:
 * - getting-started: Onboarding essentials for new team members
 * - development: Technical documentation and engineering
 * - product: Product features, curriculum, and roadmap
 * - operations: Deployment, costs, and business operations
 * - analytics: Data, metrics, and reporting
 * - policies: HR policies, security, and guidelines
 */

const { Redis } = require('@upstash/redis');

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN
});

const WIKI_KEY = 'phonologic:wiki';

// Mapping of page IDs to new categories
const categoryMapping = {
  // Getting Started (Onboarding)
  'wiki_company_overview': 'getting-started',
  'wiki_product_overview': 'getting-started',
  'wiki_team_structure': 'getting-started',
  'wiki_tools_access': 'getting-started',
  
  // Development (Technical)
  'wiki_tech_stack': 'development',
  'wiki_tech_stack_detailed': 'development',
  'wiki_environment_variables': 'development',
  'wiki_api_endpoints': 'development',
  'wiki_firestore_data_model': 'development',
  'wiki_key_files': 'development',
  'wiki_frontend_patterns': 'development',
  'wiki_shared_constants': 'development',
  
  // Product
  'wiki_phonics_curriculum': 'product',
  'wiki_narrator_system': 'product',
  'wiki_assessment_system': 'product',
  'wiki_roadmap': 'product',
  
  // Operations
  'wiki_deployment_workflow': 'operations',
  'wiki_cost_estimates': 'operations',
  'wiki_google_accelerator': 'operations',
  
  // Analytics
  'wiki_bigquery_analytics': 'analytics',
  
  // Policies & HR
  'wiki_communication_norms': 'policies',
  'wiki_expense_policy': 'policies',
  'wiki_security_patterns': 'policies'
};

// Category metadata for display
const categoryMeta = {
  'getting-started': {
    name: 'Getting Started',
    description: 'Essential information for new team members',
    icon: '🚀',
    order: 1
  },
  'development': {
    name: 'Development',
    description: 'Technical documentation and engineering guides',
    icon: '💻',
    order: 2
  },
  'product': {
    name: 'Product',
    description: 'Product features, curriculum, and roadmap',
    icon: '📦',
    order: 3
  },
  'operations': {
    name: 'Operations',
    description: 'Deployment, infrastructure, and business operations',
    icon: '⚙️',
    order: 4
  },
  'analytics': {
    name: 'Analytics',
    description: 'Data, metrics, and reporting systems',
    icon: '📊',
    order: 5
  },
  'policies': {
    name: 'Policies',
    description: 'HR policies, security, and company guidelines',
    icon: '📋',
    order: 6
  }
};

async function reorganizeWiki() {
  console.log('Reorganizing wiki by department...\n');
  
  try {
    const data = await redis.hgetall(WIKI_KEY);
    
    if (!data || Object.keys(data).length === 0) {
      console.log('No wiki pages found.');
      return;
    }
    
    let updated = 0;
    let skipped = 0;
    
    for (const [id, item] of Object.entries(data)) {
      const page = typeof item === 'string' ? JSON.parse(item) : item;
      const newCategory = categoryMapping[id];
      
      if (newCategory && page.category !== newCategory) {
        const oldCategory = page.category;
        page.category = newCategory;
        page.updatedAt = new Date().toISOString();
        
        await redis.hset(WIKI_KEY, { [id]: JSON.stringify(page) });
        console.log(`✓ ${page.title}: ${oldCategory} → ${newCategory}`);
        updated++;
      } else if (!newCategory) {
        console.log(`⚠ ${page.title}: No mapping found (keeping: ${page.category})`);
        skipped++;
      } else {
        console.log(`- ${page.title}: Already in ${newCategory}`);
        skipped++;
      }
    }
    
    console.log(`\nReorganization complete!`);
    console.log(`Updated: ${updated} pages`);
    console.log(`Skipped: ${skipped} pages`);
    
  } catch (error) {
    console.error('Error:', error);
  }
}

reorganizeWiki().catch(console.error);
