import pytest
from fastapi import status

# ===============================
# TESTS REGISTER
# ==============================

def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_200_OK  # Note: your route might return 200 instead of 201
    
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data
    
def test_register_duplicate_username(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",  # existant
            "email": "other@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "nom d'utilisateur" in response.json()["detail"].lower()
    
def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "otheruser",
            "email": "test@example.com",  # existant
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.json()["detail"].lower()

#===================================
# TEST LOGIN
#===================================

def test_login_success(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_nonexistent_user(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
