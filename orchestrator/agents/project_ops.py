"""
Project Ops Team - Agno Team for Project Management Automation
Uses custom toolkits for ClickUp, Google Drive, and Email
"""
import os
from typing import Optional

from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude
from agno.storage.sqlite import SqliteStorage

from tools.clickup_toolkit import ClickUpToolkit
from tools.google_drive_toolkit import GoogleDriveToolkit
from tools.google_sheets_toolkit import GoogleSheetsToolkit
from tools.google_slides_toolkit import GoogleSlidesToolkit
from tools.email_toolkit import EmailToolkit
from knowledge.brain import create_brain_toolkit, PhonoLogicsBrain

from models.project_management import (
    PMTeamInput,
    PMTeamOutput,
    OnboardingResult,
    ProgressReport
)


def create_project_ops_team(
    model_id: str = "gpt-4o",
    storage_path: str = "agents.db",
    brain: Optional[PhonoLogicsBrain] = None,
    debug_mode: bool = False
) -> Team:
    """
    Create the Project Ops team with automation agents.
    
    Agents:
    - Coordinator: Orchestrates workflows and manages handoffs
    - TaskManager: ClickUp task operations
    - DocumentManager: Google Drive document operations
    - Communicator: Email and notifications
    
    Args:
        model_id: OpenAI model to use
        storage_path: Path to SQLite storage file
        brain: PhonoLogics Brain instance for company knowledge
        debug_mode: Enable debug logging
    
    Returns:
        Configured Agno Team
    """
    
    storage = SqliteStorage(
        table_name="project_ops",
        db_file=storage_path
    )
    
    model = Claude(
        id=model_id,
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    brain_toolkit = create_brain_toolkit(brain)
    
    clickup_available = bool(os.getenv("CLICKUP_API_TOKEN"))
    gdrive_available = bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    email_available = bool(os.getenv("SENDGRID_API_KEY"))
    
    coordinator = Agent(
        name="Coordinator",
        role="Project Operations Coordinator",
        model=model,
        tools=[brain_toolkit],
        instructions=[
            "You are the Project Operations Coordinator for PhonoLogic.",
            "Use the PhonoLogics Brain to understand company context.",
            "Analyze incoming requests and determine the appropriate workflow.",
            "For onboarding: coordinate TaskManager, DocumentManager, and Communicator.",
            "For task updates: route to TaskManager.",
            "For document generation: route to DocumentManager.",
            "For communications: route to Communicator.",
            "Always confirm actions before executing and summarize results."
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    task_manager_tools = [brain_toolkit]
    if clickup_available:
        task_manager_tools.append(ClickUpToolkit())
    
    task_manager = Agent(
        name="TaskManager",
        role="ClickUp Task Automation Specialist",
        model=model,
        tools=task_manager_tools,
        instructions=[
            "You manage ClickUp tasks for PhonoLogic projects.",
            "Create tasks with proper priorities, due dates, and descriptions.",
            "Update task statuses when work progresses.",
            "Add comments to tasks to log important updates.",
            "When a task moves to 'Done', notify the Communicator for follow-up.",
            "Use the PhonoLogics Brain to understand project context and terminology."
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    doc_manager_tools = [brain_toolkit]
    if gdrive_available:
        doc_manager_tools.append(GoogleDriveToolkit())
        doc_manager_tools.append(GoogleSheetsToolkit())
        doc_manager_tools.append(GoogleSlidesToolkit())
    
    document_manager = Agent(
        name="DocumentManager",
        role="Google Drive Document Automation Specialist",
        model=model,
        tools=doc_manager_tools,
        instructions=[
            "You manage Google Workspace documents for PhonoLogic.",
            "Create documents from templates by filling placeholders.",
            "Manage spreadsheets: read data, append rows, create reports.",
            "Manage presentations: read slides, fill templates, generate decks.",
            "Use the company knowledge to populate relevant information.",
            "Organize documents in appropriate folders.",
            "For onboarding, generate welcome docs, training materials, and access guides.",
            "Use consistent naming conventions: [Type]_[Name]_[Date]"
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    communicator_tools = [brain_toolkit]
    if email_available:
        communicator_tools.append(EmailToolkit())
    
    communicator = Agent(
        name="Communicator",
        role="Email and Notification Specialist",
        model=model,
        tools=communicator_tools,
        instructions=[
            "You handle all email communications for PhonoLogic operations.",
            "Send professional, on-brand emails using company tone guidelines.",
            "For onboarding: send welcome emails with relevant links and resources.",
            "For progress reports: compile task summaries into formatted emails.",
            "Always include clear next steps and contact information.",
            "Use the brand guidelines from PhonoLogics Brain for tone and messaging."
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    project_ops = Team(
        name="ProjectOps",
        mode="coordinate",
        model=model,
        members=[coordinator, task_manager, document_manager, communicator],
        storage=storage,
        instructions=[
            "You are the Project Ops team for PhonoLogic.",
            "Automate operational workflows: onboarding, task management, communications.",
            "The Coordinator receives requests and delegates to specialists.",
            "For onboarding workflows:",
            "  1. TaskManager creates ClickUp tasks for the onboarding checklist",
            "  2. DocumentManager generates welcome documents from templates",
            "  3. Communicator sends welcome email with all relevant links",
            "For status updates:",
            "  1. TaskManager updates the relevant tasks",
            "  2. Communicator sends notification if needed",
            "Always maintain context using the PhonoLogics Brain."
        ],
        add_history_to_messages=True,
        enable_agentic_context=True,
        share_member_interactions=True,
        debug_mode=debug_mode
    )
    
    return project_ops


class ProjectOpsTeam:
    """Wrapper class for Project Ops operations"""
    
    def __init__(
        self,
        model_id: str = "gpt-4o",
        storage_path: str = "agents.db",
        brain: Optional[PhonoLogicsBrain] = None,
        debug_mode: bool = False
    ):
        self.brain = brain or PhonoLogicsBrain()
        self.team = create_project_ops_team(model_id, storage_path, self.brain, debug_mode)
        self.debug_mode = debug_mode
    
    def run_onboarding(
        self,
        entity_type: str,
        name: str,
        email: str,
        role: Optional[str] = None,
        department: Optional[str] = None,
        custom_data: Optional[dict] = None
    ) -> PMTeamOutput:
        """
        Run employee or client onboarding workflow.
        
        Args:
            entity_type: 'employee' or 'client'
            name: Person's name
            email: Email address
            role: Job role (for employees)
            department: Department (for employees)
            custom_data: Additional template data
        
        Returns:
            PM Team output with results
        """
        prompt = f"""
Execute an onboarding workflow for a new {entity_type}:

**Name:** {name}
**Email:** {email}
{f"**Role:** {role}" if role else ""}
{f"**Department:** {department}" if department else ""}

Steps to execute:
1. Create ClickUp tasks for {entity_type} onboarding checklist
2. Generate welcome document from template with their information
3. Send welcome email with:
   - Personal greeting
   - Links to important resources
   - First-day instructions
   - Team contact information

Use PhonoLogic's brand voice and include relevant company information.
"""
        
        response = self.team.run(prompt)
        
        return PMTeamOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            action_performed="onboarding",
            results={
                "entity_type": entity_type,
                "name": name,
                "email": email
            },
            summary=f"Onboarding workflow completed for {name} ({entity_type})"
        )
    
    def create_tasks(
        self,
        tasks: list,
        list_id: Optional[str] = None
    ) -> PMTeamOutput:
        """
        Create multiple tasks in ClickUp.
        
        Args:
            tasks: List of task dictionaries with name, description, priority
            list_id: ClickUp list ID
        
        Returns:
            PM Team output with results
        """
        task_descriptions = "\n".join([
            f"- {t.get('name')}: {t.get('description', 'No description')}"
            for t in tasks
        ])
        
        prompt = f"""
Create the following tasks in ClickUp{f" (list: {list_id})" if list_id else ""}:

{task_descriptions}

For each task:
1. Set appropriate priority based on context
2. Add relevant tags
3. Set due dates if specified
4. Include detailed descriptions

Report back the created task IDs and URLs.
"""
        
        response = self.team.run(prompt)
        
        return PMTeamOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            action_performed="create_tasks",
            results={"tasks_requested": len(tasks)},
            summary=f"Created {len(tasks)} tasks in ClickUp"
        )
    
    def send_progress_report(
        self,
        project_name: str,
        recipient_email: str,
        recipient_name: str
    ) -> PMTeamOutput:
        """
        Generate and send a progress report.
        
        Args:
            project_name: Name of the project
            recipient_email: Email to send report to
            recipient_name: Recipient's name
        
        Returns:
            PM Team output with results
        """
        prompt = f"""
Generate and send a progress report for project: {project_name}

1. TaskManager: Get all tasks for this project, summarize:
   - Tasks completed this week
   - Tasks in progress
   - Blocked tasks
   
2. Communicator: Send formatted progress report email to:
   - Name: {recipient_name}
   - Email: {recipient_email}
   
Include:
- Task summary with counts
- Key highlights and achievements
- Blockers and risks
- Next steps for the coming week

Use PhonoLogic's professional tone.
"""
        
        response = self.team.run(prompt)
        
        return PMTeamOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            action_performed="send_progress_report",
            results={
                "project": project_name,
                "recipient": recipient_email
            },
            summary=f"Progress report sent to {recipient_email}"
        )
    
    def generate_document(
        self,
        template_id: str,
        output_name: str,
        placeholders: dict
    ) -> PMTeamOutput:
        """
        Generate a document from a template.
        
        Args:
            template_id: Google Drive template ID
            output_name: Name for the output document
            placeholders: Dictionary of placeholder values
        
        Returns:
            PM Team output with results
        """
        placeholder_str = "\n".join([f"- {{{{{k}}}}}: {v}" for k, v in placeholders.items()])
        
        prompt = f"""
Generate a document from template:

**Template ID:** {template_id}
**Output Name:** {output_name}

**Placeholders to fill:**
{placeholder_str}

Use the PhonoLogics Brain to fill in any company-specific information not provided.
Report back the new document URL.
"""
        
        response = self.team.run(prompt)
        
        return PMTeamOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            action_performed="generate_document",
            results={
                "template_id": template_id,
                "output_name": output_name
            },
            summary=f"Document '{output_name}' generated from template"
        )
    
    async def arun(self, prompt: str) -> PMTeamOutput:
        """Run any custom prompt asynchronously"""
        response = await self.team.arun(prompt)
        
        return PMTeamOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            action_performed="custom",
            results={},
            summary=str(response.content) if hasattr(response, 'content') else "Task completed"
        )
