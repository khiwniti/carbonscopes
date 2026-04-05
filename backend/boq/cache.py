"""
Multi-layer Redis caching for BOQ analysis.

Layer 1: Parsed BOQ cache (24h TTL)
Layer 2: TGO emission factor cache (30d TTL)
Layer 3: Calculation results cache (7d TTL)
"""

import json
import logging
from typing import Optional, Dict, Any
from decimal import Decimal
import redis

logger = logging.getLogger(__name__)


def get_redis_client() -> redis.Redis:
    """
    Get synchronous Redis client for caching.

    Note: This is separate from the async Redis client in core.services.redis
    which is optimized for real-time streaming. This synchronous client is
    optimized for simple get/set operations in the cache layer.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_password = os.getenv("REDIS_PASSWORD", "")
    redis_username = os.getenv("REDIS_USERNAME", None)
    redis_ssl = os.getenv("REDIS_SSL", "false").lower() == "true"

    return redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password if redis_password else None,
        username=redis_username,
        ssl=redis_ssl,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
        socket_keepalive=True,
        retry_on_timeout=True,
        health_check_interval=30
    )


class BOQCacheManager:
    """
    Manages multi-layer caching for BOQ analysis pipeline.

    Provides:
    - Parsed BOQ caching (reduce parsing overhead)
    - TGO emission factor caching (reduce GraphDB queries)
    - Calculation result caching (reduce computation)
    - Cache invalidation strategies
    """

    # Cache key prefixes
    PREFIX_PARSED_BOQ = "boq:parsed"
    PREFIX_TGO_FACTOR = "tgo:factor"
    PREFIX_CALC_RESULT = "calc:result"
    PREFIX_TGO_VERSION = "tgo:version:current"

    # TTL values (in seconds)
    TTL_PARSED_BOQ = 86400  # 24 hours
    TTL_TGO_FACTOR = 2592000  # 30 days
    TTL_CALC_RESULT = 604800  # 7 days

    def __init__(self):
        """Initialize cache manager with Redis client."""
        try:
            self.redis = get_redis_client()
            # Test connection
            self.redis.ping()
            logger.info("BOQCacheManager initialized successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed, caching will be disabled: {e}")
            self.redis = None

    # ==================== Layer 1: Parsed BOQ Cache ====================

    def cache_parsed_boq(self, file_hash: str, parsed_data: Dict[str, Any]) -> bool:
        """
        Cache parsed BOQ data.

        Args:
            file_hash: SHA256 hash of BOQ file content
            parsed_data: Parsed BOQ structure (from parse_boq function)

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis:
            return False

        try:
            cache_key = f"{self.PREFIX_PARSED_BOQ}:{file_hash}"

            # Serialize with Decimal support
            data_json = json.dumps(parsed_data, default=self._decimal_serializer)

            # Store with 24h TTL
            self.redis.setex(cache_key, self.TTL_PARSED_BOQ, data_json)

            logger.debug(f"Cached parsed BOQ: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache parsed BOQ: {e}")
            return False

    def get_parsed_boq(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached parsed BOQ.

        Args:
            file_hash: SHA256 hash of BOQ file content

        Returns:
            Parsed BOQ data or None if not cached
        """
        if not self.redis:
            return None

        try:
            cache_key = f"{self.PREFIX_PARSED_BOQ}:{file_hash}"
            cached = self.redis.get(cache_key)

            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(cached)

            logger.debug(f"Cache miss: {cache_key}")
            return None

        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None

    # ==================== Layer 2: TGO Emission Factor Cache ====================

    def cache_emission_factor(
        self,
        material_id: str,
        version: str,
        factor_data: Dict[str, Any]
    ) -> bool:
        """
        Cache TGO emission factor.

        Args:
            material_id: TGO material ID (e.g., "tgo:concrete-c30")
            version: TGO version (e.g., "2026-03")
            factor_data: Emission factor data from GraphDB

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis:
            return False

        try:
            cache_key = f"{self.PREFIX_TGO_FACTOR}:{material_id}:{version}"

            # Serialize with Decimal support
            data_json = json.dumps(factor_data, default=self._decimal_serializer)

            # Store with 30d TTL
            self.redis.setex(cache_key, self.TTL_TGO_FACTOR, data_json)

            logger.debug(f"Cached emission factor: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache emission factor: {e}")
            return False

    def get_emission_factor(
        self,
        material_id: str,
        version: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached emission factor.

        Args:
            material_id: TGO material ID
            version: TGO version

        Returns:
            Emission factor data or None if not cached
        """
        if not self.redis:
            return None

        try:
            cache_key = f"{self.PREFIX_TGO_FACTOR}:{material_id}:{version}"
            cached = self.redis.get(cache_key)

            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(cached)

            logger.debug(f"Cache miss: {cache_key}")
            return None

        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None

    # ==================== Layer 3: Calculation Result Cache ====================

    def cache_calculation_result(
        self,
        boq_hash: str,
        tgo_version: str,
        result_data: Dict[str, Any]
    ) -> bool:
        """
        Cache complete calculation result.

        Args:
            boq_hash: SHA256 hash of BOQ file
            tgo_version: TGO version used
            result_data: Complete calculation result

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis:
            return False

        try:
            cache_key = f"{self.PREFIX_CALC_RESULT}:{boq_hash}:{tgo_version}"

            # Serialize with Decimal support
            data_json = json.dumps(result_data, default=self._decimal_serializer)

            # Store with 7d TTL
            self.redis.setex(cache_key, self.TTL_CALC_RESULT, data_json)

            logger.debug(f"Cached calculation result: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache calculation result: {e}")
            return False

    def get_calculation_result(
        self,
        boq_hash: str,
        tgo_version: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached calculation result.

        Args:
            boq_hash: SHA256 hash of BOQ file
            tgo_version: TGO version used

        Returns:
            Calculation result or None if not cached
        """
        if not self.redis:
            return None

        try:
            cache_key = f"{self.PREFIX_CALC_RESULT}:{boq_hash}:{tgo_version}"
            cached = self.redis.get(cache_key)

            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(cached)

            logger.debug(f"Cache miss: {cache_key}")
            return None

        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None

    # ==================== Cache Invalidation ====================

    def invalidate_tgo_version_cache(self, old_version: str, new_version: str):
        """
        Invalidate all caches dependent on TGO version.

        Called when TGO database is updated (e.g., 2026-03 → 2026-06).

        Args:
            old_version: Previous TGO version
            new_version: New TGO version

        Invalidates:
        - All TGO emission factor cache keys for old version
        - All calculation result cache keys referencing old version
        - Parsed BOQ cache is version-independent (no invalidation needed)
        """
        if not self.redis:
            return

        try:
            logger.info(f"Invalidating caches for TGO version: {old_version} → {new_version}")

            # Delete TGO factor cache for old version
            pattern = f"{self.PREFIX_TGO_FACTOR}:*:{old_version}"
            deleted_factors = self._delete_by_pattern(pattern)

            # Delete calculation result cache for old version
            pattern = f"{self.PREFIX_CALC_RESULT}:*:{old_version}"
            deleted_results = self._delete_by_pattern(pattern)

            # Update current version marker
            self.redis.set(self.PREFIX_TGO_VERSION, new_version)

            logger.info(
                f"Cache invalidation complete: "
                f"{deleted_factors} emission factors, "
                f"{deleted_results} calculation results"
            )

        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
            raise

    def invalidate_material_cache(self, material_id: str):
        """
        Invalidate caches for specific material.

        Args:
            material_id: TGO material ID

        Invalidates:
        - TGO emission factor cache for this material (all versions)
        - Calculation results are harder to invalidate by material
          (they are keyed by BOQ hash, not material ID)
        - Recommendation: Let calculation cache expire naturally (7d TTL)
        """
        if not self.redis:
            return

        try:
            logger.info(f"Invalidating cache for material: {material_id}")

            # Delete TGO factor cache for all versions of this material
            pattern = f"{self.PREFIX_TGO_FACTOR}:{material_id}:*"
            deleted = self._delete_by_pattern(pattern)

            logger.info(f"Invalidated {deleted} emission factor cache entries")

        except Exception as e:
            logger.error(f"Material cache invalidation failed: {e}")

    def _delete_by_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Redis key pattern (supports wildcards)

        Returns:
            Number of keys deleted
        """
        if not self.redis:
            return 0

        deleted_count = 0

        try:
            # Use SCAN for safe iteration (won't block Redis)
            cursor = 0
            while True:
                cursor, keys = self.redis.scan(cursor, match=pattern, count=100)

                if keys:
                    self.redis.delete(*keys)
                    deleted_count += len(keys)

                if cursor == 0:
                    break

        except Exception as e:
            logger.error(f"Pattern deletion failed for {pattern}: {e}")

        return deleted_count

    # ==================== Cache Statistics ====================

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.

        Returns:
            Dictionary with cache hit rates, memory usage, etc.
        """
        if not self.redis:
            return {"status": "disabled", "reason": "Redis not available"}

        try:
            info = self.redis.info()

            return {
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}

    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return round(hits / total * 100, 2)

    @staticmethod
    def _decimal_serializer(obj):
        """JSON serializer for Decimal objects."""
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# Singleton instance
_cache_manager = None


def get_cache_manager() -> BOQCacheManager:
    """Get global cache manager instance (singleton)."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = BOQCacheManager()
    return _cache_manager
