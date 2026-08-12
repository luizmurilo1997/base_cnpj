"""Modelos ORM — sócios."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.empresa import Empresa


class Socio(Base):
    """Tabela socios."""

    __tablename__ = "socios"

    socio_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    cnpj_basico: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    identificador_de_socio: Mapped[str] = mapped_column(String(1), nullable=False)
    nome_socio: Mapped[str | None] = mapped_column(Text)
    cnpj_cpf_do_socio: Mapped[str] = mapped_column(String(14), nullable=False)
    qualificacao_do_socio: Mapped[str | None] = mapped_column(String(2))
    data_entrada_sociedade: Mapped[date | None] = mapped_column(Date)
    pais: Mapped[str | None] = mapped_column(String(3))
    representante_legal: Mapped[str | None] = mapped_column(String(11))
    nome_do_representante: Mapped[str | None] = mapped_column(Text)
    qualificacao_do_representante_legal: Mapped[str | None] = mapped_column(String(2))
    faixa_etaria: Mapped[str | None] = mapped_column(String(1))
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_atualizacao: Mapped[datetime | None] = mapped_column(DateTime)

    empresa: Mapped[Empresa | None] = relationship(
        "Empresa",
        back_populates="socios",
        lazy="select",
        primaryjoin="foreign(Socio.cnpj_basico) == Empresa.cnpj_basico",
        viewonly=True,
    )
