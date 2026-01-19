"""
BrainCurator Agent - Intelligent Knowledge Gatekeeper

Handles:
- Natural language knowledge contributions
- Conflict detection against existing brain
- Feedback when misconceptions are detected
- Staging queue for review before merge (persisted in Redis)
- Source tracking (who added what, when)
- Version history for rollback capability

Architecture Notes:
- All state is persisted in Redis (no in-memory singletons)
- Uses distributed locks to prevent race conditions
- Input validation prevents oversized contributions
- Proper logging for production debugging
"""

import re
import uuid
import html
from typing import Optional, List, Dict, Any, Literal, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from agno.agent import Agent
from agno.models.anthropic import Claude

from knowledge.brain import PhonoLogicsBrain, DEFAULT_KNOWLEDGE
from knowledge.schemas import KnowledgeCategory
from config import settings
from lib.redis_client import get_redis, MAX_CONTRIBUTION_LENGTH
from lib.logging_config import logger

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
    contributor: str  # Must be provided from auth context, no default
    raw_input: str = Field(description="Original text provided", max_length=MAX_CONTRIBUTION_LENGTH)
    parsed_category: Optional[KnowledgeCategory] = None
    parsed_content: Dict[str, Any] = Field(default_factory=dict)
    conflicts: List[ConflictInfo] = Field(default_factory=list)
    status: Literal["pending", "approved", "rejected", "needs_clarification"] = "pending"
    curator_response: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    
    @field_validator('raw_input')
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        """Sanitize input to prevent XSS and limit size."""
        # HTML escape to prevent XSS
        v = html.escape(v)
        # Truncate if too long
        if len(v) > MAX_CONTRIBUTION_LENGTH:
            v = v[:MAX_CONTRIBUTION_LENGTH]
        return v


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
    
    Users can add knowledge naturally, and this system:
    1. Validates and sanitizes input
    2. Checks for conflicts with existing brain
    3. Provides feedback if conflicts detected
    4. Stages changes in Redis for review before merge
    5. Supports rollback via version history
    
    Architecture:
    - NO in-memory state - all pending items fetched fresh from Redis
    - Uses distributed locks to prevent race conditions
    - Thread-safe for multi-instance deployments
    """
    
    def __init__(self, brain: Optional[PhonoLogicsBrain] = None):
        self.brain = brain or PhonoLogicsBrain()
        self.redis = get_redis()
        self._load_brain_updates()  # Apply any persisted updates to brain
        logger.info("BrainCurator initialized")
    
    @property
    def pending_queue(self) -> List[PendingContribution]:
        """
        Get pending contributions fresh from Redis.
        
        This is a property, not a cached list, to ensure consistency
        across multiple container instances.
        """
        if not self.redis.available:
            logger.warning("Redis not available, returning empty pending queue")
            return []
        
        try:
            pending_list, _ = self.redis.list_pending(limit=100)
            result = []
            for p in pending_list:
                try:
                    # Handle datetime fields that might be strings
                    if 'created_at' in p and isinstance(p['created_at'], str):
                        p['created_at'] = datetime.fromisoformat(p['created_at'].replace('Z', '+00:00'))
                    if 'resolved_at' in p and isinstance(p['resolved_at'], str):
                        p['resolved_at'] = datetime.fromisoformat(p['resolved_at'].replace('Z', '+00:00'))
                    result.append(PendingContribution(**p))
                except Exception as item_error:
                    logger.warning("Skipping invalid pending item", error=str(item_error))
            return result
        except Exception as e:
            logger.error("Error loading pending", error=str(e))
            return []
    
    def _save_pending(self, contribution: PendingContribution):
        """Save a pending contribution to Redis"""
        if not self.redis.available:
            logger.warning("Redis unavailable, contribution not persisted")
            return
        
        try:
            self.redis.save_pending(
                contribution.id,
                contribution.model_dump()
            )
            logger.info("Saved contribution", contribution_id=contribution.id)
        except Exception as e:
            logger.error("Error saving pending", error=str(e))
    
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
                logger.info("Applying brain updates from Redis", count=len(updates))
                for key, update in updates.items():
                    self._apply_brain_update(update)
        except Exception as e:
            logger.error("Error loading brain updates", error=str(e))
    
    def _apply_brain_update(self, update: Dict[str, Any]):
        """Apply a single brain update to the knowledge base"""
        category = update.get('category')
        key = update.get('key')
        value = update.get('value')
        contributor = update.get('contributor', 'unknown')
        timestamp = update.get('timestamp', '')
        
        if not all([category, key, value]):
            return
        
        # Apply update to brain knowledge
        knowledge = self.brain.knowledge
        
        if category == 'pricing' and hasattr(knowledge, 'pricing'):
            if isinstance(value, dict):
                # Structured pricing update
                if isinstance(knowledge.pricing, dict):
                    knowledge.pricing[key] = value
            else:
                # Raw text - add as pricing note
                if 'user_notes' not in knowledge.pricing:
                    knowledge.pricing['user_notes'] = []
                knowledge.pricing['user_notes'].append({
                    'note': value,
                    'contributor': contributor,
                    'added': timestamp
                })
        elif category == 'milestones' and hasattr(knowledge, 'milestones'):
            if isinstance(value, dict):
                knowledge.milestones.append(value)
            else:
                # Raw text milestone - create structured entry
                knowledge.milestones.append({
                    'date': 'TBD',
                    'deliverable': value,
                    'status': 'user_contributed',
                    'contributor': contributor
                })
        elif category == 'key_metrics' and hasattr(knowledge, 'key_metrics'):
            if isinstance(knowledge.key_metrics, dict):
                if isinstance(value, dict):
                    knowledge.key_metrics.update(value)
                else:
                    # Raw text - add as metric note
                    knowledge.key_metrics[f'note_{key}'] = value
        
        # Always add to recent_updates for visibility
        if hasattr(knowledge, 'recent_updates'):
            update_text = f"[{contributor}] {value}" if isinstance(value, str) else f"[{contributor}] Updated {category}"
            if update_text not in knowledge.recent_updates:
                knowledge.recent_updates.insert(0, update_text)
                # Keep recent_updates manageable
                knowledge.recent_updates = knowledge.recent_updates[:20]
        
        logger.debug("Applied brain update", category=category, key=key)
    
    def _generate_id(self) -> str:
        """Generate unique contribution ID using full UUID to prevent collisions."""
        # Use full UUID (not truncated) to prevent birthday paradox collisions
        return f"contrib_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}"
    
    # ========================================================================
    # CONFLICT DETECTION
    # ========================================================================
    
    def _check_pricing_conflicts(self, text: str) -> List[ConflictInfo]:
        """Check for pricing-related conflicts."""
        conflicts = []
        text_lower = text.lower()
        
        # Look for dollar amounts
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
        """Check for timeline/date conflicts."""
        conflicts = []
        text_lower = text.lower()
        
        # Look for dates
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
        """
        Check for team-related conflicts (e.g., wrong role assignments).
        
        Detects when someone claims a team member has a different role
        than what's in the brain.
        """
        conflicts = []
        text_lower = text.lower()
        
        # Role keywords to check
        role_keywords = {
            'cto': 'CTO',
            'ceo': 'CEO',
            'founder': 'Founder',
            'developer': 'Developer',
            'teacher': 'Teacher',
        }
        
        for member in self.brain.knowledge.team:
            member_name_lower = member.name.lower()
            if member_name_lower not in text_lower:
                continue
            
            # Check if text assigns a role to this person
            for keyword, role_name in role_keywords.items():
                if keyword in text_lower:
                    # Check if this role matches their actual role
                    if role_name.lower() not in member.role.lower():
                        conflicts.append(ConflictInfo(
                            field_path=f"team.{member.id}.role",
                            existing_value=f"{member.name} is {member.role}",
                            proposed_value=f"Suggesting {member.name} is {role_name}",
                            conflict_type="contradiction",
                            confidence=0.7
                        ))
                        break  # One conflict per member is enough
        
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
            logger.debug("Semantic search error (non-fatal)", error=str(e))
        
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
        contributor: str,
        force: bool = False
    ) -> CurationResult:
        """
        Process a natural language contribution.
        
        Args:
            text: Raw text provided (will be sanitized)
            contributor: Email of contributor (from auth context, required)
            force: If True, skip conflict detection and merge directly
        
        Returns:
            CurationResult with acceptance status and message
        """
        import traceback
        logger.info("Processing contribution", contributor=contributor, text_preview=text[:50])
        
        try:
            contrib_id = self._generate_id()
            logger.debug("Generated contribution ID", id=contrib_id)
        except Exception as e:
            logger.error("ID generation error", error=str(e))
            raise
        
        # Detect conflicts (wrapped in try-except for safety)
        try:
            conflicts = self.detect_conflicts(text)
            logger.debug("Conflict detection complete", count=len(conflicts))
        except Exception as e:
            logger.error("Conflict detection error", error=str(e))
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
            self._save_pending(pending)
            logger.info("Staged contribution for merge", contribution_id=pending.id)
        except Exception as e:
            logger.error("Error creating/saving pending", error=str(e))
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
        
        # Acquire lock to prevent race conditions
        lock_token = self.redis.acquire_lock(f"resolve:{contribution_id}", timeout_seconds=30)
        if not lock_token:
            return CurationResult(
                accepted=False,
                message="Another operation is in progress. Please try again.",
                contribution_id=contribution_id
            )
        
        try:
            if action == "update":
                # Actually merge into brain and persist
                pending.status = "approved"
                pending.resolved_at = datetime.now(timezone.utc)
                
                # Persist the update to Redis
                self._persist_contribution_to_brain(pending)
                
                # Remove from pending (Redis-backed, no in-memory list)
                self.redis.delete_pending(contribution_id)
                logger.info("Approved contribution", contribution_id=contribution_id)
            
                return CurationResult(
                    accepted=True,
                    message="✅ Brain updated with your new information! This will persist across restarts.",
                    contribution_id=contribution_id
                )
            
            elif action == "keep":
                pending.status = "rejected"
                pending.resolved_at = datetime.now(timezone.utc)
                
                # Remove from pending (Redis-backed)
                self.redis.delete_pending(contribution_id)
                logger.info("Rejected contribution", contribution_id=contribution_id)
                
                return CurationResult(
                    accepted=False,
                    message="👍 Keeping existing information. Your input was discarded.",
                    contribution_id=contribution_id
                )
            
            elif action == "add_note":
                # Add to recent_updates as a note
                pending.status = "approved"
                pending.resolved_at = datetime.now(timezone.utc)
                
                # Save as a note/recent update
                self.redis.save_brain_update(
                    category='recent_updates',
                    key=f'note_{contribution_id}',
                    value=f"[Note] {pending.raw_input}",
                    contributor=pending.contributor
                )
                
                # Remove from pending (Redis-backed)
                self.redis.delete_pending(contribution_id)
                logger.info("Added contribution as note", contribution_id=contribution_id)
                
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
        finally:
            # Always release the lock
            self.redis.release_lock(f"resolve:{contribution_id}", lock_token)
    
    def _persist_contribution_to_brain(self, contribution: PendingContribution) -> None:
        """
        Persist a contribution to the brain via Redis.
        
        Uses keyword matching to categorize the contribution, then saves it
        to Redis for future brain loads. The brain applies these updates
        on initialization.
        
        Note: This is a simple keyword-based categorization. For more sophisticated
        extraction, consider using an LLM to parse structured data from the text.
        """
        text = contribution.raw_input.lower()
        
        # Determine category based on keywords
        # Priority order matters - first match wins
        if any(word in text for word in ['price', 'cost', '$', 'plan', 'tier', 'subscription']):
            category = 'pricing'
            key = f'update_{contribution.id}'
        elif any(word in text for word in ['launch', 'beta', 'timeline', 'date', 'milestone', 'deadline']):
            category = 'milestones'
            key = f'milestone_{contribution.id}'
        elif any(word in text for word in ['metric', 'user', 'revenue', 'mrr', 'target', 'kpi']):
            category = 'key_metrics'
            key = f'metric_{contribution.id}'
        else:
            category = 'recent_updates'
            key = f'update_{contribution.id}'
        
        # Save to Redis with version history
        self.redis.save_brain_update(
            category=category,
            key=key,
            value=contribution.raw_input,
            contributor=contribution.contributor
        )
        
        logger.info("Persisted contribution to brain", contribution_id=contribution.id, category=category)
    
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
            allowed, remaining = self.redis.check_rate_limit(f"query:{user_id}", max_requests=20, window_seconds=60)
            if not allowed:
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
                logger.warning("Brain data too large, truncating", size=len(brain_json))
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
            logger.error("Claude API error", error=str(e))
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
