"""LLM service abstraction layer."""

from config import settings
from .openai_service import OpenAIService
from .stub import StubLLMService


def get_llm_service():
    """Return the appropriate LLM service implementation.

    Uses OpenAI when an API key is configured and the package is available.
    Otherwise falls back to a local stub service for development and testing.
    """
    if settings.OPENAI_API_KEY:
        try:
            return OpenAIService()
        except RuntimeError:
            return StubLLMService()
    return StubLLMService()
