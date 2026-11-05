from application.repository_port import BookRepositoryPort
from domain.book import Book


class InMemoryBookRepository(BookRepositoryPort):
    def __init__(self) -> None:
        self._books: list[Book] = []
        self._next_id = 1

    def add(self, book: Book) -> Book:
        stored_book = Book(
            id=self._next_id,
            title=book.title,
            author=book.author,
        )
        self._books.append(stored_book)
        self._next_id += 1
        return stored_book

    def get_all(self) -> list[Book]:
        return list(self._books)
