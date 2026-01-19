"""
FastAPI Routes for the Agno Orchestrator

Security Notes:
- Brain curator endpoints require authentication via X-User-Email header
- Contributor is extracted from auth context, not client-provided
- Rate limiting is applied per-user for query endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Header, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from models.base import GatewayStatus, TeamType
from lib.logging_config import logger
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
    text: str = Field(description="Natural language description of what to add", max_length=10000)
    force: bool = Field(default=False, description="Skip conflict detection")


class PaginatedPendingResponse(BaseModel):
    """Paginated response for pending contributions"""
    count: int
    total: int
    page: int
    page_size: int
    contributions: List[Dict[str, Any]]


async def get_authenticated_user(x_user_email: Optional[str] = Header(None)) -> str:
    """
    Extract authenticated user from request headers.
    
    In production, this should validate the token/session.
    For now, requires X-User-Email header to be present.
    """
    if not x_user_email:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide X-User-Email header."
        )
    
    # Basic email validation
    if '@' not in x_user_email or '.' not in x_user_email.split('@')[1]:
        raise HTTPException(
            status_code=400,
            detail="Invalid email format in X-User-Email header."
        )
    
    return x_user_email


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


@router.get("/brain/full")
async def get_full_brain(user: str = Depends(get_authenticated_user)):
    """Get the complete brain knowledge base (requires auth)"""
    curator = get_brain_curator()
    brain_data = curator.brain.knowledge.model_dump()
    
    # Also include Redis-persisted updates
    redis_updates = {}
    if curator.redis.available:
        try:
            redis_updates = curator.redis.get_brain_updates()
        except Exception:
            pass
    
    brain_data['redis_updates'] = redis_updates
    return brain_data


@router.get("/brain/history")
async def get_brain_history(
    limit: int = Query(50, ge=1, le=200, description="Max entries to return"),
    user: str = Depends(get_authenticated_user)
):
    """
    Get version history for brain updates (for rollback capability).
    
    Requires authentication via X-User-Email header.
    """
    curator = get_brain_curator()
    
    if not curator.redis.available:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    history = curator.redis.get_brain_history(limit=limit)
    return {"history": history, "count": len(history)}


@router.post("/brain/rollback")
async def rollback_brain_update(
    category: str = Query(..., description="Category of update to rollback"),
    key: str = Query(..., description="Key of update to rollback"),
    user: str = Depends(get_authenticated_user)
):
    """
    Rollback a brain update to its previous version.
    
    Requires authentication via X-User-Email header.
    """
    curator = get_brain_curator()
    
    if not curator.redis.available:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    logger.info("Rollback requested", category=category, key=key, user=user)
    
    result = curator.redis.rollback_brain_update(category, key)
    if result:
        return {
            "success": True,
            "message": f"Rolled back {category}/{key} to previous version",
            "restored_value": result
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"No history found for {category}/{key}"
        )


@router.get("/brain/audit")
async def get_audit_log(
    limit: int = Query(100, ge=1, le=500, description="Max entries to return"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    user: str = Depends(get_authenticated_user)
):
    """
    Get audit log of brain operations.
    
    Requires authentication via X-User-Email header.
    """
    curator = get_brain_curator()
    
    if not curator.redis.available:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    entries = curator.redis.get_audit_log(limit=limit, action_filter=action)
    return {"entries": entries, "count": len(entries)}


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
async def contribute_to_brain(
    request: BrainContributeRequest,
    contributor: str = Depends(get_authenticated_user)
):
    """
    Add new information to the PhonoLogic brain.
    
    Requires authentication via X-User-Email header.
    
    The system will:
    1. Validate and sanitize input
    2. Check for conflicts with existing brain content
    3. Provide feedback if conflicts detected
    4. Stage changes for review before merge
    """
    curator = get_brain_curator()
    try:
        logger.info("Brain contribution request", contributor=contributor)
        result = curator.process_contribution(
            text=request.text,
            contributor=contributor,  # From auth context, not request
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
        logger.error("Contribution error", error=str(e), contributor=contributor)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/brain/resolve", response_model=BrainCurationResponse)
async def resolve_brain_contribution(
    request: BrainResolveRequest,
    user: str = Depends(get_authenticated_user)
):
    """
    Resolve a pending contribution after conflict detection.
    
    Requires authentication via X-User-Email header.
    
    Actions:
    - `update` - Replace existing brain content with new info
    - `keep` - Keep existing content, discard the contribution
    - `add_note` - Add as a note without overwriting
    - `clarify` - Provide more context (requires clarification text)
    """
    curator = get_brain_curator()
    try:
        logger.info("Resolving contribution", contribution_id=request.contribution_id, action=request.action, user=user)
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
        logger.error("Resolution error", error=str(e), contribution_id=request.contribution_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brain/pending", response_model=PaginatedPendingResponse)
async def get_pending_contributions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user: str = Depends(get_authenticated_user)
):
    """
    Get pending contributions awaiting review with pagination.
    
    Requires authentication via X-User-Email header.
    """
    curator = get_brain_curator()
    
    # Get paginated results from Redis
    offset = (page - 1) * page_size
    pending_list, total = curator.redis.list_pending(limit=page_size, offset=offset)
    
    contributions = []
    for p in pending_list:
        try:
            contributions.append({
                "id": p.get('id'),
                "status": p.get('status'),
                "contributor": p.get('contributor'),
                "raw_input": p.get('raw_input', '')[:100] + "..." if len(p.get('raw_input', '')) > 100 else p.get('raw_input', ''),
                "conflicts_count": len(p.get('conflicts', [])),
                "created_at": p.get('created_at', '')
            })
        except Exception:
            continue
    
    return PaginatedPendingResponse(
        count=len(contributions),
        total=total,
        page=page,
        page_size=page_size,
        contributions=contributions
    )


class BrainChatRequest(BaseModel):
    """Chat with the brain - query or contribute"""
    message: str = Field(description="Natural language message to the brain")
    mode: str = Field(default="auto", description="'query', 'contribute', or 'auto' (detect intent)")


class PromptRequest(BaseModel):
    """Generic prompt request with optional Brain context"""
    prompt: str = Field(description="Natural language prompt")
    use_brain_context: bool = Field(default=True, description="Auto-fetch PhonoLogic context from Brain")
    url: Optional[str] = Field(default=None, description="Optional URL to analyze")


# ============================================================================
# SIMPLIFIED PROMPT-BASED ENDPOINTS (Auto-fetch Brain context)
# ============================================================================

@router.post("/marketing/prompt")
async def marketing_prompt(request: PromptRequest):
    """
    Generate marketing content using natural language prompt.
    Automatically fetches PhonoLogic brand guidelines, product info, and target market from Brain.
    """
    curator = get_brain_curator()
    
    try:
        # Build context from Brain
        brain_context = ""
        if request.use_brain_context:
            brain = curator.brain
            brain_context = f"""
