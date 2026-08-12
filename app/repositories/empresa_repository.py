"""Repositório de empresas e estabelecimentos."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Select, func, select, text
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.empresa import Empresa, Estabelecimento
from app.models.referencia import Cnae, Municipio, NaturezaJuridica, QualificacaoSocio
from app.models.socio import Socio
from app.schemas.empresa import EmpresaFiltros
from app.utils.constants import MATRIZ


@dataclass(frozen=True)
class EmpresaLookupRow:
    """Linha agregada para montagem do detalhe de CNPJ."""

    estabelecimento: Estabelecimento
    empresa: Empresa
    socios: list[Socio]
    cnae_descricao: str | None
    municipio_nome: str | None
    natureza_descricao: str | None
    qualificacoes: dict[str, str | None]
    cnaes_secundarios: list[tuple[str, str | None]]


@dataclass(frozen=True)
class BuscaResultado:
    """Resultado paginado sem COUNT(*) global."""

    rows: list[tuple[Estabelecimento, Empresa, str | None, str | None]]
    has_more: bool


class EmpresaRepository:
    """Acesso a dados de empresas e estabelecimentos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_cnpj(
        self, cnpj_basico: str, cnpj_ordem: str, cnpj_dv: str
    ) -> EmpresaLookupRow | None:
        """Busca estabelecimento completo por CNPJ (PK)."""
        stmt = (
            select(Estabelecimento)
            .options(
                joinedload(Estabelecimento.empresa).selectinload(Empresa.socios),
            )
            .where(
                Estabelecimento.cnpj_basico == cnpj_basico,
                Estabelecimento.cnpj_ordem == cnpj_ordem,
                Estabelecimento.cnpj_dv == cnpj_dv,
            )
        )
        estabelecimento = self.db.scalars(stmt).unique().first()
        if estabelecimento is None or estabelecimento.empresa is None:
            return None

        empresa = estabelecimento.empresa
        socios = list(empresa.socios or [])

        cnae_descricao = self._descricao_cnae(estabelecimento.cnae_fiscal_principal)
        municipio_nome = self._descricao_municipio(estabelecimento.municipio)
        natureza_descricao = self._descricao_natureza(empresa.natureza_juridica)
        qualificacoes = self._qualificacoes_map(
            [s.qualificacao_do_socio for s in socios if s.qualificacao_do_socio]
        )
        cnaes_secundarios = self._cnaes_secundarios(estabelecimento.cnae_fiscal_secundaria)

        return EmpresaLookupRow(
            estabelecimento=estabelecimento,
            empresa=empresa,
            socios=socios,
            cnae_descricao=cnae_descricao,
            municipio_nome=municipio_nome,
            natureza_descricao=natureza_descricao,
            qualificacoes=qualificacoes,
            cnaes_secundarios=cnaes_secundarios,
        )

    def buscar(
        self,
        filtros: EmpresaFiltros,
        *,
        page: int,
        size: int,
    ) -> BuscaResultado:
        """Busca paginada sem COUNT(*) sobre a base inteira."""
        self._set_statement_timeout("20000")

        base = select(Estabelecimento, Empresa).join(
            Empresa, Estabelecimento.cnpj_basico == Empresa.cnpj_basico
        )
        if filtros.apenas_matriz:
            base = base.where(Estabelecimento.identificador_matriz_filial == MATRIZ)
        base = self._aplicar_filtros(base, filtros)

        offset = (page - 1) * size
        if filtros.nome:
            order = (
                Empresa.razao_social.asc().nulls_last(),
                Estabelecimento.cnpj_basico,
                Estabelecimento.cnpj_ordem,
            )
        else:
            order = (
                Estabelecimento.cnpj_basico,
                Estabelecimento.cnpj_ordem,
                Estabelecimento.cnpj_dv,
            )

        rows_stmt = base.order_by(*order).offset(offset).limit(size + 1)
        rows = list(self.db.execute(rows_stmt).all())
        has_more = len(rows) > size
        rows = rows[:size]

        municipio_codigos = {r[0].municipio for r in rows if r[0].municipio}
        cnae_codigos = {r[0].cnae_fiscal_principal for r in rows if r[0].cnae_fiscal_principal}
        municipios = self._map_municipios(municipio_codigos)
        cnaes = self._map_cnaes(cnae_codigos)

        result: list[tuple[Estabelecimento, Empresa, str | None, str | None]] = []
        for est, emp in rows:
            result.append(
                (
                    est,
                    emp,
                    municipios.get(est.municipio) if est.municipio else None,
                    cnaes.get(est.cnae_fiscal_principal) if est.cnae_fiscal_principal else None,
                )
            )
        return BuscaResultado(rows=result, has_more=has_more)

    def por_municipio(
        self, codigo: str, *, page: int, size: int
    ) -> BuscaResultado:
        """Empresas (estabelecimentos) por código de município."""
        return self.buscar(
            EmpresaFiltros(cidade=codigo, apenas_matriz=True),
            page=page,
            size=size,
        )

    def por_uf(self, uf: str, *, page: int, size: int) -> BuscaResultado:
        """Empresas por UF."""
        return self.buscar(
            EmpresaFiltros(uf=uf.upper(), apenas_matriz=True, situacao="02"),
            page=page,
            size=size,
        )

    def por_cnae(self, codigo: str, *, page: int, size: int) -> BuscaResultado:
        """Empresas por CNAE principal."""
        return self.buscar(
            EmpresaFiltros(cnae=codigo, apenas_matriz=True, situacao="02"),
            page=page,
            size=size,
        )

    def estatisticas(self) -> dict:
        """Agrega totais e distribuições."""
        self._set_statement_timeout("60000")
        total = self.db.scalar(select(func.count()).select_from(Estabelecimento)) or 0
        ativas = (
            self.db.scalar(
                select(func.count()).where(Estabelecimento.situacao_cadastral == "02")
            )
            or 0
        )
        baixadas = (
            self.db.scalar(
                select(func.count()).where(Estabelecimento.situacao_cadastral == "08")
            )
            or 0
        )

        por_uf_rows = self.db.execute(
            select(Estabelecimento.uf, func.count())
            .where(Estabelecimento.uf.is_not(None))
            .group_by(Estabelecimento.uf)
            .order_by(func.count().desc())
        ).all()

        por_porte_rows = self.db.execute(
            select(Empresa.porte, func.count())
            .where(Empresa.porte.is_not(None))
            .group_by(Empresa.porte)
            .order_by(func.count().desc())
        ).all()

        return {
            "total_empresas": int(total),
            "empresas_ativas": int(ativas),
            "empresas_baixadas": int(baixadas),
            "por_uf": {uf: int(qtd) for uf, qtd in por_uf_rows if uf},
            "por_porte": {porte: int(qtd) for porte, qtd in por_porte_rows if porte},
        }

    def _set_statement_timeout(self, millis: str) -> None:
        if self.db.bind is None or self.db.bind.dialect.name != "postgresql":
            return
        self.db.execute(text(f"SET LOCAL statement_timeout = '{millis}'"))

    def _aplicar_filtros(self, stmt: Select, filtros: EmpresaFiltros) -> Select:
        if filtros.nome:
            termo = filtros.nome.strip().upper()
            if filtros.busca_contem:
                stmt = stmt.where(Empresa.razao_social.like(f"%{termo}%"))
            else:
                stmt = stmt.where(Empresa.razao_social.like(f"{termo}%"))
        if filtros.nome_fantasia:
            termo = filtros.nome_fantasia.strip().upper()
            if filtros.busca_contem:
                stmt = stmt.where(Estabelecimento.nome_fantasia.like(f"%{termo}%"))
            else:
                stmt = stmt.where(Estabelecimento.nome_fantasia.like(f"{termo}%"))
        if filtros.cidade:
            cidade = filtros.cidade.strip()
            if cidade.isdigit():
                stmt = stmt.where(Estabelecimento.municipio == cidade)
            else:
                subq = select(Municipio.codigo).where(
                    Municipio.descricao.like(f"%{cidade.upper()}%")
                )
                stmt = stmt.where(Estabelecimento.municipio.in_(subq))
        if filtros.uf:
            stmt = stmt.where(Estabelecimento.uf == filtros.uf.strip().upper())
        if filtros.cnae:
            stmt = stmt.where(Estabelecimento.cnae_fiscal_principal == filtros.cnae.strip())
        if filtros.situacao:
            stmt = stmt.where(Estabelecimento.situacao_cadastral == filtros.situacao.strip())
        if filtros.natureza_juridica:
            stmt = stmt.where(Empresa.natureza_juridica == filtros.natureza_juridica.strip())
        if filtros.porte:
            stmt = stmt.where(Empresa.porte == filtros.porte.strip())
        if filtros.capital_minimo is not None:
            stmt = stmt.where(Empresa.capital_social >= filtros.capital_minimo)
        if filtros.capital_maximo is not None:
            stmt = stmt.where(Empresa.capital_social <= filtros.capital_maximo)
        return stmt

    def _descricao_cnae(self, codigo: str | None) -> str | None:
        if not codigo:
            return None
        return self.db.scalar(select(Cnae.descricao).where(Cnae.codigo == codigo))

    def _descricao_municipio(self, codigo: str | None) -> str | None:
        if not codigo:
            return None
        return self.db.scalar(select(Municipio.descricao).where(Municipio.codigo == codigo))

    def _descricao_natureza(self, codigo: str | None) -> str | None:
        if not codigo:
            return None
        return self.db.scalar(
            select(NaturezaJuridica.descricao).where(NaturezaJuridica.codigo == codigo)
        )

    def _qualificacoes_map(self, codigos: list[str]) -> dict[str, str | None]:
        if not codigos:
            return {}
        rows = self.db.execute(
            select(QualificacaoSocio.codigo, QualificacaoSocio.descricao).where(
                QualificacaoSocio.codigo.in_(set(codigos))
            )
        ).all()
        return {codigo: descricao for codigo, descricao in rows}

    def _cnaes_secundarios(self, raw: str | None) -> list[tuple[str, str | None]]:
        if not raw:
            return []
        codigos = [c.strip() for c in raw.split(",") if c.strip()]
        if not codigos:
            return []
        mapa = self._map_cnaes(set(codigos))
        return [(c, mapa.get(c)) for c in codigos]

    def _map_cnaes(self, codigos: set[str]) -> dict[str, str | None]:
        if not codigos:
            return {}
        rows = self.db.execute(
            select(Cnae.codigo, Cnae.descricao).where(Cnae.codigo.in_(codigos))
        ).all()
        return {codigo: descricao for codigo, descricao in rows}

    def _map_municipios(self, codigos: set[str]) -> dict[str, str | None]:
        if not codigos:
            return {}
        rows = self.db.execute(
            select(Municipio.codigo, Municipio.descricao).where(Municipio.codigo.in_(codigos))
        ).all()
        return {codigo: descricao for codigo, descricao in rows}
