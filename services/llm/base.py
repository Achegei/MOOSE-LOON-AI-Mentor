"""
Base LLM service interface.

This abstraction allows swapping LLM providers without changing application code.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            context: Optional context/RAG content
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text.

        Args:
            text: Text to embed

        Returns:
            Vector embedding
        """
        pass

    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate that the API key is working."""
        pass
