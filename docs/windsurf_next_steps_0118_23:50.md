# Next Development Session - Action Items
**Created:** January 18, 2026 @ 23:50 UTC-05:00  
**Priority Order:** P0 (Critical) → P1 (High) → P2 (Medium) → P3 (Nice-to-have)

---

## Immediate Actions (Start of Next Session)

### P0: Verify AI Hub Functionality
Before any new development, confirm all endpoints work:
- [ ] Marketing Campaign Generator - test the social media prompt
- [ ] PM Task Breakdown - test a simple task
- [ ] PM Report Generator - test a status report
- [ ] Browser Navigator - test slide analysis (if Playwright configured)

**Why:** We just added 4 new proxy files. Need to verify Railway backend has corresponding endpoints.

---

## P1: High Priority Features

### 1. Social Media Posting Plan Generation
**Context:** User requested a marketing prompt for LinkedIn, Reddit, Facebook, referrals, affiliate strategy spanning Private Beta → Public Beta → Full Launch

**Action Items:**
- [ ] Test the marketing/prompt endpoint with the social media prompt
- [ ] If endpoint works, generate and review the output
- [ ] Refine the prompt template based on quality of output
- [ ] Consider saving common prompts as templates in the UI

**Prompt to Test:**
```
Create a comprehensive social media posting plan for PhonoLogic's Decodable Story Generator spanning:
- Phase 1: Private Beta (waitlist building)
- Phase 2: Public Beta (testimonial gathering)  
- Phase 3: Full Public Release (growth mode)

Channels: LinkedIn, Reddit, Facebook Groups, Referral Program, Affiliate Program

Include: Key messaging, specific post templates, metrics to track, phase transition triggers
```

### 2. Complete Persona Data in Brain
**Current State:** Parent persona complete, Teacher/Tutor personas pending

**Action Items:**
- [ ] Add Teacher persona (K-3 reading teacher profile)
- [ ] Add Tutor/SLP persona
- [ ] Add School Admin persona
- [ ] Update Brain with social media URLs (get from Stephen)

### 3. Marketing Prompt Response Parsing
**Issue:** Marketing endpoint may return raw text that needs better formatting in UI

**Action Items:**
- [ ] Review response format from marketing/prompt endpoint
- [ ] Add markdown rendering if responses contain markdown
- [ ] Consider copy-to-clipboard button for generated content

---

## P2: Medium Priority

### 4. Toast Notification Enhancement
- [ ] Add close button (X) for manual dismiss
- [ ] Queue multiple toasts (currently replaces existing)
- [ ] Add loading toast type for async operations

### 5. Brain Data Viewer Improvements
- [ ] Add edit functionality (not just delete)
- [ ] Add search/filter for Redis entries
- [ ] Show entry metadata (contributor, timestamp)

### 6. Pending Contributions Polish
- [ ] Add visual indicator when pending count > 0 (badge on tab?)
- [ ] Add bulk approve/reject for multiple pending items
- [ ] Add preview of conflict details before approve

### 7. Error Handling Consistency
- [ ] Audit all fetch calls for consistent error handling
- [ ] Replace remaining alert() calls with showToast()
- [ ] Add network error detection (offline handling)

---

## P3: Nice-to-Have / Tech Debt

### 8. app.js Modularization
**Issue:** Now 1980+ lines, becoming unwieldy

**Proposed Structure:**
```
public/js/
├── app.js (main orchestrator, 200 lines)
├── auth.js (authentication, 150 lines)
├── wiki.js (wiki CRUD, 200 lines)
├── aihub.js (AI Hub features, 400 lines)
├── brain.js (Brain Curator, 300 lines)
├── ui.js (toast, modals, etc., 150 lines)
└── utils.js (helpers, 100 lines)
```

### 9. Automated Testing
- [ ] Add Playwright E2E tests for critical paths
- [ ] Add API integration tests for orchestrator proxy
- [ ] Set up CI/CD test runner on Vercel preview deploys

### 10. Rate Limit Testing
- [ ] Test Brain endpoints under simulated load
- [ ] Verify rate limit responses are user-friendly
- [ ] Add rate limit status to API responses

---

## Architecture Decisions Needed

### Decision 1: Template System for AI Prompts
**Question:** Should we build a saved templates system for marketing/PM prompts?
**Options:**
- A) Store in Redis, allow CRUD via UI
- B) Hardcode templates in seed data
- C) Store in orchestrator Brain
**Recommendation:** Option A for flexibility

### Decision 2: Real-time Notifications
**Question:** Should pending contributions trigger real-time alerts?
**Options:**
- A) Polling every 30s on AI Hub tab
- B) WebSocket from Railway
- C) Keep manual refresh
**Recommendation:** Option A as quick win

---

## Environment/Config Notes

### Railway Endpoints to Verify
These backend endpoints should exist (check routes.py):
- `POST /api/orchestrator/marketing/prompt` ✓
- `POST /api/orchestrator/pm/task` - verify exists
- `POST /api/orchestrator/pm/report` - verify exists
- `POST /api/orchestrator/browser/prompt` - verify exists

### Missing Brain Content
- Social media URLs (Instagram, LinkedIn, Twitter/X, TikTok)
- Teacher persona details
- Tutor/SLP persona details
- Detailed competitive analysis updates

---

## Quick Reference

### To Deploy Changes
```bash
git add -A && git commit -m "description" && git push
```

### To View Railway Logs
Railway Dashboard → phonologic-ops → Logs

### To Test Orchestrator Locally
```bash
cd orchestrator
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Key Files for Next Session
| Purpose | File |
|---------|------|
| Frontend logic | `/public/app.js` |
| Toast styles | `/public/styles.css` |
| Vercel proxy routes | `/api/orchestrator/*/` |
| Backend endpoints | `/orchestrator/api/routes.py` |
| Brain knowledge | `/orchestrator/knowledge/brain.py` |
| Brain curator | `/orchestrator/agents/brain_curator.py` |

---

## Session Handoff Notes

**What was working when we left:**
- Delete brain entries ✅
- Toast notifications ✅
- Pending contributions load on tab open ✅
- Approve/Reject pending ✅

**What needs testing:**
- Marketing prompt generation (new proxy file)
- PM task/report generation (new proxy files)
- Browser prompt (new proxy file)

**Known issues:**
- None blocking; all bugs from this session resolved

---

*End of next steps document*
