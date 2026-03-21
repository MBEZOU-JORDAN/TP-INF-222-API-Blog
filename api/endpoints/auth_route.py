from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from db.database import get_db
from core.deps import get_current_user
from core.security import create_access_token
from models.user_model import User
from services.user_service import UserService
from schemas.user_schema import Token, UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user_in)

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = UserService.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur ou mot de passe incorrect")
    
    return {
        "access_token": create_access_token(data={"sub": user.username}),
        "token_type": "bearer",
    }
    
@router.put("/users/{user_id}/promote", response_model=UserResponse)
def promote_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return UserService.promote_to_admin(db, user_id, current_user)