from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BookRow:
    id: int
    title: str
    author: str


class BookViewContract(ABC):
    @abstractmethod
    def show_message(self, message: str) -> None:
        pass

    @abstractmethod
    def show_books(self, rows: list[BookRow]) -> None:
        pass
