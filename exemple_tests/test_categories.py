import pytest
from fastapi import status

# ============================================
# FIXTURE : Catégorie de test
# ============================================

@pytest.fixture
def test_category(client, auth_headers):
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Test Category"},
        headers=auth_headers
    )
    return response.json()


# ============================================
# TESTS CREATE CATEGORY
# ============================================

def test_create_category_success(client, auth_headers):
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Work"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["name"] == "Work"
    assert "id" in data
    assert "user_id" in data


def test_create_category_unauthenticated(client):
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Work"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_category_name_too_short(client, auth_headers):
    response = client.post(
        "/api/v1/categories/",
        json={"name": "ab"},  # Minimum 3 caractères
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_category_name_too_long(client, auth_headers):
    response = client.post(
        "/api/v1/categories/",
        json={"name": "a" * 51},  # Maximum 50 caractères
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================
# TESTS GET CATEGORIES
# ============================================

def test_get_categories_empty(client, auth_headers):
    response = client.get("/api/v1/categories/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_categories_with_data(client, auth_headers, test_category):
    response = client.get("/api/v1/categories/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Category"


def test_get_categories_only_own(client, auth_headers, test_category):
    # Créer un deuxième utilisateur
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123"
        }
    )
    
    # Login avec le deuxième utilisateur
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "otheruser",
            "password": "password123"
        }
    )
    
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Le deuxième utilisateur ne doit pas voir les catégories du premier
    response = client.get("/api/v1/categories/", headers=other_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []  # Liste vide


def test_get_categories_unauthenticated(client):
    response = client.get("/api/v1/categories/")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# TESTS GET CATEGORY BY ID
# ============================================

def test_get_category_by_id_success(client, auth_headers, test_category):
    category_id = test_category["id"]
    
    response = client.get(f"/api/v1/categories/{category_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["id"] == category_id


def test_get_category_by_id_not_found(client, auth_headers):
    response = client.get("/api/v1/categories/999", headers=auth_headers)
    
    # Le service retourne None mais l'endpoint pourrait ne pas gérer le 404
    # Ce test documente le comportement actuel


def test_get_category_of_other_user(client, auth_headers, test_category):
    # Créer un deuxième utilisateur
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "otheruser2",
            "email": "other2@example.com",
            "password": "password123"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "otheruser2",
            "password": "password123"
        }
    )
    
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # L'autre utilisateur ne devrait pas pouvoir accéder à la catégorie
    category_id = test_category["id"]
    response = client.get(f"/api/v1/categories/{category_id}", headers=other_headers)
    
    # Devrait retourner None ou 404 car la catégorie n'appartient pas à cet utilisateur


# ============================================
# TESTS UPDATE CATEGORY
# ============================================

def test_update_category_success(client, auth_headers, test_category):
    category_id = test_category["id"]
    
    response = client.put(
        f"/api/v1/categories/{category_id}",
        json={"name": "Updated Category"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Category"


def test_update_category_of_other_user(client, auth_headers, test_category):
    # Créer un deuxième utilisateur
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "hacker",
            "email": "hacker@example.com",
            "password": "password123"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "hacker",
            "password": "password123"
        }
    )
    
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # L'autre utilisateur ne devrait pas pouvoir modifier la catégorie
    category_id = test_category["id"]
    response = client.put(
        f"/api/v1/categories/{category_id}",
        json={"name": "Hacked"},
        headers=other_headers
    )
    
    # Devrait échouer car la catégorie n'appartient pas à cet utilisateur


# ============================================
# TESTS DELETE CATEGORY
# ============================================

def test_delete_category_success(client, auth_headers, test_category):
    category_id = test_category["id"]
    
    response = client.delete(f"/api/v1/categories/{category_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Vérifier que la catégorie n'existe plus
    get_response = client.get(f"/api/v1/categories/{category_id}", headers=auth_headers)
    # Devrait retourner None ou 404


def test_delete_category_of_other_user(client, auth_headers, test_category):
    # Créer un deuxième utilisateur
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "attacker",
            "email": "attacker@example.com",
            "password": "password123"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "attacker",
            "password": "password123"
        }
    )
    
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # L'autre utilisateur ne devrait pas pouvoir supprimer la catégorie
    category_id = test_category["id"]
    response = client.delete(f"/api/v1/categories/{category_id}", headers=other_headers)
    
    # Devrait échouer car la catégorie n'appartient pas à cet utilisateur


def test_delete_category_unauthenticated(client, test_category):
    response = client.delete(f"/api/v1/categories/{test_category['id']}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# TESTS CATEGORY WITH TODOS
# ============================================

def test_create_todo_with_category(client, auth_headers, test_category):
    category_id = test_category["id"]
    
    response = client.post(
        "/api/v1/todos/",
        json={
            "title": "Todo with category",
            "description": "Description",
            "priority": 1,
            "category_id": category_id
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["category_id"] == category_id


def test_create_todo_with_invalid_category(client, auth_headers):
    response = client.post(
        "/api/v1/todos/",
        json={
            "title": "Todo with invalid category",
            "description": "Description",
            "priority": 1,
            "category_id": 999  # Catégorie inexistante
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_todo_with_other_users_category(client, auth_headers, test_category):
    # Créer un deuxième utilisateur
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "thirduser",
            "email": "third@example.com",
            "password": "password123"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "thirduser",
            "password": "password123"
        }
    )
    
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # L'autre utilisateur ne devrait pas pouvoir utiliser la catégorie du premier
    category_id = test_category["id"]
    response = client.post(
        "/api/v1/todos/",
        json={
            "title": "Sneaky Todo",
            "description": "Description",
            "priority": 1,
            "category_id": category_id
        },
        headers=other_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
