"""Tests for mentor feature helpers."""

from backend.mentor_features import _default_modules


def test_default_modules_cover_required_curriculum_topics() -> None:
    """Starter learning path should cover the v1 educational scope."""
    topics = {item["topic"] for item in _default_modules()}

    assert "AI Literacy" in topics
    assert "Prompt Engineering" in topics
    assert "n8n" in topics
    assert "AI Agents" in topics
    assert "Portfolio" in topics
