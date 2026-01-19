/**
 * Wiki Seed API - Seeds wiki with comprehensive company knowledge
 * 
 * POST /api/wiki/seed - Seeds all wiki pages (admin only)
 * Auto-seeds when wiki is empty OR when WIKI_VERSION is newer than stored version
 * 
 * @module api/wiki/seed
 */

const { getRedis, REDIS_KEYS } = require('../../lib/redis');
const { getSessionFromRequest } = require('../auth/google');

// Increment this version whenever wiki content is updated
// Format: YYYY-MM-DD-vN (date + version number for that day)
const WIKI_VERSION = '2026-01-18-v1';
const WIKI_VERSION_KEY = 'phonologic:wiki:version';

// Check if user is admin
async function checkIsAdmin(email) {
  const adminEmails = (process.env.ADMIN_EMAILS || '').split(',').map(e => e.trim().toLowerCase());
  if (adminEmails.includes(email.toLowerCase())) return true;
  
  const redis = getRedis();
  if (!redis) return false;
  
  const isAdmin = await redis.sismember(REDIS_KEYS.ADMINS, email.toLowerCase());
  return isAdmin;
}

const wikiPages = [
  // GETTING STARTED
  {
    id: 'wiki_company_overview',
    title: 'Company Overview',
    category: 'getting-started',
    content: `# PhonoLogic

**Tagline:** Where literacy meets possibility

**Mission:** Finding a text that fits your learner should not be the hard part of learning how to read. We create reading practice that fits any learner in minutes.

**Vision:** A world where every child has access to reading practice that matches their phonics skills and interests, regardless of learning differences.

---

## Company Details

| Field | Value |
|-------|-------|
| **Founded** | 2024 |
| **Headquarters** | Toronto, Canada |
| **Website** | [phonologic.cloud](https://phonologic.cloud) |
| **Marketing Site** | [phonologic.ca](https://www.phonologic.ca) |
| **Ops Portal** | [ops.phonologic.cloud](https://ops.phonologic.cloud) |
| **Stage** | Private Beta |
| **Team Size** | 3 |

---

## What We Do

PhonoLogic is an **AI-powered structured literacy engine** that turns phonics awareness into hard rules for text generation.

A teacher picks a phonics focus, a topic, and a length, and PhonoLogic produces fully decodable, personalized texts. A built-in validator layer blocks off-scope or non-decodable words before they ever reach a child.

**For teachers, it's simple:** prompt → print → teach with confidence.

---

## The Problem We Solve

Roughly half of students aren't reading at grade level by the end of primary school. For around a third of students, the issue isn't effort or behavior but the system itself, which was never built around how humans decode.

Teachers spend hours hunting for or rewriting texts, or use generic AI tools that silently violate structured-literacy rules. The result is students stall, teachers burn out, and billions spent on literacy materials don't translate into appropriately scaffolded texts.

---

## Our Moat

1. **Fidelity:** Every passage matches the exact phonics scope being taught—no unaligned or unknown words
2. **Explainability:** The validator returns clear, plain-language rationales that accelerate teacher learning
3. **Embeddability:** Modular design integrates into existing EdTech platforms, curriculum ecosystems, or SaaS tools`
  },
  {
    id: 'wiki_team_directory',
    title: 'Team Directory',
    category: 'getting-started',
    content: `# Team Directory

## Leadership Team

### Stephen Robins — CEO & Founder
- **Email:** stephen@phonologic.ca
- **Department:** Executive
- **Skills:** Business Strategy, Product Vision, Fundraising, Operations

After having won numerous awards as a Brewmaster, Stephen decided to pivot and obtained his MBA from IE Business School. PhonoLogic was born out of his desire to build something that helped his wife focus on teaching instead of finding materials.

---

### Joey Drury — CTO
- **Email:** joey@phonologic.ca
- **Department:** Technology
- **Skills:** Software Engineering, Digital Analytics, AI/ML, Technical Architecture

Digital analytics expert and former Associate Director of Implementation at Cardinal Path. With deep proficiencies in digital marketing, CX, and stakeholder management, Joey ensures that PhonoLogic is technically sound.

---

### Marysia Robins — Student Success Teacher
- **Email:** marysia@phonologic.ca
- **Department:** Education
- **Skills:** Orton-Gillingham, Special Education, Literacy Intervention, Curriculum Design

Special education teacher and literacy interventionist with training in Orton-Gillingham. She has spent the past seven years in classrooms leading projects around learning support. Marysia's work has focused on structured literacy and dyslexia support for students with language based learning differences.

---

## Contact

- **General Inquiries:** Use the Operations Portal announcements or email directly
- **Technical Issues:** joey@phonologic.ca
- **Product/Education:** marysia@phonologic.ca
- **Business/Partnerships:** stephen@phonologic.ca`
  },
  {
    id: 'wiki_tools_access',
    title: 'Tools & Access Guide',
    category: 'getting-started',
    content: `# Tools & Access Guide

All team members get access to tools with their **@phonologic.ca** Google account.

---

## Core Tools (Automatic Access)

| Tool | URL | Purpose |
|------|-----|---------|
| **Google Workspace** | workspace.google.com | Email, Calendar, Drive, Docs, Sheets, Meet |
| **Operations Portal** | ops.phonologic.cloud | Internal tools, wiki, announcements, goals |
| **ClickUp** | app.clickup.com | Project management, task tracking, sprints |

---

## Development Tools (Request Access)

| Tool | URL | Purpose |
|------|-----|---------|
| **GitHub** | github.com/phonologic | Version control, code repos |
| **Vercel** | vercel.com | Frontend hosting, deployments |
| **Railway** | railway.app | Backend services, orchestrator |
| **Upstash** | console.upstash.com | Redis database |
| **Google Cloud** | console.cloud.google.com | AI services, BigQuery |

---

## Business Tools

| Tool | URL | Purpose |
|------|-----|---------|
| **Pitch.com** | pitch.com | Investor decks, presentations |
| **Looker Studio** | lookerstudio.google.com | Analytics dashboards |
| **Figma** | figma.com | Design, prototypes |

---

## Google Drive Structure

| Folder | Link |
|--------|------|
| **Main Drive** | [PhonoLogic (Main)](https://drive.google.com/drive/folders/0AEgmJV2IpqOhUk9PVA) |
| **001: Operations** | [Operations](https://drive.google.com/drive/folders/14-pITXL-iJT-1h6Gb-RCp4yGEQ5GHc4Z) |
| **002: Sales & Outreach** | [Sales](https://drive.google.com/drive/folders/1I2pkpPYf6H9Ur26Uifyfhgmq8nqlbTnw) |
| **003: Developer** | [Developer](https://drive.google.com/drive/folders/1ALiBrIJSw5Xx5NS18oO0aN7j1fVB8jhC) |
| **004: Marketing & Feedback** | [Marketing](https://drive.google.com/drive/folders/1Qls5x8RlaEfyjLqH-rQ9fN6byRfCKWRC) |
| **005: Fundraising** | [Fundraising](https://drive.google.com/drive/folders/1PuXZ1KxsNvOoafr8FxctqCLr6wSywD4y) |

---

## Security Requirements

- ✅ Always use your @phonologic.ca account
- ✅ Enable 2FA on all accounts
- ✅ Never share credentials
- ✅ Report suspicious activity immediately`
  },

  // DEVELOPMENT
  {
    id: 'wiki_tech_stack',
    title: 'Technology Stack',
    category: 'development',
    content: `# Technology Stack

## Frontend (Ops Portal)

| Technology | Purpose |
|------------|---------|
| **Vanilla JS SPA** | Operations portal at ops.phonologic.cloud |
| **Vercel** | Hosting and serverless functions |
| **HTML/CSS** | Modern responsive design |

---

## Backend

| Technology | Purpose |
|------------|---------|
| **Vercel Serverless** | API endpoints (/api/*) |
| **Upstash Redis** | Primary database (users, wiki, announcements, goals) |
| **Google OAuth** | Authentication (@phonologic.ca only) |

---

## AI/ML Orchestrator

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Python API framework |
| **Agno** | Agentic AI framework (formerly Phidata) |
| **Claude** | LLM provider (Anthropic) |
| **Railway** | Orchestrator hosting |

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| **Vercel** | Frontend hosting, serverless functions |
| **Railway** | Python orchestrator backend |
| **Upstash** | Redis database |
| **Google Cloud** | OAuth, future AI services |
| **Hover** | Domain management |

---

## Domains

| Domain | Purpose |
|--------|---------|
| **phonologic.ca** | Marketing website |
| **phonologic.cloud** | Main application |
| **ops.phonologic.cloud** | Operations portal |
| **dev.phonologic.cloud** | Development/staging |`
  },
  {
    id: 'wiki_deployment_workflow',
    title: 'Deployment Workflow',
    category: 'development',
    content: `# Deployment Workflow

## CRITICAL RULE

> **Never deploy to production without explicit user approval.**

---

## Process

1. **Push to development branch** → auto-deploys to dev.phonologic.cloud
2. **Test on staging** → verify all features work
3. **Get explicit user approval** → document in ClickUp or Slack
4. **Merge development to main** → auto-deploys to phonologic.cloud

---

## Version Management

- Always update version in \`package.json\`
- Follow SemVer: MAJOR.MINOR.PATCH
- Tag releases in GitHub

---

## Vercel Deployments

| Branch | Environment | URL |
|--------|-------------|-----|
| \`main\` | Production | phonologic.cloud, ops.phonologic.cloud |
| \`development\` | Staging | dev.phonologic.cloud |
| \`feature/*\` | Preview | Auto-generated preview URLs |

---

## Railway Deployments (Orchestrator)

| Setting | Value |
|---------|-------|
| **Root Directory** | \`orchestrator\` |
| **Builder** | Dockerfile |
| **Port** | 8000 (hardcoded) |
| **Start Command** | \`uvicorn main:app --host 0.0.0.0 --port 8000\` |`
  },
  {
    id: 'wiki_security',
    title: 'Security Architecture',
    category: 'development',
    content: `# Security Architecture

## Authentication

- **Provider:** Google OAuth 2.0
- **Restriction:** @phonologic.ca domain only
- **Session:** JWT tokens stored in HTTP-only cookies

---

## Authorization

| Role | Capabilities |
|------|-------------|
| **User** | Read wiki, view announcements, track goals |
| **Admin** | All user capabilities + edit wiki, manage users, post announcements |

**Current Admins:** joey@phonologic.ca, stephen@phonologic.ca

---

## Rate Limiting

| Endpoint Type | Limit |
|---------------|-------|
| **Default** | 60 requests/minute |
| **Write Operations** | 20 requests/minute |
| **Authentication** | 10 requests/minute |

---

## Security Decisions (Jan 2026)

1. **Session Secret:** Must be 32+ characters, NO fallback value
2. **CORS:** Strict origin allowlist, no wildcards
3. **XSS Prevention:** HTML escaped before markdown processing
4. **Admin Protection:** Admins cannot self-demote`
  },

  // PRODUCT
  {
    id: 'wiki_product_overview',
    title: 'Product Overview',
    category: 'product',
    content: `# PhonoLogic Decodable Story Generator

**Tagline:** Reading practice that fits any learner in minutes

---

## What It Is

An AI-powered software that creates individualized decodable texts. PhonoLogic creates short stories and passages that match the phonics skills a learner is working on.

We generate Science of Reading aligned passages that fit each individual learner's interests. Made for **Kindergarten-Grade 8 students**.

---

## Key Features

- ✅ AI-generated decodable stories matching phonics scope
- ✅ Personalized to student interests (parks, travel, sports, etc.)
- ✅ Fiction and non-fiction text generation
- ✅ Decodability checks before educator sees content
- ✅ Aligned to Science of Reading and Orton-Gillingham methodology
- ✅ Differentiated curriculum and word banks
- ✅ Grade 1-4 phonics (Jan 2026), K-8 by Sept 2026

---

## Value Propositions

1. **Saves teachers 5-6 hours per week** finding appropriate reading materials
2. **Texts match student's current decoding skills**, not just grade level
3. **Rooted in social/emotional learning** - curiosity, empathy, discovery
4. **Every passage respects scope and sequence** teachers are working from

---

## Target Audience

- K-8 Teachers and reading specialists
- Speech-Language Pathologists (SLPs)
- Literacy interventionists and tutors
- Parents of children with reading difficulties
- Students with dyslexia or learning differences
- Schools and districts implementing structured literacy`
  },
  {
    id: 'wiki_pricing',
    title: 'Pricing Structure',
    category: 'product',
    content: `# Pricing Structure

## Current Tiers (Jan 2026)

### Free Tier
- **Target:** Teachers/Parents trying the product
- **Price:** $0
- **Features:** Limited generations, On-screen validator, Watermark exports

---

### Parent Plan
- **Target:** Parents/Families
- **Price:** 
  - **$20/month** (billed annually)
  - **$25/month** (billed monthly)
- **Features:** Full exports (no watermarks), 300 stories/month soft limit, Purchase additional stories as needed

---

### Teacher Pro (Coming Soon)
- **Target:** Teachers
- **Price:** TBD
- **Features:** Full exports, Folders, IEP formats, No watermarks

---

### School & District Licenses
- **Status:** Coming Soon
- **Price:** TBD`
  },
  {
    id: 'wiki_roadmap',
    title: 'Product Roadmap',
    category: 'product',
    content: `# Product Roadmap & Milestones

## Launch Timeline

### Private Beta — Jan 28, 2026
- **Goals:** Recruit 50 beta testers, Gather feedback, Iterate on core features
- **Target Users:** Teachers, SLPs, parents from pilot schools

### Public Beta — Mar 1, 2026
- **Goals:** Grow to 500 users, Product iteration, Build testimonials
- **Target Users:** K-4 teachers, reading specialists, parents

### Public Launch — May 15, 2026
- **Event:** Vancouver Web Summit (Featured Startup)
- **Goals:** Full launch, Major press, Investor meetings, School licensing

### District Ready — Sept 2026
- **Goals:** Full K-8 phonics coverage, District licensing, Partner integrations

---

## Awards & Recognition

- 🏆 Finalist Runner-Up at IE Venture Lab Competition, Dec 2025
- 🎓 Incubated at TMU Social Ventures Zone
- 🚀 Featured Startup at Vancouver Web Summit, May 2026`
  },
  {
    id: 'wiki_competitors',
    title: 'Competitive Landscape',
    category: 'product',
    content: `# Competitive Landscape

## Direct Competitors

### Reading A-Z / Raz-Kids
- **Strengths:** Massive content library, established in schools
- **Weaknesses:** Not personalized, generic content, not decodable-focused
- **Our Edge:** AI personalization, scope-aligned decodability

### Epic!
- **Strengths:** Large library, engaging UI, popular with kids
- **Weaknesses:** Not structured literacy aligned, not decodable
- **Our Edge:** Science of Reading aligned, Orton-Gillingham methodology

### Lexia Learning
- **Strengths:** Data-driven, research-backed, district adoption
- **Weaknesses:** Expensive, heavy gamification
- **Our Edge:** No gamification, teacher-first, interest-based

---

## Market Opportunity

| Metric | Value |
|--------|-------|
| **TAM** | $6.2B+ global K-8 literacy tools |
| **SAM** | ~$450M English-speaking structured literacy |
| **SOM** | ~$15M via platform licensing partners |`
  },

  // OPERATIONS
  {
    id: 'wiki_pilots_traction',
    title: 'Pilots & Traction',
    category: 'operations',
    content: `# Pilots & Traction

## Active Pilots

### Montcrest School
- **Location:** Toronto, Canada
- **Educators:** 12 | **Students:** 20
- **Status:** ✅ Active

### Multi-school Cohort
- **Schools:** 4-5 | **Students:** 100
- **Launched:** November 2025
- **Status:** ✅ Active

---

## Testimonials

> "PhonoLogic saves me 5-6 hours a week in finding appropriate reading for my students."
> — **Grade 4/5 Reading Specialist**

> "PhonoLogic doesn't just give me time back, it allows me to teach the way I aspire to."
> — **Grade 1 Homeroom Teacher**

> "I wish I had a tool like this when I was practicing. Very practical."
> — **Retired Speech Pathologist**`
  },
  {
    id: 'wiki_brand_guidelines',
    title: 'Brand Guidelines',
    category: 'operations',
    content: `# Brand Guidelines

## Brand Archetype
**The Sage** — Credible and trustworthy with parents/teachers (maroon), warm and engaging with children (orange).

## Tone of Voice
Warm, encouraging, and professional. We speak like a **trusted friend who happens to be an expert**.

---

## Key Messages
- "Where literacy meets possibility"
- "Reading practice that fits any learner in minutes"
- "Needed by some, beneficial for all"
- "Practice makes progress"

## Do NOT Say
- ❌ "Cure" or "fix" reading disorders
- ❌ "Replace professional intervention"
- ❌ "Gamified" or "game-based"
- ❌ "AI replaces teachers"

---

## Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| **Primary Orange** | #F97316 | Child-facing content, CTAs |
| **Primary Maroon** | #7C2D12 | Parent/teacher facing |
| **Secondary Cream** | #FEF3C7 | Backgrounds |

## Typography
- **General Sans** (600, 700) — Headers
- **Open Sauce Sans** (400) — Body text`
  },

  // ANALYTICS
  {
    id: 'wiki_metrics',
    title: 'Metrics & KPIs',
    category: 'analytics',
    content: `# Metrics & KPIs

## Product Metrics Targets

| Metric | Target |
|--------|--------|
| **Prep Time Saved** | ~45 minutes per lesson |
| **Validator Pass Rate** | 95% |
| **First Read Success** | ≥70% |
| **Weekly Active Teachers** | ≥60% |

---

## Business Metrics

| Metric | Target |
|--------|--------|
| **Pilot to Paid Conversion** | 60% |
| **Free to Pro Conversion** | 5-10% |
| **Teacher Churn** | 15% |
| **School Churn** | 10% |

---

## Financial Targets

| Metric | Target |
|--------|--------|
| **Inference Cost** | <2¢ per passage |
| **Gross Margin (Teacher)** | ~76% |
| **Gross Margin (School)** | ~71% |

---

## Dashboards
- **Looker Studio:** [Analytics Dashboard](https://lookerstudio.google.com/reporting/b0e96076-597e-429d-bb09-229354c85aee)`
  },

  // POLICIES
  {
    id: 'wiki_privacy',
    title: 'Data & Privacy Policy',
    category: 'policies',
    content: `# Data & Privacy Policy

## Core Principles
1. **No student identifying data collection**
2. **Privacy first** — Minimal data collection
3. **Transparency** — Clear about what we collect

---

## What We DON'T Collect
- ❌ Student names
- ❌ Student photos
- ❌ Student assessment scores
- ❌ Location data
- ❌ Third-party tracking

---

## COPPA Compliance
- No direct data collection from children under 13
- Parental/teacher consent required
- No targeted advertising`
  },
  {
    id: 'wiki_investor_materials',
    title: 'Investor Materials',
    category: 'policies',
    content: `# Investor Materials

## Current Fundraising

| Item | Details |
|------|---------|
| **Round** | Pre-Seed SAFE |
| **Target** | $250,000 |
| **Status** | Raising |

---

## Pitch Decks

| Deck | Link |
|------|------|
| **Google Accelerator Pitch** | [View on Pitch.com](https://app.pitch.com/app/presentation/f5ac655d-84e6-432f-bdf0-aa96f2deea3b/fdf5bf0d-1c5b-4a42-ba17-4ea1514d62be/d0b9f7cc-86c8-4d22-aaac-e175bc8a36a9) |
| **Branding Kit** | [View on Pitch.com](https://app.pitch.com/app/presentation/f5ac655d-84e6-432f-bdf0-aa96f2deea3b/d93a032e-cdc6-412b-94a4-8b6acf0cbb40/8f529e23-7455-4ed7-82c0-c4bd049ff90c) |

---

## Target Investors
- EdTech VCs
- Impact Investors
- Literacy-focused foundations`
  }
];

