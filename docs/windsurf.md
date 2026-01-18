# PhonoLogic Operations Portal - Windsurf Development Memory

**Last Updated:** January 18, 2026 @ 18:50 UTC-05:00

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

---

## Session History

| Date | Focus | Key Changes |
|------|-------|-------------|
| 2026-01-17 | Wiki reorg + Security audit | Department categories, rate limiting, XSS fix, pagination |
| 2026-01-18 AM | Agno Orchestrator Railway Deploy | Fixed 9 deployment issues, Claude model config, JSON brain storage |
| 2026-01-18 PM | Brain Population + AI Hub Integration | Vercel proxy routes, comprehensive brain from 6 sources, personas, ops links |

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

### Brain Update Process (Planned)
For Stephen to add info without overwriting:
1. Submit to staging queue
2. Claude checks for contradictions
3. Auto-merge or flag for review
4. Version history preserved

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

