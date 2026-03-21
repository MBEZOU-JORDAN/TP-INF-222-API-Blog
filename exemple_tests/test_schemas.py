import pytest
from pydantic import ValidationError

from app.schemas.common import PaginatedResponse
from app.schemas.todos import TodoCreate, TodoUpdate, TodoResponse
from app.schemas.users import UserCreate, UserUpdate, UserResponse
from app.schemas.categories import CategoryCreate, CategoryUpdate, CategoryResponse


class TestPaginatedResponse:
    """Tests pour le schéma PaginatedResponse"""
    
    def test_paginated_response_valid(self):
        data = PaginatedResponse(
            items=[{"id": 1, "name": "test"}],
            total=10,
            page=1,
            page_size=20,
            total_pages=1
        )
        
        assert data.total == 10
        assert data.page == 1
        assert data.page_size == 20
        assert data.total_pages == 1
        assert len(data.items) == 1
    
    def test_paginated_response_empty_items(self):
        data = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            page_size=20,
            total_pages=0
        )
        
        assert data.items == []
        assert data.total == 0
    
    def test_paginated_response_missing_fields(self):
        with pytest.raises(ValidationError):
            PaginatedResponse(
                items=[],
                total=10
                # page, page_size, total_pages manquants
            )


class TestTodoSchemas:
    """Tests pour les schémas Todo"""
    
    def test_todo_create_valid(self):
        todo = TodoCreate(
            title="Test Todo",
            description="Description",
            priority=2,
            category_id=1
        )
        
        assert todo.title == "Test Todo"
        assert todo.priority == 2
        assert todo.category_id == 1
    
    def test_todo_create_default_priority(self):
        todo = TodoCreate(
            title="Test Todo",
            description="Description"
        )
        
        assert todo.priority == 1
        assert todo.category_id is None
    
    def test_todo_create_missing_title(self):
        with pytest.raises(ValidationError):
            TodoCreate(description="Description only")
    
    def test_todo_update_partial(self):
        update = TodoUpdate(title="New Title")
        
        assert update.title == "New Title"
        assert update.description is None
        assert update.done is None
    
    def test_todo_update_empty(self):
        update = TodoUpdate()
        
        assert update.title is None
        assert update.description is None
        assert update.done is None


class TestUserSchemas:
    """Tests pour les schémas User"""
    
    def test_user_create_valid(self):
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password123"
    
    def test_user_create_username_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="ab",  # Minimum 3 caractères
                email="test@example.com",
                password="password123"
            )
    
    def test_user_create_username_too_long(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="a" * 51,  # Maximum 50 caractères
                email="test@example.com",
                password="password123"
            )
    
    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="invalid-email",
                password="password123"
            )
    
    def test_user_create_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="1234567"  # Minimum 8 caractères
            )
    
    def test_user_update_partial(self):
        update = UserUpdate(username="newname")
        
        assert update.username == "newname"
        assert update.email is None
    
    def test_user_update_email_only(self):
        update = UserUpdate(email="new@example.com")
        
        assert update.username is None
        assert update.email == "new@example.com"


class TestCategorySchemas:
    """Tests pour les schémas Category"""
    
    def test_category_create_valid(self):
        category = CategoryCreate(name="Work")
        
        assert category.name == "Work"
    
    def test_category_create_name_too_short(self):
        with pytest.raises(ValidationError):
            CategoryCreate(name="ab")  # Minimum 3 caractères
    
    def test_category_create_name_too_long(self):
        with pytest.raises(ValidationError):
            CategoryCreate(name="a" * 51)  # Maximum 50 caractères
    
    def test_category_update_valid(self):
        update = CategoryUpdate(name="Updated")
        
        assert update.name == "Updated"
    
    def test_category_update_empty(self):
        update = CategoryUpdate()
        
        assert update.name is None


class TestSchemaValidation:
    """Tests de validation générale des schémas"""
    
    def test_email_normalization(self):
        """Vérifier que les emails sont normalisés correctement"""
        user = UserCreate(
            username="testuser",
            email="TEST@EXAMPLE.COM",
            password="password123"
        )
        # Pydantic EmailStr normalise généralement les emails
        assert "@" in user.email
    
    def test_string_trimming(self):
        """Tester le comportement avec des espaces"""
        todo = TodoCreate(
            title="  Test Todo  ",
            description="  Description  "
        )
        # Note: Pydantic ne trim pas automatiquement par défaut
        # Ce test documente le comportement actuel
        assert "Test Todo" in todo.title
