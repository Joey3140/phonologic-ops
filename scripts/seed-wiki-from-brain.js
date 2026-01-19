/**
 * Wiki Seed Script - Comprehensive company wiki from Brain knowledge
 * 
 * Run with: UPSTASH_REDIS_REST_URL=xxx UPSTASH_REDIS_REST_TOKEN=xxx node scripts/seed-wiki-from-brain.js
 * 
 * Categories:
 * - getting-started: Onboarding, company overview, tools
 * - development: Tech stack, deployment, architecture
 * - product: Product info, features, roadmap
 * - operations: Processes, workflows, team
 * - analytics: Metrics, KPIs, dashboards
 * - policies: Security, guidelines, compliance
 */

const { Redis } = require('@upstash/redis');

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN
});

const WIKI_KEY = 'phonologic:wiki';

const wikiPages = [
  // ============================================================================
  // GETTING STARTED
  // ============================================================================
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

  // ============================================================================
  // DEVELOPMENT
  // ============================================================================
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
| **dev.phonologic.cloud** | Development/staging |

---

## Key Libraries

**Node.js (Vercel):**
- @upstash/redis - Database client
- google-auth-library - OAuth

**Python (Orchestrator):**
- agno - Agentic AI framework
- fastapi - API framework
- anthropic - Claude client
- pydantic - Data validation`
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
| **Start Command** | \`uvicorn main:app --host 0.0.0.0 --port 8000\` |

---

## Environment Variables

**Vercel:**
- \`UPSTASH_REDIS_REST_URL\`
- \`UPSTASH_REDIS_REST_TOKEN\`
- \`GOOGLE_CLIENT_ID\`
- \`GOOGLE_CLIENT_SECRET\`
- \`SESSION_SECRET\` (32+ chars, no fallback!)
- \`ORCHESTRATOR_URL\`

**Railway:**
- \`ANTHROPIC_API_KEY\`
- \`PORT=8000\`
- \`GOOGLE_SERVICE_ACCOUNT_JSON\`

---

## Rollback Procedure

1. Go to Vercel/Railway dashboard
2. Find previous successful deployment
3. Click "Redeploy" or "Rollback"
4. Document incident in ClickUp`
  },
  {
    id: 'wiki_architecture',
    title: 'System Architecture',
    category: 'development',
    content: `# System Architecture

## High-Level Overview

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│                     ops.phonologic.cloud                     │
│                    (Vercel - Static SPA)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Vercel Serverless APIs                    │
│  /api/auth/* │ /api/wiki/* │ /api/announcements/* │ etc.   │
└─────────────────────────────────────────────────────────────┘
                    │                       │
                    ▼                       ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│      Upstash Redis       │    │   Railway Orchestrator   │
│  (Users, Wiki, Goals)    │    │    (Agno + FastAPI)      │
└──────────────────────────┘    └──────────────────────────┘
                                            │
                                            ▼
                                ┌──────────────────────────┐
                                │    Claude (Anthropic)    │
                                │      LLM Provider        │
                                └──────────────────────────┘
\`\`\`

---

## Orchestrator Agent Teams

### 1. Marketing Fleet
- **Purpose:** Campaign strategy, market research, creative direction
- **Agents:** Researcher, TechnicalConsultant, BrandLead, ImageryArchitect
- **Output:** Marketing strategies, Midjourney prompts

### 2. Project Ops
- **Purpose:** Task automation, document generation, communications
- **Agents:** Coordinator, TaskManager, DocumentManager, Communicator
- **Integrations:** ClickUp, Google Drive, SendGrid

### 3. Browser Navigator
- **Purpose:** Browser automation, slide/canvas analysis
- **Agents:** BrowserNavigator
- **Uses:** Playwright for browser control

### 4. Brain Curator
- **Purpose:** Knowledge management for Stephen
- **Features:** Conflict detection, natural language input, misconception correction

---

## Data Flow

1. **User** → Ops Portal (Vercel)
2. **Ops Portal** → Vercel Serverless API
3. **API** → Upstash Redis (data) OR Railway Orchestrator (AI)
4. **Orchestrator** → Claude API → Response
5. **Response** → Back through chain to User`
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

**Current Admins:**
- joey@phonologic.ca
- stephen@phonologic.ca

(Configured via \`ADMIN_EMAILS\` environment variable)

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
4. **Admin Protection:** Admins cannot self-demote

---

## Data Storage

| Data Type | Storage | Encryption |
|-----------|---------|------------|
| **User Sessions** | Redis (TTL 7 days) | ✅ |
| **Wiki Content** | Redis | Transit only |
| **Announcements** | Redis | Transit only |

---

## Incident Response

1. **Detect:** Monitor Vercel/Railway logs
2. **Contain:** Revoke affected sessions
3. **Investigate:** Review logs, identify scope
4. **Remediate:** Fix vulnerability, rotate secrets
5. **Document:** Post-mortem in ClickUp`
  },

  // ============================================================================
  // PRODUCT
  // ============================================================================
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
- Schools and districts implementing structured literacy

---

## Differentiators

| What We Do | What We Don't Do |
|------------|------------------|
| No gamified reward loops | Focus on learning |
| No advertising in product | Clean experience |
| No student identifying data collection | Privacy first |
| Research-first approach | Teachers can trust |
| Built alongside educators | Real classroom feedback |`
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
- **Features:**
  - Limited generations
  - On-screen validator
  - Watermark exports

---

### Parent Plan
- **Target:** Parents/Families
- **Price:** 
  - **$20/month** (billed annually)
  - **$25/month** (billed monthly)
- **Features:**
  - Full exports (no watermarks)
  - 300 stories/month soft limit
  - Purchase additional stories as needed

---

### Teacher Pro (Coming Soon)
- **Target:** Teachers
- **Price:** TBD
- **Features:**
  - Full exports
  - Folders for organization
  - IEP-friendly formats
  - No watermarks

---

### School License (Coming Soon)
- **Target:** Schools
- **Price:** TBD
- **Features:** TBD

---

### District License (Coming Soon)
- **Target:** Districts
- **Price:** TBD
- **Features:** TBD

---

## Pricing Philosophy

- Accessible to individual parents and teachers
- Value-based pricing tied to time saved
- School/district pricing will include support and training`
  },
  {
    id: 'wiki_roadmap',
    title: 'Product Roadmap',
    category: 'product',
    content: `# Product Roadmap & Milestones

## Launch Timeline

### Private Beta — Jan 28, 2026
- **Duration:** Jan 28 - Mar 1, 2026
- **Goals:**
  - Recruit 50 beta testers
  - Gather feedback
  - Iterate on core features
- **Target Users:** Teachers, SLPs, parents from pilot schools

---

### Public Beta — Mar 1, 2026
- **Duration:** Mar 1 - May 14, 2026
- **Goals:**
  - Grow to 500 users
  - Product iteration based on feedback
  - Build testimonials
- **Target Users:** K-4 teachers, reading specialists, parents

---

### Public Launch — May 15, 2026
- **Event:** Vancouver Web Summit (Featured Startup)
- **Goals:**
  - Full launch
  - Major press coverage
  - Investor meetings
  - Drive signups and awareness
  - School licensing begins

---

### District Ready — Sept 2026
- **Goals:**
  - Full K-8 phonics coverage
  - District licensing
  - Partner integrations

---

## Completed Milestones

| Date | Milestone | Status |
|------|-----------|--------|
| Dec 2025 | Validate Scopes VI-VIII in classrooms | ✅ |
| Dec 2025 | Expand wordbank to >5,000 entries | ✅ |
| Dec 2025 | Deliver 100+ exemplar stories with evidence scorecards | ✅ |

---

## In Progress

| Date | Milestone | Status |
|------|-----------|--------|
| Jan 2026 | Ship SSO/rostering and district analytics | 🔄 |
| Jan 28 | Private Beta Launch | 📅 |

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
- **Website:** readinga-z.com
- **What They Do:** Large library of leveled readers and printable books
- **Strengths:** Massive content library, established in schools, leveling system
- **Weaknesses:** Not personalized to student interests, generic content, not decodable-focused
- **Our Differentiators:** AI personalization, scope-aligned decodability, student interest matching
- **Pricing:** School subscription

---

### Epic!
- **Website:** getepic.com
- **What They Do:** Digital library for kids with 40,000+ books
- **Strengths:** Large library, engaging UI, popular with kids
- **Weaknesses:** Not structured literacy aligned, not decodable, entertainment-focused
- **Our Differentiators:** Science of Reading aligned, decodable texts, Orton-Gillingham methodology
- **Pricing:** ~$10/month subscription

---

### Lexia Learning
- **Website:** lexialearning.com
- **What They Do:** Adaptive learning platform for literacy
- **Strengths:** Data-driven, research-backed, district adoption
- **Weaknesses:** Expensive, heavy gamification, less personalized content
- **Our Differentiators:** No gamification, teacher-first approach, interest-based personalization
- **Pricing:** District pricing

---

## Market Opportunity

| Metric | Value |
|--------|-------|
| **TAM** | $6.2B+ global annual spend on K-8 literacy tools |
| **SAM** | ~$450M in English-speaking K-5 schools using structured literacy |
| **SOM** | ~$15M via 2-3 platform licensing partners |

---

## Strategic Partner Targets

- McGraw Hill
- Newsela
- Toddle
- Microsoft Education`
  },

  // ============================================================================
  // OPERATIONS
  // ============================================================================
  {
    id: 'wiki_pilots_traction',
    title: 'Pilots & Traction',
    category: 'operations',
    content: `# Pilots & Traction

## Active Pilots

### Montcrest School
- **Location:** Toronto, Canada
- **Educators:** 12
- **Students:** 20
- **Status:** ✅ Active

---

### Multi-school Cohort
- **Schools:** 4-5 schools
- **Students:** 100
- **Launched:** November 2025
- **Status:** ✅ Active

---

## Planned Pilots

### The Einstein School
- **Location:** Florida, USA
- **Status:** 📅 Planned

---

## Testimonials

> "PhonoLogic saves me 5-6 hours a week in finding appropriate reading for my students."
> — **Grade 4/5 Reading Specialist**

> "PhonoLogic doesn't just give me time back, it allows me to teach the way I aspire to."
> — **Grade 1 Homeroom Teacher**

> "I wish I had a tool like this when I was practicing. Very practical."
> — **Retired Speech Pathologist**

---

## Traction Highlights

- ✅ Live in classrooms, iterating directly with teachers
- ✅ Finalist Runner-Up at IE Venture Lab Competition Dec 2025
- ✅ Incubated at TMU Social Ventures Zone
- ✅ Featured Startup at Vancouver Web Summit May 2026`
  },
  {
    id: 'wiki_communication_norms',
    title: 'Communication Guidelines',
    category: 'operations',
    content: `# Communication Guidelines

## Channels

| Channel | Use For |
|---------|---------|
| **Email** | External communication, formal internal matters |
| **Google Meet** | Meetings, video calls |
| **ClickUp** | Tasks, project updates, async work |
| **Ops Portal Announcements** | Team-wide updates |
| **Ops Portal Wiki** | Persistent documentation |

---

## Response Times

| Priority | Expected Response |
|----------|-------------------|
| **Urgent** | Same day |
| **Normal** | Within 24 hours |
| **Low** | Within 48 hours |

---

## Meeting Guidelines

- Default to **25 or 50 minute** meetings (not 30/60)
- Always have an **agenda**
- Document **decisions and action items**
- Prefer **async** when possible

---

## Documentation Standards

| Type | Where |
|------|-------|
| Major decisions | Wiki (this portal) |
| Project updates | ClickUp |
| Meeting notes | Google Docs |
| Team announcements | Ops Portal |

---

## Best Practices

- ✅ Be concise and clear
- ✅ Use bullet points for readability
- ✅ Include context and next steps
- ✅ Tag relevant people directly
- ❌ Don't use reply-all unnecessarily
- ❌ Don't schedule meetings that could be emails`
  },
  {
    id: 'wiki_ai_hub',
    title: 'AI Hub & Orchestrator',
    category: 'operations',
    content: `# AI Hub & Orchestrator

## Overview

The AI Hub is powered by the **Agno Orchestrator** - a multi-agent system that automates various company tasks.

**Access:** AI Hub tab in the Operations Portal

---

## Agent Teams

### 1. Marketing Fleet 🎨
- **Purpose:** Campaign strategy & creative direction
- **Agents:** Researcher, TechnicalConsultant, BrandLead, ImageryArchitect
- **Use Cases:**
  - Market research
  - Campaign strategy development
  - Midjourney prompt generation
  - Brand positioning

### 2. Project Ops 📋
- **Purpose:** Task automation & communications
- **Agents:** Coordinator, TaskManager, DocumentManager, Communicator
- **Use Cases:**
  - Employee/client onboarding
  - ClickUp task creation
  - Progress report generation
  - Email automation

### 3. Browser Navigator 🌐
- **Purpose:** Browser automation & analysis
- **Agents:** BrowserNavigator
- **Use Cases:**
  - Slide deck analysis
  - Brand compliance checking
  - Web scraping

### 4. Brain Curator 🧠
- **Purpose:** Knowledge management
- **Features:**
  - Natural language knowledge input
  - Conflict detection
  - Misconception correction
  - Query existing knowledge

---

## PhonoLogics Brain

The central knowledge base containing:
- Company information
- Brand guidelines
- Product positioning
- Team directory
- Pitch materials
- Competitor analysis

**Query via:** AI Hub → Brain Curator chat`
  },
  {
    id: 'wiki_brand_guidelines',
    title: 'Brand Guidelines',
    category: 'operations',
    content: `# Brand Guidelines

## Brand Archetype

**The Sage** — Credible and trustworthy with parents/teachers (maroon), warm and engaging with children (orange).

---

## Tone of Voice

Warm, encouraging, and professional. We speak like a **trusted friend who happens to be an expert**.

---

## Key Messages

- "Where literacy meets possibility"
- "Reading practice that fits any learner in minutes"
- "Needed by some, beneficial for all"
- "Finding a text that fits your learner should not be the hard part"
- "Practice makes progress"
- "Building confidence one story at a time"

---

## Do NOT Say

- ❌ "Cure" or "fix" reading disorders
- ❌ "Replace professional intervention"
- ❌ "Guarantee specific outcomes"
- ❌ Clinical jargon without explanation
- ❌ "Gamified" or "game-based" (we don't do gamification)
- ❌ "AI replaces teachers" (we support teachers)

---

## Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| **Primary Orange** | #F97316 | Warm, engaging - child-facing content, CTAs |
| **Primary Maroon** | #7C2D12 | Professional, trustworthy - parent/teacher facing |
| **Secondary Cream** | #FEF3C7 | Warm background color |

---

## Typography

| Font | Weight | Usage |
|------|--------|-------|
| **General Sans** | 600, 700 | Headers, display text |
| **Open Sauce Sans** | 400 | Body text |

---

## Logo Usage

- **Orange P icon:** Child-facing contexts
- **Maroon P icon:** Professional contexts
- **Assets:** [Google Drive - Marketing folder](https://drive.google.com/drive/folders/1Qls5x8RlaEfyjLqH-rQ9fN6byRfCKWRC)

---

## Approved Channels

Instagram, Facebook, LinkedIn, Email, Blog, Education Conferences`
  },

  // ============================================================================
  // ANALYTICS
  // ============================================================================
  {
    id: 'wiki_metrics_targets',
    title: 'Metrics & KPIs',
    category: 'analytics',
    content: `# Metrics & KPIs

## Product Metrics Targets

| Metric | Target |
|--------|--------|
| **Prep Time Saved** | ~45 minutes per lesson |
| **Validator Pass Rate** | 95% |
| **First Read Success** | ≥70% (no adult decoding beyond prompts) |
| **Weekly Active Teachers** | ≥60% |

---

## Business Metrics Targets

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

## Year 2 Goals

| Metric | Target |
|--------|--------|
| **Teacher Users** | >10,000 |
| **School Pilots** | >200 |
| **Time Saved per Teacher** | 3+ hours/week |

---

## Market Stats

| Metric | Value |
|--------|-------|
| **K-6 Teachers in North America** | 1.6M |
| **Structured Literacy Adoption** | 40% of public school classrooms |

---

## Dashboards

- **Looker Studio:** [Analytics Dashboard](https://lookerstudio.google.com/reporting/b0e96076-597e-429d-bb09-229354c85aee)`
  },

  // ============================================================================
  // POLICIES
  // ============================================================================
  {
    id: 'wiki_data_privacy',
    title: 'Data & Privacy Policy',
    category: 'policies',
    content: `# Data & Privacy Policy

## Core Principles

1. **No student identifying data collection** — We don't store student PII
2. **Privacy first** — Minimal data collection
3. **Transparency** — Clear about what we collect and why

---

## What We Collect

### Operations Portal
- Google account email (for @phonologic.ca users only)
- User preferences and settings
- Wiki contributions and edits

### Product (Student-facing)
- Phonics scope selections
- Interest preferences (anonymized)
- Usage patterns (anonymized)

---

## What We DON'T Collect

- ❌ Student names
- ❌ Student photos
- ❌ Student assessment scores
- ❌ Student behavioral data
- ❌ Location data
- ❌ Third-party tracking

---

## Data Storage

| Data | Location | Retention |
|------|----------|-----------|
| User sessions | Upstash Redis | 7 days |
| Wiki content | Upstash Redis | Indefinite |
| Generated stories | Not stored | Ephemeral |

---

## COPPA Compliance

As we work with K-8 students, we're committed to COPPA compliance:
- No direct data collection from children under 13
- Parental/teacher consent required
- No targeted advertising`
  },
  {
    id: 'wiki_expense_policy',
    title: 'Expense Policy',
    category: 'policies',
    content: `# Expense Policy

## General Guidelines

- All expenses must have a **clear business purpose**
- **Receipts required** for all expenses
- Submit expenses **within 30 days**

---

## Pre-Approved Expenses

No approval needed for:
- Software subscriptions under $50/month
- Books and learning materials
- Domain renewals

---

## Requires Approval

Contact Stephen before purchasing:
- Software over $50/month
- Hardware purchases
- Travel expenses
- Conference attendance

---

## How to Submit

1. Keep all receipts
2. Document business purpose
3. Submit via expense system
4. Await approval

---

## Reimbursement

- Processed bi-weekly
- Direct deposit to bank account`
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

## Key Pitch Points

1. **Problem:** 1 in 2 students don't read at grade level
2. **Solution:** AI-generated decodable texts
3. **Market:** $6.2B+ TAM, 40% structured literacy adoption
4. **Traction:** Live in classrooms, IE Venture Lab finalist
5. **Team:** Education + Tech + Business expertise
6. **Ask:** $250K SAFE for private beta → public launch

---

## Target Investors

- EdTech VCs
- Impact Investors
- Literacy-focused foundations

---

## Traction Points for Investors

- ✅ Finalist Runner-Up at IE Venture Lab Competition Dec 2025
- ✅ Incubated at TMU Social Ventures Zone
- ✅ Completed pilot with Montcrest School, Toronto
- ✅ Live in classrooms, iterating with teachers
- ✅ Featured Startup at Vancouver Web Summit May 2026
- ✅ Teacher testimonial: "Saves me 5-6 hours a week"

---

## Upcoming Events

| Event | Date | Status |
|-------|------|--------|
| **Vancouver Web Summit** | May 2026 | Featured Startup |

Public launch will be centered around this event.`
  }
];

async function seedWiki() {
  console.log('🧠 Seeding wiki from Brain knowledge...\n');
  console.log('Categories: getting-started, development, product, operations, analytics, policies\n');

  let created = 0;
  let failed = 0;

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
      await redis.hset(WIKI_KEY, { [page.id]: JSON.stringify(pageData) });
      console.log(`✓ [${page.category}] ${page.title}`);
      created++;
    } catch (error) {
      console.error(`✗ Failed: ${page.title} - ${error.message}`);
      failed++;
    }
  }

  console.log('\n' + '='.repeat(50));
  console.log(`Wiki seeding complete!`);
  console.log(`✓ Created: ${created}`);
  if (failed > 0) console.log(`✗ Failed: ${failed}`);
  console.log(`Total pages: ${wikiPages.length}`);
}

seedWiki().catch(console.error);
