"""Authenticated mentor feature endpoints for learning, projects, and progress."""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth.deps import get_current_user, get_db
from backend.chat import build_curriculum_context
from database import models
from memory.service import get_or_create_memory, serialize_memory, update_memory
from services.billing import require_subscription_tier
from services.llm import get_llm_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["mentor"])


class GoalsRequest(BaseModel):
    """Learner goals and level update payload."""

    goals: list[str] = Field(default_factory=list)
    skill_level: str = "beginner"
    notes: str | None = None


class AssignmentRequest(BaseModel):
    """Assignment generation request."""

    topic: str = "AI Literacy"
    assignment_type: str = "exercise"
    difficulty: str | None = None


class ProjectRequest(BaseModel):
    """Project recommendation request."""

    goal: str = "Build a portfolio project"
    difficulty: str | None = None


class PortfolioReviewRequest(BaseModel):
    """Portfolio review request."""

    project_title: str
    project_description: str
    repository_url: str | None = None


class ProgressUpdateRequest(BaseModel):
    """Progress update request."""

    module_id: int
    progress_percentage: float = Field(ge=0, le=100)
    completed: bool = False


def _default_modules() -> list[dict[str, str]]:
    """Return curriculum path defaults when DB modules are empty."""
    return [
        {
            "title": "AI Literacy Foundations",
            "topic": "AI Literacy",
            "difficulty": "beginner",
            "next_action": "Learn core AI terms and where human verification is required.",
        },
        {
            "title": "Prompt Engineering",
            "topic": "Prompt Engineering",
            "difficulty": "beginner",
            "next_action": "Practice role, task, context, constraints, and output format.",
        },
        {
            "title": "APIs For Automation",
            "topic": "APIs",
            "difficulty": "beginner",
            "next_action": "Understand endpoints, methods, headers, JSON, and status codes.",
        },
        {
            "title": "n8n Workflow Automation",
            "topic": "n8n",
            "difficulty": "intermediate",
            "next_action": "Build a webhook workflow with data mapping and error handling.",
        },
        {
            "title": "AI Agents",
            "topic": "AI Agents",
            "difficulty": "intermediate",
            "next_action": "Design an agent with clear tools, memory, and safety rules.",
        },
        {
            "title": "Portfolio Project",
            "topic": "Portfolio",
            "difficulty": "intermediate",
            "next_action": "Package one project with setup steps, screenshots, and tradeoffs.",
        },
    ]


def _module_catalog(db: Session) -> list[dict[str, str]]:
    """Return DB curriculum modules or starter curriculum modules."""
    modules = db.query(models.LearningModule).order_by(models.LearningModule.order).all()
    if not modules:
        return _default_modules()
    return [
        {
            "id": str(module.id),
            "title": module.title,
            "topic": module.topic or "AI",
            "difficulty": module.difficulty or "beginner",
            "next_action": module.description or "Study the lesson and complete one practice task.",
        }
        for module in modules
    ]


def _require_plan(db: Session, user, minimum_tier: str) -> None:
    """Convert subscription entitlement failures into API responses."""
    try:
        require_subscription_tier(db, user.id, minimum_tier)
    except PermissionError as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc


