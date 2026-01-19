"""
Redis client for orchestrator persistence.

Uses Upstash Redis REST API for serverless-friendly persistence.
Stores:
- Pending contributions (with sorted set index for efficient listing)
- Brain knowledge updates/overrides (with version history)
- Rate limiting counters
- Audit log for rollback capability

Key Design Decisions:
- Uses SCAN instead of KEYS for production safety
- Atomic operations via Redis pipelines where possible
- All state in Redis (no in-memory singletons)
- Version history for rollback capability
"""
import json
import uuid
import httpx
from typing import Optional, Any, List, Dict, Tuple
from datetime import datetime, timezone
from config import settings
from lib.logging_config import logger

# Input validation constants
MAX_CONTRIBUTION_LENGTH = 10_000  # 10KB max
MAX_PENDING_AGE_DAYS = 7
MAX_BRAIN_UPDATES = 1000

class RedisClient:
    """
    Upstash Redis client using REST API.

    
    Thread-safe and connection-pool free - ideal for serverless/containerized deployments.
    All state lives in Redis - no in-memory caching that could diverge across instances.
    """
    
    # Redis key prefixes for organization
    KEYS = {
        'pending': 'orchestrator:pending:',              # Individual pending items
        'pending_index': 'orchestrator:pending:index',   # Sorted set of pending IDs
        'brain_updates': 'orchestrator:brain:updates',   # Brain knowledge overrides
        'brain_history': 'orchestrator:brain:history',   # Version history for rollback
        'rate_limit': 'orchestrator:ratelimit:',         # Rate limiting
        'audit': 'orchestrator:audit:log',               # Audit log
        'campaign_task': 'orchestrator:campaign:',       # Background campaign tasks
        'campaign_events': 'orchestrator:campaign:events:',  # Campaign event streams
    }
    
    def __init__(self):
        # Strip trailing slash from URL to prevent //pipeline issues
        self.url = (settings.UPSTASH_REDIS_REST_URL or "").rstrip("/")
        self.token = settings.UPSTASH_REDIS_REST_TOKEN
        self._available = bool(self.url and self.token)
        
        if not self._available:
            logger.warning("Redis not configured - persistence disabled")
    
    @property
    def available(self) -> bool:
        return self._available
    
    def _request(self, command: List[str], raise_on_error: bool = False) -> Any:
        """
        Execute Redis command via REST API.
        
        Args:
            command: Redis command as list of strings
            raise_on_error: If True, raise exception on failure instead of returning None
        
        Returns:
            Result from Redis, or None on failure (unless raise_on_error=True)
        """
        if not self._available:
            if raise_on_error:
                raise ConnectionError("Redis not configured")
            return None
            
        try:
            response = httpx.post(
                self.url,
                headers={"Authorization": f"Bearer {self.token}"},
                json=command,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get('result')
        except httpx.TimeoutException:
            logger.error("Redis timeout", command=command[0])
            if raise_on_error:
                raise
            return None
        except Exception as e:
            logger.error("Redis error", error=str(e), command=command[0])
            if raise_on_error:
                raise
            return None
    
    def _pipeline(self, commands: List[List[str]]) -> List[Any]:
        """
        Execute multiple Redis commands in a pipeline for atomicity.
        
        Args:
            commands: List of Redis commands
        
        Returns:
            List of results from each command
        """
        if not self._available:
            return [None] * len(commands)
        
        try:
            # Upstash supports pipeline via array of commands
            response = httpx.post(
                f"{self.url}/pipeline",
                headers={"Authorization": f"Bearer {self.token}"},
                json=commands,
                timeout=15.0
            )
            response.raise_for_status()
            results = response.json()
            return [r.get('result') for r in results]
        except Exception as e:
            logger.error("Redis pipeline error", error=str(e))
            return [None] * len(commands)
    
    # ========================================================================
    # PENDING CONTRIBUTIONS
    # ========================================================================
    
    def save_pending(self, contribution_id: str, data: Dict) -> bool:
        """
        Save a pending contribution atomically.
        
        Uses a pipeline to:
        1. Store the contribution data
        2. Add to sorted set index (for efficient listing)
        3. Set expiry
        """
        key = f"{self.KEYS['pending']}{contribution_id}"
        timestamp = datetime.now(timezone.utc).timestamp()
        expiry_seconds = MAX_PENDING_AGE_DAYS * 24 * 60 * 60
        
        # Validate input size
        data_json = json.dumps(data, default=str)
        if len(data_json) > MAX_CONTRIBUTION_LENGTH:
            logger.warning("Contribution too large", size=len(data_json), max=MAX_CONTRIBUTION_LENGTH)
            return False
        
        # Note: Upstash REST API expects numbers as JSON numbers, not strings
        results = self._pipeline([
            ["SET", key, data_json],
            ["ZADD", self.KEYS['pending_index'], timestamp, contribution_id],
            ["EXPIRE", key, expiry_seconds]
        ])
        
        success = results[0] == "OK"
        if success:
            logger.info("Saved pending contribution", contribution_id=contribution_id)
        return success
    
    def get_pending(self, contribution_id: str) -> Optional[Dict]:
        """Get a single pending contribution by ID."""
        key = f"{self.KEYS['pending']}{contribution_id}"
        result = self._request(["GET", key])
        if not result:
            return None
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.error("Corrupted pending data", contribution_id=contribution_id)
            return None
    
    def delete_pending(self, contribution_id: str) -> bool:
        """
        Delete a pending contribution atomically.
        
        Removes from both the data store and the sorted set index.
        """
        key = f"{self.KEYS['pending']}{contribution_id}"
        results = self._pipeline([
            ["DEL", key],
            ["ZREM", self.KEYS['pending_index'], contribution_id]
        ])
        success = results[0] == 1
        if success:
            logger.info("Deleted pending contribution", contribution_id=contribution_id)
        return success
    
    def list_pending(
        self, 
        limit: int = 50, 
        offset: int = 0,
        order: str = "desc"
    ) -> Tuple[List[Dict], int]:
        """
        List pending contributions with pagination.
        
        Uses sorted set index for O(log N) performance instead of KEYS scan.
        
        Args:
            limit: Max items to return (default 50, max 100)
            offset: Number of items to skip
            order: 'desc' (newest first) or 'asc' (oldest first)
        
        Returns:
            Tuple of (list of contributions, total count)
        """
        limit = min(limit, 100)  # Cap at 100
        
        # Get total count
        total = self._request(["ZCARD", self.KEYS['pending_index']]) or 0
        
        if total == 0:
            return [], 0
        
        # Get IDs from sorted set with pagination
        # Note: Upstash REST API expects numbers as JSON numbers, not strings
        if order == "desc":
            ids = self._request([
                "ZREVRANGE", self.KEYS['pending_index'],
                offset, offset + limit - 1
            ])
        else:
            ids = self._request([
                "ZRANGE", self.KEYS['pending_index'],
                offset, offset + limit - 1
            ])
        
        if not ids:
            return [], total
        
        # Batch fetch all items with MGET
        keys = [f"{self.KEYS['pending']}{id}" for id in ids]
        results = self._request(["MGET"] + keys)
        
        pending = []
        for i, data in enumerate(results or []):
            if data:
                try:
                    pending.append(json.loads(data))
                except json.JSONDecodeError:
                    logger.warning("Skipping corrupted pending item", id=ids[i])
        
        return pending, total
    
    # ========================================================================
    # BRAIN KNOWLEDGE UPDATES
    # ========================================================================
    
    def save_brain_update(
        self, 
        category: str, 
        key: str, 
        value: Any, 
        contributor: str,
        save_history: bool = True
    ) -> Tuple[bool, str]:
        """
        Save a brain knowledge update with version history.
        
        Args:
            category: Category of the update (pricing, milestones, etc.)
            key: Unique key within the category
            value: The value to store
            contributor: Email of the contributor (from auth context)
            save_history: If True, save previous version for rollback
        
        Returns:
            Tuple of (success, version_id)
        """
        version_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        update = {
            'category': category,
            'key': key,
            'value': value,
            'contributor': contributor,
            'timestamp': timestamp,
            'version_id': version_id,
        }
        
        update_json = json.dumps(update, default=str)
        field_key = f"{category}:{key}"
        
        commands = []
        
        # If saving history, get current value first and archive it
        if save_history:
            current = self._request(["HGET", self.KEYS['brain_updates'], field_key])
            if current:
                # Archive the old version with timestamp score
                history_entry = {
                    'previous': json.loads(current),
                    'replaced_at': timestamp,
                    'replaced_by': contributor,
                    'new_version_id': version_id
                }
                commands.append([
                    "ZADD", self.KEYS['brain_history'],
                    str(datetime.now(timezone.utc).timestamp()),
                    json.dumps(history_entry, default=str)
                ])
        
        # Save the new update
        commands.append(["HSET", self.KEYS['brain_updates'], field_key, update_json])
        
        results = self._pipeline(commands) if commands else []
        success = len(results) > 0 and results[-1] is not None
        
        if success:
            self._log_audit('brain_update', update)
            logger.info("Saved brain update", category=category, key=key, version=version_id)
        
        return success, version_id
    
    def get_brain_updates(self) -> Dict[str, Any]:
        """Get all current brain knowledge updates/overrides."""
        result = self._request(["HGETALL", self.KEYS['brain_updates']])
        if not result:
            return {}
        
        updates = {}
        # HGETALL returns [key1, val1, key2, val2, ...]
        for i in range(0, len(result), 2):
            key = result[i]
            try:
                value = json.loads(result[i + 1])
                updates[key] = value
            except json.JSONDecodeError:
                logger.warning("Corrupted brain update", key=key)
        
        return updates
    
    def get_brain_history(self, limit: int = 50) -> List[Dict]:
        """
        Get version history for rollback capability.
        
        Returns list of historical updates, newest first.
        """
        result = self._request([
            "ZREVRANGE", self.KEYS['brain_history'],
            0, limit - 1
        ])
        
        if not result:
            return []
        
        history = []
        for entry in result:
            try:
                history.append(json.loads(entry))
            except json.JSONDecodeError:
                continue
        
        return history
    
    def rollback_brain_update(self, category: str, key: str) -> Optional[Dict]:
        """
        Rollback a brain update to its previous version.
        
        Returns the restored value, or None if no history exists.
        """
        field_key = f"{category}:{key}"
        
        # Find the most recent history entry for this field
        history = self.get_brain_history(limit=100)
        
        for entry in history:
            prev = entry.get('previous', {})
            if prev.get('category') == category and prev.get('key') == key:
                # Restore this version
                success, _ = self.save_brain_update(
                    category=prev['category'],
                    key=prev['key'],
                    value=prev['value'],
                    contributor='system:rollback',
                    save_history=True
                )
                if success:
                    logger.info("Rolled back brain update", category=category, key=key)
                    return prev
        
        return None
    
    def delete_brain_update(self, category: str, key: str) -> bool:
        """Delete a brain knowledge update"""
        field_key = f"{category}:{key}"
        logger.info("Deleting brain update", field_key=field_key)
        
        result = self._request([
            "HDEL",
            self.KEYS['brain_updates'],
            field_key
        ])
        
        logger.info("Delete result", result=result, result_type=type(result).__name__)
        
        # HDEL returns number of fields deleted (could be int or string)
        return result == 1 or result == "1" or str(result) == "1"
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    def check_rate_limit(
        self, 
        identifier: str, 
        max_requests: int = 10, 
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Check if request is within rate limit.
        
        Uses atomic INCR + EXPIRE for thread safety.
        
        Args:
            identifier: Unique identifier (e.g., "query:user@email.com")
            max_requests: Max requests allowed in window
            window_seconds: Window duration
        
        Returns:
            Tuple of (allowed: bool, remaining: int)
        """
        key = f"{self.KEYS['rate_limit']}{identifier}"
        
        # Use pipeline for atomicity
        results = self._pipeline([
            ["INCR", key],
            ["EXPIRE", key, window_seconds]
        ])
        
        count = results[0] if results[0] else 0
        remaining = max(0, max_requests - count)
        allowed = count <= max_requests
        
        if not allowed:
            logger.warning("Rate limit exceeded", identifier=identifier, count=count)
        
        return allowed, remaining
    
    def get_rate_limit_remaining(self, identifier: str, max_requests: int = 10) -> int:
        """Get remaining requests in current window."""
        key = f"{self.KEYS['rate_limit']}{identifier}"
        count = self._request(["GET", key])
        current = int(count) if count else 0
        return max(0, max_requests - current)
    
    def acquire_lock(
        self, 
        resource: str, 
        timeout_seconds: int = 10
    ) -> Optional[str]:
        """
        Acquire a distributed lock for a resource.
        
        Use this to prevent race conditions on critical operations.
        
        Args:
            resource: Name of the resource to lock
            timeout_seconds: Lock auto-expires after this many seconds
        
        Returns:
            Lock token if acquired, None if resource is already locked
        """
        lock_key = f"orchestrator:lock:{resource}"
        lock_token = str(uuid.uuid4())
        
        # SET NX (only if not exists) with expiry
        result = self._request([
            "SET", lock_key, lock_token, 
            "NX", "EX", timeout_seconds
        ])
        
        if result == "OK":
            logger.debug("Acquired lock", resource=resource, token=lock_token)
            return lock_token
        return None
    
    def release_lock(self, resource: str, token: str) -> bool:
        """
        Release a distributed lock.
        
        Only releases if the token matches (prevents releasing someone else's lock).
        """
        lock_key = f"orchestrator:lock:{resource}"
        
        # Check token matches before deleting
        current = self._request(["GET", lock_key])
        if current == token:
            self._request(["DEL", lock_key])
            logger.debug("Released lock", resource=resource)
            return True
        return False
    
    # ========================================================================
    # AUDIT LOG
    # ========================================================================
    
    def _log_audit(self, action: str, data: Dict) -> None:
        """
        Log an action to the audit trail.
        
        Uses sorted set for time-ordered retrieval.
        Auto-trims to last 1000 entries.
        """
        now = datetime.now(timezone.utc)
        entry = {
            'action': action,
            'data': data,
            'timestamp': now.isoformat(),
        }
        
        self._pipeline([
            ["ZADD", self.KEYS['audit'], now.timestamp(), json.dumps(entry, default=str)],
            ["ZREMRANGEBYRANK", self.KEYS['audit'], 0, -1001]
        ])
    
    def get_audit_log(self, limit: int = 100, action_filter: Optional[str] = None) -> List[Dict]:
        """
        Get recent audit log entries.
        
        Args:
            limit: Max entries to return
            action_filter: Optional filter by action type
        
        Returns:
            List of audit entries, newest first
        """
        result = self._request([
            "ZREVRANGE", self.KEYS['audit'],
            0, limit - 1
        ])
        
        if not result:
            return []
        
        entries = []
        for entry_str in result:
            try:
                entry = json.loads(entry_str)
                if action_filter is None or entry.get('action') == action_filter:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue
        
        return entries
    
    # ========================================================================
    # BACKGROUND CAMPAIGN TASKS
    # ========================================================================
    
    def create_campaign_task(self, task_id: str, input_data: Dict) -> bool:
        """Create a new background campaign task."""
        key = f"{self.KEYS['campaign_task']}{task_id}"
        task_data = {
            'task_id': task_id,
            'status': 'running',
            'input': input_data,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'agents': {
                'Researcher': {'status': 'pending', 'message': 'Waiting...'},
                'TechnicalConsultant': {'status': 'pending', 'message': 'Waiting...'},
                'BrandLead': {'status': 'pending', 'message': 'Waiting...'},
                'ImageryArchitect': {'status': 'pending', 'message': 'Waiting...'},
            },
            'result': None,
            'error': None,
        }
        # Expire after 1 hour
        results = self._pipeline([
            ["SET", key, json.dumps(task_data, default=str)],
            ["EXPIRE", key, 3600]
        ])
        return results[0] == "OK"
    
    def update_campaign_task(self, task_id: str, updates: Dict) -> bool:
        """Update a campaign task's state."""
        key = f"{self.KEYS['campaign_task']}{task_id}"
        current = self._request(["GET", key])
        if not current:
            return False
        try:
            task_data = json.loads(current)
            task_data.update(updates)
            task_data['updated_at'] = datetime.now(timezone.utc).isoformat()
            self._request(["SET", key, json.dumps(task_data, default=str)])
            return True
        except json.JSONDecodeError:
            return False
    
    def get_campaign_task(self, task_id: str) -> Optional[Dict]:
        """Get a campaign task by ID."""
        key = f"{self.KEYS['campaign_task']}{task_id}"
        result = self._request(["GET", key])
        if not result:
            return None
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return None
    
    def push_campaign_event(self, task_id: str, event: Dict) -> bool:
        """Push an event to the campaign's event stream."""
        key = f"{self.KEYS['campaign_events']}{task_id}"
        event['timestamp'] = datetime.now(timezone.utc).isoformat()
        results = self._pipeline([
            ["RPUSH", key, json.dumps(event, default=str)],
            ["EXPIRE", key, 3600]  # Expire after 1 hour
        ])
        return results[0] is not None
    
    def get_campaign_events(self, task_id: str, start: int = 0) -> List[Dict]:
        """Get events from a campaign's event stream starting from index."""
        key = f"{self.KEYS['campaign_events']}{task_id}"
        result = self._request(["LRANGE", key, start, -1])
        if not result:
            return []
        events = []
        for item in result:
            try:
                events.append(json.loads(item))
            except json.JSONDecodeError:
                continue
        return events
    
    def get_campaign_event_count(self, task_id: str) -> int:
        """Get the number of events in a campaign's stream."""
        key = f"{self.KEYS['campaign_events']}{task_id}"
        result = self._request(["LLEN", key])
        return int(result) if result else 0

    # ==================== Brain Overrides ====================
    
    def get_brain_overrides(self) -> Dict[str, Any]:
        """Get all brain field overrides from Redis."""
        if not self._available:
            return {}
        
        key = self.KEYS['brain_updates']
        result = self._request(["GET", key])
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_brain_overrides(self, overrides: Dict[str, Any]) -> bool:
        """Set brain field overrides in Redis."""
        if not self._available:
            return False
        
        key = self.KEYS['brain_updates']
        
        # Add metadata
        overrides['_updated_at'] = datetime.now(timezone.utc).isoformat()
        
        result = self._request(["SET", key, json.dumps(overrides)])
        return result == "OK"
    
    def update_brain_field(self, field: str, value: Any) -> bool:
        """Update a single brain field override."""
        overrides = self.get_brain_overrides()
        overrides[field] = value
        return self.set_brain_overrides(overrides)
    
    def get_brain_field(self, field: str, default: Any = None) -> Any:
        """Get a single brain field override."""
        overrides = self.get_brain_overrides()
        return overrides.get(field, default)


# Singleton instance
_redis_client: Optional[RedisClient] = None

def get_redis() -> RedisClient:
    """Get the Redis client singleton"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
