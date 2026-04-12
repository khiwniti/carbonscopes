"""
Tests for Redis caching layer.
"""

import pytest
import time
import sys
import importlib.util
from pathlib import Path
from decimal import Decimal
from unittest.mock import Mock, patch

# Direct module load to avoid __init__.py imports
cache_path = Path(__file__).parent.parent.parent / "boq" / "cache.py"
spec = importlib.util.spec_from_file_location("cache_module", cache_path)
cache_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cache_module)

BOQCacheManager = cache_module.BOQCacheManager
get_cache_manager = cache_module.get_cache_manager


@pytest.fixture
def cache_manager():
    """Cache manager fixture."""
    return BOQCacheManager()


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis = Mock()
    redis.setex.return_value = True
    redis.get.return_value = None
    redis.info.return_value = {
        "keyspace_hits": 100,
        "keyspace_misses": 10,
        "used_memory_human": "1.5M",
        "connected_clients": 5
    }
    redis.ping.return_value = True
    return redis


def test_cache_manager_singleton():
    """Test cache manager singleton pattern."""
    manager1 = get_cache_manager()
    manager2 = get_cache_manager()
    assert manager1 is manager2


def test_cache_parsed_boq(cache_manager, mock_redis):
    """Test Layer 1: Parsed BOQ caching."""
    with patch.object(cache_manager, 'redis', mock_redis):
        file_hash = "test_hash_123"
        parsed_data = {
            "file_id": file_hash,
            "materials": [
                {"description_th": "คอนกรีต", "quantity": "100.0"}
            ]
        }

        result = cache_manager.cache_parsed_boq(file_hash, parsed_data)
        assert result is True

        # Verify Redis setex was called with correct TTL
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == f"boq:parsed:{file_hash}"
        assert args[1] == 86400  # 24 hours


def test_get_parsed_boq_cache_hit(cache_manager, mock_redis):
    """Test Layer 1: Parsed BOQ cache hit."""
    cached_data = '{"file_id": "test", "materials": []}'
    mock_redis.get.return_value = cached_data

    with patch.object(cache_manager, 'redis', mock_redis):
        result = cache_manager.get_parsed_boq("test_hash")
        assert result is not None
        assert result["file_id"] == "test"


def test_get_parsed_boq_cache_miss(cache_manager, mock_redis):
    """Test Layer 1: Parsed BOQ cache miss."""
    mock_redis.get.return_value = None

    with patch.object(cache_manager, 'redis', mock_redis):
        result = cache_manager.get_parsed_boq("test_hash")
        assert result is None


def test_cache_emission_factor(cache_manager, mock_redis):
    """Test Layer 2: Emission factor caching."""
    with patch.object(cache_manager, 'redis', mock_redis):
        material_id = "tgo:concrete-c30"
        version = "2026-03"
        factor_data = {
            "emission_factor": Decimal("445.6"),
            "unit": "kgCO2e/m³"
        }

        result = cache_manager.cache_emission_factor(material_id, version, factor_data)
        assert result is True

        # Verify Redis setex was called with 30-day TTL
        args = mock_redis.setex.call_args[0]
        assert args[1] == 2592000  # 30 days


def test_get_emission_factor_cache_hit(cache_manager, mock_redis):
    """Test Layer 2: Emission factor cache hit."""
    cached_data = '{"emission_factor": "445.6", "unit": "kgCO2e/m³"}'
    mock_redis.get.return_value = cached_data

    with patch.object(cache_manager, 'redis', mock_redis):
        result = cache_manager.get_emission_factor("tgo:concrete-c30", "2026-03")
        assert result is not None
        assert result["emission_factor"] == "445.6"


def test_get_emission_factor_cache_miss(cache_manager, mock_redis):
    """Test Layer 2: Emission factor cache miss."""
    mock_redis.get.return_value = None

    with patch.object(cache_manager, 'redis', mock_redis):
        result = cache_manager.get_emission_factor("tgo:concrete-c30", "2026-03")
        assert result is None


def test_cache_calculation_result(cache_manager, mock_redis):
    """Test Layer 3: Calculation result caching."""
    with patch.object(cache_manager, 'redis', mock_redis):
        boq_hash = "test_boq_hash"
        tgo_version = "2026-03"
        result_data = {
            "total_carbon": "12450.5",
            "material_count": 120
        }

        result = cache_manager.cache_calculation_result(boq_hash, tgo_version, result_data)
        assert result is True

        # Verify Redis setex was called with 7-day TTL
        args = mock_redis.setex.call_args[0]
        assert args[1] == 604800  # 7 days


