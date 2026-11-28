from abc import ABC, abstractmethod

from domain.entities.user import User


class DuplicateEmailError(Exception):
    pass


class UserRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass
