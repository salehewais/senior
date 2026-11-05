from controllers.book_controller import BookController
from models.book_model import BookModel
from views.book_view import BookView


def main() -> None:
    model = BookModel()
    view = BookView()
    controller = BookController(model=model, view=view)

    print("--- Adding Books ---")
    controller.add_book(
        "The Pragmatic Programmer",
        "Andy Hunt and Dave Thomas",
    )
    controller.add_book(
        "Clean Code",
        "Robert C. Martin",
    )

    print("\n--- Testing Error Handling ---")
    controller.add_book("", "Some Author")

    print("\n--- Listing All Books ---")
    controller.list_books()


if __name__ == "__main__":
    main()
