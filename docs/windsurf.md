# PhonoLogic Operations Portal - Windsurf Development Memory

**Last Updated:** January 18, 2026 @ 21:46 UTC-05:00

This document serves as persistent memory for Windsurf/Cascade AI development sessions. It captures architectural decisions, patterns, gotchas, and context that should persist across sessions.

---

## Project Overview

**Purpose:** Internal operations portal for PhonoLogic team members (@phonologic.ca only)

**Stack:**
- **Frontend:** Vanilla JS SPA (`/public/app.js`, `/public/index.html`)
- **Backend:** Vercel Serverless Functions (`/api/*`)
- **Database:** Upstash Redis (REST API)
- **Auth:** Google OAuth with domain restriction
- **Deployment:** Vercel (auto-deploy from main)
- **AI Orchestrator:** Agno + FastAPI on Railway (`/orchestrator/`)

**Production URLs:**
- **Frontend:** https://ops.phonologic.cloud
- **Orchestrator:** https://phonologic-ops-production.up.railway.app

---

## Key Architecture Patterns

### Authentication Flow
1. User clicks "Sign in with Google"
2. Redirect to Google OAuth consent
3. Callback validates `@phonologic.ca` domain
4. Creates signed session token (custom JWT-like)
5. Sets `ops_auth_token` HTTP-only cookie (7-day expiry)
6. Frontend checks `/api/auth/google?action=verify` on load

### Authorization Levels
- **Authenticated:** Any `@phonologic.ca` user
- **Admin:** Users in `ADMIN_EMAILS` env var OR `phonologic:admins` Redis set

### Redis Data Model
All keys centralized in `/lib/redis.js`:
```javascript
REDIS_KEYS = {
  USERS: 'phonologic:users',           // Hash: email -> JSON user data
  ADMINS: 'phonologic:admins',         // Set: admin emails
  WIKI: 'phonologic:wiki',             // Hash: page_id -> JSON page
  ANNOUNCEMENTS: 'phonologic:announcements', // Hash: ann_id -> JSON
  COMMENTS: 'phonologic:comments',     // Hash: comment_id -> JSON (future)
  GOALS: 'phonologic:goals',           // Hash: goal_id -> JSON
  OAUTH_STATE: 'oauth_state:',         // Prefix for CSRF tokens
  RATE_LIMIT: 'rate_limit:'            // Prefix for rate limiting
}
```

### Security Middleware
Located at `/lib/auth-middleware.js`:
- CORS: Strict origin allowlist (no wildcards)
- Rate Limiting: IP-based with Redis counters
- Auth: Session validation with `withAuth()` wrapper

---

## Current Admins
- `joey@phonologic.ca` (env var default)
- `stephen@phonologic.ca` (added 2026-01-17)

---

## Wiki Categories (Department-Based)
| Category Key | Display Name | Description |
|--------------|--------------|-------------|
| `getting-started` | Getting Started | Essential info for new team members |
| `development` | Development | Technical docs and engineering |
| `product` | Product | Features, curriculum, and roadmap |
| `operations` | Operations | Deployment and business ops |
| `analytics` | Analytics | Data and reporting |
| `policies` | Policies | HR and company guidelines |

---

## Known Limitations & Gotchas

### Data Storage
- **HGETALL Performance:** All list endpoints still load all records, then paginate in-memory. For 500+ records, consider HSCAN or separate index keys.
- **Comments in Announcements:** Currently stored as nested array in announcement JSON. Each comment rewrites entire announcement. Should be separated.

### Authentication
- **No Session Revocation:** Sessions valid for 7 days, cannot be invalidated early. For true revocation, would need Redis session store.
- **Cookie Parsing:** Uses regex, not a proper cookie parser. Could break on edge cases.

### Frontend
- **Monolithic app.js:** 800+ lines in single object. No modules or components.
- **No Build Step:** Raw JS/CSS served directly. No minification, bundling, or tree-shaking.
- **Wiki UX Recently Redesigned:** Now has category cards, nested sidebar, search - ensure mobile breakpoints are tested at 768px and 480px.

