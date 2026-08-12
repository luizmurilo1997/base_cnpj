"""Repositório de sócios."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Select, select, text
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.referencia import QualificacaoSocio
from app.models.socio import Socio
from app.schemas.socio import SocioFiltros
from app.utils.cnpj import limpar_cnpj, validar_cnpj_basico


@dataclass(frozen=True)
class SocioBuscaResultado:
    """Resultado paginado sem COUNT(*) global."""

    rows: list[tuple[Socio, str | None, str | None]]
    has_more: bool


class SocioRepository:
    """Acesso a dados de sócios."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar(
        self,
        filtros: SocioFiltros,
        *,
        page: int,
        size: int,
    ) -> SocioBuscaResultado:
        """Busca paginada de sócios com filtros."""
        if self.db.bind is not None and self.db.bind.dialect.name == "postgresql":
            self.db.execute(text("SET LOCAL statement_timeout = '20000'"))

        base = select(Socio, Empresa.razao_social).outerjoin(
            Empresa, Socio.cnpj_basico == Empresa.cnpj_basico
        )
        base = self._aplicar_filtros(base, filtros)

        offset = (page - 1) * size
        rows_stmt = (
            base.order_by(Socio.nome_socio.asc().nulls_last(), Socio.cnpj_basico)
            .offset(offset)
            .limit(size + 1)
        )
        rows = list(self.db.execute(rows_stmt).all())
        has_more = len(rows) > size
        rows = rows[:size]

        quals = {s.qualificacao_do_socio for s, _ in rows if s.qualificacao_do_socio}
        mapa_qual = self._map_qualificacoes(quals)

        result: list[tuple[Socio, str | None, str | None]] = []
        for socio, razao in rows:
            qual_desc = (
                mapa_qual.get(socio.qualificacao_do_socio)
                if socio.qualificacao_do_socio
                else None
            )
            result.append((socio, razao, qual_desc))
        return SocioBuscaResultado(rows=result, has_more=has_more)

    def por_cnpj_basico(self, cnpj_basico: str) -> list[Socio]:
        """Lista sócios de uma empresa."""
        stmt = (
            select(Socio)
            .where(Socio.cnpj_basico == cnpj_basico)
            .order_by(Socio.nome_socio.asc().nulls_last())
        )
        return list(self.db.scalars(stmt).all())

    def _aplicar_filtros(self, stmt: Select, filtros: SocioFiltros) -> Select:
        if filtros.nome:
            termo = filtros.nome.strip().upper()
            stmt = stmt.where(Socio.nome_socio.like(f"{termo}%"))
        if filtros.cpf:
            cpf = "".join(ch for ch in filtros.cpf if ch.isdigit() or ch == "*")
            stmt = stmt.where(Socio.cnpj_cpf_do_socio.like(f"%{cpf}%"))
        if filtros.empresa:
            empresa = filtros.empresa.strip()
            limpo = limpar_cnpj(empresa)
            if validar_cnpj_basico(limpo[:8]) and len(limpo) >= 8:
                stmt = stmt.where(Socio.cnpj_basico == limpo[:8])
            else:
                stmt = stmt.where(Empresa.razao_social.like(f"{empresa.upper()}%"))
        return stmt

    def _map_qualificacoes(self, codigos: set[str]) -> dict[str, str | None]:
        if not codigos:
            return {}
        rows = self.db.execute(
            select(QualificacaoSocio.codigo, QualificacaoSocio.descricao).where(
                QualificacaoSocio.codigo.in_(codigos)
            )
        ).all()
        return {codigo: descricao for codigo, descricao in rows}
