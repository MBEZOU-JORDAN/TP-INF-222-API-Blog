from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.database import Base # Adapte l'import selon ton dossier db

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user") # "user" ou "admin"
    is_active = Column(Boolean, default=True)

    # Relation avec les articles
    articles = relationship("Article", back_populates="owner")