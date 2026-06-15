import re
from collections.abc import Mapping
from typing import Any

SENSITIVE_KEYS = {
    "authorization",
    "cookie",
    "set-cookie",
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "x-api-key",
    "jwt",
    "cpf",
}

EMAIL_RE = re.compile(r"(?P<first>[A-Za-z0-9._%+-])[^@\s]*@(?P<domain_first>[A-Za-z0-9])[^@\s]*")
CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("_", "-")
    return normalized in SENSITIVE_KEYS or any(part in normalized for part in SENSITIVE_KEYS)


def mask_email(value: str) -> str:
    return EMAIL_RE.sub(r"\g<first>***@\g<domain_first>***", value)


def mask_personal_identifiers(value: str) -> str:
    return CPF_RE.sub("***.***.***-**", mask_email(value))


def sanitize_value(key: str | None, value: Any) -> Any:
    if key and is_sensitive_key(key):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return sanitize_mapping(value)
    if isinstance(value, list):
        return [sanitize_value(None, item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_value(None, item) for item in value)
    if isinstance(value, str):
        return mask_personal_identifiers(value)
    return value


def sanitize_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    return {key: sanitize_value(key, value) for key, value in data.items()}

