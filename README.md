# Blog API — TAF1 INF222 – EC1 (Développement Backend)

API REST backend pour la gestion d'un blog, développée avec **FastAPI** et **MySQL**.

---

## Stack technique

- **Framework** : FastAPI (Python)
- **Base de données** : MySQL via SQLAlchemy + PyMySQL
- **Migrations** : Alembic
- **Authentification** : JWT (python-jose) + Bcrypt
- **Gestionnaire de paquets** : uv
- **Documentation** : Swagger UI intégrée (`/docs`)

---

## Structure du projet

```
blog_api/
├── api/
│   └── endpoints/
│       ├── auth_route.py       # Inscription, connexion, promotion admin
│       └── article_route.py    # CRUD articles + recherche + filtres
├── core/
│   ├── security.py             # Hachage bcrypt, génération JWT
│   └── deps.py                 # Dépendance get_current_user
├── db/
│   └── database.py             # Connexion SQLAlchemy, SessionLocal
├── models/
│   ├── user_model.py           # Modèle User (id, email, username, role...)
│   └── article_model.py        # Modèle Article (titre, contenu, auteur...)
├── schemas/
│   ├── user_schema.py          # Schémas Pydantic + validation
│   └── article_schema.py       # Schémas Pydantic + validation
├── services/
│   ├── user_service.py         # Logique métier utilisateurs
│   └── article_service.py      # Logique métier articles
├── alembic/                    # Migrations base de données
├── main.py                     # Point d'entrée FastAPI
├── start.sh                    # Script de démarrage rapide
├── setup.sh                    # Script d'installation
├── Procfile                    # Déploiement Render
├── requirements.txt
├── .env.example                # Template variables d'environnement
└── .env                        # Variables d'environnement (non versionné)
```

---

## Installation

### Prérequis

- Python 3.11+
- MySQL 8+
- [uv](https://github.com/astral-sh/uv) — `pip install uv`

### Installation rapide (recommandée)

```bash
# 1. Cloner le dépôt
git clone https://github.com/MBEZOU-JORDAN/TP-INF-222-API-Blog.git
cd TP-INF-222-API-Blog

# 2. Configurer l'environnement
cp .env.example .env
# Ouvrir .env et remplir DATABASE_URL et SECRET_KEY

# 3. Installer et migrer
./setup.sh

# 4. Démarrer le serveur
./start.sh
```

### Installation manuelle (étape par étape)

```bash
# 1. Créer et activer l'environnement virtuel
uv venv
source .venv/bin/activate

# 2. Installer les dépendances
uv pip install -r requirements.txt

# 3. Créer le fichier .env
cp .env.example .env
# Remplir les valeurs dans .env

# 4. Créer la base de données MySQL
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS blog_db;"

# 5. Appliquer les migrations
.venv/bin/python -m alembic upgrade head

# 6. Lancer le serveur
.venv/bin/python -m uvicorn main:app --reload
```

L'API est disponible sur `http://localhost:8000`
La documentation Swagger sur `http://localhost:8000/docs`

---

## Variables d'environnement

Créer un fichier `.env` à partir du template `.env.example` :

```env
DATABASE_URL=mysql+pymysql://root:TON_MOT_DE_PASSE@localhost:3306/blog_db
SECRET_KEY=une_cle_secrete_longue_et_aleatoire
```

Pour générer une `SECRET_KEY` sécurisée :
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Endpoints

### Authentification

| Méthode | Endpoint | Description | Auth requis |
|---------|----------|-------------|-------------|
| POST | `/api/auth/register` | Inscription (1er user → admin automatiquement) | Non |
| POST | `/api/auth/login` | Connexion → retourne un token JWT | Non |
| PUT | `/api/auth/users/{id}/promote` | Promouvoir un user en admin | Admin |

#### Exemple — Inscription

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jordan@example.com",
    "username": "jordan_b",
    "password": "motdepasse123"
  }'
```

Réponse `201 Created` :
```json
{
  "id": 1,
  "email": "jordan@example.com",
  "username": "jordan_b",
  "role": "admin"
}
```

#### Exemple — Connexion

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=jordan_b&password=motdepasse123"
```

Réponse `200 OK` :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Articles

Tous les endpoints articles nécessitent le token JWT dans le header :
```
Authorization: Bearer <access_token>
```

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/articles/` | Créer un article |
| GET | `/api/articles/` | Lister les articles (filtres optionnels) |
| GET | `/api/articles/search?query=texte` | Recherche plein texte |
| GET | `/api/articles/{id}` | Récupérer un article par ID |
| PUT | `/api/articles/{id}` | Modifier un article |
| DELETE | `/api/articles/{id}` | Supprimer un article |

#### Exemple — Créer un article

```bash
curl -X POST http://localhost:8000/api/articles/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "Introduction à FastAPI",
    "contenu": "FastAPI est un framework moderne pour construire des APIs avec Python.",
    "auteur": "jordan_b",
    "categorie": "Technologie",
    "tags": "python, api, backend"
  }'
```

Réponse `201 Created` :
```json
{
  "id": 1,
  "titre": "Introduction à FastAPI",
  "contenu": "FastAPI est un framework moderne pour construire des APIs avec Python.",
  "auteur": "jordan_b",
  "date": "2026-03-21T20:00:00",
  "categorie": "Technologie",
  "tags": "python, api, backend",
  "user_id": 1
}
```

#### Exemple — Lister avec filtres

```bash
# Filtrer par catégorie
GET /api/articles/?categorie=Technologie

# Filtrer par date
GET /api/articles/?date=2026-03-21

