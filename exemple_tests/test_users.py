import pytest
from fastapi import status

# ============================================
# TESTS GET USERS (Admin seulement)
# ============================================

@pytest.fixture
def admin_user(db_session):
    from app.models.user import User
    from app.core.security import get_password_hash
    
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        is_active=True,
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def admin_headers(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin",
            "password": "adminpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_all_users_as_admin(client, admin_headers, test_user):
    response = client.get("/api/v1/users/", headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Il y a l'admin et le test_user
    assert len(data) >= 1


def test_get_all_users_as_regular_user(client, auth_headers):
    response = client.get("/api/v1/users/", headers=auth_headers)
    
    # Un utilisateur non-admin ne doit pas pouvoir lister tous les utilisateurs
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_all_users_unauthenticated(client):
    response = client.get("/api/v1/users/")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# TESTS GET USER BY ID
# ============================================

def test_get_user_by_id_success(client, auth_headers, test_user):
    user_id = test_user.id
    
    response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_user_by_id_not_found(client, auth_headers):
    response = client.get("/api/v1/users/999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_unauthenticated(client, test_user):
    response = client.get(f"/api/v1/users/{test_user.id}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# TESTS UPDATE USER
# ============================================

def test_update_own_user_success(client, auth_headers, test_user):
    user_id = test_user.id
    
    response = client.put(
        f"/api/v1/users/{user_id}",
        json={"username": "updateduser"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "updateduser"


def test_update_other_user_forbidden(client, auth_headers, admin_user):
    # Un utilisateur normal ne peut pas modifier un autre utilisateur
    response = client.put(
        f"/api/v1/users/{admin_user.id}",
        json={"username": "hacked"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_update_any_user(client, admin_headers, test_user):
    # Un admin peut modifier n'importe quel utilisateur
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        json={"username": "adminupdated"},
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "adminupdated"


def test_update_user_not_found(client, admin_headers):
    response = client.put(
        "/api/v1/users/999",
        json={"username": "ghost"},
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================
# TESTS DELETE USER
# ============================================

def test_delete_own_user_success(client, test_user, db_session):
    from app.models.user import User
    from app.core.security import get_password_hash
    
    # Créer un utilisateur spécifique pour ce test
    user_to_delete = User(
        username="todelete",
        email="todelete@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db_session.add(user_to_delete)
    db_session.commit()
    db_session.refresh(user_to_delete)
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "todelete",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Supprimer son propre compte
    response = client.delete(f"/api/v1/users/{user_to_delete.id}", headers=headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_other_user_forbidden(client, auth_headers, admin_user):
    # Un utilisateur normal ne peut pas supprimer un autre utilisateur
    response = client.delete(
        f"/api/v1/users/{admin_user.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_delete_any_user(client, admin_headers, db_session):
    from app.models.user import User
    from app.core.security import get_password_hash
    
    # Créer un utilisateur à supprimer
    user_to_delete = User(
        username="tobedeleted",
        email="tobedeleted@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db_session.add(user_to_delete)
    db_session.commit()
    db_session.refresh(user_to_delete)
    
    # L'admin peut supprimer n'importe quel utilisateur
    response = client.delete(
        f"/api/v1/users/{user_to_delete.id}",
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_user_not_found(client, admin_headers):
    response = client.delete("/api/v1/users/999", headers=admin_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_unauthenticated(client, test_user):
    response = client.delete(f"/api/v1/users/{test_user.id}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
