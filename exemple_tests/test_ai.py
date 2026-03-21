import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch

# ============================================
# TESTS AI ENDPOINTS
# ============================================

# Note: Ces tests utilisent des mocks pour éviter les appels réels à l'API OpenAI
# En production, vous pourriez avoir des tests d'intégration séparés


class TestAISuggestions:
    """Tests pour l'endpoint /api/v2/ai/suggestion"""
    
    @patch('app.services.ai.gemini_service.GeminiService.generate_todo_suggestions')
    def test_generate_suggestions_success(self, mock_suggestions, client, auth_headers):
        mock_suggestions.return_value = [
            "Créer un plan de projet",
            "Définir les objectifs",
            "Identifier les ressources"
        ]
        
        response = client.post(
            "/api/v2/ai/suggestion",
            json={
                "context": "Je veux lancer un nouveau projet",
                "num_suggestions": 3
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) == 3
    
    def test_generate_suggestions_unauthenticated(self, client):
        response = client.post(
            "/api/v2/ai/suggestion",
            json={
                "context": "Test context",
                "num_suggestions": 3
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_generate_suggestions_missing_context(self, client, auth_headers):
        response = client.post(
            "/api/v2/ai/suggestion",
            json={"num_suggestions": 3},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAIPriorityAnalysis:
    """Tests pour l'endpoint /api/v2/ai/analyze-priority"""
    
    @patch('app.services.ai.gemini_service.GeminiService.analyze_todo_priority')
    def test_analyze_priority_success(self, mock_analyze, client, auth_headers):
        mock_analyze.return_value = {
            "priority": "high",
            "reasoning": "Cette tâche est urgente",
            "estimated_time": 60
        }
        
        response = client.post(
            "/api/v2/ai/analyze-priority",
            json={
                "title": "Correction de bug critique",
                "description": "Le serveur plante régulièrement"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["priority"] == "high"
        assert "reasoning" in data
        assert "estimated_time" in data
    
    def test_analyze_priority_unauthenticated(self, client):
        response = client.post(
            "/api/v2/ai/analyze-priority",
            json={
                "title": "Test",
                "description": "Test description"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_analyze_priority_missing_fields(self, client, auth_headers):
        response = client.post(
            "/api/v2/ai/analyze-priority",
            json={"title": "Only title"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAIImproveDescription:
    """Tests pour l'endpoint /api/v2/ai/improve-description"""
    
    @patch('app.services.ai.gemini_service.GeminiService.improve_todo_description')
    def test_improve_description_success(self, mock_improve, client, auth_headers):
        mock_improve.return_value = "Description améliorée et plus claire avec des étapes concrètes."
        
        response = client.post(
            "/api/v2/ai/improve-description",
            json={
                "title": "Refactoring du code",
                "description": "refactor le code"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "original" in data
        assert "improved" in data
        assert data["original"] == "refactor le code"
    
    def test_improve_description_unauthenticated(self, client):
        response = client.post(
            "/api/v2/ai/improve-description",
            json={
                "title": "Test",
                "description": "Test description"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAIChat:
    """Tests pour l'endpoint /api/v2/ai/chat"""
    
    @patch('app.services.ai.gemini_service.GeminiService.chat_with_history')
    def test_chat_success(self, mock_chat, client, auth_headers):
        mock_chat.return_value = "Bonjour! Je suis votre assistant de productivité."
        
        response = client.post(
            "/api/v2/ai/chat",
            json={
                "messages": "Bonjour, comment ça va?",
                "history": []
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
    
    @patch('app.services.ai.gemini_service.GeminiService.chat_with_history')
    def test_chat_with_history(self, mock_chat, client, auth_headers):
        mock_chat.return_value = "Je peux vous aider à organiser vos tâches."
        
        response = client.post(
            "/api/v2/ai/chat",
            json={
                "messages": "Que peux-tu faire?",
                "history": [
                    {"role": "user", "content": "Bonjour"},
                    {"role": "assistant", "content": "Bonjour! Comment puis-je vous aider?"}
                ]
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
    
    def test_chat_unauthenticated(self, client):
        response = client.post(
            "/api/v2/ai/chat",
            json={"messages": "Hello"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_chat_missing_message(self, client, auth_headers):
        response = client.post(
            "/api/v2/ai/chat",
            json={"history": []},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestOpenAIServiceErrors:
    """Tests pour la gestion des erreurs du service OpenAI"""
    
    @patch('app.services.ai.gemini_service.GeminiService.generate_todo_suggestions')
    def test_openai_api_error(self, mock_suggestions, client, auth_headers):
        mock_suggestions.side_effect = Exception("OpenAI API error: Rate limit exceeded")
        
        response = client.post(
            "/api/v2/ai/suggestion",
            json={
                "context": "Test context",
                "num_suggestions": 3
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "error" in data["detail"].lower() or "Error" in data["detail"]