# Combiner les filtres
GET /api/articles/?categorie=Technologie&date=2026-03-21
```

#### Exemple — Recherche plein texte

```bash
GET /api/articles/search?query=FastAPI
```

Réponse `200 OK` :
```json
[
  {
    "id": 1,
    "titre": "Introduction à FastAPI",
    "contenu": "FastAPI est un framework moderne...",
    "auteur": "jordan_b",
    "date": "2026-03-21T20:00:00",
    "categorie": "Technologie",
    "tags": "python, api, backend",
    "user_id": 1
  }
]
```

#### Exemple — Modifier un article

```bash
curl -X PUT http://localhost:8000/api/articles/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "Introduction à FastAPI — Mis à jour",
    "categorie": "Développement"
  }'
```

#### Exemple — Supprimer un article

```bash
curl -X DELETE http://localhost:8000/api/articles/1 \
  -H "Authorization: Bearer <token>"
```

Réponse `204 No Content` (corps vide).

---

## Validation des entrées

Les champs sont validés automatiquement par Pydantic avant tout traitement.

### Articles

| Champ | Règle |
|-------|-------|
| `titre` | Obligatoire, 1–200 caractères, non vide |
| `contenu` | Obligatoire, non vide |
| `auteur` | Obligatoire, 1–100 caractères |
| `categorie` | Optionnel, max 100 caractères |
| `tags` | Optionnel, max 255 caractères |

### Utilisateurs

| Champ | Règle |
|-------|-------|
| `email` | Obligatoire, format email valide |
| `username` | Obligatoire, 3–50 caractères, lettres/chiffres/`-`/`_` uniquement |
| `password` | Obligatoire, minimum 6 caractères |

#### Exemple — Erreur de validation

```bash
curl -X POST http://localhost:8000/api/articles/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"titre": "   ", "contenu": "test", "auteur": "jordan"}'
```

Réponse `422 Unprocessable Entity` :
```json
{
  "detail": [
    {
      "loc": ["body", "titre"],
      "msg": "Le titre ne peut pas être vide ou contenir uniquement des espaces",
      "type": "value_error"
    }
  ]
}
```

---

## Codes HTTP

| Code | Signification | Cas d'usage |
|------|--------------|-------------|
| `200` | OK | Lecture, modification réussie |
| `201` | Created | Création d'un article ou d'un utilisateur |
| `204` | No Content | Suppression réussie |
| `400` | Bad Request | Email déjà utilisé, username déjà pris |
| `401` | Unauthorized | Token manquant, invalide ou expiré |
| `403` | Forbidden | Action réservée aux admins |
| `404` | Not Found | Article ou utilisateur introuvable |
| `422` | Unprocessable Entity | Données invalides (validation Pydantic) |
| `500` | Internal Server Error | Erreur serveur inattendue |

---

## Gestion des rôles

- Le **premier utilisateur** inscrit reçoit automatiquement le rôle `admin`
- Les utilisateurs suivants reçoivent le rôle `user`
- Seul un `admin` peut promouvoir un autre utilisateur via `PUT /api/auth/users/{id}/promote`
- Un `admin` voit **tous** les articles ; un `user` ne voit que **les siens**

---

## Déploiement

Le code source est disponible sur GitHub :
**[https://github.com/MBEZOU-JORDAN/TP-INF-222-API-Blog](https://github.com/MBEZOU-JORDAN/TP-INF-222-API-Blog)**

> Le déploiement cloud n'a pas été finalisé en raison d'une contrainte sur la base de données MySQL (absence de carte bancaire pour les services gratuits compatibles). L'API fonctionne entièrement en local.

---

## Auteur

**MBEZOU DJAMEN JORDAN BENI** — Matricule : 24G2898
Informatique L2 — UE INF222 – EC1 (Développement Backend)
Université de Yaoundé I — Année académique 2025-2026

---

## Tests

Les tests sont écrits avec **pytest** et utilisent une base de données SQLite en mémoire — MySQL n'est pas requis pour les faire tourner.

### Structure

```
tests/
├── conftest.py       # Fixtures partagées (client, db, utilisateur de test, token)
├── test_auth.py      # Tests inscription, connexion, doublons
└── test_articles.py  # Tests CRUD, recherche, filtres
```

### Installation des dépendances de test

```bash
uv add pytest httpx pytest-asyncio
```

### Lancer les tests

```bash
# Tous les tests
.venv/bin/python -m pytest tests/ -v

# Un fichier spécifique
.venv/bin/python -m pytest tests/test_auth.py -v
.venv/bin/python -m pytest tests/test_articles.py -v

# Avec résumé court
.venv/bin/python -m pytest tests/ -v --tb=short
```

### Cas de test couverts

**Authentification (`test_auth.py`)**

| Test | Description |
|------|-------------|
| `test_register_success` | Inscription réussie d'un nouvel utilisateur |
| `test_register_duplicate_username` | Rejet si username déjà pris → `400` |
| `test_register_duplicate_email` | Rejet si email déjà utilisé → `400` |
| `test_login_success` | Connexion réussie → token JWT retourné |
| `test_login_wrong_password` | Rejet si mot de passe incorrect → `400` |
| `test_login_nonexistent_user` | Rejet si utilisateur inexistant → `400` |

**Articles (`test_articles.py`)**

| Test | Description |
|------|-------------|
| `test_create_article` | Création d'un article → `201` |
| `test_get_all_articles` | Liste des articles → `200` |
| `test_get_article_by_id` | Récupération par ID → `200` |
| `test_get_article_not_found` | ID inexistant → `404` |
| `test_update_article` | Modification d'un article → `200` |
| `test_delete_article` | Suppression puis vérification → `204` puis `404` |
| `test_search_articles` | Recherche plein texte → `200` |
| `test_filter_articles` | Filtrage par catégorie → `200` |