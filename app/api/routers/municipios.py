"""Router — empresas por município."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import EmpresaServiceDep, Pagination
from app.schemas.empresa import EmpresaResumoSchema
from app.schemas.responses import PaginatedResponse

router = APIRouter(prefix="/municipios", tags=["Municípios"])


@router.get(
    "/{codigo}",
    response_model=PaginatedResponse[EmpresaResumoSchema],
    summary="Empresas por município",
    description="Lista estabelecimentos pelo código de município da Receita Federal.",
)
def empresas_por_municipio(
    codigo: str,
    service: EmpresaServiceDep,
    pagination: Pagination,
) -> PaginatedResponse[EmpresaResumoSchema]:
    """Empresas filtradas por município."""
    page, size = pagination
    return service.por_municipio(codigo, page=page, size=size)
