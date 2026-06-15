from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["local", "development", "staging", "production"]
CsvList = Annotated[list[str], NoDecode]


def _split_csv(value: object) -> object:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Observabilidade"
    app_version: str = "0.1.0"
    environment: Environment = "local"
    service_name: str = "observabilidade-api"
    log_level: str = "INFO"

    docs_enabled: bool = True
    metrics_enabled: bool = True

    cors_allowed_origins: CsvList = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )
    cors_allowed_methods: CsvList = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    trusted_hosts: CsvList = Field(
        default_factory=lambda: [
            "localhost",
            "127.0.0.1",
            "testserver",
            "api",
            "observabilidade-api",
        ]
    )

    hsts_enabled: bool = False

    otel_enabled: bool = False
    otel_exporter_otlp_endpoint: str | None = None
    otel_exporter_otlp_insecure: bool = True

    @field_validator("cors_allowed_origins", "cors_allowed_methods", "trusted_hosts", mode="before")
    @classmethod
    def parse_csv_lists(cls, value: object) -> object:
        return _split_csv(value)

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if self.environment == "production":
            if "*" in self.cors_allowed_origins:
                raise ValueError("CORS wildcard is not allowed in production.")
            if "*" in self.trusted_hosts:
                raise ValueError("Trusted host wildcard is not allowed in production.")
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def should_enable_docs(self) -> bool:
        return self.docs_enabled and not self.is_production


@lru_cache
def get_settings() -> Settings:
    return Settings()
