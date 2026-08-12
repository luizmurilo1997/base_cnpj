"""Cliente Redis opcional para cache de consultas."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis_client: Any | None = None
_redis_unavailable = False


def get_redis() -> Any | None:
    """Retorna cliente Redis ou None se indisponível/desabilitado."""
    global _redis_client, _redis_unavailable

    settings = get_settings()
    if not settings.redis_enabled or not settings.redis_url:
        return None
    if _redis_unavailable:
        return None
    if _redis_client is not None:
        return _redis_client

    try:
        import redis

        client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        _redis_client = client
        logger.info("Redis conectado em %s", settings.redis_url)
        return _redis_client
    except Exception as exc:
        _redis_unavailable = True
        logger.warning("Redis indisponível, cache desabilitado: %s", exc)
        return None


def cache_get(key: str) -> dict[str, Any] | None:
    """Obtém valor JSON do cache."""
    client = get_redis()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Falha ao ler cache (%s): %s", key, exc)
        return None


def cache_set(key: str, value: dict[str, Any], ttl: int | None = None) -> None:
    """Grava valor JSON no cache com TTL."""
    client = get_redis()
    if client is None:
        return
    settings = get_settings()
    try:
        client.setex(key, ttl or settings.cache_ttl_seconds, json.dumps(value, default=str))
    except Exception as exc:
        logger.warning("Falha ao gravar cache (%s): %s", key, exc)


def cache_delete(key: str) -> None:
    """Remove chave do cache."""
    client = get_redis()
    if client is None:
        return
    try:
        client.delete(key)
    except Exception as exc:
        logger.warning("Falha ao remover cache (%s): %s", key, exc)


def check_redis() -> bool:
    """Verifica se o Redis está acessível."""
    client = get_redis()
    if client is None:
        return False
    try:
        return bool(client.ping())
    except Exception:
        return False
