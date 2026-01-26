"""
Deck Maestro - AI-Powered Presentation Analysis & Optimization
Phase 1: Deck Analyzer - Analyzes presentations and generates improvement suggestions
"""
import os
import json
from typing import Optional, Dict, Any, List

from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude
try:
    from agno.storage.sqlite import SqliteStorage
    STORAGE_AVAILABLE = True
except ImportError:
    SqliteStorage = None
    STORAGE_AVAILABLE = False

from tools.google_slides_toolkit import GoogleSlidesToolkit
from tools.google_drive_toolkit import GoogleDriveToolkit
from knowledge.brain import create_brain_toolkit, PhonoLogicsBrain


def create_deck_maestro_team(
    model_id: str = "claude-sonnet-4-20250514",
    storage_path: str = "agents.db",
    brain: Optional[PhonoLogicsBrain] = None,
    debug_mode: bool = False
) -> Team:
    """
    Create the Deck Maestro team for presentation analysis and optimization.
    
    Agents:
    - DeckAnalyzer: Analyzes presentation content and generates "Thought Signature"
    - StyleCurator: Identifies visual improvements and style consistency issues
    - NarrativeCoach: Evaluates storytelling flow and messaging clarity
    
    Args:
        model_id: Claude model to use
        storage_path: Path to SQLite storage file  
        brain: PhonoLogics Brain instance for company knowledge
        debug_mode: Enable debug logging
    
    Returns:
        Configured Agno Team
    """
    
    storage = None
    if STORAGE_AVAILABLE:
        storage = SqliteStorage(
            table_name="deck_maestro",
            db_file=storage_path
        )
    
    model = Claude(
        id=model_id,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        retries=3,
        delay_between_retries=2,
        exponential_backoff=True
    )
    
    brain_toolkit = create_brain_toolkit(brain) if brain else None
    
    slides_available = bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    
    slides_toolkit = GoogleSlidesToolkit() if slides_available else None
    drive_toolkit = GoogleDriveToolkit() if slides_available else None
    
    analyzer_tools = []
    if slides_toolkit:
        analyzer_tools.append(slides_toolkit)
    if drive_toolkit:
        analyzer_tools.append(drive_toolkit)
    if brain_toolkit:
        analyzer_tools.append(brain_toolkit)
    
    deck_analyzer = Agent(
        name="DeckAnalyzer",
        role="Presentation Content Analyst",
        model=model,
        tools=analyzer_tools,
        instructions=[
            "You are the Deck Analyzer for PhonoLogic's Maestro system.",
            "Your job is to analyze presentations and generate a 'Thought Signature' - a comprehensive understanding of the deck's narrative, structure, and visual needs.",
            "",
            "When analyzing a presentation:",
            "1. Use get_presentation_info to understand the deck structure",
            "2. Use read_all_text to extract all content",
            "3. For detailed analysis, use read_slide on specific slides",
            "",
            "Generate a Thought Signature that includes:",
            "- **Core Narrative**: The main story/argument being told",
            "- **Target Audience**: Who this deck is for",
            "- **Key Messages**: The 3-5 main takeaways",
            "- **Data Points**: Important statistics or metrics presented",
            "- **Visual Assessment**: Which slides need visual improvement",
            "- **Content Issues**: Inconsistencies, unclear messaging, or gaps",
            "- **Brand Alignment**: How well it matches PhonoLogic brand voice",
            "",
            "Always provide actionable recommendations for each slide that needs work.",
            "Use the PhonoLogics Brain to ensure suggestions align with company brand and voice."
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    style_curator = Agent(
        name="StyleCurator", 
        role="Visual Design Consultant",
        model=model,
        tools=analyzer_tools,
        instructions=[
            "You are the Style Curator for PhonoLogic's Maestro system.",
            "Your job is to evaluate visual consistency and suggest design improvements.",
            "",
            "When reviewing slides:",
            "1. Identify slides with too much text (suggest infographics)",
            "2. Flag inconsistent styling across slides",
            "3. Note where visual hierarchy is unclear",
            "4. Suggest where images/graphics would improve engagement",
            "",
            "For each issue found, provide:",
            "- Slide number and current state",
            "- Specific problem identified", 
            "- Recommended visual solution",
            "- Style reference (if applicable)",
            "",
            "Always consider PhonoLogic brand colors:",
            "- Primary Orange: #F97316 (child-facing, CTAs)",
            "- Primary Maroon: #7C2D12 (professional, parent/teacher)",
            "- Secondary Cream: #FEF3C7 (backgrounds)"
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    narrative_coach = Agent(
        name="NarrativeCoach",
        role="Storytelling & Messaging Expert", 
        model=model,
        tools=analyzer_tools,
        instructions=[
            "You are the Narrative Coach for PhonoLogic's Maestro system.",
            "Your job is to evaluate the storytelling flow and messaging effectiveness.",
            "",
            "When reviewing a deck:",
            "1. Assess the narrative arc (setup, conflict, resolution)",
            "2. Check if the value proposition is clear and compelling",
            "3. Identify where the audience might lose interest",
            "4. Evaluate call-to-action strength",
            "",
            "Provide feedback on:",
            "- **Flow Score** (1-10): How well slides connect",
            "- **Clarity Score** (1-10): How clear the message is",
            "- **Engagement Score** (1-10): How compelling the content is",
            "- **Specific rewrites**: Suggest improved text for weak slides",
            "",
            "Remember PhonoLogic's key messages:",
            "- 'Where literacy meets possibility'",
            "- 'Reading practice that fits any learner in minutes'", 
            "- 'Needed by some, beneficial for all'",
            "",
            "AVOID suggesting:",
            "- 'Cure' or 'fix' reading disorders",
            "- 'Replace professional intervention'",
            "- 'Gamified' or 'game-based'",
            "- 'AI replaces teachers'"
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    team = Team(
        name="DeckMaestro",
        agents=[deck_analyzer, style_curator, narrative_coach],
        mode="coordinate",
        model=model,
        instructions=[
            "You are the Deck Maestro coordinator for PhonoLogic.",
            "Route presentation analysis requests to the appropriate specialist:",
            "",
            "- For full deck analysis → DeckAnalyzer (generates Thought Signature)",
            "- For visual/design feedback → StyleCurator", 
            "- For messaging/storytelling → NarrativeCoach",
            "",
            "For comprehensive reviews, coordinate all three agents:",
            "1. DeckAnalyzer creates the Thought Signature",
            "2. StyleCurator reviews visual consistency",
            "3. NarrativeCoach evaluates storytelling",
            "",
            "Compile findings into a unified 'Maestro Report' with:",
            "- Executive Summary",
            "- Thought Signature",
            "- Slide-by-Slide Recommendations",
            "- Priority Actions (what to fix first)",
            "- Estimated improvement impact"
        ],
        storage=storage,
        debug_mode=debug_mode
    )
    
    return team


class DeckMaestroAnalysis:
    """
    Structured output for deck analysis results.
    Can be stored in Redis for later retrieval.
    """
    
    def __init__(
        self,
        presentation_id: str,
        title: str,
        thought_signature: Dict[str, Any],
        slide_recommendations: List[Dict[str, Any]],
        style_issues: List[Dict[str, Any]],
        narrative_scores: Dict[str, int],
        priority_actions: List[str]
    ):
        self.presentation_id = presentation_id
        self.title = title
        self.thought_signature = thought_signature
        self.slide_recommendations = slide_recommendations
        self.style_issues = style_issues
        self.narrative_scores = narrative_scores
        self.priority_actions = priority_actions
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "presentation_id": self.presentation_id,
            "title": self.title,
            "thought_signature": self.thought_signature,
            "slide_recommendations": self.slide_recommendations,
            "style_issues": self.style_issues,
            "narrative_scores": self.narrative_scores,
            "priority_actions": self.priority_actions
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeckMaestroAnalysis":
        return cls(
            presentation_id=data["presentation_id"],
            title=data["title"],
            thought_signature=data["thought_signature"],
            slide_recommendations=data["slide_recommendations"],
            style_issues=data["style_issues"],
            narrative_scores=data["narrative_scores"],
            priority_actions=data["priority_actions"]
        )


async def analyze_presentation(
    presentation_id: str,
    brain: Optional[PhonoLogicsBrain] = None,
    debug_mode: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to analyze a presentation.
    
    Args:
        presentation_id: Google Slides presentation ID
        brain: Optional PhonoLogics Brain for context
        debug_mode: Enable debug output
    
    Returns:
        Analysis results dictionary
    """
    team = create_deck_maestro_team(brain=brain, debug_mode=debug_mode)
    
    prompt = f"""Analyze this Google Slides presentation comprehensively.

Presentation ID: {presentation_id}

Please:
1. Generate a complete Thought Signature
2. Review visual design and style consistency  
3. Evaluate narrative flow and messaging
4. Provide prioritized recommendations

Return a detailed Maestro Report."""

    response = await team.arun(prompt)
    
    return {
        "presentation_id": presentation_id,
        "analysis": response.content if hasattr(response, 'content') else str(response),
        "status": "complete"
    }
