import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from db.database import Base, get_db
from main import app
from models.user_model import User
from core.security import get_password_hash

# ==========================================
# BASE DE DONNEES DE TEST (MEMOIRE) 
# ==========================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ======================================
# FIXTURES PYTEST
# ======================================

@pytest.fixture(scope="function")
def db_session():
    # Creer toutes les tables
    Base.metadata.create_all(bind=engine)
    
    # Creer une session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
 
# Client pour tester l'API sans lancer le serveur       
@pytest.fixture(scope="function")
def client(db_session):
    # Override de la dependency get_db
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
        
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
    
    
# Creer un utilisateur de test
@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# Header d'authentification pour les tests
@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
