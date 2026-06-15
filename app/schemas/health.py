from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    service: str
    environment: str
    version: str


class ReadinessResponse(HealthResponse):
    checks: dict[str, str] = Field(default_factory=dict)

