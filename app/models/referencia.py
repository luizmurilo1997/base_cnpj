"""Modelos ORM — tabelas de referência."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Cnae(Base):
    """Tabela cnaes."""

    __tablename__ = "cnaes"

    codigo: Mapped[str] = mapped_column(String(7), primary_key=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime)


class Municipio(Base):
    """Tabela municipios."""

    __tablename__ = "municipios"

    codigo: Mapped[str] = mapped_column(String(7), primary_key=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime)


class NaturezaJuridica(Base):
    """Tabela naturezas_juridicas."""

    __tablename__ = "naturezas_juridicas"

    codigo: Mapped[str] = mapped_column(String(4), primary_key=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime)


class Motivo(Base):
    """Tabela motivos."""

    __tablename__ = "motivos"

    codigo: Mapped[str] = mapped_column(String(2), primary_key=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime)


class Pais(Base):
    """Tabela paises."""

    __tablename__ = "paises"

    codigo: Mapped[str] = mapped_column(String(3), primary_key=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime)


class QualificacaoSocio(Base):
    """Tabela qualificacoes_socios."""

    __tablename__ = "qualificacoes_socios"

    codigo: Mapped[str] = mapped_column(String(2), primary_key=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime)
