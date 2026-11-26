from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class User:
    id: UUID
    name: str
    email: str

    @classmethod
    def create(cls, name: str, email: str):
        return cls(
            id=uuid4(),
            name=name,
            email=email,
        )
