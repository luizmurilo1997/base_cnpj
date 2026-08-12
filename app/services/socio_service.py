"""Serviço de busca de sócios."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.repositories.socio_repository import SocioRepository
from app.schemas.responses import PaginatedResponse
from app.schemas.socio import SocioFiltros, SocioListagemSchema
from app.utils.constants import IDENTIFICADOR_SOCIO


class SocioService:
    """Regras de negócio para consulta de sócios."""

    def __init__(self, db: Session) -> None:
        self.repo = SocioRepository(db)

    def buscar(
        self,
        filtros: SocioFiltros,
        *,
        page: int,
        size: int,
    ) -> PaginatedResponse[SocioListagemSchema]:
        """Busca paginada de sócios."""
        if not any([filtros.nome, filtros.cpf, filtros.empresa]):
            raise ValidationAppError(
                "Informe ao menos um filtro (nome, cpf ou empresa)."
            )
        if filtros.nome and len(filtros.nome.strip()) < 3:
            raise ValidationAppError("nome deve ter ao menos 3 caracteres")

        resultado = self.repo.buscar(filtros, page=page, size=size)
        items = [
            SocioListagemSchema(
                socio_id=socio.socio_id,
                cnpj_basico=socio.cnpj_basico,
                razao_social=razao,
                nome_socio=socio.nome_socio,
                cnpj_cpf_do_socio=socio.cnpj_cpf_do_socio,
                identificador_de_socio=socio.identificador_de_socio,
                identificador_de_socio_descricao=IDENTIFICADOR_SOCIO.get(
                    socio.identificador_de_socio
                ),
                qualificacao_do_socio=socio.qualificacao_do_socio,
                qualificacao_do_socio_descricao=qual_desc,
                data_entrada_sociedade=socio.data_entrada_sociedade,
            )
            for socio, razao, qual_desc in resultado.rows
        ]
        return PaginatedResponse(
            items=items,
            page=page,
            size=size,
            has_more=resultado.has_more,
            total=None,
            pages=None,
        )
