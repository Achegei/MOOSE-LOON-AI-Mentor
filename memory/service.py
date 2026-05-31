"""Persistent learner memory helpers."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from database import models


def _decode_list(value: str | None) -> list[Any]:
    """Decode a JSON list stored in a text column."""
    if not value:
        return []
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return []
    return decoded if isinstance(decoded, list) else []


def _encode_list(value: list[Any]) -> str:
    """Encode a list for storage in a text column."""
    return json.dumps(value)


def get_or_create_memory(db: Session, user: models.User) -> models.UserMemory:
    """Return persisted learner memory, creating it on first use."""
    memory = (
        db.query(models.UserMemory)
        .filter(models.UserMemory.user_id == user.id)
        .first()
    )
    if memory:
        return memory

    memory = models.UserMemory(user_id=user.id, skill_level=user.skill_level)
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


def serialize_memory(memory: models.UserMemory) -> dict[str, Any]:
    """Convert memory row into API-friendly data."""
    return {
        "goals": _decode_list(memory.goals),
        "learning_path": _decode_list(memory.learning_path),
        "active_module": memory.active_module,
        "current_projects": _decode_list(memory.current_projects),
        "skill_level": memory.skill_level,
        "notes": memory.notes,
    }


def update_memory(
    db: Session,
    user: models.User,
    *,
    goals: list[str] | None = None,
    learning_path: list[str] | None = None,
    active_module: str | None = None,
    current_projects: list[str] | None = None,
    skill_level: str | None = None,
    notes: str | None = None,
) -> models.UserMemory:
    """Update learner memory fields and keep user skill level aligned."""
    memory = get_or_create_memory(db, user)
    if goals is not None:
        memory.goals = _encode_list(goals)
    if learning_path is not None:
        memory.learning_path = _encode_list(learning_path)
    if active_module is not None:
        memory.active_module = active_module
    if current_projects is not None:
        memory.current_projects = _encode_list(current_projects)
    if skill_level is not None:
        memory.skill_level = skill_level
        user.skill_level = skill_level
        db.add(user)
    if notes is not None:
        memory.notes = notes

    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory
