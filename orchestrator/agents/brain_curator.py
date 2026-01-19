"""
BrainCurator Agent - Intelligent Knowledge Gatekeeper for Stephen

Handles:
- Natural language knowledge contributions
- Conflict detection against existing brain
- Feedback when misconceptions are detected
- Staging queue for review before merge
- Source tracking (who added what, when)
"""
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.anthropic import Claude

from knowledge.brain import PhonoLogicsBrain, DEFAULT_KNOWLEDGE
from knowledge.schemas import KnowledgeCategory
from config import settings
from lib.redis_client import get_redis


# ============================================================================
# SCHEMAS
# ============================================================================

class ConflictInfo(BaseModel):
    """Represents a conflict between new and existing information"""
    field_path: str = Field(description="Path to the conflicting field in brain")
    existing_value: Any = Field(description="Current value in the brain")
    proposed_value: Any = Field(description="Value Stephen is trying to add")
    conflict_type: Literal["update", "contradiction", "duplicate"] = Field(
        description="Type of conflict detected"
    )
    confidence: float = Field(ge=0, le=1, description="How confident we are this is a conflict")


class PendingContribution(BaseModel):
    """A contribution waiting to be reviewed/merged"""
    id: str
    contributor: str = "stephen@phonologic.ca"
    raw_input: str = Field(description="Original text Stephen provided")
    parsed_category: Optional[KnowledgeCategory] = None
    parsed_content: Dict[str, Any] = Field(default_factory=dict)
    conflicts: List[ConflictInfo] = Field(default_factory=list)
    status: Literal["pending", "approved", "rejected", "needs_clarification"] = "pending"
    curator_response: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class CurationResult(BaseModel):
    """Result of processing a contribution"""
    accepted: bool
    message: str = Field(description="Friendly message to Stephen")
    conflicts_found: List[ConflictInfo] = Field(default_factory=list)
    clarification_needed: bool = False
    suggestion: Optional[str] = None
    contribution_id: Optional[str] = None


# ============================================================================
# BRAIN CURATOR CLASS
# ============================================================================

