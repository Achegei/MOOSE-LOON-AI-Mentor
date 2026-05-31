"""
Simple CRUD helpers for user management used by the auth endpoints.
"""

from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from . import models

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(
    db: Session,
    email: str,
    username: str,
    password: str,
    full_name: Optional[str] = None,
    skill_level: str = "beginner",
) -> models.User:
    hashed = pwd_context.hash(password)
    user = models.User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hashed,
        skill_level=skill_level,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_refresh_token(db: Session, user_id: int, token: str) -> models.RefreshToken:
    rt = models.RefreshToken(user_id=user_id, token=token)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def get_refresh_token(db: Session, token: str) -> Optional[models.RefreshToken]:
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token, models.RefreshToken.revoked == False).first()


def revoke_refresh_token(db: Session, token: str) -> None:
    rt = db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()
    if rt:
        rt.revoked = True
        db.add(rt)
        db.commit()


def revoke_all_refresh_tokens_for_user(db: Session, user_id: int) -> None:
    rts = db.query(models.RefreshToken).filter(models.RefreshToken.user_id == user_id, models.RefreshToken.revoked == False).all()
    for rt in rts:
        rt.revoked = True
        db.add(rt)
    db.commit()


def get_refresh_token(db: Session, token: str) -> Optional[models.RefreshToken]:
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token, models.RefreshToken.revoked == False).first()


def blacklist_access_token(db: Session, token: str) -> models.AccessTokenBlacklist:
    at = models.AccessTokenBlacklist(token=token)
    db.add(at)
    db.commit()
    db.refresh(at)
    return at


def is_access_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(models.AccessTokenBlacklist).filter(models.AccessTokenBlacklist.token == token).first() is not None
