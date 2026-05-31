"""Tests for authentication response schemas."""

from auth.schemas import Token, UserRead


def test_token_schema_includes_refresh_token() -> None:
    """Login responses must expose refresh tokens for the frontend."""
    token = Token(
        access_token="access",
        refresh_token="refresh",
        token_type="bearer",
    )

    assert token.refresh_token == "refresh"
    assert "refresh_token" in token.model_dump()


def test_user_read_uses_pydantic_v2_attributes() -> None:
    """UserRead should support SQLAlchemy model serialization."""
    assert UserRead.model_config.get("from_attributes") is True
