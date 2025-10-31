"""
Cache interface with in-memory and Redis implementations.
Provides unified caching API with TTL support.
"""

import json
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, Optional

import structlog

from src.core.config import settings

logger = structlog.get_logger(__name__)


class CacheInterface(ABC):
    """Abstract cache interface."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL (seconds)."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern. Returns count deleted."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check cache health."""
        pass


class InMemoryCache(CacheInterface):
    """
    In-memory LRU cache with TTL support.
    Good for MVP and testing. Single-instance only (not shared across workers).
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 86400):
        """
        Initialize in-memory cache.

        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        logger.info("in_memory_cache_initialized", max_size=max_size, default_ttl=default_ttl)

    def _is_expired(self, expiry: float) -> bool:
        """Check if entry is expired."""
        return time.time() > expiry

    def _evict_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        keys_to_delete = [
            key for key, (_, expiry) in self._cache.items() if current_time > expiry
        ]
        for key in keys_to_delete:
            del self._cache[key]

    def _evict_lru(self) -> None:
        """Remove least recently used entry."""
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)  # Remove oldest (least recently used)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        self._evict_expired()

        if key not in self._cache:
            logger.debug("cache_miss", key=key, cache_type="in_memory")
            return None

        value, expiry = self._cache[key]

        if self._is_expired(expiry):
            del self._cache[key]
            logger.debug("cache_expired", key=key)
            return None

        # Move to end (mark as recently used)
        self._cache.move_to_end(key)
        logger.debug("cache_hit", key=key, cache_type="in_memory")
        return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        self._evict_expired()
        self._evict_lru()

        ttl_seconds = ttl or self.default_ttl
        expiry = time.time() + ttl_seconds

        self._cache[key] = (value, expiry)
        self._cache.move_to_end(key)  # Mark as recently used

        logger.debug(
            "cache_set", key=key, ttl=ttl_seconds, cache_type="in_memory", size=len(self._cache)
        )
        return True

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug("cache_delete", key=key, cache_type="in_memory")
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        value = await self.get(key)
        return value is not None

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern (simple substring match)."""
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        count = len(keys_to_delete)

        for key in keys_to_delete:
            del self._cache[key]

        logger.info(
            "cache_invalidate_pattern",
            pattern=pattern,
            count=count,
            cache_type="in_memory",
        )
        return count

    async def clear(self) -> bool:
        """Clear all entries."""
        self._cache.clear()
        logger.info("cache_cleared", cache_type="in_memory")
        return True

    async def health_check(self) -> Dict[str, Any]:
        """Check cache health."""
        self._evict_expired()
        return {
            "status": "healthy",
            "type": "in_memory",
            "size": len(self._cache),
            "max_size": self.max_size,
        }


class RedisCache(CacheInterface):
    """
    Redis-based cache for multi-instance deployments.
    Requires Redis server.
    """

    def __init__(self, redis_url: str, default_ttl: int = 86400):
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._redis: Optional[Any] = None
        logger.info("redis_cache_initializing", url=redis_url)

    @property
    def redis(self) -> Any:
        """Lazy-load Redis client."""
        if self._redis is None:
            try:
                import redis.asyncio as redis

                self._redis = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=settings.redis_max_connections,
                )
                logger.info("redis_client_initialized")
            except ImportError:
                logger.error("redis_not_installed")
                raise ImportError(
                    "redis is required for RedisCache. Install with: uv pip install redis"
                )
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value is None:
                logger.debug("cache_miss", key=key, cache_type="redis")
                return None

            # Deserialize JSON
            logger.debug("cache_hit", key=key, cache_type="redis")
            return json.loads(value)
        except Exception as e:
            logger.error("redis_get_failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            ttl_seconds = ttl or self.default_ttl

            # Serialize to JSON
            serialized = json.dumps(value)

            await self.redis.setex(key, ttl_seconds, serialized)
            logger.debug("cache_set", key=key, ttl=ttl_seconds, cache_type="redis")
            return True
        except Exception as e:
            logger.error("redis_set_failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            result = await self.redis.delete(key)
            logger.debug("cache_delete", key=key, deleted=result > 0, cache_type="redis")
            return result > 0
        except Exception as e:
            logger.error("redis_delete_failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error("redis_exists_failed", key=key, error=str(e))
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern (Redis glob pattern)."""
        try:
            # Use SCAN to find keys matching pattern
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                count = await self.redis.delete(*keys)
            else:
                count = 0

            logger.info(
                "cache_invalidate_pattern",
                pattern=pattern,
                count=count,
                cache_type="redis",
            )
            return count
        except Exception as e:
            logger.error("redis_invalidate_pattern_failed", pattern=pattern, error=str(e))
            return 0

    async def clear(self) -> bool:
        """Clear all entries (FLUSHDB)."""
        try:
            await self.redis.flushdb()
            logger.warning("cache_cleared", cache_type="redis")
            return True
        except Exception as e:
            logger.error("redis_clear_failed", error=str(e))
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check Redis health."""
        try:
            await self.redis.ping()
            info = await self.redis.info("stats")

            return {
                "status": "healthy",
                "type": "redis",
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
            }
        except Exception as e:
            logger.error("redis_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "type": "redis",
                "error": str(e),
            }


# Singleton cache instance
_cache: Optional[CacheInterface] = None


def get_cache() -> CacheInterface:
    """
    Get cache instance (singleton).

    Returns appropriate cache based on settings.cache_type.
    """
    global _cache

    if _cache is None:
        if settings.cache_type == "redis" and settings.redis_url:
            _cache = RedisCache(
                redis_url=str(settings.redis_url),
                default_ttl=settings.cache_default_ttl,
            )
        else:
            _cache = InMemoryCache(
                max_size=settings.query_result_cache_size,
                default_ttl=settings.cache_default_ttl,
            )

        logger.info("cache_initialized", cache_type=settings.cache_type)

    return _cache


# Convenience functions for cache key generation
def build_dashboard_cache_key(slug: str, query_hash: str, version: int) -> str:
    """Build cache key for dashboard query results."""
    return f"dashboard:{slug}:query:{query_hash}:v{version}"


def build_lineage_cache_key(slug: str) -> str:
    """Build cache key for lineage graph."""
    return f"lineage:{slug}"


def build_metadata_cache_key(slug: str) -> str:
    """Build cache key for dashboard metadata."""
    return f"metadata:{slug}"
