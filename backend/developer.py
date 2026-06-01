"""Billing and developer API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.deps import get_current_user, get_db
from backend.chat import build_curriculum_context
from services.api_keys import authenticate_api_key, create_api_key, list_api_keys, revoke_api_key
from services.billing import get_or_create_subscription, get_tier, list_tiers, set_subscription_tier
from services.llm import get_llm_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["developer"])


class TierUpdateRequest(BaseModel):
    """Subscription tier update request."""

    tier: str


class ApiKeyCreateRequest(BaseModel):
    """API key creation request."""

    name: str


class IntegrationChatRequest(BaseModel):
    """External mentor API chat request."""

    prompt: str
    learner_context: str | None = None


def _serialize_key(key) -> dict:
    """Return safe API key metadata."""
    return {
        "id": key.id,
        "name": key.name,
        "key_prefix": key.key_prefix,
        "tier": key.tier,
        "monthly_limit": key.monthly_limit,
        "requests_this_month": key.requests_this_month,
        "revoked": key.revoked,
        "created_at": key.created_at.isoformat() if key.created_at else None,
        "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
    }


@router.get("/billing/tiers")
def billing_tiers():
    """Return SaaS pricing tiers."""
    return {"tiers": list_tiers()}


@router.get("/billing/subscription")
def current_subscription(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Return the current user's subscription."""
    subscription = get_or_create_subscription(db, user.id)
    tier = get_tier(subscription.tier)
    return {
        "tier": subscription.tier,
        "status": subscription.status,
        "plan": {"id": subscription.tier, **tier},
    }


@router.post("/billing/subscription")
def update_subscription(
    req: TierUpdateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Set a subscription tier.

    This is a product-ready placeholder for billing provider integration. In
    production, replace this direct update with a checkout/webhook flow.
    """
    try:
        subscription = set_subscription_tier(db, user.id, req.tier)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    logger.info("Updated subscription tier for user_id=%s tier=%s", user.id, req.tier)
    return {"tier": subscription.tier, "status": subscription.status}


@router.get("/developer/api-keys")
def get_api_keys(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """List developer API keys for the current user."""
    subscription = get_or_create_subscription(db, user.id)
    keys = list_api_keys(db, user.id)
    return {
        "subscription": {
            "tier": subscription.tier,
            "plan": get_tier(subscription.tier),
        },
        "api_keys": [_serialize_key(key) for key in keys],
    }


@router.post("/developer/api-keys")
def create_developer_api_key(
    req: ApiKeyCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a developer API key and return the secret once."""
    try:
        key, plain_key = create_api_key(db, user.id, req.name)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    logger.info("Created developer API key id=%s for user_id=%s", key.id, user.id)
    return {"api_key": plain_key, "key": _serialize_key(key)}


@router.delete("/developer/api-keys/{key_id}")
def delete_developer_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Revoke a developer API key."""
    if not revoke_api_key(db, user.id, key_id):
        raise HTTPException(status_code=404, detail="API key not found")
    logger.info("Revoked developer API key id=%s for user_id=%s", key_id, user.id)
    return {"status": "revoked"}


@router.post("/v1/mentor/chat")
async def integration_mentor_chat(
    req: IntegrationChatRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
):
    """External API endpoint for systems integrating with the mentor."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )
    try:
        key = authenticate_api_key(db, x_api_key)
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    context_parts = []
    curriculum_context = build_curriculum_context(req.prompt)
    if curriculum_context:
        context_parts.append(curriculum_context)
    if req.learner_context:
        context_parts.append(f"External learner context:\n{req.learner_context}")

    reply = await get_llm_service().generate_response(
        req.prompt,
        context="\n\n---\n\n".join(context_parts) if context_parts else None,
    )
    logger.info("External mentor API request served for api_key_id=%s", key.id)
    return {
        "reply": reply,
        "usage": {
            "monthly_limit": key.monthly_limit,
            "requests_this_month": key.requests_this_month,
        },
    }
