from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class User:
    id: UUID
    name: str
    email: str

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @classmethod
    def create(cls, name: str, email: str):
        name = name.strip()
        email = cls.normalize_email(email)

        if not name:
            raise ValueError("Name is required")

        if "@" not in email:
            raise ValueError("Invalid email")

        return cls(
            id=uuid4(),
            name=name,
            email=email,
        )

    def change_email(self, new_email: str):
        new_email = self.normalize_email(new_email)

        if not new_email or "@" not in new_email:
            raise ValueError("Invalid email")

        self.email = new_email
