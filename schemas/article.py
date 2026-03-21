from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArticleBase(BaseModel):
    titre: str
    contenu: str
    auteur: str
    categorie: Optional[str] = None
    tags: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(ArticleBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True
        
class ArticleUpdate(BaseModel):
    titre: Optional[str] = None
    contenu: Optional[str] = None
    auteur: Optional[str] = None
    categorie: Optional[str] = None
    tags: Optional[str] = None