# Phonologic AI-First Operations Hub

An autonomous operations system powered by Claude 3.5 Sonnet that bridges data gaps and enables daily execution automation. Deployed on Vercel as a subdomain of the main PhonoLogic application.

**Live URL**: `https://ops.phonologic.cloud`

## Architecture

### Core Components
- **The Brain**: Claude 3.5 Sonnet for reasoning, coding, and decision-making
- **The Memory**: Firestore for indexing SOPs, project briefs, and workflow history
- **The Orchestrator**: Custom agent system defining AI employees and collaborative workflows

### Integration Stack
- **Google Workspace**: Drive, Gmail, Sheets integration via OAuth
- **ClickUp**: Task management and project tracking via API
- **GitHub**: Development team monitoring for remote team sync

### Tech Stack (matches main PhonoLogic app)
- **Runtime**: Node.js 18.x on Vercel serverless functions
- **Database**: Google Cloud Firestore
- **Cache**: Upstash Redis
- **AI**: Anthropic Claude 3.5 Sonnet

## Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Required API Keys
| Service | Variable | How to Get |
|---------|----------|------------|
| Anthropic | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| Google Cloud | `GOOGLE_APPLICATION_CREDENTIALS_JSON` | GCP Console → Service Accounts |
| Google OAuth | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | GCP Console → APIs & Credentials |
| ClickUp | `CLICKUP_API_TOKEN` | ClickUp Settings → Apps → API Token |
| GitHub | `GITHUB_TOKEN` | GitHub Settings → Developer → Personal Access Tokens |
| Upstash | `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN` | [upstash.com](https://upstash.com) |

### 4. Local Development
```bash
npm run dev
# Opens at http://localhost:3000
```

### 5. Deploy to Vercel
```bash
# Add to existing PhonoLogic Vercel project
vercel link

# Deploy to development
npm run deploy:dev

# Deploy to production
npm run deploy
```

## Agent Workflows

### 1. Remote Team Sync
Monitors GitHub and ClickUp to summarize Philippines dev team progress.

**API Endpoint**: `POST /api/workflows/team-sync`
```json
{
  "githubRepoUrl": "https://github.com/org/repo",
  "clickupWorkspaceId": "your_workspace_id",
  "sinceDays": 7
}
```

### 2. Knowledge-to-Task
Reads strategy docs from Drive and breaks them into ClickUp project plans.

**API Endpoint**: `POST /api/workflows/knowledge-to-task`
```json
{
  "projectName": "Q1 Product Launch",
  "documentContent": "Strategy document text...",
  "clickupListId": "optional_list_id"
}
```

### 3. B2C Marketing Campaign
Marketing crew that researches Philippine market data and drafts localized campaigns.

**API Endpoint**: `POST /api/workflows/marketing-campaign`
```json
{
  "campaignBrief": "Launch B2C product in Philippines...",
  "targetMarket": "Philippines",
  "brandGuidelines": "Professional, innovative tone..."
}
```

## AI Agents

| Agent | Role | Capabilities |
|-------|------|--------------|
| **Team Sync Specialist** | Remote team monitoring | GitHub analysis, ClickUp task tracking, progress reports |
| **Knowledge Manager** | Document processing | Requirements extraction, project planning, task breakdown |
| **Marketing Strategist** | B2C campaigns | Market research, campaign concepts, localization |
| **Project Manager** | Coordination | Task creation, timeline management, resource allocation |
| **Communication Specialist** | Drafting | Emails, reports, presentations, stakeholder updates |

## Project Structure

```
phonologic-ops/
├── api/                      # Vercel serverless functions
│   ├── agents/
│   │   └── index.js          # Execute individual agent tasks
│   ├── auth/
│   │   └── google.js         # Google OAuth flow
│   ├── workflows/
│   │   ├── team-sync.js      # Remote team sync workflow
│   │   ├── knowledge-to-task.js  # Document to tasks workflow
│   │   └── marketing-campaign.js # B2C campaign workflow
│   └── health.js             # Health check endpoint
├── lib/                      # Shared libraries
│   ├── claude-client.js      # Claude 3.5 Sonnet integration
│   ├── agent-orchestrator.js # Agent workflow management
│   ├── firestore-db.js       # Firestore helpers
│   ├── google-workspace.js   # Drive/Gmail/Sheets integration
│   ├── clickup-client.js     # ClickUp API client
│   ├── github-client.js      # GitHub API client
│   └── rate-limiter.js       # Redis rate limiting
├── public/                   # Static frontend
│   ├── index.html            # Dashboard UI
│   ├── styles.css            # Styling
│   └── app.js                # Frontend logic
├── vercel.json               # Vercel configuration
├── package.json              # Dependencies
└── .env.example              # Environment template
```

## API Reference

### Health Check
```
GET /api/health
```

### List Agents
```
GET /api/agents
Authorization: Bearer <token>
```

### Execute Agent Task
```
POST /api/agents
Authorization: Bearer <token>
Content-Type: application/json

{
  "agentRole": "TEAM_SYNC | KNOWLEDGE | MARKETING | PROJECT_MANAGER | COMMUNICATION",
  "task": "Task description...",
  "context": "Optional context..."
}
```

### Workflow Endpoints
All workflow endpoints require `Authorization: Bearer <token>` header.

- `POST /api/workflows/team-sync`
- `POST /api/workflows/knowledge-to-task`
- `POST /api/workflows/marketing-campaign`

## Vercel Domain Configuration

To set up `ops.phonologic.cloud` subdomain:

1. In Vercel Dashboard → Project Settings → Domains
2. Add `ops.phonologic.cloud`
3. Configure DNS: Add CNAME record pointing to `cname.vercel-dns.com`

## Security Notes

- All API endpoints protected by Google SSO (@phonologic.ca only)
- Rate limiting via Upstash Redis (per-user, configurable per endpoint)
- HTTP-only secure session cookies
- CSRF protection with Redis-stored state tokens
- CORS restricted to `ops.phonologic.cloud` in production

## Roadmap

### Phase 2: Developer Experience
- [ ] **CLI Support**: Run workflows from terminal (`npx phonologic-ops run team-sync`)
- [ ] **Jupyter Notebooks**: Step-by-step agent execution for debugging

### Phase 3: AG-UI Protocol Integration
- [ ] **Real-time Streaming**: Stream Claude responses to frontend
- [ ] **Human-in-the-Loop**: Approval workflows before agent actions execute
- [ ] **Agent Visibility**: Step-by-step execution UI showing agent reasoning
- [ ] **CrewAI/LlamaIndex Support**: First-party AG-UI integration
