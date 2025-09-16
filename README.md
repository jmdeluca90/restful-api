# Advanced FastAPI RESTful API Example

This is a sample advanced RESTful API using FastAPI, PostgreSQL, JWT authentication, and OAuth login (Google/GitHub).

## Features

- JWT Authentication (register/login/protected endpoints)
- OAuth login (Google, GitHub) via Authlib
- PostgreSQL database (SQLAlchemy ORM)
- User resource CRUD
- Automatic Swagger docs (`/docs`)
- Docker support (see Dockerfile)
- Modular code structure

## Quickstart

### 1. Clone and Setup

```bash
git clone https://github.com/your/repo.git
cd repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up environment

Set these environment variables for OAuth to work (see Google/GitHub developer console):

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `DATABASE_URL` (defaults to local postgres)

### 3. Run

```bash
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/docs

### 4. Docker

To run with Docker (with a local PostgreSQL):

```bash
docker-compose up --build
```

## Endpoints

- `POST /auth/register` — Register new user
- `POST /auth/token` — Obtain JWT
- `GET /users/me` — Current user info
- `GET /users/` — List users (protected)
- `GET /oauth/login/google` — Google login
- `GET /oauth/login/github` — GitHub login

---

**Note:** For production, use HTTPS, set strong secrets, and manage DB migrations with Alembic.
