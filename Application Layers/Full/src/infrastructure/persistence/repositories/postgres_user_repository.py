from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.entities.user import User
from application.interfaces.user_repository import (
    UserRepository,
    DuplicateEmailError,
)
from infrastructure.data_access.models import UserModel
from infrastructure.persistence.mappers.user_mapper import UserMapper


class PostgresUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_email(self, email: str) -> User | None:
        statement = select(UserModel).where(
            UserModel.email == email
        )
        model = self.session.scalar(statement)

        if model is None:
            return None

        return UserMapper.to_entity(model)

    def save(self, user: User) -> None:
        try:
            user_model = UserMapper.to_model(user)
            self.session.add(user_model)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise DuplicateEmailError("Email already exists")
