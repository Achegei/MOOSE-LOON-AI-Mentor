"""
SQLAlchemy models for MOOSE LOON AI Mentor Platform.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    skill_level = Column(
        String(50), default="beginner"
    )  # beginner, intermediate, advanced
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    """Conversation history model."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Message(Base):
    """Chat message model."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    role = Column(String(50), nullable=False)  # "user" or "mentor"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class LearningModule(Base):
    """Curriculum learning module model."""

    __tablename__ = "learning_modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    topic = Column(String(255), index=True)  # e.g., "AI", "Prompt Engineering", "n8n"
    difficulty = Column(String(50))  # "beginner", "intermediate", "advanced"
    content = Column(Text)
    order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserProgress(Base):
    """User progress tracking model."""

    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    module_id = Column(Integer, index=True, nullable=False)
    completed = Column(Boolean, default=False)
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class UserMemory(Base):
    """Persistent learner memory used for personalized mentorship."""

    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    goals = Column(Text, default="[]")
    learning_path = Column(Text, default="[]")
    active_module = Column(String(255))
    current_projects = Column(Text, default="[]")
    skill_level = Column(String(50), default="beginner")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Assignment(Base):
    """Assignment/exercise model."""

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    module_id = Column(Integer, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    difficulty = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted = Column(Boolean, default=False)
    submission_date = Column(DateTime)


class RefreshToken(Base):
    """Refresh tokens stored for rotation and revocation."""

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    token = Column(String(512), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)


class AccessTokenBlacklist(Base):
    """Blacklisted access tokens (for immediate revocation)."""

    __tablename__ = "access_token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Project(Base):
    """Project guidance model."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        String(50), default="planning"
    )  # planning, in_progress, completed, abandoned
    repository_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSubscription(Base):
    """Current SaaS tier for a learner or developer account."""

    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    tier = Column(String(50), default="free", nullable=False)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeveloperApiKey(Base):
    """Hashed API key for external system integrations."""

    __tablename__ = "developer_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    key_prefix = Column(String(32), index=True, nullable=False)
    key_hash = Column(String(128), unique=True, index=True, nullable=False)
    tier = Column(String(50), default="free", nullable=False)
    monthly_limit = Column(Integer, default=0, nullable=False)
    requests_this_month = Column(Integer, default=0, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)


class ChatResponseCache(Base):
    """Cached mentor responses for repeated research questions."""

    __tablename__ = "chat_response_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(128), unique=True, index=True, nullable=False)
    prompt = Column(Text, nullable=False)
    mode = Column(String(50), default="quick", nullable=False)
    context_hash = Column(String(128), nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, index=True, nullable=False)
