"""
Pydantic schemas for PhonoLogics Knowledge Brain
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class KnowledgeCategory(str, Enum):
    """Categories of company knowledge"""
    BRAND = "brand"
    PRODUCT = "product"
    TEAM = "team"
    PITCH = "pitch"
    OPERATIONS = "operations"
    MARKETING = "marketing"
    TECHNICAL = "technical"
    COMPETITIVE = "competitive"


class BrandAsset(BaseModel):
    """Brand asset information"""
    id: str
    name: str
    asset_type: str = Field(description="'logo', 'color', 'font', 'guideline', 'template'")
    description: Optional[str] = None
    url: Optional[str] = None
    hex_value: Optional[str] = Field(default=None, description="For colors")
    usage_notes: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProductInfo(BaseModel):
    """Product information and positioning"""
    id: str
    name: str
    tagline: str
    description: str
    target_audience: List[str]
    key_features: List[str]
    value_propositions: List[str]
    differentiators: List[str]
    pricing_model: Optional[str] = None
    competitors: List[str] = Field(default_factory=list)
    stage: str = Field(default="active", description="'development', 'beta', 'active', 'deprecated'")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TeamMember(BaseModel):
    """Team member information"""
    id: str
    name: str
    email: str
    role: str
    department: str
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    is_active: bool = True
    joined_date: Optional[datetime] = None


class PitchInfo(BaseModel):
    """Pitch deck and investor information"""
    id: str
    name: str
    version: str
    description: str
    key_slides: List[Dict[str, str]] = Field(description="Slide number to content summary")
    target_investors: List[str] = Field(default_factory=list)
    funding_ask: Optional[str] = None
    valuation: Optional[str] = None
    traction_points: List[str] = Field(default_factory=list)
    pitch_deck_url: Optional[str] = None
    one_pager_url: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MarketingGuideline(BaseModel):
    """Marketing and communication guidelines"""
    id: str
    topic: str
    tone_of_voice: str
    key_messages: List[str]
    do_not_say: List[str] = Field(default_factory=list)
    approved_channels: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)


class CompetitorInfo(BaseModel):
    """Competitive intelligence"""
    id: str
    name: str
    website: str
    description: str
    strengths: List[str]
    weaknesses: List[str]
    our_differentiators: List[str]
    pricing: Optional[str] = None
    target_market: Optional[str] = None


class CompanyKnowledge(BaseModel):
    """Complete company knowledge structure"""
    company_name: str = "PhonoLogic"
    tagline: Optional[str] = None
    mission: str
    vision: str
    founded_year: int
    headquarters: str
    website: str
    marketing_website: Optional[str] = None
    
    launch_timeline: Dict[str, Any] = Field(default_factory=dict, description="Launch phases with dates and goals")
    
    brand_assets: List[BrandAsset] = Field(default_factory=list)
    products: List[ProductInfo] = Field(default_factory=list)
    team: List[TeamMember] = Field(default_factory=list)
    pitch_info: List[PitchInfo] = Field(default_factory=list)
    marketing_guidelines: List[MarketingGuideline] = Field(default_factory=list)
    competitors: List[CompetitorInfo] = Field(default_factory=list)
    
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    pricing: Dict[str, Any] = Field(default_factory=dict, description="Pricing tiers and details")
    pilots: List[Dict[str, Any]] = Field(default_factory=list, description="Active and planned pilot programs")
    milestones: List[Dict[str, Any]] = Field(default_factory=list, description="Product and business milestones")
    product_metrics_targets: Dict[str, Any] = Field(default_factory=dict, description="Target metrics for product success")
    
    problem_statement: Optional[str] = None
    solution_statement: Optional[str] = None
    moat: List[str] = Field(default_factory=list, description="Competitive moat and defensibility")
    strategic_partners_targets: List[str] = Field(default_factory=list)
    incubators_awards: List[str] = Field(default_factory=list)
    
    recent_updates: List[str] = Field(default_factory=list)
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeQuery(BaseModel):
    """Query for the knowledge brain"""
    query: str
    categories: Optional[List[KnowledgeCategory]] = None
    max_results: int = 5


class KnowledgeResult(BaseModel):
    """Result from knowledge query"""
    query: str
    results: List[Dict[str, Any]]
    category: KnowledgeCategory
    confidence: float = Field(ge=0, le=1)
    source: str
