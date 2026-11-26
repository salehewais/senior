from domain.entities.user import User
from application.interfaces.user_repository import UserRepository
from infrastructure.persistence.mappers.user_mapper import UserMapper


class PostgresUserRepository(UserRepository):
    def __init__(self, session):
        self.session = session

    def save(self, user: User) -> None:
        user_model = UserMapper.to_model(user)
        self.session.add(user_model)
        self.session.commit()
