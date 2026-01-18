"""
Pydantic models for Marketing Team outputs
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ImageStyle(str, Enum):
    """Midjourney/DALL-E style options"""
    PHOTOREALISTIC = "photorealistic"
    ILLUSTRATION = "illustration"
    THREE_D_RENDER = "3d render"
    WATERCOLOR = "watercolor"
    DIGITAL_ART = "digital art"
    CINEMATIC = "cinematic"
    MINIMALIST = "minimalist"
    VINTAGE = "vintage"


class AspectRatio(str, Enum):
    """Common aspect ratios for image generation"""
    SQUARE = "1:1"
    PORTRAIT = "2:3"
    LANDSCAPE = "3:2"
    WIDE = "16:9"
    ULTRA_WIDE = "21:9"
    VERTICAL = "9:16"


class MidjourneyPrompt(BaseModel):
    """Structured output for Midjourney image generation"""
    subject: str = Field(description="Main subject of the image")
    environment: str = Field(description="Setting or background description")
    style: ImageStyle = Field(description="Visual style for the image")
    lighting: str = Field(description="Lighting description (e.g., 'soft natural light', 'dramatic shadows')")
    mood: str = Field(description="Emotional tone of the image")
    color_palette: List[str] = Field(description="Primary colors to emphasize")
    aspect_ratio: AspectRatio = Field(default=AspectRatio.LANDSCAPE)
    quality_params: str = Field(default="--q 2 --v 6", description="Midjourney quality parameters")
    negative_prompts: Optional[List[str]] = Field(default=None, description="Elements to avoid")
    
    def to_prompt_string(self) -> str:
        """Generate the full Midjourney prompt string"""
        parts = [
            self.subject,
            self.environment,
            f"{self.style.value} style",
            self.lighting,
            f"{self.mood} mood",
            f"color palette: {', '.join(self.color_palette)}"
        ]
        
        prompt = ", ".join(parts)
        prompt += f" --ar {self.aspect_ratio.value} {self.quality_params}"
        
        if self.negative_prompts:
            prompt += f" --no {', '.join(self.negative_prompts)}"
        
        return prompt


class DALLEPrompt(BaseModel):
    """Structured output for DALL-E image generation"""
    description: str = Field(description="Detailed image description")
    style: ImageStyle = Field(description="Visual style")
    size: str = Field(default="1024x1024", description="Image dimensions")
    quality: str = Field(default="hd", description="Quality level: standard or hd")


class MarketResearch(BaseModel):
    """Structured market research output"""
    target_demographics: List[str] = Field(description="Key demographic segments")
    consumer_behaviors: List[str] = Field(description="Relevant consumer behavior patterns")
    preferred_channels: List[str] = Field(description="Best marketing channels for this market")
    cultural_considerations: List[str] = Field(description="Cultural nuances to consider")
    competitor_insights: List[str] = Field(description="Key competitor observations")
    market_opportunities: List[str] = Field(description="Identified opportunities")


class CampaignConcept(BaseModel):
    """Individual campaign concept"""
    name: str = Field(description="Campaign concept name")
    theme: str = Field(description="Central theme")
    key_messaging: List[str] = Field(description="Core messages")
    visual_direction: str = Field(description="Visual style and approach")
    channel_strategy: List[str] = Field(description="Recommended channels")
    target_audience: str = Field(description="Primary audience segment")
    expected_outcomes: List[str] = Field(description="Anticipated results")


class CampaignStrategy(BaseModel):
    """Complete marketing campaign strategy output"""
    product_name: str
    target_market: str
    research: MarketResearch
    concepts: List[CampaignConcept] = Field(min_length=1, max_length=5)
    recommended_concept: str = Field(description="Name of the recommended concept")
    image_prompts: List[MidjourneyPrompt] = Field(description="Visual asset prompts")
    timeline_weeks: int = Field(description="Suggested campaign duration")
    budget_allocation: dict = Field(description="Percentage allocation by channel")


class MarketingTeamInput(BaseModel):
    """Input model for Marketing Team tasks"""
    product_concept: str = Field(description="Description of the product or service")
    target_market: str = Field(default="Global", description="Target geographic market")
    brand_guidelines: Optional[str] = Field(default=None, description="Existing brand guidelines")
    budget_range: Optional[str] = Field(default=None, description="Budget constraints")
    campaign_goals: List[str] = Field(default_factory=list, description="Specific campaign objectives")
    competitor_urls: Optional[List[str]] = Field(default=None, description="Competitor websites to analyze")


class MarketingTeamOutput(BaseModel):
    """Output model for Marketing Team"""
    task_id: str
    status: str
    strategy: CampaignStrategy
    execution_notes: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