---

## Environment Variables Required

| Variable | Required | Description |
|----------|----------|-------------|
| `SESSION_SECRET` | ✅ Yes | Min 32 chars, used for signing session tokens |
| `GOOGLE_OAUTH_CLIENT_ID` | ✅ Yes | Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | ✅ Yes | Google OAuth client secret |
| `UPSTASH_REDIS_REST_URL` | ✅ Yes | Upstash Redis REST endpoint |
| `UPSTASH_REDIS_REST_TOKEN` | ✅ Yes | Upstash Redis auth token |
| `ADMIN_EMAILS` | Optional | Comma-separated admin emails |

---

## API Patterns

### Standard Response Format
```javascript
// Success
{ success: true, data: {...} }
// or
{ pages: [...], total: 10, limit: 50, offset: 0, hasMore: false }

// Error
{ error: 'Error message' }
```

### Pagination Parameters
All list endpoints support:
- `limit` (default varies, max 50-100)
- `offset` (default 0)

### Rate Limits
- Default: 60 requests/minute
- Write operations: 20 requests/minute  
- Auth endpoints: 10 requests/minute

---

## Testing Checklist (Manual)

Before deploying major changes:
- [ ] Login works for @phonologic.ca account
- [ ] Login rejected for non-@phonologic.ca account
- [ ] Access denied screen hides all content
- [ ] Wiki pages load and display correctly
- [ ] Wiki CRUD works for admins
- [ ] Announcements load and comments work
- [ ] Admin toggle works (grant/revoke)
- [ ] Admin cannot self-demote

---

## Agno Orchestrator Architecture

**Location:** `/orchestrator/`  
**Framework:** Agno (formerly Phidata) + FastAPI  
**Deployment:** Railway (Docker)  
**Port:** 8000 (hardcoded)

### Agent Teams
| Team | Agents | Purpose |
|------|--------|---------|
| MarketingFleet | Researcher, TechnicalConsultant, BrandLead, ImageryArchitect | Campaign strategy & creative |
| ProjectOps | Coordinator, TaskManager, DocumentManager, Communicator | ClickUp, Google Drive, Email automation |
| BrowserNavigator | BrowserNavigator | Playwright-based slide/canvas analysis |

### PhonoLogics Brain
Central knowledge base at `/orchestrator/knowledge/brain.py`:
- Company info, brand guidelines, product positioning
- Team directory, pitch materials
- **Storage:** JSON file (brain.json) - not persistent across deploys
- All agents query via `create_brain_toolkit()`

### Key Files
| File | Purpose |
|------|---------|
| `main.py` | FastAPI app entry point |
| `config.py` | Pydantic settings (env vars) |
| `api/routes.py` | REST endpoints |
| `api/gateway.py` | Central orchestrator gateway |
| `agents/*.py` | Team implementations |
| `tools/*.py` | Custom Agno toolkits |
| `knowledge/brain.py` | Knowledge base |
| `railway.toml` | Railway deployment config |

### Orchestrator Environment Variables
| Variable | Required | Notes |
|----------|----------|-------|
| `ANTHROPIC_API_KEY` | ✅ Yes | Claude API access |
| `PORT` | ✅ Yes | Set to 8000 |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | For Google APIs | Full JSON string |
| `CLICKUP_API_TOKEN` | For ClickUp | Task management |
| `SENDGRID_API_KEY` | For Email | SendGrid integration |
| `SERPER_API_KEY` | Optional | Better search results |

### Orchestrator Gotchas (Learned 2026-01-18)

