"""
Phonologic Agentic Orchestrator - FastAPI Main Application
Production-grade Agno-based multi-agent system
"""
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_settings
from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    settings = get_settings()
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Debug Mode: {settings.DEBUG}")
    
    if not settings.ANTHROPIC_API_KEY:
        print("⚠️  WARNING: ANTHROPIC_API_KEY not set - agents will not function")
    
    yield
    
    print("👋 Shutting down orchestrator...")


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# Phonologic Agentic Orchestrator

Production-grade multi-agent system built with Agno (formerly Phidata).

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
- **TaskManager**: ClickUp integration
- **DocumentManager**: Google Drive automation
- **Communicator**: Email via SendGrid

### 🌐 Browser Navigator
Browser automation with Playwright:
- Navigate and analyze web pages
- Slide/canvas analysis for Google Slides & Pitch.com
- Brand compliance checking
- Edit suggestions

## Knowledge Brain
All agents share access to the PhonoLogics Brain - a central knowledge base containing:
- Company information and mission
- Brand guidelines and assets
- Product positioning
- Team directory
- Pitch materials
- Competitive intelligence
    """,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

allowed_origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "endpoints": {
            "status": "/api/orchestrator/status",
            "teams": "/api/orchestrator/teams",
            "brain": "/api/orchestrator/brain/company"
        }
    }


@app.get("/health")
async def health():
    """Health check for load balancers"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
