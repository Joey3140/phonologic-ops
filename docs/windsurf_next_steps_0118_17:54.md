# Windsurf Next Steps - Development Roadmap
**Created:** January 18, 2026 @ 17:54 UTC-05:00  
**Priority:** P0 = Immediate, P1 = This Week, P2 = Next Sprint

---

## Immediate Actions (P0) - Complete Before Next Session

### 1. Verify Railway Deployment ✅ BLOCKING
**Owner:** DevOps/Backend  
**Estimated Time:** 10 minutes

```bash
# Health check
curl https://phonologic-ops-production.up.railway.app/health

# Expected: {"status": "healthy"}

# Orchestrator status
curl https://phonologic-ops-production.up.railway.app/api/orchestrator/status

# Expected: JSON with teams array and uptime
```

**If deployment fails:**
1. Check Railway deploy logs for new errors
2. Review application logs for startup failures
3. Common issues: missing env vars, package import errors

### 2. Add ORCHESTRATOR_URL to Vercel
**Owner:** DevOps  
**Estimated Time:** 5 minutes

1. Go to Vercel Dashboard → phonologic-ops → Settings → Environment Variables
2. Add new variable:
   - **Name:** `ORCHESTRATOR_URL`
   - **Value:** `https://phonologic-ops-production.up.railway.app`
   - **Environment:** Production
3. Trigger redeploy

### 3. Test Frontend AI Hub Integration
**Owner:** Frontend  
**Estimated Time:** 15 minutes

1. Navigate to https://ops.phonologic.cloud
2. Click "AI Hub" tab
3. Verify:
   - [ ] Orchestrator status shows "operational"
   - [ ] All 3 teams display correctly
   - [ ] Brain query returns company info
   - [ ] No CORS errors in console

---

## This Week (P1) - Core Functionality

### 4. End-to-End Agent Testing
**Owner:** Backend  
**Estimated Time:** 2-3 hours

Test each agent team with real requests:

#### Marketing Fleet
```bash
curl -X POST https://phonologic-ops-production.up.railway.app/api/orchestrator/marketing/campaign \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "PhonoLogic Speech Therapy",
    "target_audience": "Parents of children with speech delays",
    "campaign_goals": ["Increase awareness", "Drive trial signups"],
    "budget_range": "$5000-10000",
    "timeline": "Q1 2026"
  }'
```

#### Project Ops (requires ClickUp/Google/SendGrid env vars)
```bash
# Test onboarding workflow
curl -X POST https://phonologic-ops-production.up.railway.app/api/orchestrator/pm/onboard \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "employee",
    "name": "Test User",
    "email": "test@phonologic.ca",
    "role": "Developer",
    "department": "Engineering"
  }'
```

#### Browser Navigator (requires Playwright)
```bash
curl -X POST https://phonologic-ops-production.up.railway.app/api/orchestrator/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.google.com/presentation/d/[TEST_ID]/edit"}'
```

### 5. Railway Environment Variables Audit
**Owner:** DevOps  
**Estimated Time:** 30 minutes

Verify all required env vars are set in Railway dashboard:

| Variable | Status | Notes |
|----------|--------|-------|
| `ANTHROPIC_API_KEY` | ⬜ Verify | Required for all agents |
| `PORT` | ⬜ Set to 8000 | Required |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ⬜ Check | Full JSON, not path |
| `CLICKUP_API_TOKEN` | ⬜ Optional | For task management |
| `CLICKUP_WORKSPACE_ID` | ⬜ Optional | ClickUp workspace |
| `CLICKUP_DEFAULT_LIST_ID` | ⬜ Optional | Default task list |
| `SENDGRID_API_KEY` | ⬜ Optional | For email sending |
| `SERPER_API_KEY` | ⬜ Optional | Better search results |

### 6. Implement Proper Brain Persistence
**Owner:** Backend  
**Estimated Time:** 2 hours

Current JSON file storage won't persist across Railway deployments. Options:

**Option A: Redis (Recommended)**
- Use existing Upstash Redis
- Add to requirements: `redis>=5.0.0` (already present)
- Replace JSON file storage with Redis hash

**Option B: Railway Volume**
- Attach persistent volume to service
- Mount at `/data`
- Store brain.json there

**Option C: PostgreSQL**
- Add Railway PostgreSQL addon
- Migrate brain to proper database

### 7. Add API Authentication
**Owner:** Backend/Security  
**Estimated Time:** 3-4 hours

The orchestrator endpoints are currently unprotected. Implement:

1. **API Key Authentication**
   - Generate `ORCHESTRATOR_API_KEY` 
   - Add to Railway and Vercel env vars
   - Validate in middleware

2. **Request Signing (Optional)**
   - HMAC signature for sensitive operations