@router.get("/learning-path")
def get_learning_path(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Generate a personalized next-step learning path."""
    memory = get_or_create_memory(db, user)
    completed_ids = {
        progress.module_id
        for progress in db.query(models.UserProgress)
        .filter(
            models.UserProgress.user_id == user.id,
            models.UserProgress.completed == True,
        )
        .all()
    }
    path = []
    for item in _module_catalog(db):
        item_id = int(item["id"]) if item.get("id", "").isdigit() else None
        if item_id and item_id in completed_ids:
            continue
        path.append(item)

    path_titles = [item["title"] for item in path]
    update_memory(db, user, learning_path=path_titles[:6], skill_level=memory.skill_level)
    logger.info("Generated learning path for user_id=%s", user.id)
    return {"skill_level": user.skill_level, "recommendations": path[:6]}


@router.post("/memory/goals")
def save_goals(req: GoalsRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Persist learner goals and skill level."""
    memory = update_memory(
        db,
        user,
        goals=req.goals,
        skill_level=req.skill_level,
        notes=req.notes,
    )
    logger.info("Updated learner memory for user_id=%s", user.id)
    return serialize_memory(memory)


@router.post("/assignments/generate")
async def generate_assignment(
    req: AssignmentRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Generate and persist a level-matched assignment."""
    _require_plan(db, user, "builder")
    difficulty = req.difficulty or user.skill_level
    context = build_curriculum_context(req.topic)
    prompt = (
        "Create one practical AI and automation learning assignment. "
        f"Topic: {req.topic}. Type: {req.assignment_type}. "
        f"Difficulty: {difficulty}. Include objective, steps, deliverable, and rubric."
    )
    content = await get_llm_service().generate_response(prompt, context=context)
    assignment = models.Assignment(
        user_id=user.id,
        title=f"{difficulty.title()} {req.topic} {req.assignment_type.title()}",
        description=f"A {difficulty} {req.assignment_type} for {req.topic}.",
        difficulty=difficulty,
        content=content,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    logger.info("Generated assignment id=%s for user_id=%s", assignment.id, user.id)
    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "difficulty": assignment.difficulty,
        "content": assignment.content,
    }


@router.post("/projects/recommend")
async def recommend_project(
    req: ProjectRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Recommend and persist a portfolio project plan."""
    _require_plan(db, user, "builder")
    difficulty = req.difficulty or user.skill_level
    context = build_curriculum_context(req.goal)
    prompt = (
        "Recommend one portfolio project for an AI and automation learner. "
        f"Goal: {req.goal}. Difficulty: {difficulty}. "
        "Return problem, users, features, tech stack, milestones, and portfolio proof."
    )
    description = await get_llm_service().generate_response(prompt, context=context)
    project = models.Project(
        user_id=user.id,
        title=f"{difficulty.title()} AI Automation Portfolio Project",
        description=description,
        status="planning",
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    memory = get_or_create_memory(db, user)
    projects = serialize_memory(memory)["current_projects"]
    projects.append(project.title)
    update_memory(db, user, current_projects=projects)
    logger.info("Recommended project id=%s for user_id=%s", project.id, user.id)
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
    }


@router.post("/portfolio-review")
async def review_portfolio(
    req: PortfolioReviewRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Review submitted portfolio content as a senior mentor."""
    _require_plan(db, user, "pro")
    context = build_curriculum_context("career portfolio project review")
    prompt = (
        "Review this AI and automation portfolio project for a beginner or intermediate learner. "
        f"Title: {req.project_title}. Description: {req.project_description}. "
        f"Repository: {req.repository_url or 'not provided'}. "
        "Return strengths, weaknesses, improvements, README advice, and next portfolio step."
    )
    review = await get_llm_service().generate_response(prompt, context=context)
    logger.info("Reviewed portfolio submission for user_id=%s", user.id)
    return {"review": review}


@router.get("/progress/summary")
def progress_summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Return learner progress, projects, assignments, and memory."""
    memory = get_or_create_memory(db, user)
    progress_rows = (
        db.query(models.UserProgress)
        .filter(models.UserProgress.user_id == user.id)
        .all()
    )
    assignments = (
        db.query(models.Assignment)
        .filter(models.Assignment.user_id == user.id)
        .order_by(models.Assignment.created_at.desc())
        .limit(10)
        .all()
    )
    projects = (
        db.query(models.Project)
        .filter(models.Project.user_id == user.id)
        .order_by(models.Project.created_at.desc())
        .limit(10)
        .all()
    )
    return {
        "memory": serialize_memory(memory),
        "progress": [
            {
                "module_id": row.module_id,
                "progress_percentage": row.progress_percentage,
                "completed": row.completed,
            }
            for row in progress_rows
        ],
        "assignments": [
            {"id": item.id, "title": item.title, "submitted": item.submitted}
            for item in assignments
        ],
        "projects": [
            {"id": item.id, "title": item.title, "status": item.status}
            for item in projects
        ],
    }


@router.post("/progress/update")
def update_progress(
    req: ProgressUpdateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create or update progress for a curriculum module."""
    progress = (
        db.query(models.UserProgress)
        .filter(
            models.UserProgress.user_id == user.id,
            models.UserProgress.module_id == req.module_id,
        )
        .first()
    )
    if not progress:
        progress = models.UserProgress(user_id=user.id, module_id=req.module_id)
    progress.progress_percentage = req.progress_percentage
    progress.completed = req.completed
    progress.completed_at = datetime.utcnow() if req.completed else None
    db.add(progress)
    db.commit()
    db.refresh(progress)
    logger.info("Updated progress for user_id=%s module_id=%s", user.id, req.module_id)
    return {
        "module_id": progress.module_id,
        "progress_percentage": progress.progress_percentage,
        "completed": progress.completed,
    }


@router.get("/settings/session")
def validate_session(user=Depends(get_current_user)):
    """Validate the current session for the frontend."""
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "skill_level": user.skill_level,
    }