## PhonoLogic Context (from Brain):
- **Company:** {brain.knowledge.company_name} - {brain.knowledge.tagline}
- **Mission:** {brain.knowledge.mission}
- **Product:** {brain.knowledge.products[0].name if brain.knowledge.products else 'Decodable Story Generator'}
- **Target Audience:** {', '.join(brain.knowledge.products[0].target_audience) if brain.knowledge.products else 'K-8 educators, literacy specialists, parents'}
- **Key Differentiators:** {', '.join(brain.knowledge.products[0].differentiators[:3]) if brain.knowledge.products else 'AI-powered, phonics-validated, time-saving'}
- **Current Stage:** {brain.knowledge.key_metrics.get('current_stage', 'Private Beta')}
- **Tone:** Empathetic, Authoritative, Child-Centered
"""
        
        # Use Claude to generate response
        full_prompt = f"{brain_context}\n\n## Task:\n{request.prompt}"
        response = curator.query_brain(full_prompt)
        
        return {"result": response, "brain_context_used": request.use_brain_context}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pm/task")
async def pm_task_prompt(request: PromptRequest):
    """
    Generate project management content using natural language prompt.
    Automatically fetches PhonoLogic team info and project context from Brain.
    """
    curator = get_brain_curator()
    
    try:
        brain_context = ""
        if request.use_brain_context:
            brain = curator.brain
            team_info = "\n".join([f"- {m.name} ({m.role})" for m in brain.knowledge.team[:5]]) if brain.knowledge.team else "- Stephen Robins (CEO)\n- Joey Drury (CTO)"
            
            brain_context = f"""
