"""
Protected mentor chat endpoint with curriculum retrieval and persistence.
"""

import asyncio
import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.deps import get_current_user, get_db
from config import settings
from services.llm import get_llm_service
from services.rag.chroma_service import ChromaService
from services.chat_cache import get_cached_response, store_cached_response
from database import models

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)
CURRICULUM_COLLECTION = "curriculum"

CHAT_MODES = {
    "quick": {
        "label": "Quick Answer",
        "rag_k": 1,
        "max_tokens": 450,
        "model": settings.LLM_FAST_MODEL,
        "instruction": "Answer in 5 bullets or fewer. Be direct, practical, and mentor-like. No long intro.",
        "cache_ttl_days": 3,
        "timeout_seconds": 8,
    },
    "deep": {
        "label": "Deep Research",
        "rag_k": 5,
        "max_tokens": 1800,
        "model": settings.LLM_MODEL,
        "instruction": "Give a structured mentor response with explanation, roadmap, tradeoffs, and next actions.",
        "cache_ttl_days": 7,
        "timeout_seconds": None,
    },
}


class ChatRequest(BaseModel):
    prompt: str
    conversation_id: int | None = None
    mode: str = "quick"


class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    mode: str
    cached: bool = False
    fallback: bool = False


def build_curriculum_context(prompt: str, k: int = 4) -> str | None:
    """Retrieve curriculum snippets for the mentor prompt."""
    try:
        retriever = ChromaService(persist_directory=settings.CHROMA_DB_PATH)
        results = retriever.query(CURRICULUM_COLLECTION, prompt, k=k)
    except Exception:
        logger.exception("Curriculum retrieval failed")
        return None

    snippets: list[str] = []
    if isinstance(results, dict):
        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []
        first_documents = documents[0] if documents else []
        first_metadatas = metadatas[0] if metadatas else []
        for index, document in enumerate(first_documents):
            metadata = first_metadatas[index] if index < len(first_metadatas) else {}
            source = metadata.get("source", "curriculum")
            snippets.append(f"Source: {source}\n{document}")
    elif isinstance(results, list):
        for item in results:
            text = item.get("text")
            if not text:
                continue
            metadata = item.get("metadata", {})
            source = metadata.get("source", "curriculum")
            snippets.append(f"Source: {source}\n{text}")

    if not snippets:
        logger.info("No curriculum context found for chat request")
        return None

    logger.info("Retrieved %s curriculum snippets for chat request", len(snippets))
    return "\n\n---\n\n".join(snippets)


def build_quick_fallback(prompt: str, context: str | None) -> str:
    """Build a fast, curriculum-grounded answer when the quick LLM path is slow."""
    if not context:
        short_prompt = prompt.strip()[:120] or "your question"
        return (
            "Quick answer:\n"
            f"- I can help with {short_prompt!r}, but I do not have enough curriculum context loaded for a precise answer yet.\n"
            "- Try asking with the topic, your skill level, and what you are building.\n"
            "- For a more complete response, switch to Deep Research."
        )

    cleaned_context = re.sub(r"Source:\s*.*\n", "", context).strip()
    cleaned_context = re.sub(r"\s+", " ", cleaned_context)
    summary = cleaned_context[:650].strip()
    if len(cleaned_context) > 650:
        summary = f"{summary.rstrip()}..."

    return (
        "Quick answer:\n"
        f"- Based on the curriculum, focus on this: {summary}\n"
        "- Turn it into one small practice task so you can apply it immediately.\n"
        "- If you want a full explanation, roadmap, and examples, use Deep Research."
    )


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    llm = get_llm_service()
    mode = req.mode if req.mode in CHAT_MODES else "quick"
    mode_config = CHAT_MODES[mode]
    logger.info("Chat request received for user_id=%s mode=%s", user.id, mode)

    # Persist conversation and user prompt before generating a response.
    if req.conversation_id:
        conv = (
            db.query(models.Conversation)
            .filter(
                models.Conversation.id == req.conversation_id,
                models.Conversation.user_id == user.id,
            )
            .first()
        )
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = models.Conversation(user_id=user.id, title=(req.prompt[:80] if req.prompt else "Chat"))
        db.add(conv)
        db.commit()
        db.refresh(conv)

    user_msg = models.Message(conversation_id=conv.id, user_id=user.id, role="user", content=req.prompt)
    db.add(user_msg)
    db.commit()

    context = build_curriculum_context(req.prompt, k=mode_config["rag_k"])
    cached_reply = get_cached_response(
        db,
        prompt=req.prompt,
        mode=mode,
        context=context,
    )
    if cached_reply:
        reply = cached_reply
        cached = True
        fallback = False
    else:
        prompt = f"{mode_config['instruction']}\n\nLearner question:\n{req.prompt}"
        try:
            response_task = llm.generate_response(
                prompt,
                context=context,
                max_tokens=mode_config["max_tokens"],
                model=mode_config["model"],
            )
            timeout_seconds = mode_config.get("timeout_seconds")
            if timeout_seconds:
                reply = await asyncio.wait_for(response_task, timeout=timeout_seconds)
            else:
                reply = await response_task
            fallback = False
        except asyncio.TimeoutError:
            if mode != "quick":
                raise
            logger.warning("Quick chat timed out for user_id=%s; returning curriculum fallback", user.id)
            reply = build_quick_fallback(req.prompt, context)
            fallback = True
        except Exception:
            if mode != "quick":
                raise
            logger.exception("Quick chat generation failed for user_id=%s; returning curriculum fallback", user.id)
            reply = build_quick_fallback(req.prompt, context)
            fallback = True

        cached = False
        if not fallback:
            store_cached_response(
                db,
                prompt=req.prompt,
                mode=mode,
                context=context,
                response=reply,
                ttl_days=mode_config["cache_ttl_days"],
            )

    mentor_msg = models.Message(conversation_id=conv.id, user_id=user.id, role="mentor", content=reply)
    db.add(mentor_msg)
    db.commit()

    return ChatResponse(reply=reply, conversation_id=conv.id, mode=mode, cached=cached, fallback=fallback)
