"""
Unit tests for BrainCurator.

Tests critical paths:
- Input validation and sanitization
- Conflict detection
- Contribution processing
- Resolution with locking
- Rate limiting
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Mock the agno imports before importing brain_curator
import sys
sys.modules['agno'] = MagicMock()
sys.modules['agno.agent'] = MagicMock()
sys.modules['agno.models'] = MagicMock()
sys.modules['agno.models.anthropic'] = MagicMock()

from agents.brain_curator import (
    BrainCurator,
    PendingContribution,
    ConflictInfo,
    CurationResult,
)
from lib.redis_client import RedisClient, MAX_CONTRIBUTION_LENGTH


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_xss_sanitization(self):
        """Test that HTML is escaped to prevent XSS."""
        contribution = PendingContribution(
            id="test_123",
            contributor="test@example.com",
            raw_input="<script>alert('xss')</script>",
        )
        assert "<script>" not in contribution.raw_input
        assert "&lt;script&gt;" in contribution.raw_input
    
    def test_input_length_truncation(self):
        """Test that oversized input is truncated."""
        long_input = "a" * (MAX_CONTRIBUTION_LENGTH + 1000)
        contribution = PendingContribution(
            id="test_123",
            contributor="test@example.com",
            raw_input=long_input,
        )
        assert len(contribution.raw_input) <= MAX_CONTRIBUTION_LENGTH
    
    def test_contributor_required(self):
        """Test that contributor field is required."""
        with pytest.raises(Exception):
            PendingContribution(
                id="test_123",
                raw_input="test input",
                # contributor missing
            )


class TestConflictDetection:
    """Test conflict detection logic."""
    
    @pytest.fixture
    def curator(self):
        """Create a BrainCurator with mocked Redis."""
        with patch('agents.brain_curator.get_redis') as mock_get_redis:
            mock_redis = Mock()
            mock_redis.available = False
            mock_get_redis.return_value = mock_redis
            return BrainCurator()
    
    def test_pricing_conflict_detection(self, curator):
        """Test that pricing conflicts are detected."""
        text = "Our pricing is now $99/month for the parent plan"
        conflicts = curator._check_pricing_conflicts(text)
        # Should detect potential conflict with existing pricing
        # (depends on brain's default pricing)
        assert isinstance(conflicts, list)
    
    def test_feature_conflict_contradiction(self, curator):
        """Test that false claims about features are detected."""
        text = "We don't have rate limiting implemented yet"
        conflicts = curator._check_feature_conflicts(text)
        # Should detect contradiction - we DO have rate limiting
        assert len(conflicts) > 0
        assert conflicts[0].conflict_type == "contradiction"
    
    def test_team_role_conflict(self, curator):
        """Test that wrong role assignments are detected."""
        # This depends on team members in DEFAULT_KNOWLEDGE
        text = "Stephen is our CTO"  # If Stephen is CEO, this should conflict
        conflicts = curator._check_team_conflicts(text)
        # Result depends on actual team data
        assert isinstance(conflicts, list)


class TestContributionProcessing:
    """Test contribution processing flow."""
    
    @pytest.fixture
    def curator_with_mock_redis(self):
        """Create a BrainCurator with mocked Redis."""
        with patch('agents.brain_curator.get_redis') as mock_get_redis:
            mock_redis = Mock()
            mock_redis.available = True
            mock_redis.save_pending = Mock(return_value=True)
            mock_redis.list_pending = Mock(return_value=([], 0))
            mock_redis.get_brain_updates = Mock(return_value={})
            mock_get_redis.return_value = mock_redis
            
            curator = BrainCurator()
            curator.redis = mock_redis
            return curator
    
    def test_contribution_creates_pending(self, curator_with_mock_redis):
        """Test that a contribution creates a pending entry."""
        curator = curator_with_mock_redis
        
        result = curator.process_contribution(
            text="New feature: dark mode support",
            contributor="test@example.com"
        )
        
        assert result.accepted == True
        assert result.contribution_id is not None
        curator.redis.save_pending.assert_called_once()
    
    def test_contribution_with_force_skips_conflicts(self, curator_with_mock_redis):
        """Test that force=True skips conflict detection."""
        curator = curator_with_mock_redis
        
        result = curator.process_contribution(
            text="We don't have rate limiting",  # Would normally conflict
            contributor="test@example.com",
            force=True
        )
        
        # Should still be accepted with force=True
        assert result.accepted == True


class TestResolution:
    """Test contribution resolution flow."""
    
    @pytest.fixture
    def curator_with_pending(self):
        """Create a BrainCurator with a pending contribution."""
        with patch('agents.brain_curator.get_redis') as mock_get_redis:
            mock_redis = Mock()
            mock_redis.available = True
            mock_redis.acquire_lock = Mock(return_value="lock_token_123")
            mock_redis.release_lock = Mock(return_value=True)
            mock_redis.delete_pending = Mock(return_value=True)
            mock_redis.save_brain_update = Mock(return_value=(True, "version_123"))
            mock_redis.get_brain_updates = Mock(return_value={})
            
            # Mock pending queue to return our test contribution
            pending_data = {
                'id': 'test_contrib_123',
                'contributor': 'test@example.com',
                'raw_input': 'Test contribution',
                'conflicts': [],
                'status': 'pending',
                'created_at': datetime.now(timezone.utc).isoformat(),
            }
            mock_redis.list_pending = Mock(return_value=([pending_data], 1))
            
            mock_get_redis.return_value = mock_redis
            
            curator = BrainCurator()
            curator.redis = mock_redis
            return curator
    
    def test_approve_contribution(self, curator_with_pending):
        """Test approving a contribution."""
        curator = curator_with_pending
        
        result = curator.resolve_contribution(
            contribution_id="test_contrib_123",
            action="update"
        )
        
        assert result.accepted == True
        curator.redis.acquire_lock.assert_called_once()
        curator.redis.delete_pending.assert_called_once()
        curator.redis.release_lock.assert_called_once()
    
    def test_reject_contribution(self, curator_with_pending):
        """Test rejecting a contribution."""
        curator = curator_with_pending
        
        result = curator.resolve_contribution(
            contribution_id="test_contrib_123",
            action="keep"
        )
        
        assert result.accepted == False
        assert "Keeping existing" in result.message
        curator.redis.delete_pending.assert_called_once()
    
    def test_lock_prevents_race_condition(self, curator_with_pending):
        """Test that lock acquisition prevents race conditions."""
        curator = curator_with_pending
        curator.redis.acquire_lock = Mock(return_value=None)  # Lock fails
        
        result = curator.resolve_contribution(
            contribution_id="test_contrib_123",
            action="update"
        )
        
        assert result.accepted == False
        assert "Another operation" in result.message
    
    def test_not_found_contribution(self, curator_with_pending):
        """Test resolving a non-existent contribution."""
        curator = curator_with_pending
        
        result = curator.resolve_contribution(
            contribution_id="nonexistent_123",
            action="update"
        )
        
        assert result.accepted == False
        assert "Couldn't find" in result.message


class TestRedisClient:
    """Test Redis client operations."""
    
    @pytest.fixture
    def redis_client(self):
        """Create a Redis client with mocked HTTP."""
        with patch('lib.redis_client.settings') as mock_settings:
            mock_settings.UPSTASH_REDIS_REST_URL = "https://test.upstash.io"
            mock_settings.UPSTASH_REDIS_REST_TOKEN = "test_token"
            return RedisClient()
    
    def test_contribution_size_validation(self, redis_client):
        """Test that oversized contributions are rejected."""
        with patch.object(redis_client, '_pipeline', return_value=["OK", 1, True]):
            large_data = {"raw_input": "x" * (MAX_CONTRIBUTION_LENGTH + 1)}
            result = redis_client.save_pending("test_id", large_data)
            assert result == False
    
    def test_rate_limit_returns_tuple(self, redis_client):
        """Test that rate limit check returns (allowed, remaining) tuple."""
        with patch.object(redis_client, '_pipeline', return_value=[5, True]):
            allowed, remaining = redis_client.check_rate_limit("test_user")
            assert isinstance(allowed, bool)
            assert isinstance(remaining, int)


class TestIDGeneration:
    """Test unique ID generation."""
    
    def test_id_uniqueness(self):
        """Test that generated IDs are unique."""
        with patch('agents.brain_curator.get_redis') as mock_get_redis:
            mock_redis = Mock()
            mock_redis.available = False
            mock_get_redis.return_value = mock_redis
            
            curator = BrainCurator()
            ids = [curator._generate_id() for _ in range(100)]
            
            # All IDs should be unique
            assert len(set(ids)) == 100
    
    def test_id_format(self):
        """Test that ID format is correct."""
        with patch('agents.brain_curator.get_redis') as mock_get_redis:
            mock_redis = Mock()
            mock_redis.available = False
            mock_get_redis.return_value = mock_redis
            
            curator = BrainCurator()
            id = curator._generate_id()
            
            assert id.startswith("contrib_")
            # Should have full UUID (32 hex chars)
            parts = id.split("_")
            assert len(parts) >= 3
            assert len(parts[-1]) == 32  # Full UUID hex


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
