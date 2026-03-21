# Pour creer la connexion a la base de donnees
from sqlalchemy import create_engine

#declarative_base est la classe de base pour tous les modeles
from sqlalchemy.ext.declarative import declarative_base

# sessionmaker cree des session de base de donnes
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# CREATION DU MOTEUR DE BASE DE DONNEES
engine = create_engine(
    settings.sqlalchemy_database_url,
    # echo=True Affiche toutes les requêtes SQL dans le terminal (utile pour déboguer)
    echo=settings.ENVIRONMENT == "development"
)

# SESSION FACTORY
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# CLASSE DE BASE POUR LES MODELES
Base = declarative_base()


#DEPENDENCY INJECTION POUR FASTAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()