from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Title is required")
        if not self.author.strip():
            raise ValueError("Author is required")
