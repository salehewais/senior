from domain.entities.user import User
from application.interfaces.user_repository import UserRepository


class CreateUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, name: str, email: str) -> User:
        user = User.create(name, email)
        self.user_repository.save(user)
        return user
