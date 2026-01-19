"""
Progress Tracker for Agent Workflows

Provides real-time progress updates via SSE (Server-Sent Events)
"""
import asyncio
import json
from typing import Optional, Callable, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from lib.logging_config import logger


class ProgressStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class AgentProgress(BaseModel):
    """Progress update for a single agent"""
    agent_name: str
    status: ProgressStatus
    message: str
    details: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class WorkflowProgress(BaseModel):
    """Overall workflow progress"""
    workflow_id: str
    workflow_name: str
    status: ProgressStatus
    current_agent: Optional[str] = None
    agents: list[AgentProgress]
    started_at: str
    elapsed_seconds: float
    message: str


class ProgressTracker:
    """
    Tracks progress of multi-agent workflows and emits SSE events.
    
    Usage:
        tracker = ProgressTracker("marketing_campaign")
        async for event in tracker.run_with_progress(workflow_func, input_data):
            yield event  # SSE event string
    """
    
    def __init__(self, workflow_name: str, agent_names: list[str]):
        self.workflow_id = f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.workflow_name = workflow_name
        self.agent_names = agent_names
        self.started_at = datetime.now()
        self.current_agent_index = -1
        self.status = ProgressStatus.PENDING
        self._queue: asyncio.Queue = asyncio.Queue()
        self._subscribers: list[asyncio.Queue] = []
    
    def _get_elapsed(self) -> float:
        return (datetime.now() - self.started_at).total_seconds()
    
    def _build_agents_status(self) -> list[AgentProgress]:
        """Build current status for all agents"""
        agents = []
        for i, name in enumerate(self.agent_names):
            if i < self.current_agent_index:
                status = ProgressStatus.COMPLETED
            elif i == self.current_agent_index:
                status = ProgressStatus.RUNNING
            else:
                status = ProgressStatus.PENDING
            
            agents.append(AgentProgress(
                agent_name=name,
                status=status,
                message=f"{name} - {status.value}"
            ))
        return agents
    
    def _build_progress(self, message: str) -> WorkflowProgress:
        """Build current workflow progress"""
        current_agent = None
        if 0 <= self.current_agent_index < len(self.agent_names):
            current_agent = self.agent_names[self.current_agent_index]
        
        return WorkflowProgress(
            workflow_id=self.workflow_id,
            workflow_name=self.workflow_name,
            status=self.status,
            current_agent=current_agent,
            agents=self._build_agents_status(),
            started_at=self.started_at.isoformat(),
            elapsed_seconds=self._get_elapsed(),
            message=message
        )
    
    def _format_sse(self, event_type: str, data: dict) -> str:
        """Format data as SSE event"""
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    
    async def emit(self, event_type: str, message: str, details: Optional[str] = None):
        """Emit a progress event"""
        progress = self._build_progress(message)
        if details and self.current_agent_index >= 0:
            progress.agents[self.current_agent_index].details = details
        
        event = self._format_sse(event_type, progress.model_dump())
        await self._queue.put(event)
        logger.info(f"Progress: {message}", agent=progress.current_agent)
    
    async def start_workflow(self):
        """Mark workflow as started"""
        self.status = ProgressStatus.RUNNING
        await self.emit("workflow_start", f"Starting {self.workflow_name}...")
    
    async def start_agent(self, agent_name: str, message: Optional[str] = None):
        """Mark an agent as started"""
        try:
            self.current_agent_index = self.agent_names.index(agent_name)
        except ValueError:
            self.current_agent_index = len(self.agent_names)
        
        msg = message or f"{agent_name} is working..."
        await self.emit("agent_start", msg)
    
    async def agent_update(self, message: str, details: Optional[str] = None):
        """Send an update for the current agent"""
        await self.emit("agent_update", message, details)
    
    async def complete_agent(self, agent_name: str, message: Optional[str] = None):
        """Mark an agent as completed"""
        msg = message or f"{agent_name} completed"
        await self.emit("agent_complete", msg)
    
    async def complete_workflow(self, message: Optional[str] = None):
        """Mark workflow as completed"""
        self.status = ProgressStatus.COMPLETED
        self.current_agent_index = len(self.agent_names)  # All done
        msg = message or f"{self.workflow_name} completed successfully"
        await self.emit("workflow_complete", msg)
    
    async def error(self, error_message: str):
        """Mark workflow as errored"""
        self.status = ProgressStatus.ERROR
        await self.emit("workflow_error", f"Error: {error_message}")
    
    async def get_events(self):
        """Async generator for SSE events"""
        # Send initial state
        yield self._format_sse("connected", {"workflow_id": self.workflow_id})
        
        while True:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=30.0)
                yield event
                
                # Check if workflow is done
                if self.status in [ProgressStatus.COMPLETED, ProgressStatus.ERROR]:
                    break
            except asyncio.TimeoutError:
                # Send keepalive
                yield ": keepalive\n\n"


def create_marketing_tracker() -> ProgressTracker:
    """Create a progress tracker for marketing campaigns"""
    return ProgressTracker(
        workflow_name="Marketing Campaign",
        agent_names=["Researcher", "TechnicalConsultant", "BrandLead", "ImageryArchitect"]
    )
