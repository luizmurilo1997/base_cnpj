"""Aplicação FastAPI — CNPJ API."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.routers import cnae, cnpj, empresas, estados, health, municipios, socios
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

settings = get_settings()
setup_logging(debug=settings.debug)

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Ciclo de vida da aplicação."""
    yield


def create_app() -> FastAPI:
    """Factory da aplicação FastAPI."""
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API REST para consulta à base pública de CNPJ da Receita Federal. "
            "Os dados são carregados pelo pipeline ETL existente (cnpj-data-pipeline)."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.add_middleware(SlowAPIMiddleware)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(GZipMiddleware, minimum_size=500)

    register_exception_handlers(application)

    application.include_router(cnpj.router)
    application.include_router(empresas.router)
    application.include_router(socios.router)
    application.include_router(cnae.router)
    application.include_router(municipios.router)
    application.include_router(estados.router)
    application.include_router(health.router_stats)
    application.include_router(health.router_health)

    @application.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "redoc": "/redoc",
        }

    return application


app = create_app()
