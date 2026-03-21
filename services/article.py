from sqlalchemy.orm import Session
from typing import Optional

from models.article import Article
from schemas.article import ArticleCreate, ArticleUpdate

import logging

logger = logging.getLogger(__name__)

class ArticleService:
    @staticmethod
    def create(db: Session, article_data: ArticleCreate, user_id: int):
        logger.info(f"Creating article for user {user_id}: {article_data.titre}")
        
        try:
            db_article = Article(**article_data.model_dump(), user_id=user_id)
            db.add(db_article)
            db.commit()
            db.refresh(db_article)
            
            logger.info(f"Article created successfully: {db_article}")
            return db_article
        
        except Exception as e:
            logger.error(f"Error creating article: {str(e)}")
            db.rollback()
            raise
        
                    
    @staticmethod
    def get_all(db: Session, user_id: int):
        return db.query(Article).filter(Article.user_id == user_id).all()
    
    @staticmethod
    def get_by_id(db: Session, article_id: int, user_id: int) -> Optional[Article]:
        """Récupère un article par son ID, vérifie qu'il appartient à l'utilisateur"""
        return db.query(Article).filter(
            Article.id == article_id,
            Article.user_id == user_id
        ).first()
    
    @staticmethod
    def update(db: Session, article_id: int, article_data: ArticleUpdate, user_id: int) -> Optional[Article]:
        """Metre à jour un article, vérifie que l'utilisateur en est le propriétaire"""
        db_article = ArticleService.get_by_id(db, article_id, user_id)
        if not db_article:
            return None
        
        # Convertir en dictionnaire
        update_data = article_data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_article, key, value)
            
        db.commit()
        db.refresh(db_article)
        return db_article

    @staticmethod
    def delete(db: Session, article_id: int, user_id: int) -> bool:
        """Supprime un article, vérifie que l'utilisateur en est le propriétaire"""
        db_article = ArticleService.get_by_id(db, article_id, user_id)
        if not db_article:
            return False
        
        db.delete(db_article)
        db.commit()
        return True