/**
 * Check if wiki needs to be reseeded based on version
 */
async function shouldReseed(redis) {
  const storedVersion = await redis.get(WIKI_VERSION_KEY);
  if (!storedVersion) return true;
  
  // Compare versions - newer version should reseed
  return storedVersion !== WIKI_VERSION;
}

/**
 * Seed wiki pages into Redis (can be called internally or via API)
 */
async function seedWikiPages(redis, force = false) {
  // Check if reseed needed (unless forced)
  if (!force) {
    const needsReseed = await shouldReseed(redis);
    if (!needsReseed) {
      console.log('[WIKI SEED] Version matches, skipping reseed');
      return 0;
    }
  }
  
  const WIKI_KEY = 'phonologic:wiki';
  
  for (const page of wikiPages) {
    const pageData = {
      title: page.title,
      content: page.content,
      category: page.category,
      author: 'Brain Sync',
      authorEmail: 'system@phonologic.ca',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    await redis.hset(WIKI_KEY, { [page.id]: JSON.stringify(pageData) });
  }
  
  // Store the current version
  await redis.set(WIKI_VERSION_KEY, WIKI_VERSION);
  console.log(`[WIKI SEED] Seeded ${wikiPages.length} pages, version: ${WIKI_VERSION}`);
  
  return wikiPages.length;
}

// API handler
const handler = async (req, res) => {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
  
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed. Use POST.' });
  }

  // Require authentication
  const session = getSessionFromRequest(req);
  if (!session) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  // Require admin
  const isAdmin = await checkIsAdmin(session.email);
  if (!isAdmin) {
    return res.status(403).json({ error: 'Admin privileges required' });
  }

  const redis = getRedis();
  if (!redis) {
    return res.status(503).json({ error: 'Database unavailable' });
  }

  console.log(`[WIKI SEED] Starting seed by ${session.email}`);

  let created = 0;
  let failed = 0;
  const errors = [];

  for (const page of wikiPages) {
    const pageData = {
      title: page.title,
      content: page.content,
      category: page.category,
      author: 'Brain Sync',
      authorEmail: 'system@phonologic.ca',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    try {
      await redis.hset(REDIS_KEYS.WIKI, { [page.id]: JSON.stringify(pageData) });
      created++;
    } catch (error) {
      failed++;
      errors.push({ page: page.title, error: error.message });
    }
  }

  console.log(`[WIKI SEED] Complete: ${created} created, ${failed} failed`);

  return res.status(200).json({
    success: true,
    message: `Wiki seeded with ${created} pages`,
    created,
    failed,
    errors: errors.length > 0 ? errors : undefined
  });
};

// Export handler as default and attach named exports
handler.seedWikiPages = seedWikiPages;
handler.shouldReseed = shouldReseed;
handler.wikiPages = wikiPages;
handler.WIKI_VERSION = WIKI_VERSION;

module.exports = handler;
