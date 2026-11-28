# FastAPI + PostgreSQL + SQLAlchemy

Clean Architecture + Domain Model example: create a User via `POST /users`.

- Domain validates name/email and owns `change_email` behavior
- Application orchestrates uniqueness checks via the repository
- Duplicate email → **409**; invalid name/email → **422**

## Docs

Open the Arabic walkthrough:

`docs/fastapi-postgres-architecture.html`

## Setup

1. Create a PostgreSQL database (default name in code: `mydb`).
2. Default connection string (overridable with `DATABASE_URL`):

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
  -d '{"name": "Ahmed", "email": "ahmed@example.com"}'
```

## Layers

| Layer | Role |
| --- | --- |
| Presentation | FastAPI controller, HTTP status mapping |
| Application | Use cases + repository interface (`find_by_email`, `DuplicateEmailError`) |
| Domain | Entity rules (`normalize_email`, `create`, `change_email`) |
| Infrastructure / Persistence | Repository + mapper |
| Infrastructure / Data Access | SQLAlchemy engine, session, models |
