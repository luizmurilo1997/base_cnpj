"""Schemas Pydantic — sócios."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SocioResumoSchema(BaseModel):
    """Sócio em resposta de detalhe de CNPJ."""

    socio_id: UUID | None = None
    nome_socio: str | None = None
    cnpj_cpf_do_socio: str | None = None
    identificador_de_socio: str | None = None
    identificador_de_socio_descricao: str | None = None
    qualificacao_do_socio: str | None = None
    qualificacao_do_socio_descricao: str | None = None
    data_entrada_sociedade: date | None = None
    faixa_etaria: str | None = None
    faixa_etaria_descricao: str | None = None
    pais: str | None = None
    representante_legal: str | None = None
    nome_do_representante: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SocioListagemSchema(BaseModel):
    """Sócio em listagens com referência à empresa."""

    socio_id: UUID
    cnpj_basico: str
    razao_social: str | None = None
    nome_socio: str | None = None
    cnpj_cpf_do_socio: str | None = None
    identificador_de_socio: str | None = None
    identificador_de_socio_descricao: str | None = None
    qualificacao_do_socio: str | None = None
    qualificacao_do_socio_descricao: str | None = None
    data_entrada_sociedade: date | None = None

    model_config = ConfigDict(from_attributes=True)


class SocioFiltros(BaseModel):
    """Filtros opcionais para busca de sócios."""

    nome: str | None = None
    cpf: str | None = Field(default=None, description="CPF parcial (dígitos visíveis)")
    empresa: str | None = Field(default=None, description="CNPJ básico ou razão social")
