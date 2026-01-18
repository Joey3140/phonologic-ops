"""
PhonoLogics Brain - Central Knowledge Base
Provides a queryable knowledge store for all agents
"""
import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from agno.tools import Toolkit
from agno.storage.sqlite import SqliteStorage

from .schemas import (
    KnowledgeCategory,
    BrandAsset,
    ProductInfo,
    TeamMember,
    PitchInfo,
    MarketingGuideline,
    CompetitorInfo,
    CompanyKnowledge,
    KnowledgeQuery,
    KnowledgeResult
)


# Default PhonoLogic company knowledge
DEFAULT_KNOWLEDGE = CompanyKnowledge(
    company_name="PhonoLogic",
    mission="Empowering children with speech sound disorders through AI-powered therapy that's accessible, engaging, and effective.",
    vision="A world where every child has access to high-quality speech therapy, regardless of location or economic status.",
    founded_year=2024,
    headquarters="Canada",
    website="https://phonologic.cloud",
    
    brand_assets=[
        BrandAsset(
            id="logo-primary",
            name="PhonoLogic Primary Logo",
            asset_type="logo",
            description="Main logo with gradient purple/blue icon and wordmark",
            url="https://drive.google.com/drive/folders/1Qls5x8RlaEfyjLqH-rQ9fN6byRfCKWRC",
            usage_notes="Use on white or light backgrounds"
        ),
        BrandAsset(
            id="color-primary",
            name="Primary Purple",
            asset_type="color",
            hex_value="#6366F1",
            usage_notes="Primary brand color, use for CTAs and headers"
        ),
        BrandAsset(
            id="color-secondary",
            name="Secondary Green",
            asset_type="color",
            hex_value="#10B981",
            usage_notes="Success states, positive actions"
        ),
        BrandAsset(
            id="font-primary",
            name="Inter",
            asset_type="font",
            description="Primary typeface for all digital applications",
            usage_notes="Weights: 400 (body), 500 (emphasis), 600 (headers), 700 (display)"
        )
    ],
    
    products=[
        ProductInfo(
            id="phonologic-app",
            name="PhonoLogic",
            tagline="AI Speech Therapy for Children",
            description="An AI-powered speech therapy application designed to help children with speech sound disorders practice and improve their articulation through engaging, gamified exercises.",
            target_audience=[
                "Parents of children (ages 3-12) with speech sound disorders",
                "Speech-Language Pathologists (SLPs)",
                "Schools and educational institutions",
                "Pediatric therapy clinics"
            ],
            key_features=[
                "Real-time speech recognition and feedback",
                "Gamified practice sessions",
                "Progress tracking and analytics",
                "SLP dashboard for remote monitoring",
                "Personalized therapy plans",
                "Multi-language support"
            ],
            value_propositions=[
                "Supplement professional therapy with at-home practice",
                "Increase practice frequency and engagement",
                "Provide data-driven insights to therapists",
                "Make therapy accessible and affordable"
            ],
            differentiators=[
                "Purpose-built AI for child speech recognition",
                "Designed by SLPs and pediatric specialists",
                "Evidence-based therapeutic approach",
                "HIPAA-compliant and privacy-first"
            ],
            pricing_model="Freemium with subscription tiers",
            competitors=["Articulation Station", "Speech Blubs", "Constant Therapy"],
            stage="active"
        )
    ],
    
    team=[
        TeamMember(
            id="joey",
            name="Joey Drury",
            email="joey@phonologic.ca",
            role="Co-Founder & CEO",
            department="Executive",
            bio="Leading product vision and business strategy",
            skills=["Product Strategy", "AI/ML", "Business Development"]
        ),
        TeamMember(
            id="stephen",
            name="Stephen",
            email="stephen@phonologic.ca",
            role="Co-Founder",
            department="Executive",
            bio="Technical leadership and product development",
            skills=["Engineering", "Architecture", "Operations"]
        )
    ],
    
    pitch_info=[
        PitchInfo(
            id="google-accelerator-deck",
            name="Google for Startups Accelerator Pitch",
            version="2.0",
            description="Main investor pitch deck for Google for Startups Accelerator application",
            key_slides=[
                {"1": "Title and tagline"},
                {"2": "Problem: Access to speech therapy"},
                {"3": "Solution: AI-powered home practice"},
                {"4": "Market opportunity"},
                {"5": "Product demo"},
                {"6": "Business model"},
                {"7": "Traction and metrics"},
                {"8": "Team"},
                {"9": "Ask and use of funds"}
            ],
            target_investors=["Google for Startups", "EdTech VCs", "HealthTech Angels"],
            traction_points=[
                "Beta users actively practicing",
                "Partnership discussions with SLP clinics",
                "Google Accelerator acceptance"
            ],
            pitch_deck_url="https://app.pitch.com/app/presentation/f5ac655d-84e6-432f-bdf0-aa96f2deea3b/fdf5bf0d-1c5b-4a42-ba17-4ea1514d62be"
        )
    ],
    
    marketing_guidelines=[
        MarketingGuideline(
            id="tone-general",
            topic="General Tone of Voice",
            tone_of_voice="Warm, encouraging, and professional. We speak like a trusted friend who happens to be an expert.",
            key_messages=[
                "Every child deserves access to quality speech therapy",
                "Practice makes progress - and we make practice fun",
                "AI-powered, SLP-designed, parent-approved",
                "Your partner in your child's speech journey"
            ],
            do_not_say=[
                "Cure or fix speech disorders",
                "Replace professional therapy",
                "Guarantee specific outcomes",
                "Use clinical jargon without explanation"
            ],
            approved_channels=["Instagram", "Facebook", "LinkedIn", "Email", "Blog"],
            examples=[
                "Watch [child's name] light up as they master new sounds!",
                "Speech therapy practice that feels like playtime"
            ]
        )
    ],
    
    competitors=[
        CompetitorInfo(
            id="articulation-station",
            name="Articulation Station",
            website="https://articulationstation.com",
            description="Popular iOS app for articulation practice",
            strengths=["Established user base", "Comprehensive sound library", "SLP-created"],
            weaknesses=["No real-time feedback", "Limited engagement", "iOS only"],
            our_differentiators=["Real-time AI feedback", "Gamification", "Cross-platform"],
            pricing="One-time purchase ~$60"
        ),
        CompetitorInfo(
            id="speech-blubs",
            name="Speech Blubs",
            website="https://speechblubs.com",
            description="Video-based speech therapy app",
            strengths=["Strong marketing", "Good UI/UX", "Video modeling"],
            weaknesses=["Not specifically for articulation disorders", "Limited clinical backing"],
            our_differentiators=["Clinically validated", "Real-time recognition", "SLP integration"],
            pricing="Subscription ~$12/month"
        )
    ],
    
    key_metrics={
        "target_users_year_1": 10000,
        "target_revenue_year_1": "$500K ARR",
        "current_stage": "Early Growth",
        "team_size": 5
    },
    
    recent_updates=[
        "Accepted into Google for Startups Accelerator",
        "Launched Operations Portal at ops.phonologic.cloud",
        "Building Agentic AI orchestrator for automation"
    ]
)


