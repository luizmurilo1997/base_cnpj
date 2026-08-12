"""Router — busca de empresas."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import EmpresaServiceDep, Pagination
from app.schemas.empresa import EmpresaFiltros, EmpresaResumoSchema
from app.schemas.responses import PaginatedResponse

router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.get(
    "",
    response_model=PaginatedResponse[EmpresaResumoSchema],
    summary="Buscar empresas",
    description=(
        "Busca empresas com filtros opcionais e paginação. "
        "Por padrão lista apenas matrizes, usa prefixo indexável no nome e "
        "não executa COUNT(*) sobre a base (retorna has_more)."
    ),
)
def buscar_empresas(
    service: EmpresaServiceDep,
    pagination: Pagination,
    nome: Annotated[
        str | None,
        Query(description="Razão social por prefixo (mín. 3 caracteres)"),
    ] = None,
    nome_fantasia: Annotated[
        str | None,
        Query(description="Nome fantasia por prefixo (mín. 3 caracteres)"),
    ] = None,
    cidade: Annotated[str | None, Query(description="Código ou nome do município")] = None,
    uf: Annotated[str | None, Query(min_length=2, max_length=2, description="UF")] = None,
    cnae: Annotated[str | None, Query(description="CNAE principal")] = None,
    situacao: Annotated[str | None, Query(description="Situação cadastral (ex: 02)")] = None,
    natureza_juridica: Annotated[str | None, Query(description="Código natureza jurídica")] = None,
    porte: Annotated[str | None, Query(description="Porte (00/01/03/05)")] = None,
    capital_minimo: Annotated[float | None, Query(ge=0, description="Capital social mínimo")] = None,
    capital_maximo: Annotated[float | None, Query(ge=0, description="Capital social máximo")] = None,
    apenas_matriz: Annotated[bool, Query(description="Somente matriz (default true)")] = True,
    busca_contem: Annotated[
        bool,
        Query(description="Busca substring (%termo%). Exige uf. Mais lento."),
    ] = False,
) -> PaginatedResponse[EmpresaResumoSchema]:
    """Lista empresas filtradas."""
    page, size = pagination
    filtros = EmpresaFiltros(
        nome=nome,
        nome_fantasia=nome_fantasia,
        cidade=cidade,
        uf=uf,
        cnae=cnae,
        situacao=situacao,
        natureza_juridica=natureza_juridica,
        porte=porte,
        capital_minimo=capital_minimo,
        capital_maximo=capital_maximo,
        apenas_matriz=apenas_matriz,
        busca_contem=busca_contem,
    )
    return service.buscar(filtros, page=page, size=size)