1. **Railway `railway.toml` overrides Dockerfile CMD** - Always check startCommand
2. **Agno `agno.storage.sqlite` doesn't exist** - Use try/except, graceful fallback
3. **Agno requires `ddgs` for DuckDuckGo** - Not bundled with `agno[all]`
4. **Model IDs must match provider** - Claude uses `claude-sonnet-4-20250514`, not `gpt-4o`
5. **Docker cache issues on Railway** - Use cache-bust comments to force rebuilds
6. **Use settings object everywhere** - Don't mix `os.getenv()` with pydantic settings
7. **Python imports in orchestrator must be absolute** - `agents/`, `knowledge/`, `config` are sibling packages at root level. Use `from knowledge.brain import X`, NOT `from ..knowledge.brain import X`
8. **config.py must export `settings` at module level** - Add `settings = get_settings()` so other modules can `from config import settings`

---

## Session History

| Date | Focus | Key Changes |
|------|-------|-------------|
| 2026-01-17 | Wiki reorg + Security audit | Department categories, rate limiting, XSS fix, pagination |
| 2026-01-18 AM | Agno Orchestrator Railway Deploy | Fixed 9 deployment issues, Claude model config, JSON brain storage |
| 2026-01-18 PM | Brain Population + AI Hub Integration | Vercel proxy routes, comprehensive brain from 6 sources, personas, ops links |
| 2026-01-18 Eve | Brain Curator + Wiki Sync | Conflict detection for Stephen, wiki auto-seed with versioning, 15 wiki pages |
| 2026-01-18 Late | Railway Import Fixes + Wiki Mobile | Fixed brain_curator.py imports, config.py settings export, wiki mobile CSS |
| 2026-01-18 21:46 | AI Hub Polish + UX Fixes | Hash routing, wiki search fix, approve/reject for pending, Brain Data Viewer |

---

## Frontend Routing Pattern (Added 2026-01-18)

**Pattern:** Hash-based routing for SPA navigation

```javascript
// In showPage()
window.history.pushState(null, '', `#${pageId}`);

// On load
const page = window.location.hash.slice(1) || 'home';
this.showPage(page);

