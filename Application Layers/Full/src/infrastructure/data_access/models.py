from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from infrastructure.data_access.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
