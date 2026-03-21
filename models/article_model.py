from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    contenu = Column(Text, nullable=False)
    auteur = Column(String(100), nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    categorie = Column(String(100))
    tags = Column(String(255)) 
    
    # NOUVEAU : Clé étrangère vers l'utilisateur
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # NOUVEAU : Relation inverse
    owner = relationship("User", back_populates="articles")