from domain.entities.user import User
from infrastructure.data_access.models import UserModel


class UserMapper:
    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            name=user.name,
            email=user.email,
        )

    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
        )