class PhonoLogicsBrain:
    """
    Central knowledge store for PhonoLogic company information.
    
    Features:
    - Query by category (brand, product, team, pitch, etc.)
    - Full-text search across all knowledge
    - CRUD operations for knowledge management
    - Persistence via SQLite
    """
    
    def __init__(
        self,
        storage_path: str = "brain.db",
        initial_knowledge: Optional[CompanyKnowledge] = None
    ):
        self.storage_path = storage_path
        self.knowledge = initial_knowledge or DEFAULT_KNOWLEDGE
        self._storage = SqliteStorage(
            table_name="phonologics_brain",
            db_file=storage_path
        )
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage with default knowledge if empty"""
        try:
            stored = self._storage.read()
            if stored and "knowledge" in stored:
                self.knowledge = CompanyKnowledge.model_validate(stored["knowledge"])
        except Exception:
            self._save()
    
    def _save(self):
        """Persist knowledge to storage"""
        self._storage.upsert({
            "id": "company_knowledge",
            "knowledge": self.knowledge.model_dump(),
            "updated_at": datetime.utcnow().isoformat()
        })
    
    def query(
        self,
        query: str,
        categories: Optional[List[KnowledgeCategory]] = None,
        max_results: int = 5
    ) -> List[KnowledgeResult]:
        """
        Query the knowledge base.
        
        Args:
            query: Search query string
            categories: Optional filter by knowledge categories
            max_results: Maximum results to return
        
        Returns:
            List of knowledge results
        """
        results = []
        query_lower = query.lower()
        
        target_categories = categories or list(KnowledgeCategory)
        
        for category in target_categories:
            category_results = self._search_category(category, query_lower)
            results.extend(category_results)
        
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:max_results]
    
    def _search_category(
        self,
        category: KnowledgeCategory,
        query: str
    ) -> List[KnowledgeResult]:
        """Search within a specific category"""
        results = []
        
        if category == KnowledgeCategory.BRAND:
            for asset in self.knowledge.brand_assets:
                score = self._calculate_relevance(query, [
                    asset.name, asset.description or "", asset.usage_notes or ""
                ])
                if score > 0.1:
                    results.append(KnowledgeResult(
                        query=query,
                        results=[asset.model_dump()],
                        category=category,
                        confidence=score,
                        source="brand_assets"
                    ))
        
        elif category == KnowledgeCategory.PRODUCT:
            for product in self.knowledge.products:
                score = self._calculate_relevance(query, [
                    product.name, product.tagline, product.description,
                    " ".join(product.key_features),
                    " ".join(product.value_propositions)
                ])
                if score > 0.1:
                    results.append(KnowledgeResult(
                        query=query,
                        results=[product.model_dump()],
                        category=category,
                        confidence=score,
                        source="products"
                    ))
        
        elif category == KnowledgeCategory.TEAM:
            for member in self.knowledge.team:
                score = self._calculate_relevance(query, [
                    member.name, member.role, member.department,
                    member.bio or "", " ".join(member.skills)
                ])
                if score > 0.1:
                    results.append(KnowledgeResult(
                        query=query,
                        results=[member.model_dump()],
                        category=category,
                        confidence=score,
                        source="team"
                    ))
        
        elif category == KnowledgeCategory.PITCH:
            for pitch in self.knowledge.pitch_info:
                score = self._calculate_relevance(query, [
                    pitch.name, pitch.description,
                    " ".join(pitch.traction_points)
                ])
                if score > 0.1:
                    results.append(KnowledgeResult(
                        query=query,
                        results=[pitch.model_dump()],
                        category=category,
                        confidence=score,
                        source="pitch_info"
                    ))
        
        elif category == KnowledgeCategory.MARKETING:
            for guideline in self.knowledge.marketing_guidelines:
                score = self._calculate_relevance(query, [
                    guideline.topic, guideline.tone_of_voice,
                    " ".join(guideline.key_messages)
                ])
                if score > 0.1:
                    results.append(KnowledgeResult(
                        query=query,
                        results=[guideline.model_dump()],
                        category=category,
                        confidence=score,
                        source="marketing_guidelines"
                    ))
        
        elif category == KnowledgeCategory.COMPETITIVE:
            for competitor in self.knowledge.competitors:
                score = self._calculate_relevance(query, [
                    competitor.name, competitor.description,
                    " ".join(competitor.strengths),
                    " ".join(competitor.our_differentiators)
                ])
                if score > 0.1:
                    results.append(KnowledgeResult(
                        query=query,
                        results=[competitor.model_dump()],
                        category=category,
                        confidence=score,
                        source="competitors"
                    ))
        
        return results
    
    def _calculate_relevance(self, query: str, texts: List[str]) -> float:
        """Calculate relevance score based on keyword matching"""
        query_words = set(query.lower().split())
        combined_text = " ".join(texts).lower()
        
        matches = sum(1 for word in query_words if word in combined_text)
        return matches / len(query_words) if query_words else 0.0
    
    def get_company_summary(self) -> str:
        """Get a brief company summary for agent context"""
        return f"""
