# Blog API — TAF1 INF222 – EC1 (Développement Backend) : Programmation Web

API REST backend pour la gestion d'un blog, développée avec **FastAPI** et **MySQL**.

---

## Stack technique

- **Framework** : FastAPI
- **Base de données** : MySQL (via SQLAlchemy + PyMySQL)
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
│   ├── user_schema.py          # Schémas Pydantic User
│   └── article_schema.py       # Schémas Pydantic Article
├── services/
│   ├── user_service.py         # Logique métier utilisateurs
│   └── article_service.py      # Logique métier articles
├── alembic/                    # Migrations base de données
├── main.py                     # Point d'entrée FastAPI
├── Procfile                    # Déploiement Render
├── requirements.txt
└── .env                        # Variables d'environnement (non versionné)
```

---

## Installation locale

### Prérequis

- Python 3.11+
- MySQL 8+
- [uv](https://github.com/astral-sh/uv)

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/ton-username/blog-api.git
cd blog-api

# 2. Créer et activer l'environnement virtuel
uv venv
source .venv/bin/activate

# 3. Installer les dépendances
uv add fastapi pymysql sqlalchemy alembic bcrypt python-jose python-dotenv uvicorn

# 4. Créer le fichier .env
cp .env.example .env
# Remplir les valeurs dans .env

# 5. Créer la base de données MySQL
mysql -u root -p -e "CREATE DATABASE blog_db;"

# 6. Appliquer les migrations
.venv/bin/python -m alembic upgrade head

# 7. Lancer le serveur
.venv/bin/python -m uvicorn main:app --reload
```

L'API est disponible sur `http://localhost:8000` et la documentation sur `http://localhost:8000/docs`.

---

## Variables d'environnement

Créer un fichier `.env` à la racine :

```env
DATABASE_URL=mysql+pymysql://root:motdepasse@localhost:3306/blog_db
SECRET_KEY=ta_cle_secrete_ici
```

---

## Endpoints

### Authentification

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/auth/register` | Inscription (1er user → admin) | Non |
| POST | `/api/auth/login` | Connexion → retourne un token JWT | Non |
| PUT | `/api/auth/users/{id}/promote` | Promouvoir un user en admin | Admin |

#### Exemple — Inscription

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "monuser", "password": "motdepasse"}'
```

Réponse :
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "monuser",
  "role": "admin"
}
```

#### Exemple — Connexion

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=monuser&password=motdepasse"
```

Réponse :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Articles

Tous les endpoints articles nécessitent un token JWT dans le header :
```
Authorization: Bearer <token>
```

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/articles/` | Créer un article |
| GET | `/api/articles/filter` | Lister les articles (filtres optionnels) |
| GET | `/api/articles/search` | Rechercher dans titres et contenu |
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
    "contenu": "FastAPI est un framework moderne...",
    "auteur": "monuser",
    "categorie": "Technologie",
    "tags": "python, api, backend"
  }'
```

Réponse `201 Created` :
```json
{
  "id": 1,
  "titre": "Introduction à FastAPI",
  "contenu": "FastAPI est un framework moderne...",
  "auteur": "monuser",
  "date": "2026-03-21T20:00:00",
  "categorie": "Technologie",
  "tags": "python, api, backend",
  "user_id": 1
}
```

#### Exemple — Filtrer par catégorie et date

```bash
GET /api/articles/?categorie=Technologie&date=2026-03-21
```

#### Exemple — Recherche plein texte

```bash
GET /api/articles/search?query=FastAPI
```

---

## Codes HTTP utilisés

| Code | Signification |
|------|--------------|
| 200 | Succès |
| 201 | Ressource créée |
| 204 | Suppression réussie |
| 400 | Requête invalide (champ manquant, email déjà utilisé...) |
| 401 | Non authentifié (token manquant ou expiré) |
| 403 | Accès interdit (droits insuffisants) |
| 404 | Ressource introuvable |
| 500 | Erreur serveur interne |

---

## Gestion des rôles

- Le **premier utilisateur** inscrit reçoit automatiquement le rôle `admin`
- Les suivants reçoivent le rôle `user`
- Seul un `admin` peut promouvoir un autre utilisateur via `PUT /api/auth/users/{id}/promote`
- Un `admin` voit tous les articles ; un `user` ne voit que les siens

---

## Déploiement

L'API est déployée sur **Render** avec une base de données MySQL hébergée séparément.

- **URL de l'API** : `https://blog-api-xxxx.onrender.com`
- **Documentation Swagger** : `https://blog-api-xxxx.onrender.com/docs`

---

## Auteur

**MBEZOU DJAMEN JORDAN BENI** — 24G2898 — INF222 – EC1 (Développement Backend): Programmation Web  
Université de Yaoundé I