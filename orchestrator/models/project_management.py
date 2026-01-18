"""
Pydantic models for Project Management Team outputs
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskPriority(int, Enum):
    """ClickUp priority levels"""
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class TaskStatus(str, Enum):
    """Common task statuses"""
    TODO = "to do"
    IN_PROGRESS = "in progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class ClickUpTask(BaseModel):
    """ClickUp task structure"""
    name: str = Field(description="Task title")
    description: Optional[str] = Field(default=None, description="Task description in markdown")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    status: Optional[str] = Field(default=None, description="Task status")
    due_date: Optional[datetime] = Field(default=None)
    due_date_offset_days: Optional[int] = Field(default=None, description="Days from now for due date")
    tags: List[str] = Field(default_factory=list)
    assignees: List[str] = Field(default_factory=list, description="Email addresses of assignees")
    checklist_items: List[str] = Field(default_factory=list, description="Subtasks as checklist")
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class ClickUpTaskResult(BaseModel):
    """Result of ClickUp task operation"""
    success: bool
    task_id: Optional[str] = None
    task_url: Optional[str] = None
    error: Optional[str] = None


class GoogleDriveDocument(BaseModel):
    """Google Drive document reference"""
    file_id: str
    name: str
    mime_type: str
    web_view_link: Optional[str] = None
    created_time: Optional[datetime] = None


class DocumentTemplate(BaseModel):
    """Template for document generation"""
    template_id: str = Field(description="Google Drive file ID of the template")
    output_folder_id: str = Field(description="Folder ID for the generated document")
    output_name: str = Field(description="Name for the generated document")
    placeholders: Dict[str, str] = Field(description="Key-value pairs for template replacement")


class DocumentGenerationResult(BaseModel):
    """Result of document generation"""
    success: bool
    document: Optional[GoogleDriveDocument] = None
    error: Optional[str] = None


class EmailRecipient(BaseModel):
    """Email recipient"""
    email: str
    name: Optional[str] = None


class EmailMessage(BaseModel):
    """Email message structure"""
    to: List[EmailRecipient]
    cc: Optional[List[EmailRecipient]] = None
    bcc: Optional[List[EmailRecipient]] = None
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: Optional[List[str]] = Field(default=None, description="File paths or URLs")


class EmailResult(BaseModel):
    """Result of email send operation"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class OnboardingRequest(BaseModel):
    """Request to onboard a new team member or client"""
    entity_type: str = Field(description="'employee' or 'client'")
    name: str
    email: str
    role: Optional[str] = None
    start_date: Optional[datetime] = None
    department: Optional[str] = None
    template_type: str = Field(description="Type of onboarding template to use")
    custom_data: Dict[str, str] = Field(default_factory=dict, description="Additional data for templates")


class OnboardingResult(BaseModel):
    """Result of onboarding automation"""
    success: bool
    tasks_created: List[ClickUpTaskResult] = Field(default_factory=list)
    documents_generated: List[DocumentGenerationResult] = Field(default_factory=list)
    emails_sent: List[EmailResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ProgressReport(BaseModel):
    """Automated progress report"""
    project_name: str
    reporting_period: str
    tasks_completed: int
    tasks_in_progress: int
    tasks_blocked: int
    highlights: List[str]
    blockers: List[str]
    next_steps: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PMTeamInput(BaseModel):
    """Input model for PM Team tasks"""
    action: str = Field(description="Action type: 'onboard', 'update_tasks', 'send_report', 'generate_docs'")
    onboarding: Optional[OnboardingRequest] = None
    tasks_to_create: Optional[List[ClickUpTask]] = None
    tasks_to_update: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None, 
        description="Task ID to update data mapping"
    )
    document_templates: Optional[List[DocumentTemplate]] = None
    emails_to_send: Optional[List[EmailMessage]] = None
    list_id: Optional[str] = Field(default=None, description="ClickUp list ID for task operations")


class PMTeamOutput(BaseModel):
    """Output model for PM Team"""
    task_id: str
    status: str
    action_performed: str
    results: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    summary: str