class BrainCurator:
    """
    Intelligent gatekeeper for knowledge contributions.
    
    Stephen can dump thoughts naturally, and this system:
    1. Parses intent and extracts structured info
    2. Checks for conflicts with existing brain
    3. Provides feedback if misconceptions detected
    4. Stages changes for review before merge
    """
    
    def __init__(self, brain: Optional[PhonoLogicsBrain] = None):
        self.brain = brain or PhonoLogicsBrain()
        self.redis = get_redis()
        self.pending_queue: List[PendingContribution] = []
        self._load_pending()
        self._load_brain_updates()  # Apply any persisted updates to brain
    
    def _load_pending(self):
        """Load pending contributions from Redis"""
        if not self.redis.available:
            print("[BRAIN CURATOR] Redis not available, skipping pending load")
            return
        
        try:
            pending_list = self.redis.list_pending()
            for p in pending_list:
                try:
                    # Handle datetime fields that might be strings
                    if 'created_at' in p and isinstance(p['created_at'], str):
                        p['created_at'] = datetime.fromisoformat(p['created_at'].replace('Z', '+00:00'))
                    if 'resolved_at' in p and isinstance(p['resolved_at'], str):
                        p['resolved_at'] = datetime.fromisoformat(p['resolved_at'].replace('Z', '+00:00'))
                    self.pending_queue.append(PendingContribution(**p))
                except Exception as item_error:
                    print(f"[BRAIN CURATOR] Skipping invalid pending item: {item_error}")
            print(f"[BRAIN CURATOR] Loaded {len(self.pending_queue)} pending contributions")
        except Exception as e:
            print(f"[BRAIN CURATOR] Error loading pending: {e}")
    
    def _save_pending(self, contribution: PendingContribution):
        """Save a pending contribution to Redis"""
        if not self.redis.available:
            print("[BRAIN CURATOR] Warning: Redis unavailable, contribution not persisted")
            return
        
        try:
            self.redis.save_pending(
                contribution.id,
                contribution.model_dump()
            )
            print(f"[BRAIN CURATOR] Saved contribution {contribution.id}")
        except Exception as e:
            print(f"[BRAIN CURATOR] Error saving pending: {e}")
    
    def _load_brain_updates(self):
        """
        Load and apply persisted brain knowledge updates.
        
        These are user-contributed updates stored in Redis that override DEFAULT_KNOWLEDGE.
        """
        if not self.redis.available:
            return
        
        try:
            updates = self.redis.get_brain_updates()
            if updates:
                print(f"[BRAIN CURATOR] Applying {len(updates)} brain updates from Redis")
                for key, update in updates.items():
                    self._apply_brain_update(update)
        except Exception as e:
            print(f"[BRAIN CURATOR] Error loading brain updates: {e}")
    
    def _apply_brain_update(self, update: Dict[str, Any]):
        """Apply a single brain update to the knowledge base"""
        category = update.get('category')
        key = update.get('key')
        value = update.get('value')
        
        if not all([category, key, value]):
            return
        
        # Apply update to brain knowledge
        knowledge = self.brain.knowledge
        
        if category == 'pricing' and hasattr(knowledge, 'pricing'):
            if isinstance(knowledge.pricing, dict):
                knowledge.pricing[key] = value
        elif category == 'milestones' and hasattr(knowledge, 'milestones'):
            # Add or update milestone
            knowledge.milestones.append(value) if isinstance(value, dict) else None
        elif category == 'recent_updates' and hasattr(knowledge, 'recent_updates'):
            if value not in knowledge.recent_updates:
                knowledge.recent_updates.insert(0, value)
        elif category == 'key_metrics' and hasattr(knowledge, 'key_metrics'):
            if isinstance(knowledge.key_metrics, dict):
                knowledge.key_metrics[key] = value
        
        print(f"[BRAIN CURATOR] Applied update: {category}/{key}")
    
    def _generate_id(self) -> str:
        """Generate unique contribution ID"""
        import uuid
        return f"contrib_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    # ========================================================================
    # CONFLICT DETECTION
    # ========================================================================
    
    def _check_pricing_conflicts(self, text: str) -> List[ConflictInfo]:
        """Check for pricing-related conflicts"""
        conflicts = []
        text_lower = text.lower()
        
        # Look for dollar amounts
        import re
        prices = re.findall(r'\$(\d+(?:\.\d{2})?)', text)
        
        if prices and any(word in text_lower for word in ['price', 'cost', 'month', 'subscription', 'plan']):
            current_pricing = self.brain.knowledge.pricing
            
            for price in prices:
                price_float = float(price)
                
                # Check against parent plan
                parent_plan = current_pricing.get('parent_plan', {})
                if 'parent' in text_lower or 'plan' in text_lower:
                    annual_price = parent_plan.get('price_annual', '')
                    monthly_price = parent_plan.get('price_monthly', '')
                    
                    # Extract numbers from current pricing
                    current_annual = re.search(r'\$(\d+)', annual_price)
                    current_monthly = re.search(r'\$(\d+)', monthly_price)
                    
                    if current_annual and price_float != float(current_annual.group(1)):
                        if price_float != float(current_monthly.group(1)) if current_monthly else True:
                            conflicts.append(ConflictInfo(
                                field_path="pricing.parent_plan",
                                existing_value=f"Annual: {annual_price}, Monthly: {monthly_price}",
                                proposed_value=f"${price}",
                                conflict_type="contradiction",
                                confidence=0.8
                            ))
        
        return conflicts
    
    def _check_timeline_conflicts(self, text: str) -> List[ConflictInfo]:
        """Check for timeline/date conflicts"""
        conflicts = []
        text_lower = text.lower()
        
        # Look for dates
        import re
        dates = re.findall(r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*(\d{1,2})?,?\s*(\d{4})?', text_lower)
        
        if dates:
            timeline = self.brain.knowledge.launch_timeline
            
            if 'beta' in text_lower or 'launch' in text_lower:
                if 'private' in text_lower and 'beta' in text_lower:
                    existing_date = timeline.get('private_beta', {}).get('start', '')
                    if existing_date and dates:
                        conflicts.append(ConflictInfo(
                            field_path="launch_timeline.private_beta.start",
                            existing_value=existing_date,
                            proposed_value=str(dates[0]),
                            conflict_type="update",
                            confidence=0.7
                        ))
        
        return conflicts
    
    def _check_feature_conflicts(self, text: str) -> List[ConflictInfo]:
        """Check if claiming a feature that doesn't exist or contradicts existing"""
        conflicts = []
        text_lower = text.lower()
        
        # Check for rate limiting claims
        if 'rate limit' in text_lower:
            # We DO have rate limiting (from auth-middleware.js)
            if any(word in text_lower for word in ["don't have", "no ", "need to add", "should add"]):
                conflicts.append(ConflictInfo(
                    field_path="technical.security.rate_limiting",
                    existing_value="Rate limiting exists: 60/min default, 20/min writes, 10/min auth",
                    proposed_value="Suggesting rate limiting doesn't exist",
                    conflict_type="contradiction",
                    confidence=0.9
                ))
        
        # Check for CORS claims
        if 'cors' in text_lower:
            if any(word in text_lower for word in ["don't have", "no ", "need to add", "should add"]):
                conflicts.append(ConflictInfo(
                    field_path="technical.security.cors",
                    existing_value="CORS configured with strict origin allowlist",
                    proposed_value="Suggesting CORS not configured",
                    conflict_type="contradiction",
                    confidence=0.9
                ))
        
        return conflicts
    
    def _check_team_conflicts(self, text: str) -> List[ConflictInfo]:
        """Check for team-related conflicts"""
        conflicts = []
        text_lower = text.lower()
        
        # Check for role claims
        for member in self.brain.knowledge.team:
            if member.name.lower() in text_lower:
                # Check if assigning wrong role
                if 'cto' in text_lower and member.role != 'CTO' and member.name.lower() in text_lower:
                    pass  # Would need more context
                if 'ceo' in text_lower and member.role != 'CEO & Founder' and member.name.lower() in text_lower:
                    pass
        
        return conflicts
    
    def _semantic_search_conflicts(self, text: str) -> List[ConflictInfo]:
        """Use brain's query function to find related existing content"""
        conflicts = []
        
        try:
            # Query the brain for related content
            results = self.brain.query(text, max_results=3)
            
            for result in results:
                if result.confidence > 0.5:
                    # High confidence match - might be duplicate or contradiction
                    conflicts.append(ConflictInfo(
                        field_path=f"{result.category.value}.{result.source}",
                        existing_value=str(result.results)[:200],
                        proposed_value=text[:200],
                        conflict_type="duplicate" if result.confidence > 0.8 else "update",
                        confidence=result.confidence
                    ))
        except Exception as e:
            print(f"[BRAIN CURATOR] Semantic search error (non-fatal): {e}")
        
        return conflicts
    
    def detect_conflicts(self, text: str) -> List[ConflictInfo]:
        """Run all conflict detection checks"""
        all_conflicts = []
        
        all_conflicts.extend(self._check_pricing_conflicts(text))
        all_conflicts.extend(self._check_timeline_conflicts(text))
        all_conflicts.extend(self._check_feature_conflicts(text))
        all_conflicts.extend(self._check_team_conflicts(text))
        all_conflicts.extend(self._semantic_search_conflicts(text))
        
        # Deduplicate by field_path
        seen = set()
        unique_conflicts = []
        for c in all_conflicts:
            if c.field_path not in seen:
                seen.add(c.field_path)
                unique_conflicts.append(c)
        
        return sorted(unique_conflicts, key=lambda x: x.confidence, reverse=True)
    
    # ========================================================================
    # CONTRIBUTION PROCESSING
    # ========================================================================
    
    def process_contribution(
        self,
        text: str,
        contributor: str = "stephen@phonologic.ca",
        force: bool = False
    ) -> CurationResult:
        """
        Process a natural language contribution from Stephen.
        
        Args:
            text: Raw text Stephen provided
            contributor: Email of contributor
            force: If True, skip conflict detection and merge directly
        
        Returns:
            CurationResult with acceptance status and message
        """
        import traceback
        print(f"[BRAIN CURATOR] Processing contribution: {text[:50]}...")
        
        try:
            contrib_id = self._generate_id()
            print(f"[BRAIN CURATOR] Generated ID: {contrib_id}")
        except Exception as e:
            print(f"[BRAIN CURATOR] ID generation error: {e}")
            print(traceback.format_exc())
            raise
        
        # Detect conflicts (wrapped in try-except for safety)
        try:
            conflicts = self.detect_conflicts(text)
            print(f"[BRAIN CURATOR] Found {len(conflicts)} conflicts")
        except Exception as e:
            print(f"[BRAIN CURATOR] Conflict detection error: {e}")
            print(traceback.format_exc())
            conflicts = []
        
        if not force and conflicts:
            # Found conflicts - need clarification
            high_confidence = [c for c in conflicts if c.confidence >= 0.7]
            
            if high_confidence:
                # Build friendly response
                message = self._build_conflict_message(text, high_confidence)
                
                # Stage for review
                pending = PendingContribution(
                    id=contrib_id,
                    contributor=contributor,
                    raw_input=text,
                    conflicts=conflicts,
                    status="needs_clarification",
                    curator_response=message
                )
                self.pending_queue.append(pending)
                self._save_pending(pending)
                
                return CurationResult(
                    accepted=False,
                    message=message,
                    conflicts_found=high_confidence,
                    clarification_needed=True,
                    contribution_id=contrib_id
                )
        
        # No conflicts or force mode - stage for merge
        try:
            pending = PendingContribution(
                id=contrib_id,
                contributor=contributor,
                raw_input=text,
                conflicts=conflicts,
                status="pending"
            )
            print(f"[BRAIN CURATOR] Created pending contribution: {pending.id}")
            self.pending_queue.append(pending)
            self._save_pending(pending)
            print(f"[BRAIN CURATOR] Saved to queue, total pending: {len(self.pending_queue)}")
        except Exception as e:
            print(f"[BRAIN CURATOR] Error creating/saving pending: {e}")
            print(traceback.format_exc())
            raise
        
        return CurationResult(
            accepted=True,
            message=f"Got it! I've staged this for the brain. No conflicts detected.\n\nContribution ID: {contrib_id}",
            conflicts_found=[],
            contribution_id=contrib_id
        )
    
    def _build_conflict_message(self, input_text: str, conflicts: List[ConflictInfo]) -> str:
        """Build a friendly conflict message for Stephen"""
        message = "🧠 **Hey Stephen, hold up!** I found some potential conflicts:\n\n"
        
        for i, conflict in enumerate(conflicts, 1):
            if conflict.conflict_type == "contradiction":
                message += f"**{i}. Contradiction detected in `{conflict.field_path}`**\n"
                message += f"   - **You said:** {conflict.proposed_value[:100]}...\n"
                message += f"   - **Brain says:** {conflict.existing_value[:100]}...\n"
                message += f"   - Confidence: {conflict.confidence:.0%}\n\n"
            elif conflict.conflict_type == "duplicate":
                message += f"**{i}. Possible duplicate in `{conflict.field_path}`**\n"
                message += f"   - This looks similar to existing info\n"
                message += f"   - **Existing:** {conflict.existing_value[:100]}...\n\n"
            else:
                message += f"**{i}. Update to `{conflict.field_path}`**\n"
                message += f"   - **Current:** {conflict.existing_value[:100]}...\n"
                message += f"   - **Proposed:** {conflict.proposed_value[:100]}...\n\n"
        
        message += "---\n"
        message += "**What would you like to do?**\n"
        message += "- `update` - Replace existing with your new info\n"
        message += "- `keep` - Keep existing, discard your input\n"
        message += "- `add_note` - Add as a note without replacing\n"
        message += "- `clarify` - Tell me more about what you meant\n"
        
        return message
    
    # ========================================================================
    # RESOLUTION
    # ========================================================================
    
    def resolve_contribution(
        self,
        contribution_id: str,
        action: Literal["update", "keep", "add_note", "clarify"],
        clarification: Optional[str] = None
    ) -> CurationResult:
        """
        Resolve a pending contribution after Stephen's decision.
        
        Args:
            contribution_id: ID of the pending contribution
            action: What to do - update/keep/add_note/clarify
            clarification: Additional context if action is 'clarify'
        """
        # Find the contribution
        pending = next((p for p in self.pending_queue if p.id == contribution_id), None)
        if not pending:
            return CurationResult(
                accepted=False,
                message=f"Couldn't find contribution {contribution_id}. It may have expired.",
                contribution_id=contribution_id
            )
        
        if action == "update":
            # Actually merge into brain and persist
            pending.status = "approved"
            pending.resolved_at = datetime.utcnow()
            
            # Persist the update to Redis
            self._persist_contribution_to_brain(pending)
            
            # Remove from pending queue
            self.pending_queue = [p for p in self.pending_queue if p.id != contribution_id]
            self.redis.delete_pending(contribution_id)
            
            return CurationResult(
                accepted=True,
                message="✅ Brain updated with your new information! This will persist across restarts.",
                contribution_id=contribution_id
            )
        
        elif action == "keep":
            pending.status = "rejected"
            pending.resolved_at = datetime.utcnow()
            
            # Remove from pending queue
            self.pending_queue = [p for p in self.pending_queue if p.id != contribution_id]
            self.redis.delete_pending(contribution_id)
            
            return CurationResult(
                accepted=False,
                message="👍 Keeping existing information. Your input was discarded.",
                contribution_id=contribution_id
            )
        
        elif action == "add_note":
            # Add to recent_updates as a note
            pending.status = "approved"
            pending.resolved_at = datetime.utcnow()
            
            # Save as a note/recent update
            self.redis.save_brain_update(
                category='recent_updates',
                key=f'note_{contribution_id}',
                value=f"[Note] {pending.raw_input}",
                contributor=pending.contributor
            )
            
            # Remove from pending queue
            self.pending_queue = [p for p in self.pending_queue if p.id != contribution_id]
            self.redis.delete_pending(contribution_id)
            
            return CurationResult(
                accepted=True,
                message="📝 Added as a note to recent updates. This won't overwrite existing info.",
                contribution_id=contribution_id
            )
        
        elif action == "clarify":
            if clarification:
                # Re-process with additional context
                combined = f"{pending.raw_input}\n\nClarification: {clarification}"
                return self.process_contribution(combined, pending.contributor)
            else:
                return CurationResult(
                    accepted=False,
                    message="Please provide clarification about what you meant.",
                    clarification_needed=True,
                    contribution_id=contribution_id
                )
        
        return CurationResult(
            accepted=False,
            message="Unknown action. Use: update, keep, add_note, or clarify",
            contribution_id=contribution_id
        )
    
    def _persist_contribution_to_brain(self, contribution: PendingContribution) -> None:
        """
        Persist a contribution to the brain via Redis.
        
        Uses Claude to extract structured data from the contribution text,
        then saves it appropriately to Redis for future brain loads.
        """
        text = contribution.raw_input.lower()
        
        # Determine category and extract key/value
        if any(word in text for word in ['price', 'cost', '$', 'plan', 'tier']):
            category = 'pricing'
            key = f'update_{contribution.id}'
        elif any(word in text for word in ['launch', 'beta', 'timeline', 'date', 'milestone']):
            category = 'milestones'
            key = f'milestone_{contribution.id}'
        elif any(word in text for word in ['metric', 'user', 'revenue', 'mrr', 'target']):
            category = 'key_metrics'
            key = f'metric_{contribution.id}'
        else:
            category = 'recent_updates'
            key = f'update_{contribution.id}'
        
        # Save to Redis
        self.redis.save_brain_update(
            category=category,
            key=key,
            value=contribution.raw_input,
            contributor=contribution.contributor
        )
        
        print(f"[BRAIN CURATOR] Persisted contribution {contribution.id} to {category}/{key}")
    
    # ========================================================================
    # QUERY MODE
    # ========================================================================
    
    def query_brain(self, question: str, user_id: str = "anonymous") -> str:
        """
        Answer a question using the FULL brain knowledge.
        
        Features:
        - Rate limiting per user
        - Streaming response to handle memory
        - Timeout handling
        - Chunked brain data for large knowledge bases
        """
        import json
        
        # Rate limiting check
        if self.redis.available:
            if not self.redis.check_rate_limit(f"query:{user_id}", max_requests=20, window_seconds=60):
                remaining = self.redis.get_rate_limit_remaining(f"query:{user_id}", max_requests=20)
                return f"⚠️ Rate limit exceeded. Please wait a moment. ({remaining} requests remaining)"
        
        try:
            from anthropic import Anthropic
            
            # Get brain data with any Redis updates merged
            brain_data = self.brain.knowledge.model_dump()
            
            # Include persisted updates from Redis
            if self.redis.available:
                redis_updates = self.redis.get_brain_updates()
                if redis_updates:
                    brain_data['_persisted_updates'] = [
                        u.get('value') for u in redis_updates.values()
                    ]
            
            # Convert to JSON - use compact format to reduce tokens
            brain_json = json.dumps(brain_data, separators=(',', ':'), default=str)
            
            # Check if brain data is too large (>100KB)
            if len(brain_json) > 100_000:
                print(f"[BRAIN CURATOR] Warning: Brain data is {len(brain_json)} bytes, truncating")
                # Truncate less critical fields for this query
                brain_data_slim = {
                    k: v for k, v in brain_data.items() 
                    if k in ['company_name', 'mission', 'vision', 'launch_timeline', 
                            'milestones', 'pricing', 'key_metrics', 'team', 'products',
                            'recent_updates', '_persisted_updates']
                }
                brain_json = json.dumps(brain_data_slim, separators=(',', ':'), default=str)
            
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            # Use streaming to handle memory efficiently
            response_text = ""
            with client.messages.stream(
                model=settings.DEFAULT_MODEL,
                max_tokens=2048,
                system="""You are the PhonoLogic Brain - the intelligent knowledge assistant for a literacy EdTech startup.

You have access to the COMPLETE company knowledge base. Answer questions by searching through ALL the provided data intelligently.

Guidelines:
- Be conversational and helpful
- Use markdown formatting (headers, bold, lists, tables) for readability  
- Be specific with dates, numbers, and details from the data
- If information isn't in the data, say so clearly
- Never make up information
- Keep responses concise but complete""",
                messages=[{
                    "role": "user",
                    "content": f"""Question: {question}

Here is the PhonoLogic knowledge base:

{brain_json}

Search through this data and provide a helpful, accurate answer."""
                }]
            ) as stream:
                for text in stream.text_stream:
                    response_text += text
                    # Safety check - cap response at 10KB
                    if len(response_text) > 10_000:
                        response_text += "\n\n[Response truncated for length]"
                        break
            
            return response_text
            
        except Exception as e:
            print(f"[BRAIN CURATOR] Claude API error: {e}")
            return f"⚠️ Error querying the brain: {str(e)}"


# ============================================================================
# AGNO AGENT WRAPPER
# ============================================================================

def create_brain_curator_agent() -> Agent:
    """Create an Agno agent that uses BrainCurator for knowledge management"""
    
    curator = BrainCurator()
    
    def add_to_brain(text: str, force: bool = False) -> str:
        """
        Add new information to the PhonoLogic brain.
        
        Args:
            text: Natural language description of what to add
            force: If True, skip conflict detection
        
        Returns:
            Status message with any conflicts found
        """
        result = curator.process_contribution(text, force=force)
        return result.message
    
    def query_brain_tool(question: str) -> str:
        """
        Query the PhonoLogic brain for existing information.
        
        Args:
            question: What you want to know about
        
        Returns:
            Relevant information from the brain
        """
        return curator.query_brain(question)
    
    def resolve_conflict(contribution_id: str, action: str, clarification: str = "") -> str:
        """
        Resolve a pending contribution after conflict detection.
        
        Args:
            contribution_id: ID of the pending contribution
            action: One of: update, keep, add_note, clarify
            clarification: Additional context if action is 'clarify'
        
        Returns:
            Status message
        """
        result = curator.resolve_contribution(
            contribution_id,
            action,  # type: ignore
            clarification or None
        )
        return result.message
    
    def get_pending() -> str:
        """Get all pending contributions awaiting review"""
        if not curator.pending_queue:
            return "No pending contributions."
        
        response = f"**{len(curator.pending_queue)} pending contribution(s):**\n\n"
        for p in curator.pending_queue:
            response += f"- **{p.id}** ({p.status}): {p.raw_input[:50]}...\n"
            if p.conflicts:
                response += f"  ⚠️ {len(p.conflicts)} conflict(s)\n"
        return response
    
    agent = Agent(
        name="BrainCurator",
        model=Claude(id=settings.DEFAULT_MODEL),
        tools=[add_to_brain, query_brain_tool, resolve_conflict, get_pending],
        instructions=[
            "You are the PhonoLogic Brain Curator - an intelligent gatekeeper for company knowledge.",
            "Your job is to help Stephen (the CEO) add information to the brain safely.",
            "",
            "CONFLICT HANDLING:",
            "- When Stephen tries to add something that conflicts with existing info, push back gently",
            "- Example: 'Hey Stephen, I found conflicting info! Our pricing is actually $20/mo, not $15...'",
            "- Always check existing brain before accepting new info",
            "- Never overwrite without confirmation",
            "",
            "QUERY MODE:",
            "- If Stephen asks a question, use query_brain_tool to find existing info",
            "- Be helpful and conversational",
            "",
            "ADD MODE:",
            "- If Stephen wants to add info, use add_to_brain",
            "- Report any conflicts found",
            "- Guide him through resolution",
            "",
            "Be friendly, casual, and helpful. Stephen is 'scatterbrained' so be patient!"
        ],
        show_tool_calls=True,
        markdown=True
    )
    
    return agent
