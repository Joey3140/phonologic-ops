"""
Base Pydantic models for the Orchestrator
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class TeamType(str, Enum):
    """Available team types"""
    MARKETING = "marketing"
    PROJECT_MANAGEMENT = "project_management"
    BROWSER = "browser"


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRole(str, Enum):
    """Agent roles within teams"""
    # Marketing Team
    LEAD_RESEARCHER = "lead_researcher"
    TECH_CONSULTANT = "tech_consultant"
    BRANDING_EXPERT = "branding_expert"
    SOCIAL_EXPERT = "social_expert"
    
    # PM Team
    PROJECT_COORDINATOR = "project_coordinator"
    TASK_MANAGER = "task_manager"
    COMMUNICATION_SPECIALIST = "communication_specialist"
    
    # Browser Team
    NAVIGATION_AGENT = "navigation_agent"


class AgentMessage(BaseModel):
    """Message from an agent"""
    agent_id: str
    agent_role: AgentRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class TaskRequest(BaseModel):
    """Base request for task execution"""
    team: TeamType
    task_description: str
    context: Optional[Dict[str, Any]] = None
    priority: int = Field(default=1, ge=1, le=5)
    callback_url: Optional[str] = None


class TaskResponse(BaseModel):
    """Base response for task execution"""
    task_id: str
    team: TeamType
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent_messages: List[AgentMessage] = []


class TeamStatus(BaseModel):
    """Status of a team"""
    team: TeamType
    agents: List[str]
    active_tasks: int
    last_activity: Optional[datetime] = None
    is_healthy: bool = True


class GatewayStatus(BaseModel):
    """Overall gateway status"""
    status: str = "operational"
    version: str
    teams: List[TeamStatus]
    uptime_seconds: float
