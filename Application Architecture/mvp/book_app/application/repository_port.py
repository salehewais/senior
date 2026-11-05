from abc import ABC, abstractmethod

from domain.book import Book


class BookRepositoryPort(ABC):
    @abstractmethod
    def add(self, book: Book) -> Book:
        pass

    @abstractmethod
    def get_all(self) -> list[Book]:
        pass
