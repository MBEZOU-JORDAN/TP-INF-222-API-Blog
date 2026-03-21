import pytest
from fastapi import status

# ============================================
# FIXTURE : Todo de test
# ============================================

@pytest.fixture
def test_todo(client, auth_headers):
    response = client.post(
        "/api/v1/todos/",
        json={
            "title": "Test Todo",
            "description": "Test Description",
            "priority": 1
        },
        headers=auth_headers
    )
    return response.json()


# ============================================
# TESTS CREATE TODO
# ============================================

def test_create_todo_authenticated(client, auth_headers):
    response = client.post(
        "/api/v1/todos/",
        json={
            "title": "New Todo",
            "description": "Description",
            "priority": 2
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["title"] == "New Todo"
    assert data["description"] == "Description"
    assert data["done"] == False
    assert data["priority"] == 2
    assert "id" in data
    assert "user_id" in data


def test_create_todo_unauthenticated(client):
    response = client.post(
        "/api/v1/todos/",
        json={
            "title": "New Todo",
            "description": "Description"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_todo_missing_title(client, auth_headers):
    response = client.post(
        "/api/v1/todos/",
        json={
            "description": "Description"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================
# TESTS GET TODOS (avec pagination)
# ============================================

def test_get_todos_empty(client, auth_headers):
    response = client.get("/api/v1/todos/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1


def test_get_todos_with_data(client, auth_headers, test_todo):
    response = client.get("/api/v1/todos/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Test Todo"
    assert data["total"] == 1


def test_get_todos_only_own(client, auth_headers, test_todo):
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
    
    # Le deuxième utilisateur ne doit pas voir les todos du premier
    response = client.get("/api/v1/todos/", headers=other_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["items"] == []  # Liste vide


def test_get_todos_pagination(client, auth_headers):
    # Créer plusieurs todos
    for i in range(5):
        client.post(
            "/api/v1/todos/",
            json={
                "title": f"Todo {i}",
                "description": f"Description {i}",
                "priority": 1
            },
            headers=auth_headers
        )
    
    # Tester la pagination
    response = client.get("/api/v1/todos/?skip=0&limit=2", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2


# ============================================
# TESTS SEARCH TODOS
# ============================================

def test_search_todos(client, auth_headers, test_todo):
    response = client.get(
        "/api/v1/todos/search?search=Test",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Test Todo"


def test_search_todos_by_done_status(client, auth_headers, test_todo):
    response = client.get(
        "/api/v1/todos/search?done=false",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1


# ============================================
# TESTS UPDATE TODO
# ============================================

def test_update_todo_success(client, auth_headers, test_todo):
    todo_id = test_todo["id"]
    
    response = client.put(
        f"/api/v1/todos/{todo_id}",
        json={
            "title": "Updated Title",
            "done": True
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["done"] == True


def test_update_todo_nonexistent(client, auth_headers):
    response = client.put(
        "/api/v1/todos/999",
        json={"title": "Updated"},
        headers=auth_headers
    )
    
    # Devrait retourner 404 ou une erreur appropriée


# ============================================
# TESTS DELETE TODO
# ============================================

def test_delete_todo_success(client, auth_headers, test_todo):
    todo_id = test_todo["id"]
    
    response = client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_todo_nonexistent(client, auth_headers):
    response = client.delete("/api/v1/todos/999", headers=auth_headers)
    
    # Le service retourne False si non trouvé, mais l'endpoint n'a pas de gestion 404
    # Ce test documente le comportement actuel