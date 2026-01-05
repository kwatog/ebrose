from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from typing import Literal, Optional


_TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
_FALSE_VALUES = {"0", "false", "f", "no", "n", "off"}


def _get_env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    return default if value is None else value


def _get_env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False

    return default


def _get_env_csv(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if value is None:
        return default

    items = [part.strip() for part in value.split(",")]
    return [item for item in items if item]


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    
    try:
        return int(value.strip())
    except ValueError:
        import logging
        logging.warning(f"Invalid integer value for {name}: '{value}', using default: {default}")
        return default


def _is_production_environment(environment: str) -> bool:
    return environment.lower() in {"production", "prod", "staging"}


CookieSameSite = Literal["lax", "strict", "none"]


@dataclass(frozen=True)
class Settings:
    environment: str
    is_production: bool

    debug: bool
    docs_enabled: bool
    log_level: str

    run_migrations_on_startup: bool
    auto_create_tables: bool

    cors_allowed_origins: list[str]
    cors_allow_credentials: bool
    cors_allow_methods: list[str]
    cors_allow_headers: list[str]

    cookie_secure: bool
    cookie_samesite: CookieSameSite
    cookie_path: str
    cookie_domain: Optional[str]
    
    rate_limit_enabled: bool
    rate_limit_max_attempts: int
    rate_limit_window_seconds: int
    rate_limit_block_seconds: int
    
    trusted_proxies: list[str]



@lru_cache
def get_settings() -> Settings:
    environment = _get_env_str("ENVIRONMENT", "development").strip()
    is_production = _is_production_environment(environment)

    debug_default = not is_production
    docs_enabled_default = not is_production

    allowed_origins_default = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    cors_allowed_origins = _get_env_csv("ALLOWED_ORIGINS", allowed_origins_default)

    cors_allow_methods = _get_env_csv(
        "CORS_ALLOW_METHODS",
        ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    cors_allow_headers_default = ["Authorization", "Content-Type"] if is_production else ["*"]
    cors_allow_headers = _get_env_csv("CORS_ALLOW_HEADERS", cors_allow_headers_default)

    cookie_samesite_raw = _get_env_str("COOKIE_SAMESITE", "lax").strip().lower()
    if cookie_samesite_raw == "strict":
        cookie_samesite: Literal["lax", "strict", "none"] = "strict"
    elif cookie_samesite_raw == "none":
        cookie_samesite = "none"
    else:
        cookie_samesite = "lax"

    cookie_secure_default = is_production or cookie_samesite == "none"
    cookie_secure = _get_env_bool("COOKIE_SECURE", default=cookie_secure_default)
    if cookie_samesite == "none" and not cookie_secure:
        cookie_secure = True

    rate_limit_enabled_default = environment.lower() not in {"test", "testing"}
    
    return Settings(
        environment=environment,
        is_production=is_production,
        debug=_get_env_bool("DEBUG", default=debug_default),
        docs_enabled=_get_env_bool("DOCS_ENABLED", default=docs_enabled_default),
        log_level=_get_env_str("LOG_LEVEL", "INFO"),
        run_migrations_on_startup=_get_env_bool("RUN_MIGRATIONS_ON_STARTUP", default=not is_production),
        auto_create_tables=_get_env_bool("AUTO_CREATE_TABLES", default=not is_production),
        cors_allowed_origins=cors_allowed_origins,
        cors_allow_credentials=_get_env_bool("CORS_ALLOW_CREDENTIALS", default=True),
        cors_allow_methods=cors_allow_methods,
        cors_allow_headers=cors_allow_headers,
        cookie_secure=cookie_secure,
        cookie_samesite=cookie_samesite,
        cookie_path=_get_env_str("COOKIE_PATH", "/"),
        cookie_domain=os.getenv("COOKIE_DOMAIN"),
        rate_limit_enabled=_get_env_bool("RATE_LIMIT_ENABLED", default=rate_limit_enabled_default),
        rate_limit_max_attempts=_get_env_int("RATE_LIMIT_MAX_ATTEMPTS", 5),
        rate_limit_window_seconds=_get_env_int("RATE_LIMIT_WINDOW_SECONDS", 60),
        rate_limit_block_seconds=_get_env_int("RATE_LIMIT_BLOCK_SECONDS", 60),
        trusted_proxies=_get_env_csv("TRUSTED_PROXIES", []),
    )

