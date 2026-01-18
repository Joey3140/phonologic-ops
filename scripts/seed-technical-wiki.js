/**
 * Technical Wiki Seed Script - Adds comprehensive technical documentation
 */

const { Redis } = require('@upstash/redis');

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN
});

const WIKI_KEY = 'phonologic:wiki';

const technicalPages = [
  {
    id: 'wiki_product_overview',
    title: 'Product Overview',
    category: 'onboarding',
    content: `**What is PhonoLogic?**

PhonoLogic is an **AI-powered decodable story generator** for early literacy education. It generates phonologically-constrained stories based on:
- Child's current phonics level (assessment-driven)
- Child's interests (AI-personalized content)
- Science of reading methodology (17-scope curriculum)

**Core Value Proposition**
"Every child gets stories written just for them, targeting exactly what they need to learn."

**Current Version:** v6.4.3 (as of Jan 2026)

**Domains**
| Environment | Domain | Branch |
|-------------|--------|--------|
| Production | phonologic.cloud | main |
| Staging | dev.phonologic.cloud | development |

**Target Users:**
- Children aged 3-12 with speech/reading difficulties
- Parents seeking literacy resources
- Speech-Language Pathologists (SLPs)
- Schools and educational institutions

**Key Differentiators:**
- Real-time AI story generation
- Phonics-based curriculum (17 scopes)
- Engaging personalized content
- Affordable compared to traditional therapy
- Accessible from home`
  },
  {
    id: 'wiki_tech_stack_detailed',
    title: 'Technology Stack (Detailed)',
    category: 'decisions',
    content: `**Backend**
| Technology | Version | Purpose |
|------------|---------|---------|
| Node.js | 16+ | Runtime |
| Express.js | ^4.19.2 | Web framework |
| Vercel | Serverless | Deployment platform |

**AI/LLM Providers**
| Provider | Models | Use Case |
|----------|--------|----------|
| Google Gemini | gemini-2.5-pro, gemini-3 | Primary story generation (cheapest, fastest) |
| OpenAI | gpt-4o-mini, gpt-5, gpt-5-mini | Fallback, premium quality |

**Database & Caching**
| Service | Purpose |
|---------|---------|
| Google Firestore | Primary database (accounts, profiles, stories, assessments) |
| Upstash Redis | Rate limiting, session cache, generation locks |
| Google BigQuery | Analytics, ML training data |

**Authentication**
| Method | Users |
|--------|-------|
| Google OAuth | New users (OAuth 2.0 flow) |
| Legacy Password | Pilot accounts (admin, school_montcrest, individual, school_marysia) |

**Key Dependencies**
- @google-cloud/bigquery: ^8.1.1
- @google-cloud/firestore: ^7.10.0
- @google-cloud/secret-manager: ^5.6.0
- @upstash/redis: ^1.36.0
- openai: ^4.56.0
- express-rate-limit: ^7.2.0
- google-auth-library: ^9.0.0`
  },
  {
    id: 'wiki_environment_variables',
    title: 'Environment Variables',
    category: 'howto',
    content: `**Required Environment Variables**

**AI APIs**
- OPENAI_API_KEY - OpenAI API key for fallback generation

**Google OAuth**
- GOOGLE_OAUTH_CLIENT_ID - OAuth client ID
- GOOGLE_OAUTH_CLIENT_SECRET - OAuth client secret

**Session Security**
- SESSION_SECRET - Session secret (32+ chars)

**Redis (Rate Limiting)**
- UPSTASH_REDIS_REST_URL - Upstash Redis URL
- UPSTASH_REDIS_REST_TOKEN - Upstash Redis token

**Google Cloud (Firestore, BigQuery)**
- GOOGLE_APPLICATION_CREDENTIALS_JSON - Service account JSON

**Optional Variables**
- OPENAI_MODEL - Default: gpt-4o-mini
- MAX_RETRIES - Default: 5
- MAX_WORDS - Default: 120
- MIN_FOCUS_PERCENT - Default: 10
- MAX_DISALLOWED - Default: 8`
  },
  {
    id: 'wiki_firestore_data_model',
    title: 'Firestore Data Model',
    category: 'decisions',
    content: `**Collections Hierarchy**

accounts/{accountId}
- googleId: string
- email: string
- name: string
- type: "admin" | "school" | "individual" | "parent"
- authMethod: "google" | "password"
- createdAt: string
- lastLoginAt: string
- profileCount: number
- isActive: boolean

accounts/{accountId}/profiles/{profileId}
- name: string (FirstName L. format)
- grade: string (K, 1, 2, ..., 7/8)
- interests: string
- createdAt: string
- storyCount: number
- learningPlan: { mastered: string[], focus: string[] }
- learningData: { troubleWords: string[] }

accounts/{accountId}/profiles/{profileId}/stories/{storyId}
- title: string
- prompt: string
- content: string
- narrator: string
- grade: string
- aiModel: string
- focusWordsBySubscope: object
- focusPercent: number
- disallowedWords: string[]
- isFavorite: boolean
- createdAt: string

**Other Collections**
- audit_log/{logId} - Security audit trail
- privacy_requests/{requestId} - GDPR data requests
- assessmentSessions/{id} - Assessment v2 sessions

**ID Patterns**
- ACCOUNT: /^acct_\\d+_[a-z0-9]+$/ (e.g., acct_1704067200000_abc123)
- PROFILE: /^prof_\\d+_[a-zA-Z0-9]+$/ (e.g., prof_1704067200000_XyZ789)
- STORY: /^story_\\d+_[a-zA-Z0-9]+$/ (e.g., story_1704067200000_AbC456)
- LEGACY_ACCOUNT: /^[a-z_]+$/ (e.g., admin, school_montcrest)`
  },
  {
    id: 'wiki_api_endpoints',
    title: 'API Endpoints Reference',
    category: 'howto',
    content: `**Authentication**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/auth | POST | Legacy password login |
| /api/auth-google | GET | Google OAuth initiate/callback |

**Profiles**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/profiles | GET | List profiles for account |
| /api/profiles | POST | Create new profile (max 4) |
| /api/profiles | PUT | Update profile |
| /api/profiles | DELETE | Delete profile |
| /api/switch-profile | POST | Switch active profile |

**Stories**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/generate | POST | Generate new story (SSE streaming) |
| /api/validate-text | POST | Validate edited story text |
| /api/stories | GET | List stories for profile |
| /api/stories | PUT | Update story (favorite toggle) |
| /api/stories | DELETE | Delete story |

**Assessment**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/assessment | POST | Assessment v1 (checkbox-based) |
| /api/assessment-v2 | POST | Assessment v2 (story-based) |
| /api/trouble-words | GET/POST/DELETE | Trouble word tracking |
| /api/progress-report | GET | Learner progress data |

**Utility**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/stats | GET | Usage statistics |
| /api/version | GET | Current version info |
| /api/privacy-contact | POST | GDPR contact form |

**Function Timeouts (vercel.json)**
- /api/generate - 420s (7 minutes)
- /api/assessment-v2 - Default
- Most others - 10s`
  },
  {
    id: 'wiki_phonics_curriculum',
    title: 'Phonics Curriculum (17 Scopes)',
    category: 'decisions',
    content: `**Scope Sequence (Canonical)**

| Scope | Name | Grade | Key Subscopes |
|-------|------|-------|---------------|
| I | CVC | K | cvc |
| II | Basic Blends | K | blend |
| III | Digraphs | K | ch, sh, th, wh, ck, ng, nk, ff, ll, ss, zz |
| IV | Magic E (VCe) | 1 | VCe (a_e), VCe (i_e), VCe (o_e), VCe (u_e), VCe (e_e) |
| V | R-Controlled | 2 | ar, er, ir, or, ur |
| VI | Vowel Teams I | 2 | ai/ay, ea/ee, oa/oe, ue/ui, ow_long |
| VII | Diphthongs | 3 | oo, au/aw, ou/ow, oi/oy, igh |
| VIII | Inflections | 3 | -s/es, -ed, -ing |
| IX | Compounds | 3 | compound |
| X | Final Syllables | 4 | final -le, -tch, -dge |
| XI | Soft C/G | 4 | soft c (ce, ci, cy), soft g (ge, gi, gy) |
| XII | Silent Letters | 5 | kn-, wr-, -mb, gn |
| XIII | Common Suffixes | 5 | -ful, -less, -ness, -ment, -ly, -ship |
| XIV | Latin Suffixes | 6 | -tion, -sion, -ture, -ive, -ous, -able, -ible, -ist |
| XV | Prefixes | 6 | un-, re-, pre-, dis-, mis-, para- |
| XVI | Latin Roots | 7/8 | tract, port, spect, form, struct |
| XVII | Greek Forms | 7/8 | bio, geo, graph, phone, photo, tele |

**Subscope Source of Truth**
CRITICAL: public/index.html is the canonical source for subscope assignments.
1. index.html = SOURCE OF TRUTH
2. api/subscope-definitions.js = must match index.html
3. Other files reference these

**Wordbank**
- Source file: Wordbank_MASTER.csv
- Compiled data: api/wordbank-data.json (3.1MB, ~116 subscope buckets)
- Build command: node build-wordbank.js
- Context vocabulary: api/context-wordbank.json (49KB)`
  },
  {
    id: 'wiki_narrator_system',
    title: 'Narrator System',
    category: 'howto',
    content: `**Available Narrators (6 total)**

| ID | Label | Tone | Style |
|----|-------|------|-------|
| reteller | Reteller | Calm, Kind | Warm, simple storyteller (Cynthia Rylant style) |
| adventurer | Adventurer | Brave, Playful | Energetic, action-forward |
| detective | Detective | Curious, Serious | Spots clues, small reveals |
| builder | Builder | Curious, Calm | Procedural, materials-and-steps |
| friend | Friend | Kind, Friendly | Cooperation, acts of care |
| naturalist | Naturalist | Curious, Calm | Nonfiction-leaning, field notes |

**Narrator Configuration Parameters**
Each narrator has:
- dialogue_ratio_target_range: [min, max]
- sentence_length_words_target by scope group
- contraction_policy_by_scope
- sensory_priority: ["sight", "sound", "touch", etc.]
- ending_style: "small_win", "reveal", etc.
- question_prefs: ["literal", "inference", "prediction"]

**Config file:** narrator-config.json`
  },
  {
    id: 'wiki_assessment_system',
    title: 'Assessment System',
    category: 'howto',
    content: `**Assessment v1 (Checkbox-Based)**
- Quick initial placement
- Parent checks off known patterns
- Generates learning plan (mastered vs focus)
- Endpoint: /api/assessment

**Assessment v2 (Story-Based)**
- 3 short stories (60-80 words each)
- Difficulty levels: Grade-1, Grade, Grade+1
- Parent rates patterns as Good/Struggled/Needs Practice
- 5-8 minute total assessment
- Pause/resume capability (7-day session persistence)

**Key files:**
- API: /api/assessment-v2.js
- UI: /public/assessment-v2.html
- Schema: /docs/bigquery-assessment-tables.sql

**Learning Plan Output**
{
  mastered: ["cvc", "blend", "sh", "ch", ...],  // Green
  focus: ["ai/ay", "ea/ee", "-ed", ...],        // Orange
}

**Auto-Mastery Logic**
When reading level is high, system auto-marks lower grade subscopes as mastered.`
  },
  {
    id: 'wiki_security_patterns',
    title: 'Security Patterns',
    category: 'policies',
    content: `**Authentication Flow**
1. Google OAuth with CSRF state parameter (stored in Redis)
2. HTTP-only secure cookie for session token
3. Cookie verified on each API request

**ID Validation**
All IDs validated with regex patterns:
- isValidProfileId: /^prof_\\d+_[a-zA-Z0-9]+$/
- isValidAccountId: /^acct_\\d+_[a-z0-9]+$/
- isValidStoryId: /^story_\\d+_[a-zA-Z0-9]+$/

**Rate Limiting (per endpoint)**
| Endpoint | Limit |
|----------|-------|
| /api/generate | 10/min |
| /api/auth | 5/min |
| /api/validate-text | 30/min |
| /api/trouble-words | 30/min |

Implementation: Redis INCR with time-bucketed keys (O(1) memory)

**Input Sanitization**
- Profile names: FirstName L. format only
- Story titles: HTML stripped, 100 char max
- XSS prevention for LLM output

**Security Headers (vercel.json)**
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security: max-age=31536000

**CORS Origins**
- https://phonologic.cloud
- https://www.phonologic.cloud
- https://dev.phonologic.cloud
- https://staging.phonologic.cloud
- http://localhost:3000
- http://localhost:5000`
  },
  {
    id: 'wiki_deployment_workflow',
    title: 'Deployment Workflow',
    category: 'policies',
    content: `**CRITICAL RULE**
Never deploy to production without explicit user approval.

**Process**
1. Push to development branch - auto-deploys to dev.phonologic.cloud
2. Test on staging
3. Get explicit user approval
4. Merge development to main - auto-deploys to phonologic.cloud

**Version Management**
- Always update version in package.json
- Follow SemVer: MAJOR.MINOR.PATCH
- Update CHANGELOG.md with every release

**Build Command**
node build-wordbank.js && node build-context-wordbank.js

**Quick Reference Commands**
# Local development
npm run dev

# Build wordbank
npm run build

# Deploy to staging (auto on push to development)
git push origin development

# Deploy to production (REQUIRES APPROVAL)
git checkout main && git merge development && git push origin main`
  },
  {
    id: 'wiki_key_files',
    title: 'Key File Reference',
    category: 'howto',
    content: `**Core API Files**
| File | Purpose |
|------|---------|
| api/generate.js | Story generation (155KB, main logic) |
| api/accounts-db.js | Firestore helpers, ID validation |
| api/auth-google.js | Google OAuth flow |
| api/subscope-definitions.js | Subscope to grade mapping |
| api/rate-limiter.js | Redis rate limiting |
| api/cors-helper.js | CORS configuration |

**Frontend Files**
| File | Purpose |
|------|---------|
| public/index.html | Story configurator (SUBSCOPE SOURCE OF TRUTH) |
| public/script.js | Main UI logic, toggle handling |
| public/results.html | Story results display |
| public/library.html | Story library |
| public/progress.html | Learner progress dashboard |
| public/assessment-v2.html | Story-based assessment |
| public/global-header.js | Shared header component |

**Data Files**
| File | Purpose |
|------|---------|
| Wordbank_MASTER.csv | Source vocabulary data |
| api/wordbank-data.json | Compiled wordbank (3.1MB) |
| narrator-config.json | Narrator personalities |
| scope-sequence-canonical.tsv | Scope definitions |

**Documentation**
| File | Purpose |
|------|---------|
| CHANGELOG.md | Version history |
| DEPLOY_CHECKLIST.md | Deployment steps |
| INFRASTRUCTURE.md | Architecture docs |
| SCALING_STRATEGY.md | Scaling plans |`
  },
  {
    id: 'wiki_frontend_patterns',
    title: 'Frontend Patterns',
    category: 'decisions',
    content: `**Grade Badge Color System**
Dynamic coloring based on subscope mastery:
- --badge-default: #dc9435 (Orange)
- --badge-not-started: #ef4444 (Red)
- --badge-in-progress: #f59e0b (Yellow)
- --badge-mastered: #22c55e (Green)

**Brand Colors**
| Usage | Hex |
|-------|-----|
| Primary Orange | #dc9435 |
| Orange Hover | #c17f2a |
| Accent Red | #c1535e |
| Light Background | #ffefda |

**Collapsible Sections**
Scopes organized into 8 grade-level accordion groups with smart auto-expansion.

**Flash Prevention**
Inline script at top of <body> reads cache and injects CSS via document.write() BEFORE DOM renders.`
  },
  {
    id: 'wiki_shared_constants',
    title: 'Shared Constants',
    category: 'howto',
    content: `**PHONOLOGIC_CONSTANTS**

GRADES:
- ALL: ['K', '1', '2', '3', '4', '5', '6', '7/8']
- VALID_SET: Set of valid grades including 'advanced'

READING_LEVELS:
- MIN: 1
- MAX: 5
- DEFAULT: 3

API:
- MAX_FOCUS_AREAS: 10
- GENERATION_LOCK_TTL: 120
- LOGIN_DEBOUNCE_MS: 3600000

VALIDATION:
- MIN_FOCUS_PERCENT: 10
- TARGET_FOCUS_PERCENT: 15
- MAX_DISALLOWED: 8
- MAX_FOCUS_AREAS: 10`
  },
  {
    id: 'wiki_bigquery_analytics',
    title: 'BigQuery Analytics',
    category: 'decisions',
    content: `**Tables**
| Table | Purpose |
|-------|---------|
| phonologic_v2.assessments_v2 | Assessment summaries |
| phonologic_v2.assessment_patterns_v2 | Pattern-level ratings (ML training) |
| phonologic_v2.story_generations | Story generation logs |

**Key Queries**
See docs/bigquery-assessment-tables.sql for example queries:
- Students who improved reading level
- Most challenging subscopes by grade
- Interest prompt effectiveness`
  },
  {
    id: 'wiki_cost_estimates',
    title: 'Cost Estimates',
    category: 'decisions',
    content: `**Per 1000 Stories**
- Gemini 2.5 Pro: ~$1.50-3.00
- GPT-5: ~$3.00-6.00

**Monthly Estimate (20 concurrent users)**
| Service | Cost |
|---------|------|
| Vercel | $20-50 |
| Gemini API | $3-6 |
| OpenAI API | $2-5 |
| Firestore | $5-10 |
| Redis | $5-8 |
| **Total** | **$35-79/month** |`
  },
  {
    id: 'wiki_roadmap',
    title: 'Product Roadmap',
    category: 'decisions',
    content: `**Current Phase: Parent Product Excellence**
- [x] Story generation with personalization
- [x] Assessment v2 with analytics
- [x] Progress reporting
- [ ] Mobile app
- [ ] Offline mode

**Future Phases**
- Q3-Q4 2026: School pilot program (50 schools)
- 2027: District sales (500 schools)
- 2028+: 1M teachers, international expansion`
  }
];

async function seedTechnicalWiki() {
  console.log('Seeding wiki with technical documentation...\n');

  for (const page of technicalPages) {
    const pageData = {
      title: page.title,
      content: page.content,
      category: page.category,
      author: 'Technical Team',
      authorEmail: 'tech@phonologic.ca',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    try {
      await redis.hset(WIKI_KEY, { [page.id]: JSON.stringify(pageData) });
      console.log(`+ Created: ${page.title} (${page.category})`);
    } catch (error) {
      console.error(`x Failed: ${page.title} - ${error.message}`);
    }
  }

  console.log('\nTechnical wiki seeding complete!');
  console.log(`Total pages added: ${technicalPages.length}`);
}

seedTechnicalWiki().catch(console.error);
