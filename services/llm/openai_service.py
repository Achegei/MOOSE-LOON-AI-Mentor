"""
OpenAI LLM service implementation.

Provides integration with OpenAI API for the mentoring platform.
"""

import asyncio
import logging
from typing import Optional, List

from config import settings
from .base import BaseLLMService

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None

logger = logging.getLogger(__name__)


class OpenAIService(BaseLLMService):
    """OpenAI implementation of LLM service."""

    def __init__(self):
        """Initialize OpenAI service."""
        if openai is None:
            raise RuntimeError("OpenAI package is not installed. Install it with 'pip install openai'.")
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set in environment")
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response using OpenAI API.

        Args:
            prompt: The user prompt
            context: Optional context for RAG
            temperature: Temperature for response
            max_tokens: Maximum tokens in response

        Returns:
            Generated response
        """
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE

        # Construct full prompt with context if provided
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"

        if openai is None:
            raise RuntimeError("OpenAI package is not installed; install it with 'pip install openai'.")

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are MOOSE LOON, an expert AI mentor. Teach, explain, guide, and mentor learners about AI and automation. Always be clear, supportive, and optimize for learning.",
                    },
                    {"role": "user", "content": full_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens or 2000,
            )
            message = response.choices[0].message
            if isinstance(message, dict):
                return message.get("content", "")
            return getattr(message, "content", "")
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {e}")
            raise

    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using OpenAI API.

        Args:
            text: Text to embed

        Returns:
            Vector embedding
        """
        if openai is None:
            raise RuntimeError("OpenAI package is not installed; install it with 'pip install openai'.")

        try:
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                input=text,
                model="text-embedding-3-small",
            )
            embedding = response.data[0].embedding
            return getattr(embedding, "tolist", lambda: embedding)()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    async def validate_api_key(self) -> bool:
        """
        Validate OpenAI API key.

        Returns:
            True if valid, False otherwise
        """
        if openai is None:
            logger.error("OpenAI package is not installed; validate it after installing openai.")
            return False

        try:
            await asyncio.to_thread(self.client.models.retrieve, settings.LLM_MODEL)
            return True
        except Exception as e:
            logger.error(f"OpenAI API key validation failed: {e}")
            return False