**{self.knowledge.company_name}**
- Mission: {self.knowledge.mission}
- Website: {self.knowledge.website}
- Stage: {self.knowledge.key_metrics.get('current_stage', 'Growth')}

**Primary Product:** {self.knowledge.products[0].name if self.knowledge.products else 'N/A'}
- {self.knowledge.products[0].tagline if self.knowledge.products else ''}

**Team Size:** {len(self.knowledge.team)} members

**Recent Updates:**
{chr(10).join('- ' + u for u in self.knowledge.recent_updates[:3])}
"""
    
    def get_brand_context(self) -> str:
        """Get brand guidelines for marketing agents"""
        guidelines = self.knowledge.marketing_guidelines[0] if self.knowledge.marketing_guidelines else None
        if not guidelines:
            return "No brand guidelines available."
        
        return f"""
**Tone of Voice:** {guidelines.tone_of_voice}

**Key Messages:**
{chr(10).join('- ' + m for m in guidelines.key_messages)}

**Do NOT Say:**
{chr(10).join('- ' + d for d in guidelines.do_not_say)}

**Primary Colors:**
{chr(10).join(f'- {a.name}: {a.hex_value}' for a in self.knowledge.brand_assets if a.asset_type == 'color')}
"""
    
    def get_product_context(self) -> str:
        """Get product information for agents"""
        product = self.knowledge.products[0] if self.knowledge.products else None
        if not product:
            return "No product information available."
        
        return f"""
