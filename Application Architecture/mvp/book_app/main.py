from infrastructure.memory_repository import InMemoryBookRepository
from presentation.console_view import ConsoleBookView
from presentation.presenter import BookPresenter


def main() -> None:
    repo = InMemoryBookRepository()
    view = ConsoleBookView()
    presenter = BookPresenter(repo=repo, view=view)

    print("=== Adding Books ===")
    presenter.add_book("Domain-Driven Design", "Eric Evans")
    presenter.add_book(
        "Patterns of Enterprise Application Architecture",
        "Martin Fowler",
    )

    print("\n=== Testing Empty Title ===")
    presenter.add_book("   ", "Some Author")

    print("\n=== Testing Empty Author ===")
    presenter.add_book("Clean Code", "   ")


if __name__ == "__main__":
    main()
