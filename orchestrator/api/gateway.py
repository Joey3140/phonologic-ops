"""
Orchestrator Gateway - Central hub for all agent teams
"""
import time
from typing import Optional, Dict, Any
from datetime import datetime

from knowledge.brain import PhonoLogicsBrain
from agents.marketing_fleet import MarketingFleet
from agents.project_ops import ProjectOpsTeam
from agents.browser_navigator import BrowserNavigator

from models.base import TeamType, GatewayStatus, TeamStatus
from models.marketing import MarketingTeamInput, MarketingTeamOutput
from models.project_management import PMTeamInput, PMTeamOutput
from models.browser import BrowserNavigatorInput, BrowserNavigatorOutput


class OrchestratorGateway:
    """
    Central gateway for all Agno agent teams.
    
    Provides:
    - Unified access to all teams
    - Shared knowledge brain
    - Status monitoring
    - Request routing
    """
    
    def __init__(
        self,
        model_id: str = "gpt-4o",
        storage_path: str = "agents.db",
        brain_storage_path: str = "brain.db",
        debug_mode: bool = False
    ):
        self.model_id = model_id
        self.storage_path = storage_path
        self.debug_mode = debug_mode
        self.start_time = time.time()
        
        self.brain = PhonoLogicsBrain(storage_path=brain_storage_path)
        
        self._marketing_fleet: Optional[MarketingFleet] = None
        self._project_ops: Optional[ProjectOpsTeam] = None
        self._browser_navigator: Optional[BrowserNavigator] = None
    
    @property
    def marketing_fleet(self) -> MarketingFleet:
        """Lazy-load Marketing Fleet"""
        if self._marketing_fleet is None:
            self._marketing_fleet = MarketingFleet(
                model_id=self.model_id,
                storage_path=self.storage_path,
                debug_mode=self.debug_mode
            )
        return self._marketing_fleet
    
    @property
    def project_ops(self) -> ProjectOpsTeam:
        """Lazy-load Project Ops Team"""
        if self._project_ops is None:
            self._project_ops = ProjectOpsTeam(
                model_id=self.model_id,
                storage_path=self.storage_path,
                brain=self.brain,
                debug_mode=self.debug_mode
            )
        return self._project_ops
    
    @property
    def browser_navigator(self) -> BrowserNavigator:
        """Lazy-load Browser Navigator"""
        if self._browser_navigator is None:
            self._browser_navigator = BrowserNavigator(
                model_id=self.model_id,
                storage_path=self.storage_path,
                brain=self.brain,
                headless=not self.debug_mode,
                debug_mode=self.debug_mode
            )
        return self._browser_navigator
    
    def get_status(self) -> GatewayStatus:
        """Get gateway and team status"""
        return GatewayStatus(
            status="operational",
            version="1.0.0",
            teams=[
                TeamStatus(
                    team=TeamType.MARKETING,
                    agents=["Researcher", "TechnicalConsultant", "BrandLead", "ImageryArchitect"],
                    active_tasks=0,
                    is_healthy=True
                ),
                TeamStatus(
                    team=TeamType.PROJECT_MANAGEMENT,
                    agents=["Coordinator", "TaskManager", "DocumentManager", "Communicator"],
                    active_tasks=0,
                    is_healthy=True
                ),
                TeamStatus(
                    team=TeamType.BROWSER,
                    agents=["BrowserNavigator"],
                    active_tasks=0,
                    is_healthy=True
                )
            ],
            uptime_seconds=time.time() - self.start_time
        )
    
    def run_marketing_campaign(
        self,
        input_data: MarketingTeamInput
    ) -> MarketingTeamOutput:
        """Run marketing campaign workflow"""
        return self.marketing_fleet.run_campaign(input_data)
    
    async def arun_marketing_campaign(
        self,
        input_data: MarketingTeamInput
    ) -> MarketingTeamOutput:
        """Async run marketing campaign workflow"""
        return await self.marketing_fleet.arun_campaign(input_data)
    
    def run_onboarding(
        self,
        entity_type: str,
        name: str,
        email: str,
        role: Optional[str] = None,
        department: Optional[str] = None
    ) -> PMTeamOutput:
        """Run onboarding workflow"""
        return self.project_ops.run_onboarding(
            entity_type=entity_type,
            name=name,
            email=email,
            role=role,
            department=department
        )
    
    def create_tasks(
        self,
        tasks: list,
        list_id: Optional[str] = None
    ) -> PMTeamOutput:
        """Create ClickUp tasks"""
        return self.project_ops.create_tasks(tasks, list_id)
    
    def send_progress_report(
        self,
        project_name: str,
        recipient_email: str,
        recipient_name: str
    ) -> PMTeamOutput:
        """Send progress report"""
        return self.project_ops.send_progress_report(
            project_name, recipient_email, recipient_name
        )
    
    def analyze_slides(
        self,
        url: str,
        check_brand_compliance: bool = True
    ) -> BrowserNavigatorOutput:
        """Analyze presentation slides"""
        return self.browser_navigator.analyze_slides(url, check_brand_compliance)
    
    def navigate_and_report(self, url: str) -> BrowserNavigatorOutput:
        """Navigate to URL and report state"""
        return self.browser_navigator.navigate_and_report(url)
    
    def get_company_info(self) -> str:
        """Get company summary from brain"""
        return self.brain.get_company_summary()
    
    def get_brand_guidelines(self) -> str:
        """Get brand guidelines from brain"""
        return self.brain.get_brand_context()
    
    def get_product_info(self) -> str:
        """Get product info from brain"""
        return self.brain.get_product_context()
    
    def query_brain(
        self,
        query: str,
        category: Optional[str] = None
    ) -> list:
        """Query the knowledge brain"""
        from knowledge.schemas import KnowledgeCategory
        
        categories = None
        if category:
            try:
                categories = [KnowledgeCategory(category)]
            except ValueError:
                pass
        
        return self.brain.query(query, categories)
