"""Serviço de busca unificada e estatísticas."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.empresa import EmpresaFiltros, EmpresaResumoSchema
from app.schemas.responses import PaginatedResponse
from app.services.empresa_service import EmpresaService
from app.utils.constants import PORTE_EMPRESA


class BuscaService:
    """Fachada de buscas por filtros compostos."""

    def __init__(self, db: Session) -> None:
        self.empresa_service = EmpresaService(db)

    def empresas(
        self,
        filtros: EmpresaFiltros,
        *,
        page: int,
        size: int,
    ) -> PaginatedResponse[EmpresaResumoSchema]:
        """Delega busca de empresas."""
        return self.empresa_service.buscar(filtros, page=page, size=size)


class EstatisticaService:
    """Agregações estatísticas da base."""

    def __init__(self, db: Session) -> None:
        self.repo = EmpresaRepository(db)

    def obter(self) -> dict:
        """Retorna estatísticas com descrições de porte."""
        raw = self.repo.estatisticas()
        por_porte = {
            PORTE_EMPRESA.get(codigo, codigo): quantidade
            for codigo, quantidade in raw["por_porte"].items()
        }
        return {
            "total_empresas": raw["total_empresas"],
            "empresas_ativas": raw["empresas_ativas"],
            "empresas_baixadas": raw["empresas_baixadas"],
            "empresas_por_uf": raw["por_uf"],
            "empresas_por_porte": por_porte,
        }
