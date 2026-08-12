"""Router — consulta por CNPJ."""

from __future__ import annotations

from fastapi import APIRouter, Path

from app.api.dependencies import EmpresaServiceDep
from app.schemas.empresa import EmpresaDetalheSchema
from app.schemas.responses import ErrorResponse

router = APIRouter(prefix="/cnpj", tags=["CNPJ"])


@router.get(
    "/{cnpj:path}",
    response_model=EmpresaDetalheSchema,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Consultar CNPJ",
    description=(
        "Retorna dados cadastrais completos de um estabelecimento pelo CNPJ. "
        "Aceita 14 caracteres sem máscara ou formato XX.XXX.XXX/XXXX-XX."
    ),
)
def consultar_cnpj(
    service: EmpresaServiceDep,
    cnpj: str = Path(..., description="CNPJ com ou sem máscara"),
) -> EmpresaDetalheSchema:
    """Consulta detalhada de um CNPJ."""
    return service.consultar_cnpj(cnpj)