```python
# Middleware example
from fastapi import Request, HTTPException

async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if api_key != settings.ORCHESTRATOR_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

---

## Next Sprint (P2) - Enhancements

### 8. Observability & Monitoring
**Owner:** DevOps  
**Estimated Time:** 4-6 hours

- [ ] Add structured logging with `structlog` (already in deps)
- [ ] Implement request tracing (correlation IDs)
- [ ] Add Prometheus metrics endpoint
- [ ] Set up Railway alerts for errors/downtime
- [ ] Consider Sentry integration for error tracking

### 9. Agent Response Caching
**Owner:** Backend  
**Estimated Time:** 3-4 hours

Marketing research and brain queries are expensive. Implement:

- Redis-based response cache
- TTL: 1 hour for research, 24 hours for brain queries
- Cache invalidation on brain updates

### 10. Vercel Proxy Route
**Owner:** Frontend/Backend  
**Estimated Time:** 2 hours

Currently, frontend calls Railway directly. For security:

1. Create `/api/orchestrator/[...path].js` in Vercel
2. Proxy requests to Railway with API key
3. Rate limit at Vercel edge

```javascript
// /api/orchestrator/[...path].js
export default async function handler(req, res) {
  const path = req.query.path.join('/');
  const response = await fetch(
    `${process.env.ORCHESTRATOR_URL}/api/orchestrator/${path}`,
    {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.ORCHESTRATOR_API_KEY
      },
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
    }
  );
  const data = await response.json();
  res.status(response.status).json(data);
}
```

### 11. Frontend AI Hub Improvements
**Owner:** Frontend  
**Estimated Time:** 4-6 hours

Current AI Hub is basic. Enhance with:

- [ ] Real-time task status updates (WebSocket or polling)
- [ ] Campaign history and results display
- [ ] Brain knowledge explorer UI
- [ ] Agent chat interface for interactive queries
- [ ] Loading states and error handling

### 12. Documentation
**Owner:** All  
**Estimated Time:** 2-3 hours

- [ ] Update README with orchestrator architecture
- [ ] API documentation (consider FastAPI's built-in docs)
- [ ] Runbook for common operations
- [ ] Troubleshooting guide for deployment issues

---

## Technical Debt

### High Priority
1. **Agno Storage Fallback** - Currently agents work without storage, but session history is lost. Need proper alternative.
2. **Docker Image Size** - Playwright + Chromium makes image large (~2GB). Consider separate service or lazy loading.
3. **Hardcoded Port** - Port 8000 is hardcoded. Railway should set PORT env var properly.

### Medium Priority
4. **Monolithic Agent Files** - Each agent file is 300-400 lines. Consider splitting into modules.
5. **No Unit Tests** - Zero test coverage for orchestrator. Add pytest suite.
6. **Lint Warnings** - "Restricted scope" warnings in Google toolkit files (non-blocking but should fix).

### Low Priority
7. **Unused start.sh** - Created during debugging, now unused. Delete it.
8. **Playwright in Docker** - Consider using playwright-python with bundled browser to reduce image size.

---

## Questions for Product/Leadership

1. **Agent Priority:** Which team should be production-ready first?
   - Marketing Fleet (research + creative)
   - Project Ops (automation)
   - Browser Navigator (analysis)

2. **Usage Model:** Will this be:
   - On-demand (user triggers workflows)
   - Scheduled (cron-based automation)
   - Event-driven (webhook triggers)

3. **Data Retention:** How long to keep:
   - Campaign results
   - Agent conversation history
   - Brain knowledge updates

4. **Access Control:** Who should have access to:
   - View orchestrator status (all users?)
   - Trigger marketing campaigns (admins only?)
   - Modify brain knowledge (admins only?)

---

## Session Handoff Checklist

Before starting next session, verify:

- [ ] Railway deployment is healthy
- [ ] ORCHESTRATOR_URL added to Vercel
- [ ] Frontend AI Hub loads without errors
- [ ] At least one agent endpoint responds correctly
- [ ] All env vars documented and set

**If any of these fail, that becomes P0 for next session.**

---

## Useful Commands

```bash
# Local development
cd orchestrator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Docker local test
docker build -t orchestrator .
docker run -p 8000:8000 --env-file .env orchestrator

# Git status
git log --oneline -5
git status

# Railway CLI (if installed)
railway status
railway logs
```

---

## Contact Points

- **Railway Dashboard:** https://railway.app/project/[PROJECT_ID]
- **Vercel Dashboard:** https://vercel.com/[TEAM]/phonologic-ops
- **GitHub Repo:** https://github.com/Joey3140/phonologic-ops
- **Production Frontend:** https://ops.phonologic.cloud
- **Production Orchestrator:** https://phonologic-ops-production.up.railway.app