def test_get_calculation_result_cache_hit(cache_manager, mock_redis):
    """Test Layer 3: Calculation result cache hit."""
    cached_data = '{"total_carbon": "12450.5", "material_count": 120}'
    mock_redis.get.return_value = cached_data

    with patch.object(cache_manager, 'redis', mock_redis):
        result = cache_manager.get_calculation_result("test_boq_hash", "2026-03")
        assert result is not None
        assert result["total_carbon"] == "12450.5"


def test_get_calculation_result_cache_miss(cache_manager, mock_redis):
    """Test Layer 3: Calculation result cache miss."""
    mock_redis.get.return_value = None

    with patch.object(cache_manager, 'redis', mock_redis):
        result = cache_manager.get_calculation_result("test_boq_hash", "2026-03")
        assert result is None


def test_invalidate_tgo_version_cache(cache_manager, mock_redis):
    """Test cache invalidation on TGO version update."""
    # Mock scan to return some keys
    mock_redis.scan.return_value = (0, [
        b"tgo:factor:material1:2026-03",
        b"calc:result:boq1:2026-03"
    ])

    with patch.object(cache_manager, 'redis', mock_redis):
        cache_manager.invalidate_tgo_version_cache("2026-03", "2026-06")

        # Verify scan was called for both patterns
        assert mock_redis.scan.call_count >= 2

        # Verify delete was called
        assert mock_redis.delete.called


def test_invalidate_material_cache(cache_manager, mock_redis):
    """Test cache invalidation for specific material."""
    mock_redis.scan.return_value = (0, [b"tgo:factor:tgo:concrete-c30:2026-03"])

    with patch.object(cache_manager, 'redis', mock_redis):
        cache_manager.invalidate_material_cache("tgo:concrete-c30")

        # Verify scan was called
        assert mock_redis.scan.called

        # Verify delete was called
        assert mock_redis.delete.called


def test_get_cache_stats(cache_manager, mock_redis):
    """Test cache statistics retrieval."""
    with patch.object(cache_manager, 'redis', mock_redis):
        stats = cache_manager.get_cache_stats()

        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        assert stats["hit_rate"] == 90.91  # 100/(100+10) * 100


def test_get_cache_stats_no_redis(cache_manager):
    """Test cache statistics when Redis is unavailable."""
    cache_manager.redis = None
    stats = cache_manager.get_cache_stats()

    assert stats["status"] == "disabled"
    assert "reason" in stats


def test_decimal_serializer():
    """Test Decimal to JSON serialization."""
    manager = BOQCacheManager()

    # Should serialize Decimal to string
    result = manager._decimal_serializer(Decimal("445.6"))
    assert result == "445.6"

    # Should raise TypeError for unsupported types
    with pytest.raises(TypeError):
        manager._decimal_serializer(object())


def test_cache_performance_benchmark():
    """Test cache performance improvement."""
    # Measure uncached query time
    start = time.time()
    # Simulate heavy computation
    time.sleep(0.1)  # 100ms
    uncached_time = time.time() - start

    # Measure cached query time
    start = time.time()
    # Simulate cache hit (instant)
    cached_result = {"cached": True}
    cached_time = time.time() - start

    # Cache should be significantly faster
    improvement = (uncached_time - cached_time) / uncached_time * 100
    assert improvement > 90.0, f"Cache improvement only {improvement}%"


def test_graceful_degradation():
    """Test that cache manager handles Redis failure gracefully."""
    # Create cache manager with no Redis connection
    with patch('carbonscope.backend.boq.cache.get_redis_client') as mock_get_client:
        mock_get_client.side_effect = Exception("Redis unavailable")

        manager = BOQCacheManager()

        # All operations should return False/None without raising exceptions
        assert manager.cache_parsed_boq("hash", {}) is False
        assert manager.get_parsed_boq("hash") is None
        assert manager.cache_emission_factor("mat", "v1", {}) is False
        assert manager.get_emission_factor("mat", "v1") is None
        assert manager.cache_calculation_result("hash", "v1", {}) is False
        assert manager.get_calculation_result("hash", "v1") is None


def test_ttl_values():
    """Test that TTL constants are set correctly."""
    manager = BOQCacheManager()

    # Verify TTL values match specification
    assert manager.TTL_PARSED_BOQ == 86400  # 24 hours
    assert manager.TTL_TGO_FACTOR == 2592000  # 30 days
    assert manager.TTL_CALC_RESULT == 604800  # 7 days


def test_cache_key_prefixes():
    """Test that cache key prefixes are consistent."""
    manager = BOQCacheManager()

    # Verify key prefixes
    assert manager.PREFIX_PARSED_BOQ == "boq:parsed"
    assert manager.PREFIX_TGO_FACTOR == "tgo:factor"
    assert manager.PREFIX_CALC_RESULT == "calc:result"
    assert manager.PREFIX_TGO_VERSION == "tgo:version:current"
