"""Router — estatísticas e health checks."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.dependencies import EstatisticaServiceDep
from app.core.cache import check_redis
from app.core.config import get_settings
from app.core.database import check_database
from app.schemas.responses import HealthResponse, ReadyResponse

router_stats = APIRouter(tags=["Estatísticas"])
router_health = APIRouter(tags=["Health"])


class EstatisticasResponse(BaseModel):
    """Agregados da base CNPJ."""

    total_empresas: int
    empresas_ativas: int
    empresas_baixadas: int
    empresas_por_uf: dict[str, int] = Field(default_factory=dict)
    empresas_por_porte: dict[str, int] = Field(default_factory=dict)


@router_stats.get(
    "/estatisticas",
    response_model=EstatisticasResponse,
    summary="Estatísticas da base",
)
def estatisticas(service: EstatisticaServiceDep) -> EstatisticasResponse:
    """Retorna totais e distribuições."""
    return EstatisticasResponse(**service.obter())


@router_health.get("/health", response_model=HealthResponse, summary="Liveness")
def health() -> HealthResponse:
    """Indica que o processo da API está no ar."""
    settings = get_settings()
    return HealthResponse(status="ok", version=settings.app_version)


@router_health.get("/ready", response_model=ReadyResponse, summary="Readiness")
def ready() -> ReadyResponse:
    """Verifica dependências (PostgreSQL e Redis)."""
    db_ok = check_database()
    redis_ok = check_redis()
    status = "ok" if db_ok else "degraded"
    return ReadyResponse(status=status, database=db_ok, redis=redis_ok)
