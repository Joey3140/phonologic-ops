"""
Marketing Fleet - Agno Team for Campaign Strategy & Creative
Uses Agno's native Team class with coordinate=True for agent handoffs
"""
import os
from typing import Optional

from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools
try:
    from agno.db.sqlite import SqliteDb
    STORAGE_AVAILABLE = True
except ImportError:
    try:
        from agno.storage.sqlite import SqliteStorage as SqliteDb
        STORAGE_AVAILABLE = True
    except ImportError:
        SqliteDb = None
        STORAGE_AVAILABLE = False

try:
    from agno.tools.serper import SerperTools
    SERPER_AVAILABLE = True
except ImportError:
    SERPER_AVAILABLE = False

from knowledge.brain import create_brain_toolkit, PhonoLogicsBrain

from models.marketing import (
    MarketingTeamInput,
    MarketingTeamOutput,
    CampaignStrategy,
    MidjourneyPrompt,
    MarketResearch,
    CampaignConcept
)


def create_marketing_fleet(
    model_id: str = "claude-sonnet-4-20250514",
    storage_path: str = "agents.db",
    brain: Optional[PhonoLogicsBrain] = None,
    debug_mode: bool = False
) -> Team:
    """
    Create the Marketing Fleet team with specialized agents.
    
    Agents:
    - Researcher: Market research using DuckDuckGo
    - TechnicalConsultant: Product-market fit analysis
    - BrandLead: Brand strategy and messaging
    - ImageryArchitect: Visual direction and Midjourney prompts
    
    Args:
        model_id: Claude model to use
        storage_path: Path to SQLite storage file
        debug_mode: Enable debug logging
    
    Returns:
        Configured Agno Team
    """
    
    storage = None
    if STORAGE_AVAILABLE:
        storage = SqliteDb(
            db_file=storage_path
        )
    
    model = Claude(
        id=model_id,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        retries=3,
        delay_between_retries=2,
        exponential_backoff=True
    )
    
    brain_toolkit = create_brain_toolkit(brain)
    
    # Use Serper if available (better results), fallback to DuckDuckGo
    search_tools = []
    if SERPER_AVAILABLE and os.getenv("SERPER_API_KEY"):
        search_tools.append(SerperTools())
    else:
        search_tools.append(DuckDuckGoTools())
    search_tools.append(brain_toolkit)
    
    researcher = Agent(
        name="Researcher",
        role="Lead Market Researcher",
        model=model,
        tools=search_tools,
        description="Expert market researcher who conducts thorough competitive and market analysis.",
        instructions=[
            "You are an expert market researcher specializing in consumer insights.",
            "ALWAYS use your search tools to research target markets, competitors, and consumer trends.",
            "Conduct at least 3-5 searches to gather comprehensive data.",
            "Focus on actionable insights that inform marketing strategy.",
            "Always provide data sources and confidence levels for your findings.",
            "Structure your research output with clear sections: Demographics, Behaviors, Channels, Competitors, Opportunities.",
            "Be thorough - this research will inform the entire campaign strategy."
        ],
        add_history_to_context=True,
        add_datetime_to_context=True,
        stream=True,
        debug_mode=debug_mode
    )
    
    tech_consultant = Agent(
        name="TechnicalConsultant",
        role="Product-Market Fit Analyst",
        model=model,
        tools=[brain_toolkit],
        description="Product strategist who analyzes market fit and competitive positioning.",
        instructions=[
            "You analyze products and their market positioning based on the Researcher's findings.",
            "Use the brain toolkit to access PhonoLogic's product details and differentiators.",
            "Evaluate technical differentiators and competitive advantages.",
            "Identify target customer pain points and how the product addresses them.",
            "Provide insights on pricing strategy and market entry.",
            "Challenge assumptions - if the research is missing key insights, note what's needed.",
            "Output a clear product-market fit analysis with strengths, weaknesses, and opportunities."
        ],
        add_history_to_context=True,
        add_datetime_to_context=True,
        stream=True,
        debug_mode=debug_mode
    )
    
    brand_lead = Agent(
        name="BrandLead",
        role="Brand Strategy Director",
        model=model,
        tools=[brain_toolkit],
        description="Creative director who develops brand strategy and campaign concepts.",
        instructions=[
            "You craft compelling brand narratives and messaging frameworks.",
            "Use the brain toolkit to access PhonoLogic's brand guidelines and tone.",
            "Build upon the Researcher's market insights and TechnicalConsultant's analysis.",
            "Develop campaign themes that resonate with target audiences.",
            "Ensure brand consistency across all touchpoints.",
            "Create 2-3 DISTINCT campaign concepts with unique positioning - don't make them too similar.",
            "For each concept, provide: name, theme, key messages, visual direction, channels, expected outcomes.",
            "Recommend the strongest concept and explain WHY based on the research.",
            "Be creative and bold - these concepts should stand out in the market."
        ],
        add_history_to_context=True,
        add_datetime_to_context=True,
        stream=True,
        debug_mode=debug_mode
    )
    
    brain_reviewer = Agent(
        name="BrainReviewer",
        role="Campaign Strategist & Knowledge Curator",
        model=model,
        tools=[brain_toolkit],
        description="Senior strategist who synthesizes all research into a final campaign strategy and stores it in the knowledge base.",
        instructions=[
            "You are the final reviewer who synthesizes all previous agent work into a cohesive campaign strategy.",
            "Review ALL previous agent outputs: research, product analysis, and brand concepts.",
            "Your job is to:",
            "1. Select the BEST campaign concept from BrandLead's proposals and explain why",
            "2. Synthesize key insights from the research and analysis",
            "3. Create a clear execution plan with timeline and budget allocation",
            "4. Store the final strategy in the brain for future reference",
            "",
            "OUTPUT FORMAT (use this exact structure):",
            "## Campaign Strategy Summary",
            "**Product:** [name]",
            "**Target Market:** [description]",
            "**Recommended Concept:** [concept name]",
            "**Why This Concept:** [2-3 sentences]",
            "",
            "## Key Messages",
            "- [message 1]",
            "- [message 2]", 
            "- [message 3]",
            "",
            "## Channels & Tactics",
            "[list recommended channels with tactics]",
            "",
            "## Timeline",
            "[week-by-week or phase breakdown]",
            "",
            "## Budget Allocation",
            "[percentage breakdown by channel/activity]",
            "",
            "## Next Steps",
            "[immediate action items]",
            "",
            "Use the brain toolkit to store key campaign decisions for future reference."
        ],
        add_history_to_context=True,
        add_datetime_to_context=True,
        stream=True,
        debug_mode=debug_mode
    )
    
    marketing_fleet = Team(
        name="MarketingFleet",
        model=model,
        members=[researcher, tech_consultant, brand_lead, brain_reviewer],
        db=storage,
        description="Senior marketing director coordinating a full-service campaign team.",
        instructions=[
            "You are the Marketing Fleet coordinator for PhonoLogic.",
            "Your job is to orchestrate agents to produce comprehensive marketing campaigns.",
            "",
            "WORKFLOW (follow this order strictly):",
            "1. DELEGATE to Researcher first - they MUST conduct actual web searches",
            "2. REVIEW Researcher's output - if insufficient, ask them to dig deeper",
            "3. DELEGATE to TechnicalConsultant with the research findings",
            "4. DELEGATE to BrandLead with research + product analysis",
            "5. DELEGATE to BrainReviewer to synthesize and finalize the campaign strategy",
            "",
            "QUALITY CONTROL:",
            "- If any agent's output is thin or generic, push back and ask for more depth",
            "- Ensure Researcher actually uses search tools (not just guessing)",
            "- Ensure BrandLead creates truly distinct concepts (not variations of the same idea)",
            "- BrainReviewer must produce a complete, actionable campaign strategy",
            "",
            "Final output must be a comprehensive campaign strategy from BrainReviewer."
        ],
        add_history_to_context=True,
        add_datetime_to_context=True,
        share_member_interactions=True,
        show_members_responses=True,
        stream_member_events=True,
        markdown=True,
        debug_mode=debug_mode
    )
    
    return marketing_fleet


