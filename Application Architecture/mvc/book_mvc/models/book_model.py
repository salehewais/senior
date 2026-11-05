from domain.book import Book


class BookModel:
    def __init__(self) -> None:
        self._books: list[Book] = []
        self._next_id = 1

    def add_book(self, title: str, author: str) -> Book:
        book = Book(
            id=self._next_id,
            title=title.strip(),
            author=author.strip(),
        )
        self._books.append(book)
        self._next_id += 1
        return book

    def get_all(self) -> list[Book]:
        return list(self._books)
