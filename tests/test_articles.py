import pytest
from fastapi import status
from models.article_model import Article

# ===============================
# FIXTURE D'ARTICLE
# ===============================
@pytest.fixture(scope="function")
def test_article(db_session, test_user):
    article = Article(
        titre="Test Article",
        contenu="Ceci est le contenu de l'article de test.",
        auteur=test_user.username,
        user_id=test_user.id,
        categorie="Tech",
        tags="test,pytest"
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    return article

# ===============================
# TESTS ARTICLES
# ===============================

def test_create_article(client, auth_headers):
    response = client.post(
        "/api/articles/",
        headers=auth_headers,
        json={
            "titre": "Nouvel Article",
            "contenu": "Contenu du nouvel article",
            "auteur": "Auteur Test",
            "categorie": "Science",
            "tags": "science,nouveau"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["titre"] == "Nouvel Article"
    assert "id" in data

def test_get_all_articles(client, auth_headers, test_article):
    response = client.get(
        "/api/articles/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["titre"] == "Test Article"

def test_get_article_by_id(client, auth_headers, test_article):
    response = client.get(
        f"/api/articles/{test_article.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_article.id
    assert data["titre"] == "Test Article"

def test_get_article_not_found(client, auth_headers):
    response = client.get(
        "/api/articles/9999",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_article(client, auth_headers, test_article):
    response = client.put(
        f"/api/articles/{test_article.id}",
        headers=auth_headers,
        json={
            "titre": "Titre Modifié",
            "contenu": "Nouveau contenu"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["titre"] == "Titre Modifié"

def test_delete_article(client, auth_headers, test_article):
    response = client.delete(
        f"/api/articles/{test_article.id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Vérifier que l'article a bien été supprimé
    response_get = client.get(
        f"/api/articles/{test_article.id}",
        headers=auth_headers
    )
    assert response_get.status_code == status.HTTP_404_NOT_FOUND

def test_search_articles(client, auth_headers, test_article):
    response = client.get(
        "/api/articles/search?query=Contenu",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["id"] == test_article.id

def test_filter_articles(client, auth_headers, test_article):
    response = client.get(
        "/api/articles/filter?categorie=Tech",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["categorie"] == "Tech"
