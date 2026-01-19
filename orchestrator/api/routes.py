"""
FastAPI Routes for the Agno Orchestrator
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from models.base import GatewayStatus, TeamType
from models.marketing import MarketingTeamInput, MarketingTeamOutput
from models.project_management import PMTeamOutput
from models.browser import BrowserNavigatorOutput

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])

_gateway = None


def get_gateway():
    """Get or create gateway instance"""
    global _gateway
    if _gateway is None:
        from .gateway import OrchestratorGateway
        from config import get_settings
        settings = get_settings()
        _gateway = OrchestratorGateway(
            model_id=settings.DEFAULT_MODEL,
            debug_mode=settings.DEBUG
        )
    return _gateway


class OnboardingRequest(BaseModel):
    entity_type: str = Field(description="'employee' or 'client'")
    name: str
    email: str
    role: Optional[str] = None
    department: Optional[str] = None


class TaskCreateRequest(BaseModel):
    tasks: List[Dict[str, Any]]
    list_id: Optional[str] = None


class ProgressReportRequest(BaseModel):
    project_name: str
    recipient_email: str
    recipient_name: str


class BrowserAnalyzeRequest(BaseModel):
    url: str
    check_brand_compliance: bool = True


class BrowserNavigateRequest(BaseModel):
    url: str


class BrainQueryRequest(BaseModel):
    query: str
    category: Optional[str] = None


class BrainQueryResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]


class BrainContributeRequest(BaseModel):
    """Request to add new information to the brain"""
    text: str = Field(description="Natural language description of what to add")
    contributor: str = Field(default="stephen@phonologic.ca")
    force: bool = Field(default=False, description="Skip conflict detection")


class BrainResolveRequest(BaseModel):
    """Request to resolve a pending contribution"""
    contribution_id: str
    action: str = Field(description="One of: update, keep, add_note, clarify")
    clarification: Optional[str] = None


class BrainCurationResponse(BaseModel):
    """Response from brain curation operations"""
    accepted: bool
    message: str
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    clarification_needed: bool = False
    contribution_id: Optional[str] = None


@router.get("/status", response_model=GatewayStatus)
async def get_status():
    """Get orchestrator gateway status"""
    gateway = get_gateway()
    return gateway.get_status()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agno-orchestrator"}


@router.post("/marketing/campaign", response_model=MarketingTeamOutput)
async def run_marketing_campaign(
    input_data: MarketingTeamInput,
    background_tasks: BackgroundTasks
):
    """
    Run a marketing campaign workflow.
    
    The Marketing Fleet team will:
    1. Research the market and competitors
    2. Analyze product-market fit
    3. Develop brand strategy and messaging
    4. Create visual direction with Midjourney prompts
    """
    gateway = get_gateway()
    try:
        result = await gateway.arun_marketing_campaign(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pm/onboard", response_model=PMTeamOutput)
async def run_onboarding(request: OnboardingRequest):
    """
    Run employee or client onboarding workflow.
    
    Creates ClickUp tasks, generates documents, and sends welcome email.
    """
    gateway = get_gateway()
    try:
        result = gateway.run_onboarding(
            entity_type=request.entity_type,
            name=request.name,
            email=request.email,
            role=request.role,
            department=request.department
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pm/tasks", response_model=PMTeamOutput)
async def create_tasks(request: TaskCreateRequest):
    """Create multiple ClickUp tasks"""
    gateway = get_gateway()
    try:
        result = gateway.create_tasks(request.tasks, request.list_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pm/progress-report", response_model=PMTeamOutput)
async def send_progress_report(request: ProgressReportRequest):
    """Generate and send a progress report"""
    gateway = get_gateway()
    try:
        result = gateway.send_progress_report(
            project_name=request.project_name,
            recipient_email=request.recipient_email,
            recipient_name=request.recipient_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/browser/analyze", response_model=BrowserNavigatorOutput)
async def analyze_slides(request: BrowserAnalyzeRequest):
    """
    Analyze presentation slides for brand compliance and improvements.
    
    Navigates to the URL and provides edit suggestions.
    """
    gateway = get_gateway()
    try:
        result = gateway.analyze_slides(
            url=request.url,
            check_brand_compliance=request.check_brand_compliance
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/browser/navigate", response_model=BrowserNavigatorOutput)
async def navigate_and_report(request: BrowserNavigateRequest):
    """Navigate to a URL and report the current state"""
    gateway = get_gateway()
    try:
        result = gateway.navigate_and_report(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brain/company")
async def get_company_info():
    """Get PhonoLogic company summary"""
    gateway = get_gateway()
    return {"content": gateway.get_company_info()}


@router.get("/brain/brand")
async def get_brand_guidelines():
    """Get PhonoLogic brand guidelines"""
    gateway = get_gateway()
    return {"content": gateway.get_brand_guidelines()}


@router.get("/brain/product")
async def get_product_info():
    """Get PhonoLogic product information"""
    gateway = get_gateway()
    return {"content": gateway.get_product_info()}


@router.post("/brain/query", response_model=BrainQueryResponse)
async def query_brain(request: BrainQueryRequest):
    """Query the PhonoLogics knowledge brain"""
    gateway = get_gateway()
    try:
        results = gateway.query_brain(request.query, request.category)
        return BrainQueryResponse(
            query=request.query,
            results=[r.model_dump() for r in results]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams")
async def list_teams():
    """List available teams and their capabilities"""
    return {
        "teams": [
            {
                "id": "marketing",
                "name": "Marketing Fleet",
                "description": "Campaign strategy, market research, and creative direction",
                "agents": ["Researcher", "TechnicalConsultant", "BrandLead", "ImageryArchitect"],
                "endpoints": ["/api/orchestrator/marketing/campaign"]
            },
            {
                "id": "project_management",
                "name": "Project Ops",
                "description": "Task automation, document generation, and communications",
                "agents": ["Coordinator", "TaskManager", "DocumentManager", "Communicator"],
                "endpoints": [
                    "/api/orchestrator/pm/onboard",
                    "/api/orchestrator/pm/tasks",
                    "/api/orchestrator/pm/progress-report"
                ]
            },
            {
                "id": "browser",
                "name": "Browser Navigator",
                "description": "Browser automation and slide/canvas analysis",
                "agents": ["BrowserNavigator"],
                "endpoints": [
                    "/api/orchestrator/browser/analyze",
                    "/api/orchestrator/browser/navigate"
                ]
            },
            {
                "id": "brain_curator",
                "name": "Brain Curator",
                "description": "Intelligent knowledge gatekeeper for Stephen's contributions",
                "agents": ["BrainCurator"],
                "endpoints": [
                    "/api/orchestrator/brain/contribute",
                    "/api/orchestrator/brain/resolve",
                    "/api/orchestrator/brain/pending",
                    "/api/orchestrator/brain/chat"
                ]
            }
        ]
    }


# ============================================================================
# BRAIN CURATOR ENDPOINTS (for Stephen)
# ============================================================================

_brain_curator = None

def get_brain_curator():
    """Get or create BrainCurator instance"""
    global _brain_curator
    if _brain_curator is None:
        from agents.brain_curator import BrainCurator
        _brain_curator = BrainCurator()
    return _brain_curator


@router.post("/brain/contribute", response_model=BrainCurationResponse)
async def contribute_to_brain(request: BrainContributeRequest):
    """
    Add new information to the PhonoLogic brain.
    
    Stephen can dump thoughts naturally. The system will:
    1. Parse the intent and extract structured info
    2. Check for conflicts with existing brain content
    3. Provide feedback if misconceptions detected
    4. Stage changes for review before merge
    
    Example:
        "Our pricing is $15/month now" 
        -> Response: "Hey Stephen, conflict! Brain says $20/mo. Update or keep existing?"
    """
    curator = get_brain_curator()
    try:
        result = curator.process_contribution(
            text=request.text,
            contributor=request.contributor,
            force=request.force
        )
        return BrainCurationResponse(
            accepted=result.accepted,
            message=result.message,
            conflicts=[c.model_dump() for c in result.conflicts_found],
            clarification_needed=result.clarification_needed,
            contribution_id=result.contribution_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/brain/resolve", response_model=BrainCurationResponse)
async def resolve_brain_contribution(request: BrainResolveRequest):
    """
    Resolve a pending contribution after conflict detection.
    
    Actions:
    - `update` - Replace existing brain content with new info
    - `keep` - Keep existing content, discard the contribution
    - `add_note` - Add as a note without overwriting
    - `clarify` - Provide more context (requires clarification text)
    """
    curator = get_brain_curator()
    try:
        result = curator.resolve_contribution(
            contribution_id=request.contribution_id,
            action=request.action,  # type: ignore
            clarification=request.clarification
        )
        return BrainCurationResponse(
            accepted=result.accepted,
            message=result.message,
            conflicts=[c.model_dump() for c in result.conflicts_found],
            clarification_needed=result.clarification_needed,
            contribution_id=result.contribution_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brain/pending")
async def get_pending_contributions():
    """Get all pending contributions awaiting review"""
    curator = get_brain_curator()
    pending = curator.pending_queue
    return {
        "count": len(pending),
        "contributions": [
            {
                "id": p.id,
                "status": p.status,
                "contributor": p.contributor,
                "raw_input": p.raw_input[:100] + "..." if len(p.raw_input) > 100 else p.raw_input,
                "conflicts_count": len(p.conflicts),
                "created_at": p.created_at.isoformat()
            }
            for p in pending
        ]
    }


class BrainChatRequest(BaseModel):
    """Chat with the brain - query or contribute"""
    message: str = Field(description="Natural language message to the brain")
    mode: str = Field(default="auto", description="'query', 'contribute', or 'auto' (detect intent)")


@router.post("/brain/chat")
async def chat_with_brain(request: BrainChatRequest):
    """
    Natural language interface to the brain for Stephen.
    
    Modes:
    - `query` - Just ask a question, don't try to add anything
    - `contribute` - Add new information
    - `auto` - Detect intent from the message
    
    Examples:
        "What's our current pricing?" -> Query mode, returns pricing info
        "Update: we now have rate limiting" -> Contribute mode, checks for conflicts
        "Do we have CORS set up?" -> Query mode, returns CORS info
    """
    curator = get_brain_curator()
    message = request.message.lower()
    
    # Auto-detect mode
    mode = request.mode
    if mode == "auto":
        query_indicators = ["what", "how", "do we", "is there", "where", "when", "who", "?"]
        contribute_indicators = ["update", "add", "change", "new", "now", "should be", "actually"]
        
        is_query = any(ind in message for ind in query_indicators)
        is_contribute = any(ind in message for ind in contribute_indicators)
        
        mode = "query" if is_query and not is_contribute else "contribute"
    
    try:
        if mode == "query":
            response = curator.query_brain(request.message)
            return {
                "mode": "query",
                "response": response,
                "conflicts": []
            }
        else:
            result = curator.process_contribution(request.message)
            return {
                "mode": "contribute",
                "response": result.message,
                "accepted": result.accepted,
                "conflicts": [c.model_dump() for c in result.conflicts_found],
                "contribution_id": result.contribution_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
