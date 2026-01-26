"""
Agno Agent Teams for Phonologic Operations
"""
from .marketing_fleet import MarketingFleet, create_marketing_fleet
from .project_ops import ProjectOpsTeam, create_project_ops_team
from .browser_navigator import BrowserNavigator, create_browser_navigator
from .brain_curator import BrainCurator, create_brain_curator_agent
from .deck_maestro import create_deck_maestro_team, analyze_presentation

__all__ = [
    "MarketingFleet",
    "create_marketing_fleet",
    "ProjectOpsTeam",
    "create_project_ops_team",
    "BrowserNavigator",
    "create_browser_navigator",
    "BrainCurator",
    "create_brain_curator_agent",
    "create_deck_maestro_team",
    "analyze_presentation"
]
