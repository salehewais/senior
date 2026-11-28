from domain.entities.user import User
from application.interfaces.user_repository import (
    UserRepository,
    DuplicateEmailError,
)


class CreateUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, name: str, email: str) -> User:
        normalized_email = User.normalize_email(email)

        existing_user = self.user_repository.find_by_email(
            normalized_email
        )

        if existing_user:
            raise DuplicateEmailError("Email already exists")

        user = User.create(
            name=name,
            email=normalized_email,
        )

        self.user_repository.save(user)
        return user
