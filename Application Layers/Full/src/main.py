from contextlib import asynccontextmanager

from fastapi import FastAPI

from presentation.api.user_controller import router
from infrastructure.data_access.database import Base, engine
# Import model so SQLAlchemy registers its table
from infrastructure.data_access.models import UserModel  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Create User — Clean Architecture + Domain Model",
    lifespan=lifespan,
)
app.include_router(router)
