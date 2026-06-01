"""Database-backed cache for repeated mentor chat responses."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from database import models


def context_hash(context: str | None) -> str:
    """Hash retrieved context for cache identity."""
    return hashlib.sha256((context or "").encode("utf-8")).hexdigest()


def build_cache_key(prompt: str, mode: str, context: str | None) -> tuple[str, str]:
    """Build a stable cache key for a prompt, mode, and context."""
    normalized_prompt = " ".join(prompt.lower().split())
    ctx_hash = context_hash(context)
    raw_key = f"{mode}:{normalized_prompt}:{ctx_hash}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest(), ctx_hash


def get_cached_response(
    db: Session,
    *,
    prompt: str,
    mode: str,
    context: str | None,
) -> str | None:
    """Return a non-expired cached response when available."""
    cache_key, _ = build_cache_key(prompt, mode, context)
    cached = (
        db.query(models.ChatResponseCache)
        .filter(
            models.ChatResponseCache.cache_key == cache_key,
            models.ChatResponseCache.expires_at > datetime.utcnow(),
        )
        .first()
    )
    return cached.response if cached else None


def store_cached_response(
    db: Session,
    *,
    prompt: str,
    mode: str,
    context: str | None,
    response: str,
    ttl_days: int = 3,
) -> None:
    """Persist a cacheable mentor response."""
    cache_key, ctx_hash = build_cache_key(prompt, mode, context)
    cached = (
        db.query(models.ChatResponseCache)
        .filter(models.ChatResponseCache.cache_key == cache_key)
        .first()
    )
    if cached:
        cached.response = response
        cached.expires_at = datetime.utcnow() + timedelta(days=ttl_days)
    else:
        cached = models.ChatResponseCache(
            cache_key=cache_key,
            prompt=prompt,
            mode=mode,
            context_hash=ctx_hash,
            response=response,
            expires_at=datetime.utcnow() + timedelta(days=ttl_days),
        )
    db.add(cached)
    db.commit()
