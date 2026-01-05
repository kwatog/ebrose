import base64
import json
import re
from datetime import timedelta
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    get_current_user_from_token,
    get_db,
    get_password_hash,
    now_utc,
    verify_password,
)
from ..config import get_settings
from ..rate_limiter import get_client_ip, login_rate_limiter_check, login_rate_limiter_reset

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()

PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True


def validate_password(password: str) -> Tuple[bool, str]:
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"

    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if PASSWORD_REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"

    return True, ""


def _set_auth_cookies(response: Response, *, access_token: str, user: models.User) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path=settings.cookie_path,
        domain=settings.cookie_domain,
    )

    user_info = {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "department": user.department,
    }
    user_info_b64 = base64.b64encode(json.dumps(user_info).encode()).decode()
    response.set_cookie(
        key="user_info",
        value=user_info_b64,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path=settings.cookie_path,
        domain=settings.cookie_domain,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path=settings.cookie_path, domain=settings.cookie_domain)
    response.delete_cookie("user_info", path=settings.cookie_path, domain=settings.cookie_domain)


@router.post("/register", response_model=schemas.User)
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Only Admins can register new users")

    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    is_valid, error_msg = validate_password(user.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    hashed_pw = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        full_name=user.full_name,
        department=user.department,
        role=user.role,
        created_at=now_utc(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.UserResponse)
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> schemas.UserResponse:
    client_ip = get_client_ip(request)
    rate_limit_key = f"{client_ip}:{form_data.username}"
    
    login_rate_limiter_check(rate_limit_key, client_ip)
    
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    login_rate_limiter_reset(rate_limit_key, client_ip)
    
    user.last_login = now_utc()
    db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    _set_auth_cookies(response, access_token=access_token, user=user)

    return {"message": "Login successful", "user": user}


@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token found in cookies")

    try:
        user = get_current_user_from_token(token, db)
    except HTTPException:
        _clear_auth_cookies(response)
        raise

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    _set_auth_cookies(response, access_token=new_access_token, user=user)

    return {"message": "Token refreshed successfully"}


@router.post("/logout")
def logout(response: Response) -> dict:
    _clear_auth_cookies(response)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)) -> models.User:
    return current_user


@router.put("/me", response_model=schemas.User)
def update_users_me(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.department is not None:
        current_user.department = user_update.department

    current_user.updated_by = current_user.id
    current_user.updated_at = now_utc()

    db.commit()
    db.refresh(current_user)
    return current_user


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/password")
def change_password(
    password_change: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> dict:
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    is_valid, error_msg = validate_password(password_change.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    current_user.hashed_password = get_password_hash(password_change.new_password)
    current_user.updated_by = current_user.id
    current_user.updated_at = now_utc()

    db.commit()

    return {"message": "Password changed successfully"}
