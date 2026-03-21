from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.user_model import User
from schemas.user_schema import UserCreate
from core.security import get_password_hash, verify_password

class UserService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate):
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        if db.query(User).filter(User.username == user_in.username).first():
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

        # Premier user créé → admin, sinon → user
        is_first_user = db.query(User).count() == 0
        role = "admin" if is_first_user else "user"

        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            role=role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def promote_to_admin(db: Session, target_user_id: int, current_user: User):
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Réservé aux admins")
        user = db.query(User).filter(User.id == target_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")
        user.role = "admin"
        db.commit()
        db.refresh(user)
        return user