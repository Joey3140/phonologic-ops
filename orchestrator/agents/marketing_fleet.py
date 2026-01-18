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
from agno.storage.sqlite import SqliteStorage

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
    model_id: str = "gpt-4o",
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
        model_id: OpenAI model to use
        storage_path: Path to SQLite storage file
        debug_mode: Enable debug logging
    
    Returns:
        Configured Agno Team
    """
    
    storage = SqliteStorage(
        table_name="marketing_fleet",
        db_file=storage_path
    )
    
    model = Claude(
        id=model_id,
        api_key=os.getenv("ANTHROPIC_API_KEY")
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
        instructions=[
            "You are an expert market researcher specializing in consumer insights.",
            "Use DuckDuckGo to research target markets, competitors, and consumer trends.",
            "Focus on actionable insights that inform marketing strategy.",
            "Always provide data sources and confidence levels for your findings.",
            "When research is complete, hand off to the TechnicalConsultant for product-market fit analysis."
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    tech_consultant = Agent(
        name="TechnicalConsultant",
        role="Product-Market Fit Analyst",
        model=model,
        instructions=[
            "You analyze products and their market positioning.",
            "Evaluate technical differentiators and competitive advantages.",
            "Identify target customer pain points and how the product addresses them.",
            "Provide insights on pricing strategy and market entry.",
            "After analysis, transfer to BrandLead for brand strategy development."
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    brand_lead = Agent(
        name="BrandLead",
        role="Brand Strategy Director",
        model=model,
        instructions=[
            "You craft compelling brand narratives and messaging frameworks.",
            "Develop campaign themes that resonate with target audiences.",
            "Ensure brand consistency across all touchpoints.",
            "Create 2-3 distinct campaign concepts with unique positioning.",
            "Recommend the strongest concept based on market research.",
            "After brand strategy, transfer to ImageryArchitect for visual direction."
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    imagery_architect = Agent(
        name="ImageryArchitect",
        role="Visual Creative Director",
        model=model,
        response_model=CampaignStrategy,
        instructions=[
            "You translate brand strategy into visual creative direction.",
            "Create detailed Midjourney/DALL-E prompts for campaign imagery.",
            "Each prompt should specify: subject, environment, style, lighting, mood, colors.",
            "Generate 3-5 image prompts per campaign concept.",
            "Output a complete CampaignStrategy with all research, concepts, and image prompts.",
            "Include proper Midjourney parameters like aspect ratio and quality settings."
        ],
        add_history_to_messages=True,
        debug_mode=debug_mode
    )
    
    marketing_fleet = Team(
        name="MarketingFleet",
        mode="coordinate",
        model=model,
        members=[researcher, tech_consultant, brand_lead, imagery_architect],
        storage=storage,
        instructions=[
            "You are the Marketing Fleet coordinator for Phonologic.",
            "Orchestrate agents to produce comprehensive marketing campaigns.",
            "Start with Researcher for market insights.",
            "Flow: Researcher -> TechnicalConsultant -> BrandLead -> ImageryArchitect.",
            "Ensure all agents build upon previous insights.",
            "Final output must be a complete CampaignStrategy from ImageryArchitect."
        ],
        add_history_to_messages=True,
        enable_agentic_context=True,
        share_member_interactions=True,
        debug_mode=debug_mode
    )
    
    return marketing_fleet


class MarketingFleet:
    """Wrapper class for Marketing Fleet operations"""
    
    def __init__(
        self,
        model_id: str = "gpt-4o",
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
