"""Schemas Pydantic — respostas comuns e paginação."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Resposta padrão de erro."""

    error: str
    details: object | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Envelope de paginação (sem COUNT(*) obrigatório)."""

    items: list[T]
    page: int = Field(ge=1)
    size: int = Field(ge=1)
    has_more: bool = False
    total: int | None = None
    pages: int | None = None

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Resposta do health check."""

    status: str
    version: str


class ReadyResponse(BaseModel):
    """Resposta do readiness check."""

    status: str
    database: bool
    redis: bool


class CodigoDescricao(BaseModel):
    """Par código + descrição de domínio."""

    codigo: str | None = None
    descricao: str | None = None


class EnderecoSchema(BaseModel):
    """Endereço completo do estabelecimento."""

    tipo_logradouro: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cep: str | None = None
    municipio: str | None = None
    municipio_nome: str | None = None
    uf: str | None = None
    pais: str | None = None
    nome_cidade_exterior: str | None = None


class ContatoSchema(BaseModel):
    """Telefones e e-mail."""

    telefone: str | None = None
    telefone_2: str | None = None
    fax: str | None = None
    email: str | None = None
