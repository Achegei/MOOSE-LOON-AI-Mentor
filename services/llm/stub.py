"""
Simple LLM stub service used for local development and testing.
"""
from typing import Optional, List
from .base import BaseLLMService


class StubLLMService(BaseLLMService):
    async def generate_response(self, prompt: str, context: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None, model: Optional[str] = None) -> str:
        # Minimal deterministic response for testing
        ctx = f"\nContext: {context}" if context else ""
        model_note = f"\nModel: {model}" if model else ""
        limit_note = f"\nMax tokens: {max_tokens}" if max_tokens else ""
        return f"[STUB RESPONSE] Prompt: {prompt}{ctx}{model_note}{limit_note}\n\nTry integrating a real LLM service in services/llm/."

    async def generate_embeddings(self, text: str) -> List[float]:
        # Return a tiny deterministic vector
        return [float(len(text))]

    async def validate_api_key(self) -> bool:
        return True
