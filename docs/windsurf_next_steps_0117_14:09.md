# Next Development Session - Recommended Tasks
**Created:** January 17, 2026 @ 14:09 UTC-05:00  
**Priority:** Ordered by impact and dependency

---

## Session Preparation

Before starting next session, ensure:
1. Review `/docs/windsurf.md` for architectural context
2. Review `/docs/windsurf_summary_session_0117_14:09.md` for recent changes
3. Verify production is stable: https://ops.phonologic.cloud

---

## Priority 1: Critical Technical Debt

### 1.1 Separate Comments from Announcements
**Time Estimate:** 45 mins  
**Impact:** Fixes race condition, improves write performance

**Current Problem:**
- Comments stored as array inside announcement JSON
- Every comment rewrites entire announcement
- Risk of data loss with concurrent writes

**Solution:**
1. Create new Redis hash `phonologic:comments`
2. Store comments with key: `{announcementId}:{commentId}`
3. Migrate existing comments with script
4. Update API to fetch comments separately
5. Join in API response

**Files to Modify:**
- `/lib/redis.js` - Already has COMMENTS key
- `/api/announcements/index.js` - Update comment handlers
- Create `/scripts/migrate-comments.js`

---

### 1.2 Add Integration Tests
**Time Estimate:** 60 mins  
**Impact:** Enables safe refactoring, CI/CD readiness

**Approach:**
1. Install Jest + supertest
2. Create test fixtures (mock Redis)
3. Write tests for critical paths:
   - Auth flow (login, verify, logout)
   - Admin check logic
   - Wiki CRUD
   - Rate limiting

**Files to Create:**
- `/tests/setup.js` - Test configuration
- `/tests/auth.test.js`
- `/tests/wiki.test.js`
- `/tests/users.test.js`
- `package.json` - Add test scripts

---

## Priority 2: Scalability Improvements

### 2.1 Implement Redis HSCAN for Large Collections
**Time Estimate:** 30 mins  
**Impact:** Prevents timeout at 500+ records

**Current Problem:**
- `HGETALL` loads everything into memory
- Will timeout on Vercel's 10s limit with large datasets

**Solution:**
1. Replace `hgetall` with `hscan` cursor pagination
2. Stream results to client or batch process
3. Add index keys for common queries (e.g., by category)

**Files to Modify:**
- `/api/wiki/index.js`
- `/api/announcements/index.js`
- `/api/users/index.js`

---

### 2.2 Add Search Functionality
**Time Estimate:** 45 mins  
**Impact:** Enables finding content as wiki grows

**Approach:**
1. Add full-text search to wiki API
2. Client-side search for announcements (smaller dataset)
3. Consider Upstash Vector for semantic search (future)

**Implementation:**
```javascript
// GET /api/wiki?search=deployment
const searchTerm = req.query.search?.toLowerCase();
if (searchTerm) {
  pages = pages.filter(p => 
    p.title.toLowerCase().includes(searchTerm) ||
    p.content.toLowerCase().includes(searchTerm)
  );
}
```

---

## Priority 3: Security Hardening

### 3.1 Session Revocation Support
**Time Estimate:** 30 mins  
**Impact:** Enables logout-all, security incident response

**Solution:**
1. Store session IDs in Redis with user email
2. On logout, delete from Redis
3. On verify, check Redis (not just signature)
4. Add "Revoke All Sessions" admin function

**Files to Modify:**
- `/api/auth/google.js`
- `/lib/redis.js` - Add SESSIONS key

---

### 3.2 Audit Logging
**Time Estimate:** 30 mins  
**Impact:** Compliance, debugging, security monitoring

**Events to Log:**
- Login/logout
- Admin status changes
- Wiki create/update/delete
- Announcement create/delete
- Failed auth attempts

**Implementation:**
- Create `/lib/audit.js` with `logEvent(type, actor, details)`
- Store in Redis list or send to external service

---

## Priority 4: Developer Experience

### 4.1 Add TypeScript (Incremental)
**Time Estimate:** 60 mins for setup  
**Impact:** Type safety, better IDE support

**Approach:**
1. Add `tsconfig.json` with `allowJs: true`
2. Create `/types/index.d.ts` with interfaces
3. Convert new files to `.ts`
4. Gradually convert existing files

**Key Interfaces Needed:**
```typescript
interface User { email: string; name: string; picture?: string; isAdmin: boolean; }
interface WikiPage { id: string; title: string; category: string; content: string; ... }
interface Session { email: string; name: string; exp: number; ... }
```

---

### 4.2 Add API Documentation
**Time Estimate:** 45 mins  
**Impact:** Onboarding, external integrations

**Approach:**
1. Add OpenAPI/Swagger spec in `/docs/api.yaml`
2. Generate from JSDoc comments
3. Optional: Add Swagger UI endpoint

---

## Priority 5: UX Improvements

### 5.1 Add Wiki Page Versioning
**Time Estimate:** 60 mins  
**Impact:** Recover from accidental edits, audit trail

**Solution:**
1. Store versions in separate hash: `phonologic:wiki:versions:{pageId}`
2. On save, push current to versions before overwriting
3. Add "View History" UI for admins
4. Add "Restore Version" function

---

### 5.2 Improve Mobile Responsiveness
**Time Estimate:** 30 mins  
**Impact:** Mobile users

**Focus Areas:**
- Wiki sidebar collapses to hamburger menu
- Tool cards stack vertically
- Announcement cards full-width
- Touch-friendly buttons (min 44px)

---

## Quick Wins (< 15 mins each)

| Task | Description | File |
|------|-------------|------|
| Add loading spinners | Show spinner during API calls | `app.js` |
| Improve error messages | User-friendly error toasts | `app.js` |
| Add keyboard shortcuts | Ctrl+K for search, Esc to close modals | `app.js` |
| Add favicon | Currently missing | `/public/favicon.ico` |
| Add meta description | SEO/social sharing | `index.html` |

---

## Do NOT Do (Scope Creep)

These are explicitly out of scope for near-term sessions:
- ❌ Migrate to React/Vue/Svelte (too disruptive)
- ❌ Add real-time updates with WebSockets (overkill for team size)
- ❌ Multi-tenant support (not needed)
- ❌ Custom domain email integration (use Google Workspace)

---

## Recommended Session Structure

1. **First 10 mins:** Review this doc + test production
2. **Next 45 mins:** Pick ONE Priority 1 task, complete it
3. **Next 30 mins:** Pick ONE Priority 2-3 task
4. **Last 15 mins:** Quick wins, update docs, deploy

---

## Commands Reference

```bash
# Local development
npm run dev          # Start Vercel dev server
npm test             # Run tests (after setup)

# Deployment
vercel --prod        # Deploy to production

# Scripts
node scripts/reorganize-wiki.js  # Run wiki migration (already done)
node scripts/seed-wiki.js        # Re-seed wiki data if needed
```

---

## Contact & Resources

- **Production:** https://ops.phonologic.cloud
- **Vercel Dashboard:** https://vercel.com/twenty-fifty-six/phonologic-ops
- **Redis Console:** Upstash dashboard
- **OAuth Console:** Google Cloud Console

