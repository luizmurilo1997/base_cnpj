"""Modelos ORM — empresas e estabelecimentos."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Double, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.socio import Socio


class Empresa(Base):
    """Tabela empresas (nível empresa / CNPJ básico)."""

    __tablename__ = "empresas"

    cnpj_basico: Mapped[str] = mapped_column(String(8), primary_key=True)
    razao_social: Mapped[str | None] = mapped_column(Text)
    natureza_juridica: Mapped[str | None] = mapped_column(String(4))
    qualificacao_responsavel: Mapped[str | None] = mapped_column(String(2))
    capital_social: Mapped[float | None] = mapped_column(Double)
    porte: Mapped[str | None] = mapped_column(String(2))
    ente_federativo_responsavel: Mapped[str | None] = mapped_column(Text)
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime)

    estabelecimentos: Mapped[list[Estabelecimento]] = relationship(
        "Estabelecimento",
        back_populates="empresa",
        lazy="select",
        primaryjoin="Empresa.cnpj_basico == foreign(Estabelecimento.cnpj_basico)",
        viewonly=True,
    )
    socios: Mapped[list[Socio]] = relationship(
        "Socio",
        back_populates="empresa",
        lazy="select",
        primaryjoin="Empresa.cnpj_basico == foreign(Socio.cnpj_basico)",
        viewonly=True,
    )


class Estabelecimento(Base):
    """Tabela estabelecimentos (matriz/filiais)."""

    __tablename__ = "estabelecimentos"

    cnpj_basico: Mapped[str] = mapped_column(String(8), primary_key=True)
    cnpj_ordem: Mapped[str] = mapped_column(String(4), primary_key=True)
    cnpj_dv: Mapped[str] = mapped_column(String(2), primary_key=True)
    identificador_matriz_filial: Mapped[int | None] = mapped_column(Integer)
    nome_fantasia: Mapped[str | None] = mapped_column(Text)
    situacao_cadastral: Mapped[str | None] = mapped_column(String(2))
    data_situacao_cadastral: Mapped[date | None] = mapped_column(Date)
    motivo_situacao_cadastral: Mapped[str | None] = mapped_column(String(2))
    nome_cidade_exterior: Mapped[str | None] = mapped_column(Text)
    pais: Mapped[str | None] = mapped_column(String(3))
    data_inicio_atividade: Mapped[date | None] = mapped_column(Date)
    cnae_fiscal_principal: Mapped[str | None] = mapped_column(String(7))
    cnae_fiscal_secundaria: Mapped[str | None] = mapped_column(Text)
    tipo_logradouro: Mapped[str | None] = mapped_column(Text)
    logradouro: Mapped[str | None] = mapped_column(Text)
    numero: Mapped[str | None] = mapped_column(Text)
    complemento: Mapped[str | None] = mapped_column(Text)
    bairro: Mapped[str | None] = mapped_column(Text)
    cep: Mapped[str | None] = mapped_column(String(8))
    uf: Mapped[str | None] = mapped_column(String(2))
    municipio: Mapped[str | None] = mapped_column(String(7))
    ddd_1: Mapped[str | None] = mapped_column(String(4))
    telefone_1: Mapped[str | None] = mapped_column(String(8))
    ddd_2: Mapped[str | None] = mapped_column(String(4))
    telefone_2: Mapped[str | None] = mapped_column(String(8))
    ddd_fax: Mapped[str | None] = mapped_column(String(4))
    fax: Mapped[str | None] = mapped_column(String(8))
    correio_eletronico: Mapped[str | None] = mapped_column(Text)
    situacao_especial: Mapped[str | None] = mapped_column(Text)
    data_situacao_especial: Mapped[date | None] = mapped_column(Date)
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime)

    empresa: Mapped[Empresa | None] = relationship(
        "Empresa",
        back_populates="estabelecimentos",
        lazy="joined",
        primaryjoin="foreign(Estabelecimento.cnpj_basico) == Empresa.cnpj_basico",
        viewonly=True,
    )
