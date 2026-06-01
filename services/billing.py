"""SaaS tier definitions and subscription helpers."""

from __future__ import annotations

from sqlalchemy.orm import Session

from config import settings
from database import models


TIER_ORDER = ("free", "builder", "pro", "team")

TIERS: dict[str, dict] = {
    "free": {
        "name": "Free",
        "price": "$0",
        "description": "Explore the mentor workspace and test one small integration.",
        "features": [
            "Mentor chat with curriculum grounding",
            "Learning path recommendations",
            "Basic progress tracking",
            "Trial developer API access",
        ],
        "api_keys": 1,
        "monthly_api_calls": 50,
    },
    "builder": {
        "name": "Builder",
        "price": "$19/mo",
        "description": "For learners building projects and practicing every week.",
        "features": [
            "Everything in Free",
            "Assignment and mini-project generation",
            "Project coach and portfolio review",
            "Developer API access",
        ],
        "api_keys": 2,
        "monthly_api_calls": 1_000,
    },
    "pro": {
        "name": "Pro",
        "price": "$49/mo",
        "description": "For career changers, developers, and automation builders.",
        "features": [
            "Everything in Builder",
            "Higher API limits",
            "Portfolio and career roadmap workflows",
            "Priority project coaching capacity",
        ],
        "api_keys": 10,
        "monthly_api_calls": 10_000,
    },
    "team": {
        "name": "Team",
        "price": "$149/mo",
        "description": "For cohorts, teams, and training programs.",
        "features": [
            "Everything in Pro",
            "Shared learning and automation enablement",
            "Team integration keys",
            "Higher usage allowance",
        ],
        "api_keys": 50,
        "monthly_api_calls": 50_000,
    },
}


CHECKOUT_URLS = {
    "builder": settings.BILLING_CHECKOUT_BUILDER_URL,
    "pro": settings.BILLING_CHECKOUT_PRO_URL,
    "team": settings.BILLING_CHECKOUT_TEAM_URL,
}


def list_tiers() -> list[dict]:
    """Return public tier data."""
    return [{"id": tier_id, **tier} for tier_id, tier in TIERS.items()]


def get_tier(tier_id: str) -> dict:
    """Return tier config, falling back to Free."""
    return TIERS.get(tier_id, TIERS["free"])


def get_checkout_url(tier_id: str) -> str | None:
    """Return the configured checkout URL for a paid tier."""
    return CHECKOUT_URLS.get(tier_id)


def tier_allows(current_tier: str, minimum_tier: str) -> bool:
    """Return whether a tier includes a minimum tier entitlement."""
    try:
        return TIER_ORDER.index(current_tier) >= TIER_ORDER.index(minimum_tier)
    except ValueError:
        return False


def get_or_create_subscription(db: Session, user_id: int) -> models.UserSubscription:
    """Return a user's subscription row."""
    subscription = (
        db.query(models.UserSubscription)
        .filter(models.UserSubscription.user_id == user_id)
        .first()
    )
    if subscription:
        return subscription

    subscription = models.UserSubscription(user_id=user_id, tier="free", status="active")
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def set_subscription_tier(
    db: Session,
    user_id: int,
    tier: str,
) -> models.UserSubscription:
    """Set a user's current tier."""
    if tier not in TIERS:
        raise ValueError("Unknown tier")
    subscription = get_or_create_subscription(db, user_id)
    subscription.tier = tier
    subscription.status = "active"
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def require_subscription_tier(db: Session, user_id: int, minimum_tier: str) -> models.UserSubscription:
    """Require an active subscription at or above a tier."""
    subscription = get_or_create_subscription(db, user_id)
    current_tier = subscription.tier if subscription.status == "active" else "free"
    if not tier_allows(current_tier, minimum_tier):
        required = get_tier(minimum_tier)["name"]
        raise PermissionError(f"{required} plan or higher required for this feature")
    return subscription
