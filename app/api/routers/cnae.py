"""Router — empresas por CNAE."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import EmpresaServiceDep, Pagination
from app.schemas.empresa import EmpresaResumoSchema
from app.schemas.responses import PaginatedResponse

router = APIRouter(prefix="/cnae", tags=["CNAE"])


@router.get(
    "/{codigo}",
    response_model=PaginatedResponse[EmpresaResumoSchema],
    summary="Empresas por CNAE",
    description="Lista estabelecimentos com o CNAE fiscal principal informado.",
)
def empresas_por_cnae(
    codigo: str,
    service: EmpresaServiceDep,
    pagination: Pagination,
) -> PaginatedResponse[EmpresaResumoSchema]:
    """Empresas filtradas por CNAE."""
    page, size = pagination
    return service.por_cnae(codigo, page=page, size=size)
