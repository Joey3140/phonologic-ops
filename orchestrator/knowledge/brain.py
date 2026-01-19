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
            "target": "Teachers/Parents",
            "features": ["Limited generations", "On-screen validator", "Watermark exports"],
            "price": "$0"
        },
        "parent_plan": {
            "name": "Parent Plan",
            "target": "Parents/Families",
            "features": ["Full exports", "300 stories/month soft limit", "Purchase additional stories as needed", "No watermarks"],
            "price_annual": "$20/month (billed annually)",
            "price_monthly": "$25/month",
            "story_limit": "300/month soft limit (can purchase more)"
        },
        "teacher_pro": {
            "name": "Teacher Pro",
            "target": "Teachers",
            "features": ["Full exports", "Folders", "IEP formats", "No watermarks"],
            "price": "TBD - not yet finalized",
            "status": "Coming soon"
        },
        "school": {
            "name": "School License",
            "target": "Schools",
            "price": "TBD - not yet finalized",
            "status": "Coming soon"
        },
        "district": {
            "name": "District License",
            "target": "Districts",
            "price": "TBD - not yet finalized",
            "status": "Coming soon"
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
        {"date": "May 2026", "deliverable": "Vancouver Web Summit - Featured Startup (Public Launch centered around this event)", "status": "upcoming"},
        {"date": "May 15, 2026", "deliverable": "Public Launch", "status": "upcoming"},
        {"date": "Sept 2026", "deliverable": "Full K-8 phonics coverage, District licensing ready", "status": "upcoming"}
    ],
    
    events=[
        {
            "name": "Vancouver Web Summit",
            "date": "May 2026",
            "location": "Vancouver, Canada",
            "status": "Featured Startup",
            "significance": "Public launch will be centered around this event",
            "goals": ["Major press coverage", "Investor meetings", "Partnership announcements", "User acquisition push"]
        }
    ],
    
    # Product Architecture Components
    product_components={
        "generator": {
            "name": "Generator",
            "description": "Uses a rules-based logic engine to create decodable passages aligned to the selected phonics scope, with customizable tone and length",
            "key_features": ["Scope-aligned text generation", "Customizable tone via narrator settings", "Adjustable length", "Fiction and non-fiction support"]
        },
        "validator": {
            "name": "Validator",
            "description": "Checks each passage against predefined phonological rules and returns pass/fail outcomes with concise rationales",
            "key_features": ["Phoneme rule checking", "Suffix validation", "Scope control", "Plain-language rationales for teachers"]
        },
        "teacher_console": {
            "name": "Teacher Console",
            "description": "Displays key metrics (generation counts, validator outcomes, first-read success) while remaining lightweight and privacy compliant",
            "key_features": ["Usage metrics dashboard", "Validator outcomes tracking", "First-read success monitoring", "Privacy-first design"]
        }
    },
    
    # Go-to-Market Strategy Phases
    go_to_market={
        "phase_1": {
            "name": "Teacher-Led Entry",
            "focus": "Bottom-up adoption with freemium teacher tier",
            "strategy": [
                "Launch freemium tier for teachers to generate decodable stories, word banks, and nonfiction passages within Scopes 1-8",
                "Establish daily classroom utility and promote organic word-of-mouth growth",
                "Invite consistent users to upgrade to PhonoLogic Pro (Scopes 9-14, TSV exports, emotional tone control)",
                "Use early pilots (Montcrest School, The Einstein School) to generate anchor data for investors"
            ],
            "kpis": ["Daily active teachers", "Word-of-mouth referrals", "Hours saved per teacher"]
        },
        "phase_2": {
            "name": "District & Institutional Adoption",
            "focus": "Shift toward district-level licensing after teacher traction validated",
            "strategy": [
                "Leverage early data and testimonials for site-wide adoption agreements",
                "Target states implementing Science of Reading mandates or literacy reform funding",
                "Focus on interoperability with existing LMS and IEP reporting systems",
                "Pricing: USD $2,000-5,000 per school per year"
            ],
            "kpis": ["School pilots", "District contracts", "Compliance data exports"]
        },
        "phase_3": {
            "name": "Platform Integration & Strategic Partnerships",
            "focus": "Integration and acquisition pathways with major curriculum publishers",
            "strategy": [
                "Position validator/generator as plug-in fidelity layer for existing EdTech ecosystems",
                "Turn unsafe generative AI tools into scope-locked, Science of Reading compliant systems",
                "Target partners: McGraw Hill, Newsela, Toddle, Microsoft Education"
            ],
            "kpis": ["Partner integrations", "API usage", "Enterprise contracts"]
        }
    },
    
    # Capital Ask & Use of Funds
    capital_ask={
        "amount": "$250,000",
        "instrument": "SAFE",
        "status": "Raising",
        "timeline": "Complete by January 2026",
        "use_of_funds": {
            "salaries": {"amount": "$100,000", "purpose": "Engineering, pedagogy, pilot management"},
            "product_infrastructure": {"amount": "$50,000", "purpose": "Finalize full product launch"},
            "legal_compliance": {"amount": "$50,000", "purpose": "DPAs, FERPA/PIPEDA certification"},
            "ai_training_data": {"amount": "$25,000", "purpose": "Improve generator accuracy"},
            "go_to_market": {"amount": "$25,000", "purpose": "Sales enablement, school pilots"}
        },
        "expected_outcomes": [
            "Validated system across 25+ classrooms, 50 educators, and 120 students",
            ">10,000 teacher users by Year 2",
            ">200 school pilots by Year 2",
            "Validated classroom time savings exceeding 3 hours per week"
        ]
    },
    
    # Unit Economics
    unit_economics={
        "teacher_pro": {
            "annual_revenue": "$100",
            "inference_cost_per_year": "$16",
            "support_infrastructure": "$8",
            "gross_margin": "~76%"
        },
        "school_license": {
            "seats": 30,
            "annual_revenue": "$2,700",
            "inference_cost": "$480",
            "support_infrastructure": "$300",
            "gross_margin": "~71%"
        },
        "key_assumptions": {
            "passages_per_teacher_per_year": "~800",
            "pilot_to_paid_conversion": "60%",
            "free_to_pro_conversion": "5-10%",
            "teacher_churn": "15%",
            "school_churn": "10%",
            "inference_cost_per_passage": "<2¢"
        }
    },
    
    # Market Analysis
    market_analysis={
        "tam": {
            "description": "Global annual spend on K-8 literacy tools and AI-assisted instruction",
            "value": "$6.2B+"
        },
        "sam": {
            "description": "English-speaking K-5 schools using or moving toward structured literacy (Canada, US, UK, Australia, NZ)",
            "value": "~$450M"
        },
        "som": {
            "description": "2-3 platform licensing partners embedding PhonoLogic as their structured-literacy engine",
            "value": "~$15M"
        },
        "market_drivers": [
            "1.6M K-6 teachers in North America",
            "40% of public school classrooms now use structured literacy or phonics-based frameworks",
            "Rapid expansion of structured literacy mandates (U.S., Canada, U.K., NZ)",
            "Growing demand for AI tools that are transparent, aligned, and privacy-safe"
        ],
        "competitive_gap": "Platforms like Reading Eggs deliver engagement but introduce advanced spelling patterns too early. UFLI Foundations is research-based but limited to static materials. Lexia Core5 has impressive reach but lacks true decodable text generation. ChatGPT/MagicSchool AI can produce infinite text but lack phoneme, suffix, and scope control."
    },
    
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
        "Finalist Runner-Up at IE Business School Venture Lab Competition, December 2025",
        "Featured Startup at Vancouver Web Summit, May 2026"
    ],
    
    # Customer Personas
    personas=[
        {
            "id": "parent-persona",
            "name": "Parent Persona",
            "title": "The Concerned Parent",
            "description": "Parent of a child struggling with reading, looking for ways to support their child's literacy development at home",
            "demographics": {
                "age_range": "30-45",
                "education": "College educated",
                "income": "Middle to upper-middle class",
                "location": "Suburban/urban North America"
            },
            "pain_points": [
                "Child is falling behind in reading at school",
                "Doesn't know how to help without making it worse",
                "Frustrated by generic reading apps that don't match what's being taught",
                "Worried about screen time but needs digital tools",
                "Feels overwhelmed by educational jargon"
            ],
            "goals": [
                "Help child catch up to grade level",
                "Make reading practice enjoyable, not a battle",
                "Feel confident they're doing the right thing",
                "See measurable progress"
            ],
            "motivations": [
                "Child's success and confidence",
                "Reducing homework stress",
                "Teacher recommended structured literacy"
            ],
            "objections": [
                "Is this actually aligned to what my child is learning?",
                "Will my child find this engaging?",
                "Is $20/month worth it?",
                "Is my child's data safe?"
            ],
            "messaging_approach": "Warm, reassuring, parent-to-parent tone. Emphasize that this is built by educators, not just tech people. Focus on confidence building and progress visibility.",
            "status": "Active"
        },
        {
            "id": "teacher-persona",
            "name": "Teacher Persona",
            "title": "TBD - Pending",
            "description": "Persona for K-4 teachers and reading specialists",
            "status": "Pending development"
        },
        {
            "id": "tutor-persona",
            "name": "Tutor/SLP Persona",
            "title": "TBD - Pending",
            "description": "Persona for private tutors and speech-language pathologists",
            "status": "Pending development"
        }
    ],
    
    # Operations Portal Links (ops.phonologic.cloud)
    ops_portal={
        "url": "https://ops.phonologic.cloud",
        "google_drive_folders": {
            "main": {"name": "PhonoLogic (Main)", "url": "https://drive.google.com/drive/folders/0AEgmJV2IpqOhUk9PVA"},
            "operations": {"name": "001: Operations", "url": "https://drive.google.com/drive/folders/14-pITXL-iJT-1h6Gb-RCp4yGEQ5GHc4Z"},
            "sales_outreach": {"name": "002: Sales & Outreach", "url": "https://drive.google.com/drive/folders/1I2pkpPYf6H9Ur26Uifyfhgmq8nqlbTnw"},
            "developer": {"name": "003: Developer", "url": "https://drive.google.com/drive/folders/1ALiBrIJSw5Xx5NS18oO0aN7j1fVB8jhC"},
            "marketing_feedback": {"name": "004: Marketing & Feedback", "url": "https://drive.google.com/drive/folders/1Qls5x8RlaEfyjLqH-rQ9fN6byRfCKWRC"},
            "fundraising": {"name": "005: Fundraising", "url": "https://drive.google.com/drive/folders/1PuXZ1KxsNvOoafr8FxctqCLr6wSywD4y"},
            "crewai_inputs": {"name": "006: CrewAI Inputs", "url": "https://drive.google.com/drive/folders/1UiP9DljA1NeZABrvsBR1NMlsPick34xV"},
            "archived": {"name": "009: Archived", "url": "https://drive.google.com/drive/folders/1YvqOr0Ns3ecgY1oLMl2Ry4MSW1Vu1QPw"}
        },
        "pitch_decks": {
            "google_accelerator": {"name": "Google Accelerator Pitch Deck", "url": "https://app.pitch.com/app/presentation/f5ac655d-84e6-432f-bdf0-aa96f2deea3b/fdf5bf0d-1c5b-4a42-ba17-4ea1514d62be/d0b9f7cc-86c8-4d22-aaac-e175bc8a36a9"},
            "branding_kit": {"name": "PhonoLogic Branding Kit", "url": "https://app.pitch.com/app/presentation/f5ac655d-84e6-432f-bdf0-aa96f2deea3b/d93a032e-cdc6-412b-94a4-8b6acf0cbb40/8f529e23-7455-4ed7-82c0-c4bd049ff90c"}
        },
        "dashboards": {
            "looker_studio": {"name": "Looker Studio Dashboard", "url": "https://lookerstudio.google.com/reporting/b0e96076-597e-429d-bb09-229354c85aee"}
        },
        "tools": {
            "clickup": "https://app.clickup.com",
            "github": "https://github.com/phonologic",
            "vercel": "https://vercel.com",
            "figma": "https://www.figma.com",
            "google_cloud": "https://console.cloud.google.com"
        }
    },
    
    # Social Media & External Profiles (GAPS - need to be filled)
    social_media={
        "linkedin_company": "TBD - need company LinkedIn URL",
        "instagram": "TBD - need Instagram handle",
        "twitter": "TBD - need Twitter/X handle",
        "facebook": "TBD - need Facebook page URL",
        "crunchbase": "TBD - need Crunchbase company profile URL",
        "youtube": "TBD - if applicable"
    },
    
    # Testimonials (from phonologic.ca)
    testimonials=[
        {
            "quote": "PhonoLogic saves me 5-6 hours a week in finding appropriate reading for my students.",
            "attribution": "Grade 4/5 Reading Specialist",
            "rating": 5,
            "source": "phonologic.ca"
        },
        {
            "quote": "PhonoLogic doesn't just give me time back, it allows me to teach the way I aspire to.",
            "attribution": "Grade 1 Homeroom Teacher",
            "rating": 5,
            "source": "phonologic.ca"
        },
        {
            "quote": "I wish I had a tool like this when I was practicing. Very practical.",
            "attribution": "Retired Speech Pathologist",
            "rating": 5,
            "source": "phonologic.ca"
        }
    ],
    
    recent_updates=[
        "Private Beta launching January 28, 2026",
        "Completed pilot with Montcrest School, Toronto",
        "Finalist Runner-Up at IE Venture Lab Competition Dec 2025",
        "Launched Operations Portal at ops.phonologic.cloud",
        "Building Agentic AI orchestrator for automation"
    ],
    
    # Website Content (from phonologic.ca)
    website_content={
        "how_it_works": {
            "url": "https://www.phonologic.ca/how-phonologic-works/",
            "summary": "PhonoLogic is an AI powered software that creates individualised texts. Every passage is checked against our decodability rules before an educator sees it.",
            "text_types": [
                "Fiction and non-fictional immersive stories",
                "Differentiated/decodable curriculum",
                "Word banks",
                "General phonics practice"
            ],
            "scope_coverage": {
                "pilot_1": "Scopes typically taught from early Grade 2 until middle of Grade 3",
                "pilot_2": "Grade 1-4 phonic concepts (January 2026)",
                "full_release": "Kindergarten-Grade 8 phonics (September 2026)"
            },
            "example": "Story for Maria, a grade 5 student reading at grade 3 level who likes parks and recently visited Madrid with her family. Working on vowel teams: oa/oe, ue/ui, oo, ou/ow, and igh."
        },
        "faq": {
            "url": "https://www.phonologic.ca/faq/",
            "questions": [
                {
                    "q": "Is PhonoLogic just for struggling readers?",
                    "a": "No. All students benefit from decodable, scope aligned texts. PhonoLogic is designed for whole classrooms using structured literacy, with an extra layer of protection for students with dyslexia, learning differences, or those working below or above grade level."
                },
                {
                    "q": "Who uses PhonoLogic?",
                    "a": "K-8 classroom teachers, Reading interventionists and SPED teams, Tutors and specialists, Homeschooling parents. We can also partner with school districts and boards."
                },
                {
                    "q": "Will I need training?",
                    "a": "PhonoLogic is designed to fit into existing classroom and home practice, not replace it. Most users can choose a phonics scope, pick a text type, and generate their first passage in their very first session. Onboarding is simple and intuitive. We fit into the lives of teachers, not the other way round."
                },
                {
                    "q": "What about student data and privacy?",
                    "a": "PhonoLogic is a teacher, parent, and tutor facing tool and does not require student logins. We do not collect student-identifying data, run ads, or sell data to third parties."
                },
                {
                    "q": "Can it be integrated into my school's platform?",
                    "a": "Yes. We support integrations for districts and partners."
                },
                {
                    "q": "Is this only available in English?",
                    "a": "For now, yes. We are piloting in English and looking to expand to Spanish, French, and Portuguese next."
                }
            ],
            "contact_email": "phonologic.mvp@gmail.com"
        },
        "philosophy": {
            "url": "https://www.phonologic.ca/our-philosophy/",
            "core_belief": "At PhonoLogic we believe that reading is a fundamental life skill and that the adults supporting it deserve tools that make good practice easier to deliver consistently.",
            "quote": "Literacy is a bridge from misery to hope. It is a tool for daily life in modern society.",
            "what_we_believe": [
                "Reading is not a talent but a learned skill that quietly shapes almost everything else a child can do",
                "When literacy works it provides invisible infrastructure that scaffolds success beyond school",
                "It's about being able to fill out a form, read a contract, understand medication instructions, follow a news story, and spot when information is misleading"
            ],
            "literacy_enables": [
                "Access knowledge beyond what's spoken in the room",
                "Participate in their communities",
                "Protect themselves against misinformation and exploitation",
                "Imagine futures different from the one they were born into"
            ],
            "who_we_serve": "There are many reasons why children have difficulty reading - dyslexia, lack of access to educational materials, patchy instruction, misaligned texts. No matter the background, language, or learning profile, every child deserves explicit, systematic instruction in how written language works.",
            "every_child_deserves": [
                "Explicit, systematic instruction in how written language works",
                "Texts that match their current decoding skills, not just their grade level",
                "Time to practise without being punished for needing that time",
                "Adults who see their struggle as a signal, not a character flaw"
            ],
            "how_we_do_it": "We root our stories in social/emotional learning, creating texts that foster curiosity, empathy, and discovery. Every passage respects the scope and sequence teachers are working from. A balance of structure and wonder is seen in every text generated."
        },
        "who_we_are": {
            "url": "https://www.phonologic.ca/who-we-are/",
            "origin_story": "PhonoLogic was developed to solve a problem our founding team knew firsthand: creating reading practice that truly fits a learner takes too much time to do consistently. This pain point was the spark and the opportunity to make structured literacy easier to deliver consistently for educators and families.",
            "team_composition": "Our team is comprised of a business strategist, a software developer, and a literacy specialist. Together we combine literacy expertise, product strategy, and software structure engineering.",
            "goal": "Our goal is to help teachers, tutors, and families participate in a practice that supports progress and empowerment instead of guesswork, building confidence one story at a time."
        }
    },
    
    # Technical Product Details (from company wiki)
    technical_details={
        "ops_portal_stack": {
            "frontend": "Vanilla JS SPA",
            "hosting": "Vercel",
            "styling": "Modern responsive HTML/CSS"
        },
        "backend_stack": {
            "api": "Vercel Serverless Functions",
            "database": "Upstash Redis",
            "auth": "Google OAuth (@phonologic.ca only)"
        },
        "orchestrator_stack": {
            "framework": "FastAPI (Python)",
            "ai_framework": "Agno (formerly Phidata)",
            "llm_provider": "Claude (Anthropic)",
            "hosting": "Railway"
        },
        "infrastructure": {
            "domains": {
                "phonologic.ca": "Marketing website",
                "phonologic.cloud": "Main application",
                "ops.phonologic.cloud": "Operations portal",
                "dev.phonologic.cloud": "Development/staging"
            },
            "services": ["Vercel", "Railway", "Upstash", "Google Cloud", "Hover"]
        },
        "agent_teams": {
            "marketing_fleet": {
                "purpose": "Campaign strategy, market research, creative direction",
                "agents": ["Researcher", "TechnicalConsultant", "BrandLead", "ImageryArchitect"],
                "output": "Marketing strategies, Midjourney prompts"
            },
            "project_ops": {
                "purpose": "Task automation, document generation, communications",
                "agents": ["Coordinator", "TaskManager", "DocumentManager", "Communicator"],
                "integrations": ["ClickUp", "Google Drive", "SendGrid"]
            },
            "browser_navigator": {
                "purpose": "Browser automation, slide/canvas analysis",
                "agents": ["BrowserNavigator"],
                "uses": "Playwright for browser control"
            },
            "brain_curator": {
                "purpose": "Knowledge management for Stephen",
                "features": ["Conflict detection", "Natural language input", "Misconception correction", "Query existing knowledge"]
            }
        },
        "security": {
            "auth_provider": "Google OAuth 2.0",
            "domain_restriction": "@phonologic.ca only",
            "session_storage": "JWT tokens in HTTP-only cookies",
            "rate_limits": {
                "default": "60 requests/minute",
                "write_operations": "20 requests/minute",
                "authentication": "10 requests/minute"
            },
            "admins": ["joey@phonologic.ca", "stephen@phonologic.ca"]
        }
    },
    
    # Company Wiki Structure (synced with ops.phonologic.cloud/wiki)
    wiki_structure={
        "url": "https://ops.phonologic.cloud (Wiki tab)",
        "categories": {
            "getting-started": {
                "name": "Getting Started",
                "description": "Onboarding, company overview, tools access",
                "pages": ["Company Overview", "Team Directory", "Tools & Access Guide"]
            },
            "development": {
                "name": "Development",
                "description": "Tech stack, deployment, architecture, security",
                "pages": ["Technology Stack", "Deployment Workflow", "System Architecture", "Security Architecture"]
            },
            "product": {
                "name": "Product",
                "description": "Product info, features, pricing, roadmap, competitors",
                "pages": ["Product Overview", "Pricing Structure", "Product Roadmap", "Competitive Landscape"]
            },
            "operations": {
                "name": "Operations",
                "description": "Processes, workflows, team operations, brand",
                "pages": ["Pilots & Traction", "Communication Guidelines", "AI Hub & Orchestrator", "Brand Guidelines"]
            },
            "analytics": {
                "name": "Analytics",
                "description": "Metrics, KPIs, dashboards",
                "pages": ["Metrics & KPIs"]
            },
            "policies": {
                "name": "Policies",
                "description": "Security, guidelines, compliance, investor info",
                "pages": ["Data & Privacy Policy", "Expense Policy", "Investor Materials"]
            }
        },
        "total_pages": 16,
        "last_synced": "2026-01-18"
    }
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
        Query the knowledge base - searches ALL data intelligently.
        
        Args:
            query: Search query string
            categories: Optional filter by knowledge categories
            max_results: Maximum results to return
        
        Returns:
            List of knowledge results
        """
        results = []
        query_lower = query.lower()
        
        # Search ALL knowledge fields comprehensively
        results.extend(self._search_all_fields(query_lower))
        
        # Also search specific categories if needed
        target_categories = categories or list(KnowledgeCategory)
        for category in target_categories:
            category_results = self._search_category(category, query_lower)
            results.extend(category_results)
        
        # Deduplicate by source
        seen_sources = set()
        unique_results = []
        for r in results:
            if r.source not in seen_sources:
                seen_sources.add(r.source)
                unique_results.append(r)
        
        unique_results.sort(key=lambda x: x.confidence, reverse=True)
        return unique_results[:max_results]
    
    def _search_all_fields(self, query: str) -> List[KnowledgeResult]:
        """Search across ALL knowledge fields - timeline, milestones, events, pricing, etc."""
        results = []
        
        # Launch Timeline
        timeline_text = str(self.knowledge.launch_timeline)
        score = self._calculate_relevance(query, [timeline_text])
        if score > 0.1 or any(word in query for word in ['timeline', 'launch', 'beta', 'release', 'date', 'when', 'schedule']):
            results.append(KnowledgeResult(
                query=query,
                results=[self.knowledge.launch_timeline],
                category=KnowledgeCategory.OPERATIONS,
                confidence=max(score, 0.7) if any(word in query for word in ['timeline', 'launch', 'beta']) else score,
                source="launch_timeline"
            ))
        
        # Milestones
        milestones_text = " ".join([str(m) for m in self.knowledge.milestones])
        score = self._calculate_relevance(query, [milestones_text])
        if score > 0.1 or any(word in query for word in ['milestone', 'roadmap', 'deliverable', 'progress', 'timeline', 'market']):
            results.append(KnowledgeResult(
                query=query,
                results=self.knowledge.milestones,
                category=KnowledgeCategory.OPERATIONS,
                confidence=max(score, 0.6) if any(word in query for word in ['milestone', 'roadmap', 'market']) else score,
                source="milestones"
            ))
        
        # Events (Vancouver Web Summit, etc.)
        events_text = " ".join([str(e) for e in self.knowledge.events])
        score = self._calculate_relevance(query, [events_text])
        if score > 0.1 or any(word in query for word in ['event', 'summit', 'conference', 'vancouver', 'launch']):
            results.append(KnowledgeResult(
                query=query,
                results=self.knowledge.events,
                category=KnowledgeCategory.OPERATIONS,
                confidence=max(score, 0.7) if 'vancouver' in query or 'summit' in query else score,
                source="events"
            ))
        
        # Pricing
        pricing_text = str(self.knowledge.pricing)
        score = self._calculate_relevance(query, [pricing_text])
        if score > 0.1 or any(word in query for word in ['price', 'cost', 'pricing', 'tier', 'plan', 'subscription']):
            results.append(KnowledgeResult(
                query=query,
                results=[self.knowledge.pricing],
                category=KnowledgeCategory.PRODUCT,
                confidence=max(score, 0.8) if any(word in query for word in ['price', 'cost', 'pricing']) else score,
                source="pricing"
            ))
        
        # Pilots
        pilots_text = " ".join([str(p) for p in self.knowledge.pilots])
        score = self._calculate_relevance(query, [pilots_text])
        if score > 0.1 or any(word in query for word in ['pilot', 'traction', 'school', 'montcrest', 'customer']):
            results.append(KnowledgeResult(
                query=query,
                results=self.knowledge.pilots,
                category=KnowledgeCategory.OPERATIONS,
                confidence=max(score, 0.7) if 'pilot' in query or 'traction' in query else score,
                source="pilots"
            ))
        
        # Key Metrics
        metrics_text = str(self.knowledge.key_metrics)
        score = self._calculate_relevance(query, [metrics_text])
        if score > 0.1 or any(word in query for word in ['metric', 'kpi', 'target', 'goal', 'funding', 'raise']):
            results.append(KnowledgeResult(
                query=query,
                results=[self.knowledge.key_metrics],
                category=KnowledgeCategory.OPERATIONS,
                confidence=max(score, 0.6) if any(word in query for word in ['metric', 'funding']) else score,
                source="key_metrics"
            ))
        
        # Company Info (mission, vision, tagline)
        company_text = f"{self.knowledge.company_name} {self.knowledge.tagline} {self.knowledge.mission} {self.knowledge.vision}"
        score = self._calculate_relevance(query, [company_text])
        if score > 0.1 or any(word in query for word in ['mission', 'vision', 'about', 'company', 'what do']):
            results.append(KnowledgeResult(
                query=query,
                results=[{
                    "company_name": self.knowledge.company_name,
                    "tagline": self.knowledge.tagline,
                    "mission": self.knowledge.mission,
                    "vision": self.knowledge.vision,
                    "founded_year": self.knowledge.founded_year,
                    "headquarters": self.knowledge.headquarters
                }],
                category=KnowledgeCategory.BRAND,
                confidence=max(score, 0.6),
                source="company_info"
            ))
        
        # Recent Updates
        updates_text = " ".join(self.knowledge.recent_updates)
        score = self._calculate_relevance(query, [updates_text])
        if score > 0.1 or any(word in query for word in ['update', 'recent', 'news', 'latest', 'new']):
            results.append(KnowledgeResult(
                query=query,
                results=[{"update": u} for u in self.knowledge.recent_updates],
                category=KnowledgeCategory.OPERATIONS,
                confidence=max(score, 0.5),
                source="recent_updates"
            ))
        
        # Incubators/Awards
        awards_text = " ".join(self.knowledge.incubators_awards)
        score = self._calculate_relevance(query, [awards_text])
        if score > 0.1 or any(word in query for word in ['award', 'incubator', 'recognition', 'competition', 'tmu', 'ie']):
            results.append(KnowledgeResult(
                query=query,
                results=[{"award": a} for a in self.knowledge.incubators_awards],
                category=KnowledgeCategory.PITCH,
                confidence=max(score, 0.6),
                source="incubators_awards"
            ))
        
        return results
    
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
