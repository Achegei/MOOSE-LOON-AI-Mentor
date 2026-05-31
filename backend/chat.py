"""
Protected mentor chat endpoint with curriculum retrieval and persistence.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from auth.deps import get_current_user, get_db
from config import settings
from services.llm import get_llm_service
from services.rag.chroma_service import ChromaService
from database import models

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)
CURRICULUM_COLLECTION = "curriculum"


class ChatRequest(BaseModel):
    prompt: str
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: int


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


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    llm = get_llm_service()
    logger.info("Chat request received for user_id=%s", user.id)

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

    context = build_curriculum_context(req.prompt)
    reply = await llm.generate_response(req.prompt, context=context)

    mentor_msg = models.Message(conversation_id=conv.id, user_id=user.id, role="mentor", content=reply)
    db.add(mentor_msg)
    db.commit()

    return ChatResponse(reply=reply, conversation_id=conv.id)
