"""
Browser Navigator Agent - Agno Agent with Playwright for Browser Control
Provides canvas/slide editing assistance and browser automation
"""
import os
from typing import Optional

from agno.agent import Agent
from agno.models.anthropic import Claude
try:
    from agno.storage.sqlite import SqliteStorage
    STORAGE_AVAILABLE = True
except ImportError:
    SqliteStorage = None
    STORAGE_AVAILABLE = False

from knowledge.brain import create_brain_toolkit, PhonoLogicsBrain

from models.browser import (
    BrowserNavigatorInput,
    BrowserNavigatorOutput,
    CanvasAnalysis,
    EditSuggestion,
    ViewportState,
    ScreenReport
)


try:
    from agno.tools.playwright import PlaywrightTools
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def create_browser_navigator(
    model_id: str = "claude-sonnet-4-20250514",
    storage_path: str = "agents.db",
    brain: Optional[PhonoLogicsBrain] = None,
    headless: bool = True,
    debug_mode: bool = False
) -> Agent:
    """
    Create the Browser Navigator agent with Playwright toolkit.
    
    Capabilities:
    - Navigate to URLs (Google Slides, Pitch.com, etc.)
    - Analyze slide/canvas content
    - Suggest edits based on brand guidelines
    - Report screen state back to user
    - Perform basic browser actions (click, type, scroll)
    
    Args:
        model_id: Claude model to use
        storage_path: Path to SQLite storage file
        brain: PhonoLogics Brain instance
        headless: Run browser in headless mode (False for debugging)
        debug_mode: Enable debug logging
    
    Returns:
        Configured Agno Agent
    """
    
    storage = None
    if STORAGE_AVAILABLE:
        storage = SqliteStorage(
            table_name="browser_navigator",
            db_file=storage_path
        )
    
    model = Claude(
        id=model_id,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        retries=3,
        delay_between_retries=2,
        exponential_backoff=True
    )
    
    tools = [create_brain_toolkit(brain)]
    
    if PLAYWRIGHT_AVAILABLE:
        tools.append(PlaywrightTools(headless=headless))
    
    navigator = Agent(
        name="BrowserNavigator",
        role="Browser Navigation & Canvas Analysis Specialist",
        model=model,
        tools=tools,
        storage=storage,
        instructions=[
            "You are a Browser Navigator agent for PhonoLogic operations.",
            "You can control a browser to navigate web applications like Google Slides and Pitch.com.",
            "",
            "**Core Capabilities:**",
            "1. Navigate to URLs and analyze page content",
            "2. Identify editable elements in canvas/slide applications",
            "3. Suggest edits based on PhonoLogic brand guidelines",
            "4. Report current screen state with element positions",
            "5. Perform basic actions: click, type, scroll, screenshot",
            "",
            "**For Slide/Canvas Analysis:**",
            "- Identify text elements, images, and shapes",
            "- Check brand compliance (colors, fonts, messaging)",
            "- Suggest improvements based on brand guidelines",
            "- Note accessibility issues (contrast, readability)",
            "",
            "**Reporting Format:**",
            "Always report back with:",
            "- Current URL and page title",
            "- Key visible elements",
            "- Suggested edits with priority",
            "- Screenshot if requested",
            "",
            "**Safety Rules:**",
            "- Never enter credentials or sensitive information",
            "- Only interact with approved domains",
            "- Always confirm destructive actions before executing",
            "",
            "Use the PhonoLogics Brain to understand brand guidelines and product context."
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    return navigator


class BrowserNavigator:
    """Wrapper class for Browser Navigator operations"""
    
    def __init__(
        self,
        model_id: str = "claude-sonnet-4-20250514",
        storage_path: str = "agents.db",
        brain: Optional[PhonoLogicsBrain] = None,
        headless: bool = True,
        debug_mode: bool = False
    ):
        self.brain = brain or PhonoLogicsBrain()
        self.headless = headless
        self.agent = create_browser_navigator(
            model_id, storage_path, self.brain, headless, debug_mode
        )
        self.debug_mode = debug_mode
    
    def analyze_slides(
        self,
        url: str,
        check_brand_compliance: bool = True
    ) -> BrowserNavigatorOutput:
        """
        Navigate to a presentation and analyze slides.
        
        Args:
            url: URL of the presentation (Google Slides, Pitch.com)
            check_brand_compliance: Whether to check against brand guidelines
        
        Returns:
            Browser navigator output with analysis
        """
        prompt = f"""
Navigate to this presentation: {url}

Perform the following analysis:

1. **Page Identification:**
   - Confirm the platform (Google Slides, Pitch.com, etc.)
   - Report current slide number and total slides

2. **Content Analysis:**
   - List all text elements visible on the current slide
   - Identify images and their approximate positions
   - Note any charts, shapes, or other elements

3. **{"Brand Compliance Check:" if check_brand_compliance else "Visual Assessment:"}**
   {"- Check if colors match PhonoLogic brand (Primary: #6366F1, Secondary: #10B981)" if check_brand_compliance else ""}
   {"- Verify messaging aligns with key brand messages" if check_brand_compliance else ""}
   {"- Check font consistency" if check_brand_compliance else ""}
   - Assess visual hierarchy and readability
   - Note any accessibility concerns

4. **Edit Suggestions:**
   - List specific improvements with priority (high/medium/low)
   - Indicate which suggestions can be auto-applied
   - Provide exact text/color changes where applicable

5. **Screen Report:**
   - Current viewport state
   - Editable elements with their positions
   - Take a screenshot for reference

Use the PhonoLogics Brain to understand our brand guidelines.
"""
        
        response = self.agent.run(prompt)
        
        return BrowserNavigatorOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            url_visited=url,
            actions_performed=[],
            edit_suggestions=[],
            report=str(response.content) if hasattr(response, 'content') else "Analysis complete"
        )
    
    def navigate_and_report(self, url: str) -> BrowserNavigatorOutput:
        """
        Navigate to a URL and report the current state.
        
        Args:
            url: URL to navigate to
        
        Returns:
            Browser navigator output with screen state
        """
        prompt = f"""
Navigate to: {url}

Report back:
1. Page title and URL
2. Main visible content
3. Key interactive elements (buttons, links, inputs)
4. Current viewport size and scroll position
5. Take a screenshot

Do not perform any actions, just observe and report.
"""
        
        response = self.agent.run(prompt)
        
        return BrowserNavigatorOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            url_visited=url,
            actions_performed=[],
            report=str(response.content) if hasattr(response, 'content') else "Navigation complete"
        )
    
    def suggest_edits(
        self,
        url: str,
        context: str
    ) -> BrowserNavigatorOutput:
        """
        Analyze a page and suggest edits based on context.
        
        Args:
            url: URL to analyze
            context: What kind of edits to suggest (e.g., "investor pitch", "marketing")
        
        Returns:
            Browser navigator output with edit suggestions
        """
        prompt = f"""
Navigate to: {url}

Context: {context}

Analyze the content and provide specific edit suggestions:

1. Review all visible content against PhonoLogic brand guidelines
2. Identify areas that could be improved for the context: "{context}"
3. For each suggestion provide:
   - Element description (what to edit)
   - Current value (if text)
   - Suggested value
   - Reasoning
   - Priority (high/medium/low)
   - Whether it can be auto-applied

Focus on:
- Messaging alignment with key value propositions
- Visual consistency with brand
- Clarity and impact for the target audience

Use the PhonoLogics Brain for brand context and product positioning.
"""
        
        response = self.agent.run(prompt)
        
        return BrowserNavigatorOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            url_visited=url,
            actions_performed=[],
            edit_suggestions=[],
            report=str(response.content) if hasattr(response, 'content') else "Edit suggestions complete"
        )
    
    def execute_action(
        self,
        url: str,
        action: str,
        target_selector: Optional[str] = None,
        value: Optional[str] = None
    ) -> BrowserNavigatorOutput:
        """
        Execute a specific browser action.
        
        Args:
            url: URL to navigate to (if not already there)
            action: Action to perform (click, type, scroll)
            target_selector: CSS selector for target element
            value: Value to type (for type action)
        
        Returns:
            Browser navigator output with action result
        """
        prompt = f"""
Navigate to: {url}

Execute action: {action}
{f"Target element: {target_selector}" if target_selector else ""}
{f"Value to input: {value}" if value else ""}

Steps:
1. Navigate to the URL if not already there
2. Wait for page to load
3. {"Find the element: " + target_selector if target_selector else "Identify the main content"}
4. Execute the {action} action
5. Report the result and new page state
6. Take a screenshot after the action

Confirm success or report any errors.
"""
        
        response = self.agent.run(prompt)
        
        return BrowserNavigatorOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            url_visited=url,
            actions_performed=[],
            report=str(response.content) if hasattr(response, 'content') else "Action executed"
        )
    
    def get_screen_state(self) -> ScreenReport:
        """
        Get the current screen state without navigation.
        
        Returns:
            Current screen report
        """
        prompt = """
Report the current browser state:

1. Current URL and page title
2. Viewport dimensions
3. Scroll position
4. All visible text content (summarized)
5. Interactive elements:
   - Buttons (with text)
   - Links (with href)
   - Input fields (with placeholders)
   - Dropdowns
6. Editable elements (for canvas/slide apps):
   - Text boxes with content
   - Image placeholders
   - Shape elements

Take a screenshot and include it in the response.
"""
        
        response = self.agent.run(prompt)
        
        return ScreenReport(
            viewport_state=ViewportState(
                url="current",
                title="Current Page",
                viewport_size=(1920, 1080),
                scroll_position=(0, 0)
            ),
            suggested_actions=[str(response.content) if hasattr(response, 'content') else ""]
        )
    
    async def arun(self, prompt: str) -> BrowserNavigatorOutput:
        """Run any custom prompt asynchronously"""
        response = await self.agent.arun(prompt)
        
        return BrowserNavigatorOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            url_visited="custom",
            actions_performed=[],
            report=str(response.content) if hasattr(response, 'content') else "Task completed"
        )
