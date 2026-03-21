from fastapi import FastAPI

from db.database import Base, engine
from api.endpoints.auth_route import router as auth_router
from api.endpoints.article_route import router as article_router

# Création des tables si elles n'existent pas encore
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blog API",
    description="API backend pour la gestion d'un blog - INF222 TAF1",
    version="1.0.0"
)

# Enregistrement des routes
app.include_router(auth_router)
app.include_router(article_router)

@app.get("/", tags=["root"])
def root():
    return {"message": "Bienvenue sur Blog API", "docs": "/docs"}