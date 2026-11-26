from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from infrastructure.data_access.database import SessionLocal
from infrastructure.persistence.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from application.use_cases.create_user import CreateUser

router = APIRouter()


class CreateUserRequest(BaseModel):
    name: str
    email: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users")
def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
):
    repository = PostgresUserRepository(db)
    use_case = CreateUser(repository)
    user = use_case.execute(request.name, request.email)
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
    }
