"""Repository secret hygiene checks."""

from pathlib import Path


def test_env_example_does_not_include_real_openai_key() -> None:
    """Example environment files must not expose real API keys."""
    env_example = Path(".env.example").read_text(encoding="utf-8")

    assert "OPENAI_API_KEY=sk-" not in env_example
    assert "sk-proj-" not in env_example
