"""
Authentication routes for registration and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from auth import schemas, utils
from auth.deps import get_current_user, get_db, security
from database import crud

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email) or crud.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="User with given email or username already exists")
    user = crud.create_user(
        db,
        email=user_in.email,
        username=user_in.username,
        password=user_in.password,
        full_name=user_in.full_name,
    )
    return user


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.Login, db: Session = Depends(get_db)):
    # Accept either username or email
    user = crud.get_user_by_email(db, form_data.username_or_email) or crud.get_user_by_username(db, form_data.username_or_email)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    if not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    access_token = utils.create_access_token({"sub": str(user.id), "type": "access"})
    refresh_token = utils.create_refresh_token({"sub": str(user.id)})

    # persist refresh token for rotation/revocation
    crud.create_refresh_token(db, user_id=user.id, token=refresh_token)

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}



@router.post("/refresh", response_model=schemas.Token)
def refresh_access_token(refresh_token: dict, db: Session = Depends(get_db)):
    # Expect body: {"refresh_token": "..."}
    token = refresh_token.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Missing refresh_token")

    try:
        payload = utils.decode_token(token)
    except utils.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except utils.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if not utils.is_refresh_token(payload):
        raise HTTPException(status_code=401, detail="Invalid refresh token type")

    stored = crud.get_refresh_token(db, token)
    if not stored:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

    user_id = int(payload.get("sub"))
    # rotate: revoke old and issue new
    crud.revoke_refresh_token(db, token)
    new_refresh = utils.create_refresh_token({"sub": str(user_id)})
    crud.create_refresh_token(db, user_id=user_id, token=new_refresh)

    access_token = utils.create_access_token({"sub": str(user_id), "type": "access"})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": new_refresh}


@router.post("/logout")
def logout(
    body: dict | None = Body(None),
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Depends(security),
    current_user=Depends(get_current_user),
):
    """Logout helper — blacklist the current access token and revoke a refresh token if provided."""
    access_token = creds.credentials
    crud.blacklist_access_token(db, access_token)

    rt = (body or {}).get("refresh_token")
    revoked_refresh = False
    if rt:
        crud.revoke_refresh_token(db, rt)
        revoked_refresh = True

    return {
        "status": "ok",
        "access_token_revoked": True,
        "revoked_refresh_token": revoked_refresh,
    }


@router.post("/logout_all")
def logout_all(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Revoke all refresh tokens for the current authenticated user."""
    crud.revoke_all_refresh_tokens_for_user(db, current_user.id)
    return {"status": "ok", "revoked_all_refresh_tokens": True}
