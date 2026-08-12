"""Router — busca de sócios."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import Pagination, SocioServiceDep
from app.schemas.responses import PaginatedResponse
from app.schemas.socio import SocioFiltros, SocioListagemSchema

router = APIRouter(prefix="/socios", tags=["Sócios"])


@router.get(
    "",
    response_model=PaginatedResponse[SocioListagemSchema],
    summary="Buscar sócios",
    description="Busca sócios por nome, CPF parcial ou empresa.",
)
def buscar_socios(
    service: SocioServiceDep,
    pagination: Pagination,
    nome: Annotated[str | None, Query(description="Nome do sócio (parcial)")] = None,
    cpf: Annotated[str | None, Query(description="CPF parcial (dígitos visíveis)")] = None,
    empresa: Annotated[
        str | None, Query(description="CNPJ básico ou razão social da empresa")
    ] = None,
) -> PaginatedResponse[SocioListagemSchema]:
    """Lista sócios filtrados."""
    page, size = pagination
    filtros = SocioFiltros(nome=nome, cpf=cpf, empresa=empresa)
    return service.buscar(filtros, page=page, size=size)
