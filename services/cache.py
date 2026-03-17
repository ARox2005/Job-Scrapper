import hashlib
import numpy as np
import redis
import config

# Connect to Redis
_redis = redis.Redis.from_url(config.REDIS)

# Embedding dimension for all-MiniLM-L6-v2
EMBEDDING_DIM = 384
CACHE_TTL = 86400  # 24 hours in seconds

def text_hash(text: str) -> str:
    """Generate a SHA-256 hash of the text for use as cache key."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_embedding(key: str) -> np.ndarray | None:
    """Retrieve a cached embedding from Redis. Returns None on cache miss."""
    data = _redis.get(f"emb:{key}")
    if data is None:
        return None
    return np.frombuffer(data, dtype=np.float32)

def set_embedding(key: str, embedding: np.ndarray, ttl: int = CACHE_TTL):
    """Cache an embedding in Redis with a TTL."""
    _redis.set(f"emb:{key}", embedding.astype(np.float32).tobytes(), ex=ttl)