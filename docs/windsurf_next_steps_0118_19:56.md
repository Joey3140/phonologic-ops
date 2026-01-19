# Next Steps: January 18, 2026 @ 19:56

**Prepared for:** Next Windsurf Development Session  
**Priority Framework:** P0 = Blocking, P1 = High Value, P2 = Nice to Have

---

## Immediate Actions (Start of Next Session)

### 1. Verify Railway Orchestrator Health (P0)
**Time Estimate:** 5 minutes

The orchestrator was just fixed and redeployed. First verify it's running:

```bash
# Check Railway logs for successful startup
# Look for: "INFO: Uvicorn running on http://0.0.0.0:8000"
```

Or test via the portal:
1. Go to https://ops.phonologic.cloud
2. Navigate to AI Hub tab
3. Check orchestrator status shows "Connected"
4. Test a brain query like "What is PhonoLogic's pricing?"

If still failing, check Railway logs for new error messages.

---

## High Priority Tasks (P1)

### 2. Complete Teacher & Tutor Personas in Brain
**Time Estimate:** 30-45 minutes  
**Why:** Parent persona is complete, but Teacher and Tutor personas are marked as "pending" in brain.py. These are critical for marketing content generation.

**Action:**
1. Edit `/orchestrator/knowledge/brain.py`
2. Add Teacher persona (K-3 literacy teacher profile, pain points, goals)
3. Add Tutor persona (private tutor/learning specialist profile)
4. Bump brain version and redeploy

**Reference:** Parent persona structure in brain.py for format.

---

### 3. Add Social Media URLs to Brain
**Time Estimate:** 15 minutes  
**Why:** Currently marked as "❌ Missing - Need URLs from Stephen"

**Action:**
1. Get from Stephen: LinkedIn, Twitter/X, Instagram, TikTok, YouTube URLs
2. Add to brain.py under company/social section
3. Redeploy orchestrator

---

### 4. Brain-to-Wiki Sync Feature
**Time Estimate:** 1-2 hours  
**Why:** Currently brain.py and wiki seed data are separate. When brain is updated, wiki doesn't reflect changes automatically.

**Proposed Implementation:**
1. Create `/scripts/seed-wiki-from-brain.js` (file already exists but empty)
2. Script fetches from orchestrator `/api/brain/company`, `/api/brain/product`, etc.
3. Transforms brain data into wiki page format
4. Updates seed.js or directly seeds Redis
5. Add manual trigger endpoint `/api/wiki/sync-from-brain`

**Considerations:**
- Should this be automatic or manual?
- How to handle wiki pages that have been manually edited?
- Version control for brain→wiki sync

---

### 5. Implement Wiki Page Editing for Admins
**Time Estimate:** 1 hour  
**Why:** Wiki editor UI exists but may not be fully functional for creating/editing pages through the new redesigned interface.

**Verify:**
1. Test "Edit" button on wiki pages as admin
2. Test "New Page" functionality
3. Ensure save/cancel work properly with new layout

---

## Medium Priority Tasks (P2)

### 6. Brain Curator UI in AI Hub
**Time Estimate:** 2-3 hours  
**Why:** The BrainCurator agent exists but has no frontend UI. Stephen needs a way to contribute knowledge.

**Requirements:**
- Add "Contribute Knowledge" section to AI Hub
- Text input for natural language contributions
- Display conflict warnings when detected
- Show pending contributions queue
- Allow resolution (Update/Keep Existing/Add as Note)

**API Endpoints (already exist):**
- `POST /api/orchestrator/brain/contribute`
- `POST /api/orchestrator/brain/resolve`
- `GET /api/orchestrator/brain/pending`

---

### 7. MarketingFleet Integration Testing
**Time Estimate:** 1-2 hours  
**Why:** MarketingFleet agent exists but hasn't been tested end-to-end through the portal.

**Test Scenarios:**
1. Request a campaign brief for "Back to School 2026"
2. Verify DuckDuckGo research works (requires `ddgs` package)
3. Test MidjourneyPrompt output generation
4. Verify brain toolkit integration (brand guidelines in output)

---

### 8. ProjectOps ClickUp Integration
**Time Estimate:** 2-3 hours  
**Why:** ProjectOps team exists but ClickUp integration may not be configured.

**Prerequisites:**
- `CLICKUP_API_TOKEN` env var in Railway
- `CLICKUP_WORKSPACE_ID` env var
- `CLICKUP_DEFAULT_LIST_ID` env var

**Actions:**
1. Verify env vars are set in Railway
2. Test creating a task via AI Hub
3. Test reading/listing tasks
4. Add ClickUp quick-action buttons to AI Hub

---

### 9. Goals Module Expansion
**Time Estimate:** 1-2 hours  
**Why:** Goals tab exists but may be underutilized. Could integrate with brain metrics.

**Ideas:**
- Auto-populate goals from brain.py milestones
- Add progress tracking visualization
- Weekly goals summary email (via SendGrid)

---

## Technical Debt

### 10. app.js Refactoring
**Time Estimate:** 3-4 hours  
**Why:** 800+ lines in single object. Hard to maintain.

**Approach:**
- Split into modules (auth.js, wiki.js, announcements.js, etc.)
- Consider lightweight bundler (esbuild)
- Maintain vanilla JS (no framework switch)

### 11. Redis Pagination Optimization
**Time Estimate:** 2 hours  
**Why:** HGETALL loads all records, then paginates in-memory. Will become slow at scale.

**Fix:** Use HSCAN for large collections or add index keys.

### 12. Announcement Comments Separation
**Time Estimate:** 2 hours  
**Why:** Comments stored in announcement JSON. Each comment rewrites entire record.

**Fix:** Separate `phonologic:comments:{ann_id}` keys.

---

## Feature Backlog (Future Sessions)

| Feature | Effort | Value | Notes |
|---------|--------|-------|-------|
| Email notifications | Medium | High | SendGrid integration exists |
| Mobile app wrapper | High | Medium | PWA or React Native |
| Team activity feed | Medium | Medium | Recent actions across all modules |
| Dark/light theme toggle | Low | Low | Currently dark only |
| Keyboard shortcuts | Low | Low | Power user feature |
| Export wiki to PDF | Medium | Medium | For offline reference |
| Integration with Pitch.com | High | High | Auto-update deck from brain |

---

## Questions for Stephen

Before next session, clarify with Stephen:

1. **Social Media URLs** - What accounts does PhonoLogic have?
2. **Teacher/Tutor Personas** - Any specific characteristics to include?
3. **ClickUp Setup** - Is there a specific workspace/list to use?
4. **Priority Override** - Any urgent features not listed here?

---

## Environment Checklist

Verify before starting development:

- [ ] Railway orchestrator showing healthy
- [ ] Vercel deployment successful (check dashboard)
- [ ] Can log in to ops.phonologic.cloud
- [ ] AI Hub shows "Connected" status
- [ ] Wiki loads all 15 pages
- [ ] Mobile view works (test at 375px width)

---

## Session Workflow Recommendation

1. **First 10 min:** Verify health checks, review any new errors
2. **Next 30-60 min:** Complete one P1 task fully
3. **Mid-session:** Commit and deploy, verify in production
4. **Remaining time:** Start next P1 or address P2 if time permits
5. **Last 10 min:** Create session summary and next steps docs

This cadence ensures incremental progress with frequent deployments and verification.
