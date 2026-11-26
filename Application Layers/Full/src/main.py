from fastapi import FastAPI

from infrastructure.data_access.database import Base, engine
from infrastructure.data_access import models  # noqa: F401 — register models
from presentation.api.user_controller import router

app = FastAPI(title="Create User — Clean Architecture Example")
app.include_router(router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