**{product.name}**: {product.tagline}

{product.description}

**Key Features:**
{chr(10).join('- ' + f for f in product.key_features)}

**Value Propositions:**
{chr(10).join('- ' + v for v in product.value_propositions)}

**Differentiators:**
{chr(10).join('- ' + d for d in product.differentiators)}

**Target Audience:**
{chr(10).join('- ' + a for a in product.target_audience)}
"""
    
    def add_team_member(self, member: TeamMember):
        """Add a team member"""
        self.knowledge.team.append(member)
        self._save()
    
    def update_product(self, product: ProductInfo):
        """Update or add a product"""
        for i, p in enumerate(self.knowledge.products):
            if p.id == product.id:
                self.knowledge.products[i] = product
                self._save()
                return
        self.knowledge.products.append(product)
        self._save()
    
    def add_recent_update(self, update: str):
        """Add a recent update"""
        self.knowledge.recent_updates.insert(0, update)
        self.knowledge.recent_updates = self.knowledge.recent_updates[:10]
        self._save()


def create_brain_toolkit(brain: Optional[PhonoLogicsBrain] = None) -> Toolkit:
    """
    Create an Agno Toolkit for querying the PhonoLogics Brain.
    
    This toolkit can be added to any agent to give them access to company knowledge.
    """
    _brain = brain or PhonoLogicsBrain()
    
    class BrainToolkit(Toolkit):
        def __init__(self):
            super().__init__(name="phonologics_brain")
            self.brain = _brain
            
            self.register(self.query_knowledge)
            self.register(self.get_company_info)
            self.register(self.get_brand_guidelines)
            self.register(self.get_product_info)
            self.register(self.get_team_info)
            self.register(self.get_pitch_info)
            self.register(self.get_competitor_info)
        
        def query_knowledge(
            self,
            query: str,
            category: Optional[str] = None
        ) -> str:
            """
            Search PhonoLogic's knowledge base for relevant information.
            
            Args:
                query: Natural language search query
                category: Optional category filter: 'brand', 'product', 'team', 'pitch', 'marketing', 'competitive'
            
            Returns:
                JSON string with relevant knowledge results
            """
            categories = None
            if category:
                try:
                    categories = [KnowledgeCategory(category)]
                except ValueError:
                    pass
            
            results = self.brain.query(query, categories)
            return json.dumps([r.model_dump() for r in results], default=str)
        
        def get_company_info(self) -> str:
            """
            Get a summary of PhonoLogic company information.
            
            Returns:
                Formatted company summary
            """
            return self.brain.get_company_summary()
        
        def get_brand_guidelines(self) -> str:
            """
            Get PhonoLogic brand guidelines including tone, messaging, and colors.
            
            Returns:
                Formatted brand guidelines
            """
            return self.brain.get_brand_context()
        
        def get_product_info(self) -> str:
            """
            Get detailed PhonoLogic product information.
            
            Returns:
                Formatted product information
            """
            return self.brain.get_product_context()
        
        def get_team_info(self) -> str:
            """
            Get PhonoLogic team member information.
            
            Returns:
                JSON string with team member details
            """
            return json.dumps([m.model_dump() for m in self.brain.knowledge.team], default=str)
        
        def get_pitch_info(self) -> str:
            """
            Get PhonoLogic pitch deck and investor information.
            
            Returns:
                JSON string with pitch information
            """
            return json.dumps([p.model_dump() for p in self.brain.knowledge.pitch_info], default=str)
        
        def get_competitor_info(self) -> str:
            """
            Get competitive intelligence about PhonoLogic's market.
            
            Returns:
                JSON string with competitor analysis
            """
            return json.dumps([c.model_dump() for c in self.brain.knowledge.competitors], default=str)
    
    return BrainToolkit()
