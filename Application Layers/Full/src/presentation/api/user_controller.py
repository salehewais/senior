from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from infrastructure.data_access.database import SessionLocal
from infrastructure.persistence.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from application.use_cases.create_user import CreateUser
from application.interfaces.user_repository import DuplicateEmailError

router = APIRouter()


class CreateUserRequest(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users", response_model=UserResponse)
def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
):
    repository = PostgresUserRepository(db)
    use_case = CreateUser(repository)

    try:
        user = use_case.execute(request.name, request.email)
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
    )
