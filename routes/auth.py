from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import service.auth as auth_service
from database.database import get_db
from models import User, UserRole
from schemas.auth import LoginRequest, Token, UserCreate, UserRead, UserUpdate
from utils.security import create_access_token, get_current_user, require_admin


AUTH_ONLY = ["Auth"]
ADMIN_ONLY = ["Admin"]

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=Token, tags=AUTH_ONLY)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return Token(access_token=create_access_token(user.user_id))


@router.get("/me", response_model=UserRead, tags=AUTH_ONLY)
def me(current_user: User = Depends(get_current_user)):
    return current_user



@router.post("/users", response_model=UserRead, status_code=201, tags=ADMIN_ONLY)
def create_staff_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    return auth_service.create_user(db, payload, role=UserRole.STAFF)


@router.get("/users", response_model=List[UserRead], tags=ADMIN_ONLY)
def list_staff_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return auth_service.list_staff_users(db)


@router.get("/users/{user_id}", response_model=UserRead, tags=ADMIN_ONLY)
def get_staff_user(
    user_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = auth_service.get_user(db, user_id)
    if user is None or user.role != UserRole.STAFF:
        raise HTTPException(status_code=404, detail="Staff user not found")
    return user


@router.put("/users/{user_id}", response_model=UserRead, tags=ADMIN_ONLY)
def update_staff_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = auth_service.update_staff_user(db, user_id, payload)
    if user is None:
        raise HTTPException(status_code=404, detail="Staff user not found")
    return user


@router.delete("/users/{user_id}", response_model=UserRead, tags=ADMIN_ONLY)
def deactivate_staff_user(
    user_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = auth_service.deactivate_staff_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Staff user not found")
    return user
