from models.book_model import BookModel
from views.book_view import BookView


class BookController:
    def __init__(self, model: BookModel, view: BookView) -> None:
        self.model = model
        self.view = view

    def add_book(self, title: str, author: str) -> None:
        try:
            book = self.model.add_book(title, author)
            self.view.show_book_added(book)
        except ValueError as error:
            self.view.show_error(str(error))

    def list_books(self) -> None:
        books = self.model.get_all()
        self.view.show_all(books)
