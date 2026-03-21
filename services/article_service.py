import logging
from typing import Optional
from sqlalchemy.orm import Session

from models.user_model import User
from models.article_model import Article
from schemas.article_schema import ArticleCreate, ArticleUpdate

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
    def get_all(db: Session, current_user: User):
        return db.query(Article).filter(Article.user_id == current_user.id).all()
    
    @staticmethod
    def get_by_id(db: Session, article_id: int, current_user: User) -> Optional[Article]:
        return db.query(Article).filter(
            Article.id == article_id,
            Article.user_id == current_user.id
        ).first()    
    
    @staticmethod
    def update(db: Session, article_id: int, article_data: ArticleUpdate, current_user: User) -> Optional[Article]:
        # On utilise notre nouvelle méthode get_by_id qui gère déjà la logique Admin/User
        db_article = ArticleService.get_by_id(db, article_id, current_user)
        if not db_article:
            return None
        
        update_data = article_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_article, key, value)
            
        db.commit()
        db.refresh(db_article)
        return db_article
 
    @staticmethod
    def delete(db: Session, article_id: int, current_user: User) -> bool:
        db_article = ArticleService.get_by_id(db, article_id, current_user)
        if not db_article:
            return False
        
        db.delete(db_article)
        db.commit()
        return True

    @staticmethod
    def search(db: Session, query_str: str, current_user: User):
        query = db.query(Article).filter(
            Article.titre.ilike(f"%{query_str}%") | Article.contenu.ilike(f"%{query_str}%")
        )
        return query.all()
    
    @staticmethod
    def get_by_categorie_date(db: Session, current_user: User, categorie: Optional[str] = None, date: Optional[str] = None):
        query = db.query(Article)
        
        if categorie:
            query = query.filter(Article.categorie == categorie)
            
        if date:
            query = query.filter(Article.date == date)
            
        return query.all()