# PhonoLogic Operations Portal - Windsurf Development Memory

**Last Updated:** January 17, 2026 @ 14:09 UTC-05:00

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

**Production URL:** https://ops.phonologic.cloud

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

## Session History

| Date | Focus | Key Changes |
|------|-------|-------------|
| 2026-01-17 | Wiki reorg + Security audit | Department categories, rate limiting, XSS fix, pagination |

