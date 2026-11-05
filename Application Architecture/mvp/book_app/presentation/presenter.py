from application.repository_port import BookRepositoryPort
from domain.book import Book
from presentation.contracts import BookRow, BookViewContract


class BookPresenter:
    def __init__(
        self,
        repo: BookRepositoryPort,
        view: BookViewContract,
    ) -> None:
        self.repo = repo
        self.view = view

    def add_book(self, title: str, author: str) -> None:
        if not title.strip():
            self.view.show_message("Title is required")
            return
        if not author.strip():
            self.view.show_message("Author is required")
            return

        try:
            book = Book(
                id=0,
                title=title.strip(),
                author=author.strip(),
            )
            self.repo.add(book)
        except ValueError as exc:
            self.view.show_message(str(exc))
            return

        self.view.show_books(self._rows())

    def _rows(self) -> list[BookRow]:
        return [
            BookRow(id=book.id, title=book.title, author=book.author)
            for book in self.repo.get_all()
        ]
