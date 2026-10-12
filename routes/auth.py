from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import service.auth as auth_service
from database.database import get_db
from models import User, UserRole
from schemas.auth import (
    BusinessRegisterRequest,
    BusinessRegisterResponse,
    LoginRequest,
    Token,
    UserCreate,
    UserRead,
    UserUpdate,
)
from utils.security import create_access_token, get_current_user, require_business_admin

AUTH_ONLY = ["Auth"]
BUSINESS_ADMIN_ONLY = ["Business Admin"]

router = APIRouter(prefix="/auth")


@router.post("/register-business", response_model=BusinessRegisterResponse, status_code=201, tags=AUTH_ONLY)
def register_business(payload: BusinessRegisterRequest, db: Session = Depends(get_db)):
    try:
        business, owner = auth_service.register_business(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return BusinessRegisterResponse(business=business, owner=owner)


@router.post("/login", response_model=Token, tags=AUTH_ONLY)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return Token(access_token=create_access_token(user.user_id))


@router.get("/me", response_model=UserRead, tags=AUTH_ONLY)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users", response_model=UserRead, status_code=201, tags=BUSINESS_ADMIN_ONLY)
def create_staff_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_business_admin),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    return auth_service.create_staff_user(db, payload, business_id=admin.business_id)


@router.get("/users", response_model=List[UserRead], tags=BUSINESS_ADMIN_ONLY)
def list_staff_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_business_admin),
):
    return auth_service.list_staff_users(db, business_id=admin.business_id)



@router.get("/users/{user_id}", response_model=UserRead, tags=BUSINESS_ADMIN_ONLY)
def get_staff_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_business_admin),
):
    user = auth_service.get_staff_user_in_business(db, user_id, admin.business_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Staff user not found")
    return user


@router.put("/users/{user_id}", response_model=UserRead, tags=BUSINESS_ADMIN_ONLY)
def update_staff_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_business_admin),
):
    user = auth_service.update_staff_user(db, user_id, admin.business_id, payload)
    if user is None:
        raise HTTPException(status_code=404, detail="Staff user not found")
    return user


@router.patch("/users/{user_id}", response_model=UserRead, tags=BUSINESS_ADMIN_ONLY)
def deactivate_staff_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_business_admin),
):
    user = auth_service.deactivate_staff_user(db, user_id, admin.business_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Staff user not found")
    return 



@router.delete("/users/{user_id}", status_code=204, tags=BUSINESS_ADMIN_ONLY)
def delete_staff_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_business_admin),
):
    deleted = auth_service.delete_staff_user(db, user_id, admin.business_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Staff user not found")

    