class MarketingFleet:
    """Wrapper class for Marketing Fleet operations"""
    
    def __init__(
        self,
        model_id: str = "claude-sonnet-4-20250514",
        storage_path: str = "agents.db",
        debug_mode: bool = False
    ):
        self.team = create_marketing_fleet(model_id, storage_path, debug_mode)
        self.debug_mode = debug_mode
    
    def run_campaign(self, input_data: MarketingTeamInput) -> MarketingTeamOutput:
        """
        Run a full marketing campaign strategy workflow.
        
        Args:
            input_data: Marketing team input with product concept and requirements
        
        Returns:
            Complete campaign strategy with image prompts
        """
        prompt = self._build_prompt(input_data)
        
        response = self.team.run(prompt)
        
        if hasattr(response, 'content') and isinstance(response.content, CampaignStrategy):
            strategy = response.content
        else:
            strategy = self._parse_response(response)
        
        return MarketingTeamOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            strategy=strategy,
            execution_notes=[f"Team coordination completed with {len(self.team.members)} agents"],
            next_steps=["Review campaign concepts", "Select preferred concept", "Generate assets"]
        )
    
    async def arun_campaign(self, input_data: MarketingTeamInput) -> MarketingTeamOutput:
        """Async version of run_campaign"""
        prompt = self._build_prompt(input_data)
        response = await self.team.arun(prompt)
        
        if hasattr(response, 'content') and isinstance(response.content, CampaignStrategy):
            strategy = response.content
        else:
            strategy = self._parse_response(response)
        
        return MarketingTeamOutput(
            task_id=str(response.run_id) if hasattr(response, 'run_id') else "unknown",
            status="completed",
            strategy=strategy,
            execution_notes=[f"Team coordination completed with {len(self.team.members)} agents"],
            next_steps=["Review campaign concepts", "Select preferred concept", "Generate assets"]
        )
    
    async def arun_campaign_streaming(self, input_data: MarketingTeamInput):
        """
        Async streaming version that yields real-time progress events.
        
        Uses Agno's stream=True and stream_events=True to get actual agent activity.
        
        Agno Event Types (from docs):
        - TeamRunStarted: Run started
        - TeamRunContent: Content chunk streaming
        - TeamRunIntermediateContent: Intermediate content from members
        - TeamRunCompleted: Final completion with content and member_responses
        - TeamToolCallStarted/Completed: Tool usage
        - RunEvent.* for member agent events (when stream_member_events=True)
        
        Yields:
            Dict with event_type and data for each agent step.
            The LAST yielded event will have 'is_final': True and contain the result.
        """
        prompt = self._build_prompt(input_data)
        
        # Get the async stream with stream=True and stream_events=True
        # When stream=True, arun() returns AsyncIterator directly (not a coroutine)
        # Returns: AsyncIterator[Union[RunOutputEvent, TeamRunOutputEvent]]
        # yield_run_output=True ensures final TeamRunOutput is yielded at end
        stream = self.team.arun(prompt, stream=True, stream_events=True, yield_run_output=True)
        
        final_content = None
        final_member_responses = None
        stream_error = None
        
        # Iterate over streaming events with error handling for connection issues
        try:
            async for event in stream:
                event_data = self._parse_stream_event(event)
                if event_data:
                    yield event_data
                
                # Capture final result - check multiple possible sources
                event_type = getattr(event, 'event', '') or type(event).__name__
                
                # TeamRunCompleted event
                if event_type == "TeamRunCompleted":
                    final_content = getattr(event, 'content', None)
                    final_member_responses = getattr(event, 'member_responses', [])
                
                # TeamRunOutput object (from yield_run_output=True)
                if event_type == "TeamRunOutput" or hasattr(event, 'content') and hasattr(event, 'messages'):
                    # This is the final output object
                    final_content = getattr(event, 'content', None)
                    final_member_responses = getattr(event, 'member_responses', [])
        except Exception as e:
            # Handle connection errors (ConnectionTerminated, etc.)
            stream_error = str(e)
            yield {
                "event_type": "stream_error",
                "agent_name": None,
                "status": "error",
                "message": f"Stream interrupted: {stream_error[:100]}",
                "is_final": False,
            }
        
        # If stream errored, yield error as final result
        if stream_error:
            yield {
                "event_type": "final_result",
                "agent_name": None,
                "status": "error",
                "message": f"Campaign failed: {stream_error[:150]}",
                "is_final": True,
                "result": None,
                "error": stream_error,
                "member_count": 0
            }
            return
        
        # Yield the final result
        if final_content is not None:
            # Try to parse as CampaignStrategy
            result_data = None
            if isinstance(final_content, CampaignStrategy):
                result_data = final_content.model_dump()
            elif hasattr(final_content, 'model_dump'):
                result_data = final_content.model_dump()
            elif isinstance(final_content, dict):
                result_data = final_content
            elif isinstance(final_content, str):
                # Claude returns JSON string when structured outputs not supported
                import json
                try:
                    parsed = json.loads(final_content)
                    if isinstance(parsed, dict):
                        result_data = parsed
                except json.JSONDecodeError:
                    # Not JSON, store as raw content
                    result_data = {"raw_content": final_content}
            
            yield {
                "event_type": "final_result",
                "agent_name": None,
                "status": "completed",
                "message": "Campaign complete",
                "is_final": True,
                "result": result_data,
                "member_count": len(final_member_responses) if final_member_responses else 0
            }
    
    def _parse_stream_event(self, event) -> Optional[dict]:
        """
        Parse Agno TeamRunOutputEvent into our progress format.
        
        Agno event attributes (from docs):
        - event.event: str like "TeamRunStarted", "TeamRunContent", "TeamToolCallStarted"
        - event.content: Optional content
        - event.team_name: Team name
        - event.run_id: Run ID
        - event.tool (for tool events): ToolExecution object
        
        For member events (RunEvent):
        - event.agent_name or similar for member identification
        """
        try:
            # Get event type string from event.event attribute
            event_type = getattr(event, 'event', '') or type(event).__name__
            
            # Get team/agent info
            team_name = getattr(event, 'team_name', None)
            agent_name = getattr(event, 'agent_name', None)
            
            # For member events, try to get agent info
            if not agent_name:
                # Check if this is a member/agent-level event
                if hasattr(event, 'step_name'):
                    agent_name = event.step_name
                elif hasattr(event, 'member_name'):
                    agent_name = event.member_name
            
            # Get content/message
            message = None
            content = getattr(event, 'content', None)
            if content:
                if isinstance(content, str):
                    # Truncate long content
                    message = content[:150] + "..." if len(content) > 150 else content
                elif hasattr(content, 'model_dump'):
                    message = f"Structured output received"
                else:
                    message = str(content)[:150]
            
            # Handle tool events specifically
            if 'ToolCall' in event_type:
                tool = getattr(event, 'tool', None)
                if tool:
                    tool_name = getattr(tool, 'name', None) or getattr(tool, 'tool_name', 'unknown')
                    if 'Started' in event_type:
                        message = f"Using tool: {tool_name}"
                    else:
                        message = f"Tool completed: {tool_name}"
            
            # Determine status from event type
            status = "running"
            if 'Completed' in event_type or 'completed' in event_type:
                status = "completed"
            elif 'Error' in event_type:
                status = "error"
            elif 'Started' in event_type:
                status = "started"
            elif 'Content' in event_type:
                status = "streaming"
            
            # Create descriptive message if none
            if not message:
                event_desc = {
                    "TeamRunStarted": "Marketing Fleet started",
                    "TeamRunContent": "Generating content...",
                    "TeamRunIntermediateContent": "Processing intermediate results...",
                    "TeamRunCompleted": "Campaign complete",
                    "TeamToolCallStarted": "Using tool...",
                    "TeamToolCallCompleted": "Tool call done",
                    "TeamReasoningStarted": "Analyzing...",
                    "TeamReasoningStep": "Reasoning...",
                    "TeamReasoningCompleted": "Analysis complete",
                }.get(event_type, f"Processing ({event_type})...")
                message = event_desc
            
            return {
                "event_type": str(event_type),
                "agent_name": agent_name,
                "team_name": team_name,
                "status": status,
                "message": message,
            }
        except Exception as e:
            return {
                "event_type": "parse_error",
                "agent_name": None,
                "status": "running",
                "message": f"Processing... (parse error: {str(e)[:30]})"
            }
    
    def _build_prompt(self, input_data: MarketingTeamInput) -> str:
        """Build the prompt for the team"""
        prompt_parts = [
            f"Create a comprehensive marketing campaign strategy for the following product:",
            f"\n**Product Concept:** {input_data.product_concept}",
            f"\n**Target Market:** {input_data.target_market}"
        ]
        
        if input_data.brand_guidelines:
            prompt_parts.append(f"\n**Brand Guidelines:** {input_data.brand_guidelines}")
        
        if input_data.budget_range:
            prompt_parts.append(f"\n**Budget Range:** {input_data.budget_range}")
        
        if input_data.campaign_goals:
            prompt_parts.append(f"\n**Campaign Goals:** {', '.join(input_data.campaign_goals)}")
        
        if input_data.competitor_urls:
            prompt_parts.append(f"\n**Competitors to Research:** {', '.join(input_data.competitor_urls)}")
        
        prompt_parts.append("\n\nDeliver a complete campaign strategy with market research, 2-3 campaign concepts, and detailed Midjourney prompts for visual assets.")
        
        return "".join(prompt_parts)
    
    def _parse_response(self, response) -> CampaignStrategy:
        """Parse team response into CampaignStrategy if not already structured"""
        return CampaignStrategy(
            product_name="Parsed Campaign",
            target_market="Global",
            research=MarketResearch(
                target_demographics=["General audience"],
                consumer_behaviors=["Online research"],
                preferred_channels=["Digital"],
                cultural_considerations=["Standard"],
                competitor_insights=["Market competitive"],
                market_opportunities=["Growth potential"]
            ),
            concepts=[
                CampaignConcept(
                    name="Primary Concept",
                    theme="Innovation",
                    key_messaging=["Quality", "Value"],
                    visual_direction="Modern, clean aesthetic",
                    channel_strategy=["Social media", "Digital ads"],
                    target_audience="Primary demographic",
                    expected_outcomes=["Brand awareness", "Lead generation"]
                )
            ],
            recommended_concept="Primary Concept",
            image_prompts=[
                MidjourneyPrompt(
                    subject="Product hero shot",
                    environment="Clean studio background",
                    style="photorealistic",
                    lighting="Soft studio lighting",
                    mood="Professional and innovative",
                    color_palette=["white", "blue", "gray"]
                )
            ],
            timeline_weeks=8,
            budget_allocation={"social": 40, "digital": 35, "content": 25}
        )
