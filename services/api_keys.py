"""Developer API key generation, hashing, and validation."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime

from sqlalchemy.orm import Session

from database import models
from services.billing import get_or_create_subscription, get_tier


KEY_PREFIX = "mlm"


def hash_api_key(api_key: str) -> str:
    """Hash an API key before storage."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    """Generate a new integration API key."""
    return f"{KEY_PREFIX}_{secrets.token_urlsafe(32)}"


def create_api_key(db: Session, user_id: int, name: str) -> tuple[models.DeveloperApiKey, str]:
    """Create a hashed API key and return the one-time plain secret."""
    subscription = get_or_create_subscription(db, user_id)
    tier_config = get_tier(subscription.tier)
    allowed_keys = tier_config["api_keys"]
    active_count = (
        db.query(models.DeveloperApiKey)
        .filter(
            models.DeveloperApiKey.user_id == user_id,
            models.DeveloperApiKey.revoked == False,
        )
        .count()
    )
    if allowed_keys <= active_count:
        raise PermissionError("API key limit reached for this tier")
    if tier_config["monthly_api_calls"] <= 0:
        raise PermissionError("Upgrade required for API access")

    plain_key = generate_api_key()
    key = models.DeveloperApiKey(
        user_id=user_id,
        name=name,
        key_prefix=plain_key[:12],
        key_hash=hash_api_key(plain_key),
        tier=subscription.tier,
        monthly_limit=tier_config["monthly_api_calls"],
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return key, plain_key


def list_api_keys(db: Session, user_id: int) -> list[models.DeveloperApiKey]:
    """List API keys for a user."""
    return (
        db.query(models.DeveloperApiKey)
        .filter(models.DeveloperApiKey.user_id == user_id)
        .order_by(models.DeveloperApiKey.created_at.desc())
        .all()
    )


def revoke_api_key(db: Session, user_id: int, key_id: int) -> bool:
    """Revoke a user's API key."""
    key = (
        db.query(models.DeveloperApiKey)
        .filter(
            models.DeveloperApiKey.id == key_id,
            models.DeveloperApiKey.user_id == user_id,
        )
        .first()
    )
    if not key:
        return False
    key.revoked = True
    db.add(key)
    db.commit()
    return True


def authenticate_api_key(db: Session, api_key: str) -> models.DeveloperApiKey | None:
    """Validate an API key and increment usage."""
    key_hash = hash_api_key(api_key)
    key = (
        db.query(models.DeveloperApiKey)
        .filter(
            models.DeveloperApiKey.key_hash == key_hash,
            models.DeveloperApiKey.revoked == False,
        )
        .first()
    )
    if not key:
        return None
    if key.requests_this_month >= key.monthly_limit:
        raise PermissionError("Monthly API limit reached")

    key.requests_this_month += 1
    key.last_used_at = datetime.utcnow()
    db.add(key)
    db.commit()
    db.refresh(key)
    return key
