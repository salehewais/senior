from presentation.contracts import BookRow, BookViewContract


class ConsoleBookView(BookViewContract):
    def show_message(self, message: str) -> None:
        print(f"\nMessage: {message}")

    def show_books(self, rows: list[BookRow]) -> None:
        print("\nCurrent Books:")
        print("-" * 50)
        if not rows:
            print("No books available.")
            return
        for book in rows:
            print(f"[{book.id}] {book.title} by {book.author}")
        print("-" * 50)
