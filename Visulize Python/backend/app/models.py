from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TraceRequest(BaseModel):
    code: str
    stdin: str = ""


class BindingModel(BaseModel):
    name: str
    value: dict[str, Any]


class FrameModel(BaseModel):
    func: str
    line: int
    locals: list[BindingModel]


class ExceptionInfo(BaseModel):
    type: str
    message: str


class StepModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    line: int
    event: Literal["line", "call", "return", "exception"]
    func: str
    stdout: str
    exception: ExceptionInfo | None = None
    stack: list[FrameModel]
    globals_: list[BindingModel] = Field(alias="globals")
    heap: dict[str, Any]
    return_value: dict[str, Any] | None = None


class TraceErrorModel(BaseModel):
    type: str
    message: str
    line: int | None = None


class TraceResponse(BaseModel):
    steps: list[StepModel]
    stopped: Literal["step_limit", "timeout"] | None = None
    error: TraceErrorModel | None = None
