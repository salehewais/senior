import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from application.repository_port import BookRepositoryPort
from domain.book import Book
from infrastructure.memory_repository import InMemoryBookRepository
from presentation.contracts import BookRow, BookViewContract
from presentation.presenter import BookPresenter


class FakeBookRepository(BookRepositoryPort):
    def __init__(self) -> None:
        self.books: list[Book] = []

    def add(self, book: Book) -> Book:
        stored_book = Book(
            id=len(self.books) + 1,
            title=book.title,
            author=book.author,
        )
        self.books.append(stored_book)
        return stored_book

    def get_all(self) -> list[Book]:
        return list(self.books)


class FakeBookView(BookViewContract):
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.displayed_books: list[BookRow] = []

    def show_message(self, message: str) -> None:
        self.messages.append(message)

    def show_books(self, rows: list[BookRow]) -> None:
        self.displayed_books = list(rows)


class BookPresenterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = FakeBookRepository()
        self.view = FakeBookView()
        self.presenter = BookPresenter(repo=self.repo, view=self.view)

    def test_empty_title_does_not_persist(self) -> None:
        self.presenter.add_book("   ", "Eric Evans")

        self.assertEqual(self.view.messages, ["Title is required"])
        self.assertEqual(self.repo.books, [])
        self.assertEqual(self.view.displayed_books, [])

    def test_empty_author_does_not_persist(self) -> None:
        self.presenter.add_book("Domain-Driven Design", "  ")

        self.assertEqual(self.view.messages, ["Author is required"])
        self.assertEqual(self.repo.get_all(), [])
        self.assertEqual(self.view.displayed_books, [])

    def test_add_book_stores_entity_and_shows_row(self) -> None:
        self.presenter.add_book("  Domain-Driven Design  ", " Eric Evans ")

        stored = self.repo.get_all()
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0].id, 1)
        self.assertEqual(stored[0].title, "Domain-Driven Design")
        self.assertEqual(stored[0].author, "Eric Evans")
        self.assertEqual(self.view.messages, [])
        self.assertEqual(
            self.view.displayed_books,
            [BookRow(1, "Domain-Driven Design", "Eric Evans")],
        )

    def test_second_add_refreshes_every_row(self) -> None:
        self.presenter.add_book("Domain-Driven Design", "Eric Evans")
        self.presenter.add_book(
            "Patterns of Enterprise Application Architecture",
            "Martin Fowler",
        )

        self.assertEqual(
            [(row.id, row.title) for row in self.view.displayed_books],
            [
                (1, "Domain-Driven Design"),
                (2, "Patterns of Enterprise Application Architecture"),
            ],
        )


class BookInvariantTests(unittest.TestCase):
    def test_blank_title_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "title"):
            Book(id=1, title="   ", author="Eric Evans")

    def test_blank_author_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "author"):
            Book(id=1, title="Domain-Driven Design", author="   ")


class InMemoryBookRepositoryTests(unittest.TestCase):
    def test_repository_assigns_id(self) -> None:
        repo = InMemoryBookRepository()
        incoming = Book(id=0, title="Domain-Driven Design", author="Eric Evans")

        stored = repo.add(incoming)

        self.assertEqual(stored.id, 1)
        self.assertEqual(incoming.id, 0)
        self.assertEqual(repo.get_all(), [stored])
