"""Dependências FastAPI compartilhadas."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.services.busca_service import BuscaService, EstatisticaService
from app.services.empresa_service import EmpresaService
from app.services.socio_service import SocioService

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_empresa_service(db: DbSession) -> EmpresaService:
    """Injeta EmpresaService."""
    return EmpresaService(db)


def get_socio_service(db: DbSession) -> SocioService:
    """Injeta SocioService."""
    return SocioService(db)


def get_busca_service(db: DbSession) -> BuscaService:
    """Injeta BuscaService."""
    return BuscaService(db)


def get_estatistica_service(db: DbSession) -> EstatisticaService:
    """Injeta EstatisticaService."""
    return EstatisticaService(db)


def pagination_params(
    page: Annotated[int, Query(ge=1, description="Número da página")] = 1,
    size: Annotated[
        int,
        Query(ge=1, le=100, description="Itens por página (máx. 100)"),
    ] = 20,
) -> tuple[int, int]:
    """Parâmetros de paginação padrão."""
    return page, size


Pagination = Annotated[tuple[int, int], Depends(pagination_params)]

EmpresaServiceDep = Annotated[EmpresaService, Depends(get_empresa_service)]
SocioServiceDep = Annotated[SocioService, Depends(get_socio_service)]
BuscaServiceDep = Annotated[BuscaService, Depends(get_busca_service)]
EstatisticaServiceDep = Annotated[EstatisticaService, Depends(get_estatistica_service)]
