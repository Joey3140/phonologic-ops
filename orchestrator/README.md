# Phonologic Agentic Orchestrator

Production-grade multi-agent system built with **Agno** (formerly Phidata) and **FastAPI**.

## Architecture

```
orchestrator/
├── agents/                 # Agno Agent Teams
│   ├── marketing_fleet.py  # Marketing campaign automation
│   ├── project_ops.py      # PM automation (ClickUp, Drive, Email)
│   └── browser_navigator.py # Playwright browser control
├── api/                    # FastAPI Routes
│   ├── gateway.py          # Central orchestrator gateway
│   └── routes.py           # API endpoints
├── knowledge/              # PhonoLogics Brain
│   ├── brain.py            # Knowledge base implementation
│   └── schemas.py          # Knowledge Pydantic models
├── models/                 # Pydantic Models
│   ├── marketing.py        # Campaign, MidjourneyPrompt
│   ├── project_management.py # ClickUp, Email models
│   └── browser.py          # Browser action models
├── tools/                  # Custom Agno Toolkits
│   ├── clickup_toolkit.py
│   ├── google_drive_toolkit.py
│   ├── google_sheets_toolkit.py
│   ├── google_slides_toolkit.py
│   └── email_toolkit.py
├── main.py                 # FastAPI application
├── config.py               # Settings management
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Teams

### 🎨 Marketing Fleet
Orchestrates specialized agents to create comprehensive marketing campaigns:
- **Researcher**: Market research using DuckDuckGo
- **TechnicalConsultant**: Product-market fit analysis
- **BrandLead**: Brand strategy and messaging
- **ImageryArchitect**: Visual direction with Midjourney/DALL-E prompts

### 📋 Project Ops
Automates operational workflows:
- **Coordinator**: Workflow orchestration
- **TaskManager**: ClickUp task management
- **DocumentManager**: Google Drive document generation
- **Communicator**: Email via SendGrid

### 🌐 Browser Navigator
Browser automation with Playwright:
- Navigate and analyze web pages
- Slide/canvas analysis for Google Slides & Pitch.com
- Brand compliance checking
- Edit suggestions

## 🧠 PhonoLogics Brain

Central knowledge base accessible by all agents containing:
- Company mission, vision, and key metrics
- Brand guidelines (colors, tone, messaging)
- Product positioning and differentiators
- Team directory
- Pitch deck information
- Competitive intelligence

## Quick Start

### Local Development

```bash
cd orchestrator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for Browser Navigator)
playwright install chromium

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run the server
python main.py
# Or with uvicorn for hot reload:
uvicorn main:app --reload --port 8000
```

### Using Docker

```bash
cd orchestrator

# Build and run
docker-compose up --build

# Or run in background
docker-compose up -d
```

### Agno Studio (Debugging)

To visualize agent traces and tool calls:

```bash
pip install agno
agno dev  # Opens Agno Studio in browser
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/orchestrator/status` | GET | Gateway status and team health |
| `/api/orchestrator/teams` | GET | List available teams |
| `/api/orchestrator/marketing/campaign` | POST | Run marketing campaign workflow |
| `/api/orchestrator/pm/onboard` | POST | Run onboarding workflow |
| `/api/orchestrator/pm/tasks` | POST | Create ClickUp tasks |
| `/api/orchestrator/pm/progress-report` | POST | Send progress report |
| `/api/orchestrator/browser/analyze` | POST | Analyze slides for brand compliance |
| `/api/orchestrator/browser/navigate` | POST | Navigate and report page state |
| `/api/orchestrator/brain/company` | GET | Get company summary |
| `/api/orchestrator/brain/brand` | GET | Get brand guidelines |
| `/api/orchestrator/brain/product` | GET | Get product info |
| `/api/orchestrator/brain/query` | POST | Query knowledge brain |

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude agents |

### Optional - Integrations

| Variable | Description |
|----------|-------------|
| `CLICKUP_API_TOKEN` | ClickUp API token for task management |
| `CLICKUP_WORKSPACE_ID` | ClickUp workspace ID |
| `CLICKUP_DEFAULT_LIST_ID` | Default list for task creation |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google service account JSON (as string) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account file |
| `GOOGLE_DRIVE_FOLDER_ID` | Default Google Drive folder |
| `SENDGRID_API_KEY` | SendGrid API key for emails |
| `SENDGRID_FROM_EMAIL` | Sender email address |

### Optional - Debugging

| Variable | Description |
|----------|-------------|
| `AGNO_API_KEY` | Agno Studio API key for visual traces |
| `DEBUG` | Enable debug mode (`true`/`false`) |

## Deployment on ops.phonologic.cloud

### Option 1: Railway (Recommended)

1. Push code to GitHub
2. Go to [Railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select the `orchestrator` folder as root directory
4. Add environment variables in Railway dashboard
5. Copy the Railway URL (e.g., `your-app.railway.app`)
6. In Vercel dashboard, add: `ORCHESTRATOR_URL=your-app.railway.app`

### Option 2: Render

1. Go to [Render.com](https://render.com) → New Web Service
2. Connect your GitHub repo
3. Select Docker as runtime
4. Set root directory to `orchestrator`
5. Add environment variables
6. Copy URL and add to Vercel as `ORCHESTRATOR_URL`

### Option 3: Docker on VPS

```bash
ssh your-vps
cd /opt
git clone <repo> phonologic
cd phonologic/orchestrator
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

Then add `ORCHESTRATOR_URL=your-vps-ip:8000` to Vercel.

### Option 4: Cloudflare Tunnel

For secure team-only access:

```bash
# Install cloudflared
cloudflared tunnel create phonologic-orchestrator
cloudflared tunnel route dns phonologic-orchestrator api.ops.phonologic.cloud

# Run with tunnel
cloudflared tunnel run --url http://localhost:8000 phonologic-orchestrator
```

## Example Usage

### Run Marketing Campaign

```python
import httpx

response = httpx.post(
    "https://ops.phonologic.cloud/api/orchestrator/marketing/campaign",
    json={
        "product_concept": "AI-powered speech therapy app for children",
        "target_market": "North America",
        "campaign_goals": ["Brand awareness", "App downloads"]
    }
)

result = response.json()
print(result["strategy"]["image_prompts"])  # Midjourney prompts
```

### Query the Brain

```python
response = httpx.post(
    "https://ops.phonologic.cloud/api/orchestrator/brain/query",
    json={
        "query": "What are our key differentiators?",
        "category": "product"
    }
)
```

## Security Notes

- All endpoints require authentication via the ops.phonologic.cloud session
- CORS is restricted to allowed origins
- API keys are never exposed to the frontend
- Google OAuth scopes are "restricted/sensitive" - this is expected for Drive/Docs access

## License

MIT - Phonologic Team
