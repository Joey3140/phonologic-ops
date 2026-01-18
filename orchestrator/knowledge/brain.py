"""
PhonoLogics Brain - Central Knowledge Base
Provides a queryable knowledge store for all agents
"""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from agno.tools import Toolkit

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
    tagline="Where literacy meets possibility",
    mission="Finding a text that fits your learner should not be the hard part of learning how to read. We create reading practice that fits any learner in minutes.",
    vision="A world where every child has access to reading practice that matches their phonics skills and interests, regardless of learning differences.",
    founded_year=2024,
    headquarters="Toronto, Canada",
    website="https://phonologic.cloud",
    marketing_website="https://www.phonologic.ca",
    
    # Launch Timeline
    launch_timeline={
        "private_beta": {
            "start": "2026-01-28",
            "end": "2026-03-01",
            "goals": ["Recruit 50 beta testers", "Gather feedback", "Iterate on core features"],
            "target_users": "Teachers, SLPs, and parents from pilot schools"
        },
        "public_beta": {
            "start": "2026-03-01",
            "end": "2026-05-14",
            "goals": ["Grow to 500 users", "Product iteration based on feedback", "Build testimonials"],
            "target_users": "K-4 teachers, reading specialists, parents of struggling readers"
        },
        "public_launch": {
            "date": "2026-05-15",
            "goals": ["Full launch", "Drive signups and awareness", "School licensing"],
            "target_users": "K-8 educators, districts, families"
        },
        "district_ready": {
            "date": "2026-09-01",
            "goals": ["Full K-8 phonics coverage", "District licensing", "Partner integrations"]
        }
    },
    
    brand_assets=[
        BrandAsset(
            id="logo-primary",
            name="PhonoLogic Primary Logo",
            asset_type="logo",
            description="Orange/maroon P icon with wordmark",
            url="https://drive.google.com/drive/folders/1Qls5x8RlaEfyjLqH-rQ9fN6byRfCKWRC",
            usage_notes="Orange for child-facing, maroon for professional contexts"
        ),
        BrandAsset(
            id="color-primary-orange",
            name="Primary Orange",
            asset_type="color",
            hex_value="#F97316",
            usage_notes="Warm, engaging - use for child-facing content and CTAs"
        ),
        BrandAsset(
            id="color-primary-maroon",
            name="Primary Maroon",
            asset_type="color",
            hex_value="#7C2D12",
            usage_notes="Professional, trustworthy - use for parent/teacher facing content"
        ),
        BrandAsset(
            id="color-secondary-cream",
            name="Secondary Cream",
            asset_type="color",
            hex_value="#FEF3C7",
            usage_notes="Warm background color"
        ),
        BrandAsset(
            id="font-primary",
            name="General Sans",
            asset_type="font",
            description="Primary typeface for headers and display",
            usage_notes="Weights: 600 (Semibold), 700 (Bold) for headers"
        ),
        BrandAsset(
            id="font-secondary",
            name="Open Sauce Sans",
            asset_type="font",
            description="Secondary typeface for body text",
            usage_notes="Weight: 400 (Regular) for body text"
        )
    ],
    
    products=[
        ProductInfo(
            id="phonologic-decodable-generator",
            name="PhonoLogic Decodable Story Generator",
            tagline="Reading practice that fits any learner in minutes",
            description="An AI-powered software that creates individualized decodable texts. PhonoLogic creates short stories and passages that match the phonics skills a learner is working on. We generate Science of Reading aligned passages that fit each individual learner's interests. Made for Kindergarten-Grade 8 students.",
            target_audience=[
                "K-8 Teachers and reading specialists",
                "Speech-Language Pathologists (SLPs)",
                "Literacy interventionists and tutors",
                "Parents of children with reading difficulties",
                "Students with dyslexia or learning differences",
                "Schools and districts implementing structured literacy"
            ],
            key_features=[
                "AI-generated decodable stories matching phonics scope",
                "Personalized to student interests (e.g., parks, travel, sports)",
                "Fiction and non-fiction text generation",
                "Decodability checks before educator sees content",
                "Aligned to Science of Reading and Orton-Gillingham methodology",
                "Differentiated curriculum and word banks",
                "Grade 1-4 phonics (Jan 2026), K-8 by Sept 2026"
            ],
            value_propositions=[
                "Saves teachers 5-6 hours per week finding appropriate reading materials",
                "Texts match student's current decoding skills, not just grade level",
                "Rooted in social/emotional learning - curiosity, empathy, discovery",
                "Every passage respects scope and sequence teachers are working from"
            ],
            differentiators=[
                "No gamified reward loops - focus on learning",
                "No advertising in product",
                "No student identifying data collection",
                "Research-first approach teachers can trust",
                "Built alongside educators in real classrooms"
            ],
            pricing_model="Freemium with subscription tiers",
            competitors=["Reading A-Z", "Epic!", "Raz-Kids", "Lexia"],
            stage="private_beta"
        )
    ],
    
    team=[
        TeamMember(
            id="stephen",
            name="Stephen Robins",
            email="stephen@phonologic.ca",
            role="CEO & Founder",
            department="Executive",
            bio="After having won numerous awards as a Brewmaster, Stephen decided to pivot and obtained his MBA from IE Business School. PhonoLogic was born out of his desire to build something that helped his wife focus on teaching instead of finding materials.",
            skills=["Business Strategy", "Product Vision", "Fundraising", "Operations"]
        ),
        TeamMember(
            id="joey",
            name="Joey Drury",
            email="joey@phonologic.ca",
            role="CTO",
            department="Technology",
            bio="Digital analytics expert and former Associate Director of Implementation at Cardinal Path. With deep proficiencies in digital marketing, CX, and stakeholder management, Joey ensures that PhonoLogic is technically sound.",
            skills=["Software Engineering", "Digital Analytics", "AI/ML", "Technical Architecture"]
        ),
        TeamMember(
            id="marysia",
            name="Marysia Robins",
            email="marysia@phonologic.ca",
            role="Student Success Teacher",
            department="Education",
            bio="Special education teacher and literacy interventionist with training in Orton-Gillingham. She has spent the past seven years in classrooms leading projects around learning support. Marysia's work has focused on structured literacy and dyslexia support for students with language based learning differences.",
            skills=["Orton-Gillingham", "Special Education", "Literacy Intervention", "Curriculum Design"]
        )
    ],
    
    pitch_info=[
        PitchInfo(
            id="venture-lab-deck",
            name="IE Venture Lab Competition Pitch",
            version="1.0",
            description="Finalist Runner-Up pitch deck for IE Business School Venture Lab Competition, December 2025",
            key_slides=[
                {"1": "Title - Where literacy meets possibility"},
                {"2": "Problem: 1 in 2 students don't read at grade level"},
                {"3": "Solution: AI-generated decodable texts"},
                {"4": "How it works: Scope-aligned stories"},
                {"5": "Market opportunity: EdTech + Structured Literacy"},
                {"6": "Product demo"},
                {"7": "Business model"},
                {"8": "Traction: Pilot schools, teacher testimonials"},
                {"9": "Team"},
                {"10": "Ask and use of funds"}
            ],
            target_investors=["EdTech VCs", "Impact Investors", "Literacy-focused foundations"],
            traction_points=[
                "Finalist Runner-Up at IE Venture Lab Competition Dec 2025",
                "Incubated at TMU Social Ventures Zone",
                "Completed pilot with early adopter school in Toronto",
                "Live in classrooms, iterating directly with teachers",
                "Teacher testimonial: 'Saves me 5-6 hours a week'"
            ],
            pitch_deck_url="https://app.pitch.com/app/presentation/f5ac655d-84e6-432f-bdf0-aa96f2deea3b/fdf5bf0d-1c5b-4a42-ba17-4ea1514d62be"
        )
    ],
    
    marketing_guidelines=[
        MarketingGuideline(
            id="tone-general",
            topic="General Tone of Voice",
            tone_of_voice="Warm, encouraging, and professional. We speak like a trusted friend who happens to be an expert. Brand archetype: The Sage - credible and trustworthy with parents/teachers (maroon), warm and engaging with children (orange).",
            key_messages=[
                "Where literacy meets possibility",
                "Reading practice that fits any learner in minutes",
                "Needed by some, beneficial for all",
                "Finding a text that fits your learner should not be the hard part",
                "Practice makes progress",
                "Building confidence one story at a time"
            ],
            do_not_say=[
                "Cure or fix reading disorders",
                "Replace professional intervention",
                "Guarantee specific outcomes",
                "Use clinical jargon without explanation",
                "Gamified or game-based (we don't do gamification)",
                "AI replaces teachers (we support teachers)"
            ],
            approved_channels=["Instagram", "Facebook", "LinkedIn", "Email", "Blog", "Education Conferences"],
            examples=[
                "PhonoLogic saves me 5-6 hours a week in finding appropriate reading for my students. - Grade 4/5 Reading Specialist",
                "PhonoLogic doesn't just give me time back, it allows me to teach the way I aspire to. - Grade 1 Homeroom Teacher",
                "I wish I had a tool like this when I was practicing. Very practical. - Retired Speech Pathologist"
            ]
        )
    ],
    
    competitors=[
        CompetitorInfo(
            id="reading-az",
            name="Reading A-Z / Raz-Kids",
            website="https://www.readinga-z.com",
            description="Large library of leveled readers and printable books",
            strengths=["Massive content library", "Established in schools", "Leveling system"],
            weaknesses=["Not personalized to student interests", "Generic content", "Not decodable-focused"],
            our_differentiators=["AI personalization", "Scope-aligned decodability", "Student interest matching"],
            pricing="School subscription"
        ),
        CompetitorInfo(
            id="epic",
            name="Epic!",
            website="https://www.getepic.com",
            description="Digital library for kids with 40,000+ books",
            strengths=["Large library", "Engaging UI", "Popular with kids"],
            weaknesses=["Not structured literacy aligned", "Not decodable", "Entertainment-focused"],
            our_differentiators=["Science of Reading aligned", "Decodable texts", "Orton-Gillingham methodology"],
            pricing="Subscription ~$10/month"
        ),
        CompetitorInfo(
            id="lexia",
            name="Lexia Learning",
            website="https://www.lexialearning.com",
            description="Adaptive learning platform for literacy",
            strengths=["Data-driven", "Research-backed", "District adoption"],
            weaknesses=["Expensive", "Heavy gamification", "Less personalized content"],
            our_differentiators=["No gamification", "Teacher-first approach", "Interest-based personalization"],
            pricing="District pricing"
        )
    ],
    
    key_metrics={
        "tam": "$6.2B+ global annual spend on K-8 literacy tools and AI assisted instruction",
        "sam": "~$450M in English-speaking K-5 schools using or moving toward structured literacy (Canada, US, UK, Australia, NZ)",
        "som": "~$15M via 2-3 platform licensing partners embedding PhonoLogic as their structured-literacy engine",
        "target_teachers_north_america": "1.6M K-6 teachers",
        "structured_literacy_adoption": "40% of public school classrooms now use structured literacy or phonics-based frameworks",
        "target_users_year_2": ">10,000 teacher users",
        "target_schools_year_2": ">200 school pilots",
        "target_time_savings": "3+ hours per week per teacher",
        "current_stage": "Private Beta",
        "team_size": 3,
        "funding_round": "$250,000 SAFE",
        "funding_status": "Raising"
    },
    
    pricing={
        "free_tier": {
            "name": "Free",
            "target": "Teachers/Tutors",
            "features": ["Limited generations", "On-screen validator", "Watermark exports"],
            "price": "$0"
        },
        "teacher_pro": {
            "name": "Teacher Pro",
            "target": "Teachers/Tutors/Parents",
            "features": ["Full exports", "Folders", "IEP formats", "No watermarks"],
            "price": "$8-10/month (annual billing)"
        },
        "school": {
            "name": "School",
            "target": "Up to 30 seats",
            "features": ["Shared library", "Pooled seats", "Procurement pack"],
            "price": "$2,500-3,000/year"
        },
        "district": {
            "name": "District",
            "target": "Multi-school",
            "features": ["SSO", "Rostering", "Analytics", "Volume pricing"],
            "price": "Custom (launching Jan 2026)"
        }
    },
    
    pilots=[
        {
            "name": "Montcrest School",
            "location": "Toronto, Canada",
            "educators": 12,
            "students": 20,
            "status": "Active"
        },
        {
            "name": "The Einstein School",
            "location": "Florida, USA",
            "status": "Planned"
        },
        {
            "name": "Multi-school Cohort",
            "schools": "4-5 schools",
            "students": 100,
            "launch": "November 2025",
            "status": "Launched"
        }
    ],
    
    milestones=[
        {"date": "Dec 2025", "deliverable": "Validate Scopes VI-VIII in classrooms; expand wordbank to >5,000 entries", "status": "completed"},
        {"date": "Dec 2025", "deliverable": "Deliver 100+ exemplar stories with evidence scorecards", "status": "completed"},
        {"date": "Jan 2026", "deliverable": "Ship SSO/rostering and district analytics (Enterprise Readiness)", "status": "in_progress"},
        {"date": "Jan 28, 2026", "deliverable": "Private Beta Launch", "status": "upcoming"},
        {"date": "Mar 1, 2026", "deliverable": "Public Beta Launch", "status": "upcoming"},
        {"date": "May 15, 2026", "deliverable": "Public Launch", "status": "upcoming"},
        {"date": "Sept 2026", "deliverable": "Full K-8 phonics coverage, District licensing ready", "status": "upcoming"}
    ],
    
    product_metrics_targets={
        "prep_time_saved": "~45 minutes per lesson",
        "validator_pass_rate": "95%",
        "first_read_success": "≥70% (no adult decoding beyond prompts)",
        "weekly_active_teachers": "≥60%",
        "pilot_to_paid_conversion": "60%",
        "free_to_pro_conversion": "5-10%",
        "teacher_churn": "15%",
        "school_churn": "10%",
        "inference_cost": "<2¢ per passage",
        "gross_margin_teacher": "~76%",
        "gross_margin_school": "~71%"
    },
    
    problem_statement="Roughly half of students aren't reading at grade level by the end of primary school. For around a third of students, the issue isn't effort or behavior but the system itself, which was never built around how humans decode. Teachers spend hours hunting for or rewriting texts, or use generic AI tools that silently violate structured-literacy rules. The result is students stall, teachers burn out, and billions spent on literacy materials don't translate into appropriately scaffolded texts.",
    
    solution_statement="PhonoLogic is an AI-powered structured literacy engine that turns phonics awareness into hard rules for text generation. A teacher picks a phonics focus, a topic, and a length, and PhonoLogic produces fully decodable, personalized texts. A built-in validator layer blocks off-scope or non-decodable words before they ever reach a child. For teachers, it's simple: prompt → print → teach with confidence.",
    
    moat=[
        "Fidelity: Every passage matches the exact phonics scope being taught—no unaligned or unknown words",
        "Explainability: The validator returns clear, plain-language rationales that accelerate teacher learning",
        "Embeddability: Modular design integrates into existing EdTech platforms, curriculum ecosystems, or SaaS tools"
    ],
    
    strategic_partners_targets=["McGraw Hill", "Newsela", "Toddle", "Microsoft Education"],
    
    incubators_awards=[
        "Incubated at Toronto Metropolitan University's Social Ventures Zone",
        "Finalist Runner-Up at IE Business School Venture Lab Competition, December 2025"
    ],
    
    recent_updates=[
        "Private Beta launching January 28, 2026",
        "Completed pilot with Montcrest School, Toronto",
        "Finalist Runner-Up at IE Venture Lab Competition Dec 2025",
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
    - Persistence via JSON file
    """
    
    def __init__(
        self,
        storage_path: str = "brain.json",
        initial_knowledge: Optional[CompanyKnowledge] = None
    ):
        self.storage_path = Path(storage_path)
        self.knowledge = initial_knowledge or DEFAULT_KNOWLEDGE
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage with default knowledge if empty"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    stored = json.load(f)
                    if stored and "knowledge" in stored:
                        self.knowledge = CompanyKnowledge.model_validate(stored["knowledge"])
        except Exception:
            self._save()
    
    def _save(self):
        """Persist knowledge to JSON file"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump({
                    "id": "company_knowledge",
                    "knowledge": self.knowledge.model_dump(),
                    "updated_at": datetime.utcnow().isoformat()
                }, f, indent=2, default=str)
        except Exception:
            pass
    
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
