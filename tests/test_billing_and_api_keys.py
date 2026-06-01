"""Tests for monetization tier and API key primitives."""

from services.api_keys import generate_api_key, hash_api_key
from services.billing import get_tier, list_tiers


def test_tiers_include_paid_api_access() -> None:
    """Paid tiers should expose API key capacity."""
    tiers = {tier["id"]: tier for tier in list_tiers()}

    assert tiers["free"]["api_keys"] == 1
    assert tiers["free"]["monthly_api_calls"] == 50
    assert tiers["builder"]["api_keys"] > 0
    assert tiers["pro"]["monthly_api_calls"] > tiers["builder"]["monthly_api_calls"]


def test_unknown_tier_falls_back_to_free() -> None:
    """Unknown tiers should not grant paid capability."""
    assert get_tier("missing")["name"] == "Free"


def test_generated_api_key_is_prefixed_and_hashed() -> None:
    """Developer API keys should be recognizable and stored as hashes."""
    key = generate_api_key()
    hashed = hash_api_key(key)

    assert key.startswith("mlm_")
    assert key not in hashed
    assert len(hashed) == 64
