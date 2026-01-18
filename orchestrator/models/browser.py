"""
Pydantic models for Browser/Canvas Agent outputs
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from datetime import datetime


class BrowserAction(str, Enum):
    """Available browser actions"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    SELECT = "select"
    HOVER = "hover"
    WAIT = "wait"
    EXTRACT = "extract"


class ElementLocator(BaseModel):
    """Element locator for browser interactions"""
    selector: str = Field(description="CSS selector or XPath")
    selector_type: str = Field(default="css", description="'css' or 'xpath'")
    description: Optional[str] = Field(default=None, description="Human-readable element description")


class ScreenCoordinates(BaseModel):
    """Screen position information"""
    x: int
    y: int
    width: Optional[int] = None
    height: Optional[int] = None


class ViewportState(BaseModel):
    """Current browser viewport state"""
    url: str
    title: str
    viewport_size: Tuple[int, int]
    scroll_position: Tuple[int, int]
    visible_elements: List[str] = Field(default_factory=list, description="Key visible element descriptions")
    active_element: Optional[str] = None


class BrowserActionRequest(BaseModel):
    """Request for a browser action"""
    action: BrowserAction
    target: Optional[ElementLocator] = None
    value: Optional[str] = Field(default=None, description="Text to type or URL to navigate to")
    coordinates: Optional[ScreenCoordinates] = None
    wait_ms: Optional[int] = Field(default=None, description="Wait time in milliseconds")


class BrowserActionResult(BaseModel):
    """Result of a browser action"""
    success: bool
    action: BrowserAction
    screenshot_path: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    viewport_state: Optional[ViewportState] = None


class SlideElement(BaseModel):
    """Element within a presentation slide"""
    element_type: str = Field(description="'text', 'image', 'shape', 'chart'")
    content: Optional[str] = None
    position: ScreenCoordinates
    editable: bool = True
    locator: Optional[ElementLocator] = None


class SlideState(BaseModel):
    """Current state of a presentation slide"""
    slide_number: int
    total_slides: int
    elements: List[SlideElement]
    title: Optional[str] = None
    notes: Optional[str] = None


class EditSuggestion(BaseModel):
    """Suggested edit for a canvas/slide element"""
    element_description: str
    current_value: Optional[str] = None
    suggested_value: str
    reasoning: str
    priority: str = Field(default="medium", description="'high', 'medium', 'low'")
    auto_applicable: bool = Field(default=False, description="Can be applied automatically")


class CanvasAnalysis(BaseModel):
    """Analysis of a canvas/slide presentation"""
    platform: str = Field(description="'google_slides', 'pitch', 'figma', etc.")
    current_slide: SlideState
    overall_assessment: str
    edit_suggestions: List[EditSuggestion]
    accessibility_issues: List[str] = Field(default_factory=list)
    brand_compliance: Optional[Dict[str, bool]] = None


class BrowserNavigatorInput(BaseModel):
    """Input model for Browser Navigator agent"""
    url: str = Field(description="URL to navigate to")
    task_type: str = Field(description="'analyze', 'edit', 'extract', 'navigate'")
    instructions: str = Field(description="Natural language instructions for the agent")
    target_elements: Optional[List[ElementLocator]] = None
    wait_for_selector: Optional[str] = None
    screenshot_on_complete: bool = True
    headless: bool = Field(default=True, description="Run browser in headless mode")


class BrowserNavigatorOutput(BaseModel):
    """Output model for Browser Navigator agent"""
    task_id: str
    status: str
    url_visited: str
    actions_performed: List[BrowserActionResult]
    canvas_analysis: Optional[CanvasAnalysis] = None
    edit_suggestions: List[EditSuggestion] = Field(default_factory=list)
    final_screenshot: Optional[str] = None
    viewport_state: Optional[ViewportState] = None
    report: str = Field(description="Human-readable summary of what the agent observed and did")


class ScreenReportRequest(BaseModel):
    """Request for the agent to report its current screen state"""
    include_screenshot: bool = True
    include_dom_snapshot: bool = False
    identify_editable_elements: bool = True


class ScreenReport(BaseModel):
    """Report of current screen state from the agent"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    viewport_state: ViewportState
    screenshot_base64: Optional[str] = None
    editable_elements: List[SlideElement] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
