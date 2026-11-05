from domain.book import Book


class BookView:
    def show_book_added(self, book: Book) -> None:
        print(f"Added: {book.id} — {book.title}")

    def show_error(self, message: str) -> None:
        print(f"Error: {message}")

    def show_all(self, books: list[Book]) -> None:
        print("\nCurrent Books:")
        print("-" * 50)
        if not books:
            print("No books available.")
            return
        for book in books:
            print(f"{book.id}: {book.title} by {book.author}")
        print("-" * 50)