// Back/forward support
window.addEventListener('popstate', () => {
  this.showPage(this.getPageFromHash(), false);
});
```

**Why hash instead of path:**
- No server-side routing needed
- Works with Vercel static file serving
- Bookmarkable URLs (ops.phonologic.cloud/#wiki)
- Browser history works correctly

---

## Brain Curator UX Pattern (Updated 2026-01-18)

**Explicit Mode Toggle (not auto-detection):**
- Auto-detection based on keywords was error-prone
- Frontend now has "Ask" and "Add Info" buttons
- "Add Info" is admin-only (checks `isAdmin`)
- Mode is sent explicitly in API request

**Pending Contribution Workflow:**
1. User submits via "Add Info" mode
2. Backend stages contribution with conflict check
3. Shows in "Pending Contributions" section with approve/reject buttons
4. Admin clicks approve → triggers `/brain/resolve` with action "update"
5. Admin clicks reject → triggers `/brain/resolve` with action "keep"

**Key Insight:** Even admin contributions should be reviewable to prevent accidents.

---

## PhonoLogics Brain - Knowledge Base

**Location:** `/orchestrator/knowledge/brain.py`  
**Schema:** `/orchestrator/knowledge/schemas.py`

### Brain Contents (as of 2026-01-18)
| Category | Status | Notes |
|----------|--------|-------|
| Company info | ✅ Complete | Tagline, mission, vision, HQ |
| Team bios | ✅ Complete | Stephen, Joey, Marysia with full bios |
| Product | ✅ Complete | Decodable Story Generator, features, differentiators |
| Launch timeline | ✅ Complete | Private Beta → Public Beta → Web Summit → Launch |
| Pricing | ⚠️ Partial | Parent plan $20/25mo, others TBD |
| Pilots | ✅ Complete | Montcrest, Einstein, Multi-school |
| Milestones | ✅ Complete | Full roadmap with status |
| Metrics targets | ✅ Complete | 45 min saved, 95% pass rate, margins |
| Problem/Solution | ✅ Complete | Elevator pitch statements |
| Moat | ✅ Complete | Fidelity, Explainability, Embeddability |
| Competitors | ✅ Complete | Reading A-Z, Epic!, Lexia with SWOT |
| Events | ✅ Complete | Vancouver Web Summit May 2026 |
| Personas | ⚠️ Partial | Parent complete, Teacher/Tutor pending |
| Testimonials | ✅ Complete | 3 from phonologic.ca |
| Ops portal | ✅ Complete | All Drive folders, Pitch decks, tools |
| Brand guidelines | ✅ Complete | Colors, fonts, tone, messaging |
| Social media | ❌ Missing | Need URLs from Stephen |

### Brain Curator System (Built 2026-01-18)
**Location:** `/orchestrator/agents/brain_curator.py`

For Stephen to add info without overwriting:
1. Natural language input via chat UI or API
2. BrainCurator checks for conflicts against existing brain
3. If conflict: pushes back with "Hey Stephen, conflict! Brain says X, you said Y"
4. User resolves: Update / Keep Existing / Add as Note
5. Staging queue holds unresolved contributions

**API Endpoints:**
- `POST /api/orchestrator/brain/chat` - Natural language interface (auto-detects query vs contribute)
- `POST /api/orchestrator/brain/contribute` - Direct contribution with conflict check
- `POST /api/orchestrator/brain/resolve` - Resolve pending contribution
- `GET /api/orchestrator/brain/pending` - View pending queue

**Conflict Detection Covers:**
- Pricing (dollar amounts)
- Timeline (launch dates)
- Features (rate limiting, CORS claims)
- Semantic similarity (duplicate detection)

---

## Wiki Auto-Seed System (Built 2026-01-18)

**Seed Data:** `/api/wiki/seed.js`  
**Version Key:** `phonologic:wiki:version` in Redis

### How It Works
1. User visits Wiki tab → triggers `GET /api/wiki`
2. `index.js` checks `WIKI_VERSION` constant vs stored Redis version
3. If mismatch OR empty → auto-seeds all pages from `seed.js`
4. Stores new version in Redis

### To Update Wiki Content
1. Edit pages in `/api/wiki/seed.js`
2. Bump `WIKI_VERSION` (e.g., `'2026-01-18-v1'` → `'2026-01-18-v2'`)
3. Push to git → Vercel deploys
4. Next wiki visit triggers reseed

### Current Wiki Pages (15 total)
| Category | Pages |
|----------|-------|
| getting-started | Company Overview, Team Directory, Tools & Access Guide |
| development | Technology Stack, Deployment Workflow, Security Architecture |
| product | Product Overview, Pricing Structure, Product Roadmap, Competitive Landscape |
| operations | Pilots & Traction, Communication Guidelines, Brand Guidelines |
| analytics | Metrics & KPIs |
| policies | Data & Privacy Policy, Investor Materials |

---

## Vercel Deployment Pattern (Learned 2026-01-18)

**Key Learning:** Windsurf's `deploy_web_app` tool is Netlify-only. This project uses Vercel.

### How to Deploy
```bash
git add . && git commit -m "message" && git push
```
Vercel auto-deploys from main branch.

### Environment Variables
All env vars are in **Vercel Dashboard**, NOT local `.env` files:
- `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `SESSION_SECRET`, `ADMIN_EMAILS`, `ORCHESTRATOR_URL`

### Implication for Scripts
Local scripts cannot access Vercel env vars. When needing database access:
- ❌ Don't create local scripts like `scripts/seed-wiki.js`
- ✅ Do create API endpoints like `/api/wiki/seed.js`

---

## Vercel Proxy Routes for Orchestrator

When proxying to Railway orchestrator, **explicit routes are more reliable than catch-all**:

```
/api/orchestrator/status.js           → GET status
/api/orchestrator/marketing/campaign.js → POST campaigns
/api/orchestrator/brain/query.js      → POST brain queries
/api/orchestrator/brain/[type].js     → GET brain info by type
```

**Key Learning:** Vercel's `[...path].js` catch-all can be unreliable. Create dedicated files for critical endpoints.

