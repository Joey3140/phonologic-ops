"""
Redis client for orchestrator persistence.

Uses Upstash Redis REST API for serverless-friendly persistence.
Stores:
- Pending contributions
- Brain knowledge updates/overrides
- Rate limiting counters
"""
import json
import httpx
from typing import Optional, Any, List, Dict
from datetime import datetime, timedelta
from config import settings


class RedisClient:
    """
    Upstash Redis client using REST API.
    
    Thread-safe and connection-pool free - ideal for serverless/containerized deployments.
    """
    
    # Redis key prefixes for organization
    KEYS = {
        'pending': 'orchestrator:pending:',           # Pending contributions
        'brain_updates': 'orchestrator:brain:updates',  # Brain knowledge overrides
        'rate_limit': 'orchestrator:ratelimit:',      # Rate limiting
        'audit': 'orchestrator:audit:',               # Audit log
    }
    
    def __init__(self):
        self.url = settings.UPSTASH_REDIS_REST_URL
        self.token = settings.UPSTASH_REDIS_REST_TOKEN
        self._available = bool(self.url and self.token)
        
        if not self._available:
            print("[REDIS] Warning: Redis not configured. Persistence disabled.")
    
    @property
    def available(self) -> bool:
        return self._available
    
    def _request(self, command: List[str]) -> Any:
        """Execute Redis command via REST API"""
        if not self._available:
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
        except Exception as e:
            print(f"[REDIS] Error: {e}")
            return None
    
    # ========================================================================
    # PENDING CONTRIBUTIONS
    # ========================================================================
    
    def save_pending(self, contribution_id: str, data: Dict) -> bool:
        """Save a pending contribution"""
        key = f"{self.KEYS['pending']}{contribution_id}"
        result = self._request(["SET", key, json.dumps(data, default=str)])
        # Set expiry of 7 days for pending items
        self._request(["EXPIRE", key, str(7 * 24 * 60 * 60)])
        return result == "OK"
    
    def get_pending(self, contribution_id: str) -> Optional[Dict]:
        """Get a pending contribution"""
        key = f"{self.KEYS['pending']}{contribution_id}"
        result = self._request(["GET", key])
        return json.loads(result) if result else None
    
    def delete_pending(self, contribution_id: str) -> bool:
        """Delete a pending contribution (after resolution)"""
        key = f"{self.KEYS['pending']}{contribution_id}"
        result = self._request(["DEL", key])
        return result == 1
    
    def list_pending(self) -> List[Dict]:
        """List all pending contributions"""
        # Get all keys matching prefix
        keys = self._request(["KEYS", f"{self.KEYS['pending']}*"])
        if not keys:
            return []
        
        pending = []
        for key in keys:
            data = self._request(["GET", key])
            if data:
                pending.append(json.loads(data))
        
        return pending
    
    # ========================================================================
    # BRAIN KNOWLEDGE UPDATES
    # ========================================================================
    
    def save_brain_update(self, category: str, key: str, value: Any, contributor: str) -> bool:
        """
        Save a brain knowledge update.
        
        These are stored as overrides that get merged with DEFAULT_KNOWLEDGE.
        """
        update = {
            'category': category,
            'key': key,
            'value': value,
            'contributor': contributor,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Store in a hash for the category
        result = self._request([
            "HSET", 
            self.KEYS['brain_updates'], 
            f"{category}:{key}", 
            json.dumps(update, default=str)
        ])
        
        # Also log to audit trail
        self._log_audit('brain_update', update)
        
        return result is not None
    
    def get_brain_updates(self) -> Dict[str, Any]:
        """Get all brain knowledge updates/overrides"""
        result = self._request(["HGETALL", self.KEYS['brain_updates']])
        if not result:
            return {}
        
        updates = {}
        # HGETALL returns [key1, val1, key2, val2, ...]
        for i in range(0, len(result), 2):
            key = result[i]
            value = json.loads(result[i + 1])
            updates[key] = value
        
        return updates
    
    def delete_brain_update(self, category: str, key: str) -> bool:
        """Delete a brain knowledge update"""
        result = self._request([
            "HDEL",
            self.KEYS['brain_updates'],
            f"{category}:{key}"
        ])
        return result == 1
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    def check_rate_limit(self, identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """
        Check if request is within rate limit.
        
        Returns True if allowed, False if rate limited.
        Uses sliding window counter.
        """
        key = f"{self.KEYS['rate_limit']}{identifier}"
        
        # Increment counter
        count = self._request(["INCR", key])
        
        # Set expiry on first request
        if count == 1:
            self._request(["EXPIRE", key, str(window_seconds)])
        
        return count <= max_requests
    
    def get_rate_limit_remaining(self, identifier: str, max_requests: int = 10) -> int:
        """Get remaining requests in current window"""
        key = f"{self.KEYS['rate_limit']}{identifier}"
        count = self._request(["GET", key])
        current = int(count) if count else 0
        return max(0, max_requests - current)
    
    # ========================================================================
    # AUDIT LOG
    # ========================================================================
    
    def _log_audit(self, action: str, data: Dict) -> None:
        """Log an action to the audit trail"""
        entry = {
            'action': action,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Use a sorted set with timestamp as score for time-ordered retrieval
        score = datetime.utcnow().timestamp()
        self._request([
            "ZADD",
            f"{self.KEYS['audit']}log",
            str(score),
            json.dumps(entry, default=str)
        ])
        
        # Trim to last 1000 entries
        self._request(["ZREMRANGEBYRANK", f"{self.KEYS['audit']}log", "0", "-1001"])
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent audit log entries"""
        result = self._request([
            "ZREVRANGE",
            f"{self.KEYS['audit']}log",
            "0",
            str(limit - 1)
        ])
        
        if not result:
            return []
        
        return [json.loads(entry) for entry in result]


# Singleton instance
_redis_client: Optional[RedisClient] = None

def get_redis() -> RedisClient:
    """Get the Redis client singleton"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