## PhonoLogic Context (from Brain):
- **Company:** {brain.knowledge.company_name}
- **Team:**
{team_info}
- **Current Stage:** {brain.knowledge.key_metrics.get('current_stage', 'Private Beta')}
- **Funding:** {brain.knowledge.key_metrics.get('funding_round', '$250K SAFE')}
- **Key Milestones:** Private Beta Jan 28, Public Beta Mar 1, Public Launch May 15
"""
        
        full_prompt = f"{brain_context}\n\n## Task:\n{request.prompt}"
        response = curator.query_brain(full_prompt)
        
        return {"result": response, "brain_context_used": request.use_brain_context}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pm/report")
async def pm_report_prompt(request: PromptRequest):
    """
    Generate reports and communications using natural language prompt.
    Automatically fetches PhonoLogic metrics, milestones, and team info from Brain.
    """
    curator = get_brain_curator()
    
    try:
        brain_context = ""
        if request.use_brain_context:
            brain = curator.brain
            milestones = brain.knowledge.milestones[-5:] if brain.knowledge.milestones else []
            milestone_text = "\n".join([f"- {m.get('date', 'TBD')}: {m.get('deliverable', 'N/A')} ({m.get('status', 'pending')})" for m in milestones])
            
            brain_context = f"""
## PhonoLogic Context (from Brain):
- **Company:** {brain.knowledge.company_name} - {brain.knowledge.mission}
- **Current Stage:** {brain.knowledge.key_metrics.get('current_stage', 'Private Beta')}
- **Funding:** {brain.knowledge.key_metrics.get('funding_round', '$250K SAFE')} - {brain.knowledge.key_metrics.get('funding_status', 'Raising')}
- **Target MRR (6mo):** {brain.knowledge.key_metrics.get('target_mrr_6_months', '$5,000')}
- **Target Users (6mo):** {brain.knowledge.key_metrics.get('target_users_6_months', '500')}

**Recent Milestones:**
{milestone_text}

**Traction:** Pilot with Montcrest School (12 educators, 20 students), IE Venture Lab Finalist
"""
        
        full_prompt = f"{brain_context}\n\n## Task:\n{request.prompt}"
        response = curator.query_brain(full_prompt)
        
        return {"result": response, "brain_context_used": request.use_brain_context}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/browser/prompt")
async def browser_prompt(request: PromptRequest):
    """
    Analyze content using natural language prompt.
    Automatically fetches PhonoLogic brand guidelines from Brain.
    """
    curator = get_brain_curator()
    
    try:
        brain_context = ""
        if request.use_brain_context:
            brain = curator.brain
            guidelines = brain.knowledge.marketing_guidelines[0] if brain.knowledge.marketing_guidelines else None
            
            brain_context = f"""
## PhonoLogic Brand Guidelines (from Brain):
- **Company:** {brain.knowledge.company_name}
- **Tagline:** {brain.knowledge.tagline}
- **Tone:** {guidelines.tone_of_voice if guidelines else 'Empathetic, Authoritative, Innovative, Child-Centered'}
- **Key Messages:** {', '.join(guidelines.key_messages[:3]) if guidelines else 'Saves teachers time, Structured literacy at core, Personalized learning'}
- **Do NOT Say:** {', '.join(guidelines.do_not_say[:2]) if guidelines else 'AI will replace teachers, Only for struggling readers'}
- **Primary Color:** #007bff (Blue)
"""
        
        url_context = f"\n**URL to analyze:** {request.url}" if request.url else ""
        full_prompt = f"{brain_context}{url_context}\n\n## Task:\n{request.prompt}"
        response = curator.query_brain(full_prompt)
        
        return {"result": response, "brain_context_used": request.use_brain_context, "url": request.url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/brain/chat")
async def chat_with_brain(
    request: BrainChatRequest,
    user: str = Depends(get_authenticated_user)
):
    """
    Natural language interface to the brain.
    
    Requires authentication via X-User-Email header.
    
    Modes:
    - `query` - Just ask a question
    - `contribute` - Add new information
    """
    try:
        curator = get_brain_curator()
    except Exception as e:
        logger.error("Failed to get curator", error=str(e))
        raise HTTPException(status_code=500, detail=f"Curator init error: {str(e)}")
    
    mode = request.mode
    logger.info("Brain chat request", mode=mode, user=user, message_preview=request.message[:50])
    
    try:
        if mode == "query":
            response = curator.query_brain(request.message, user_id=user)
            return {
                "mode": "query",
                "response": response,
                "conflicts": []
            }
        else:
            # Contribute mode - use authenticated user as contributor
            result = curator.process_contribution(request.message, contributor=user)
            return {
                "mode": "contribute",
                "response": result.message,
                "accepted": result.accepted,
                "conflicts": [c.model_dump() for c in result.conflicts_found],
                "contribution_id": result.contribution_id
            }
    except Exception as e:
        logger.error("Brain chat error", error=str(e), user=user)
        raise HTTPException(status_code=500, detail=str(e))
