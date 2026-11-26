# FastAPI + PostgreSQL + SQLAlchemy

Clean Architecture example: create a User via `POST /users`.

## Docs

Open the Arabic walkthrough:

`docs/fastapi-postgres-architecture.html`

## Setup

1. Create a PostgreSQL database (default name in code: `mydb`).
2. Update the connection string in `src/infrastructure/data_access/database.py` if needed:

```
postgresql+psycopg://postgres:password@localhost:5432/mydb
```

3. Create a virtualenv (use Python 3.10+) and install dependencies from the project root (`Full/`):

```bash
cd ~/senior/Application\ Layers/Full
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Run from the `src` folder (with the venv still active):

```bash
cd src
uvicorn main:app --reload
```

5. Open Swagger UI: http://127.0.0.1:8000/docs

## Create a user

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Saleh", "email": "saleh@example.com"}'
```

## Layers

| Layer | Role |
| --- | --- |
| Presentation | FastAPI controller |
| Application | Use cases + repository interface |
| Domain | Entities |
| Infrastructure / Persistence | Repository + mapper |
| Infrastructure / Data Access | SQLAlchemy engine, session, models |
