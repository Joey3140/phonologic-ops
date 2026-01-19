# Next Steps: PhonoLogic Development Priorities
**Created:** January 18, 2026 @ 19:20 UTC-05:00  
**For:** Next Windsurf Development Session

---

## Immediate Actions (Start of Next Session)

### 1. Deploy Orchestrator to Railway
The Brain Curator agent was created but not deployed to Railway.

```bash
# Railway should auto-deploy from main, but verify:
# 1. Check Railway dashboard for deployment status
# 2. Test endpoint: GET https://phonologic-ops-production.up.railway.app/api/orchestrator/health
# 3. Test brain chat: POST /api/orchestrator/brain/chat
```

### 2. Verify Wiki Auto-Seed
Visit ops.phonologic.cloud → Wiki tab. Should see 15 pages auto-populated.
If not working, check Vercel logs for `[WIKI API]` or `[WIKI SEED]` messages.

---

## Priority 1: Complete Brain Curator (Estimated: 1-2 hours)

### A. Implement Actual Brain Merge Logic
**Current State:** `resolve_contribution()` returns success messages but doesn't actually update `brain.py`

**TODO:**
1. Parse contribution text to identify which brain field to update
2. Use Claude to extract structured data from natural language
3. Update appropriate field in `DEFAULT_KNOWLEDGE`
4. Persist to `brain.json` file
5. Handle merge conflicts gracefully

**File:** `/orchestrator/agents/brain_curator.py`

### B. Add Redis Persistence for Pending Queue
**Current State:** `pending_queue` is in-memory, lost on restart

**TODO:**
1. Store pending contributions in Redis
2. Add expiration (7 days?) for unresolved contributions
3. Load pending on BrainCurator init

### C. Enhance Conflict Detection
**Current coverage:** Pricing, timeline, features (rate limiting, CORS)

**TODO:**
- Team role changes
- Product feature additions
- Milestone status changes
- Competitor updates

---

## Priority 2: Missing Brain Content (Estimated: 30 mins)

### Social Media URLs (Stephen needs to provide)
```python
social_media={
    "linkedin_company": "???",
    "instagram": "???",
    "twitter": "???",
    "crunchbase": "???",
}
```

### Teacher & Tutor Personas
Parent persona is complete. Need:
- Teacher Persona (K-4 teachers, reading specialists)
- Tutor/SLP Persona (private tutors, speech-language pathologists)

### Support Process
- Support email (support@phonologic.ca?)
- Response SLA
- Escalation process

---

## Priority 3: Wiki Enhancements (Estimated: 1 hour)

### A. Add Missing Wiki Pages
Consider adding:
- **Development:** API Reference, Database Schema
- **Operations:** Meeting Cadence, Decision Log
- **Product:** User Research Findings, Feature Requests

### B. Wiki Edit Sync to Brain
When admin edits wiki page, should it update the brain?
- Option A: Wiki is read-only (synced from brain only)
- Option B: Wiki edits update brain (complex, needs conflict resolution)
- **Recommendation:** Start with Option A for simplicity

### C. Wiki Search
Current: No search functionality
TODO: Add full-text search across wiki pages

---

## Priority 4: Slack Integration for Brain Curator (Estimated: 2-3 hours)

**Goal:** Stephen can DM a Slack bot to add to brain

### Architecture
```
Stephen DMs Slack → Slack webhook → /api/slack/brain endpoint → BrainCurator
```

### Requirements
1. Create Slack App in PhonoLogic workspace
2. Add `/api/slack/brain.js` webhook handler
3. Forward messages to orchestrator's brain/chat endpoint
4. Return conflict messages back to Slack

---

## Priority 5: Frontend Improvements (Estimated: 1-2 hours)

### A. Brain Curator UI Polish
- Add keyboard shortcut (Enter to send)
- Show typing indicator while waiting
- Persist chat history in localStorage
- Add "Clear chat" button

### B. Wiki UI Improvements
- Add search bar
- Show "Last synced" timestamp
- Highlight recently updated pages

### C. Mobile Responsiveness
Test and fix:
- Brain Curator chat on mobile
- Wiki navigation on tablet

---

## Technical Debt to Address

### High Priority
1. **app.js monolith** - 1200+ lines now, consider splitting into modules
2. **No TypeScript** - Consider migrating critical files
3. **No tests** - At minimum, add tests for auth and brain conflict detection

### Medium Priority
1. **Comments stored in announcements** - Should be separate Redis hash
2. **HGETALL performance** - Will degrade with 500+ wiki pages
3. **Brain JSON persistence** - Lost on Railway redeploy, consider Redis

### Low Priority
1. **No build step** - Could add esbuild for minification
2. **Cookie parsing regex** - Replace with proper parser
3. **Session revocation** - Currently impossible without waiting 7 days

---

## Questions to Resolve with Stakeholders

### For Stephen (CEO)
1. What are the social media URLs?
2. What's the support email and process?
3. Do you want Slack integration for brain contributions?
4. Any corrections to the wiki content?

### For Team
1. What wiki pages are missing?
2. What should the Teacher persona look like?
3. Any brand guideline updates needed?

---

## Session Checklist for Next Time

```markdown
## Start of Session
- [ ] Pull latest from main
- [ ] Check Railway deployment status
- [ ] Check Vercel deployment status
- [ ] Review any failed deployments

## During Session
- [ ] Commit frequently (every major feature)
- [ ] Push to trigger auto-deploy
- [ ] Test in production after each push

## End of Session
- [ ] Run full manual test checklist
- [ ] Update windsurf.md with learnings
- [ ] Create session summary
- [ ] Create next steps document
- [ ] Commit all documentation
```

---

## Estimated Time for All Priorities

| Priority | Task | Time |
|----------|------|------|
| P1 | Complete Brain Curator | 1-2 hours |
| P2 | Missing Brain Content | 30 mins |
| P3 | Wiki Enhancements | 1 hour |
| P4 | Slack Integration | 2-3 hours |
| P5 | Frontend Improvements | 1-2 hours |
| Debt | Technical Debt | Ongoing |

**Total for P1-P3:** ~3 hours  
**Total for P1-P5:** ~7 hours
