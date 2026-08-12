"""Router — empresas por estado (UF)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import EmpresaServiceDep, Pagination
from app.schemas.empresa import EmpresaResumoSchema
from app.schemas.responses import PaginatedResponse

router = APIRouter(prefix="/estados", tags=["Estados"])


@router.get(
    "/{uf}",
    response_model=PaginatedResponse[EmpresaResumoSchema],
    summary="Empresas por UF",
    description="Lista estabelecimentos pela sigla do estado (ex: SP, RJ).",
)
def empresas_por_uf(
    uf: str,
    service: EmpresaServiceDep,
    pagination: Pagination,
) -> PaginatedResponse[EmpresaResumoSchema]:
    """Empresas filtradas por UF."""
    page, size = pagination
    return service.por_uf(uf, page=page, size=size)
