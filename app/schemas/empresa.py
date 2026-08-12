"""Schemas Pydantic — empresa / estabelecimento / CNPJ."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.responses import CodigoDescricao, ContatoSchema, EnderecoSchema
from app.schemas.socio import SocioResumoSchema


class EmpresaResumoSchema(BaseModel):
    """Resumo de empresa para listagens."""

    cnpj: str
    cnpj_basico: str
    razao_social: str | None = None
    nome_fantasia: str | None = None
    situacao_cadastral: str | None = None
    situacao_cadastral_descricao: str | None = None
    uf: str | None = None
    municipio: str | None = None
    municipio_nome: str | None = None
    cnae_principal: str | None = None
    cnae_principal_descricao: str | None = None
    porte: str | None = None
    porte_descricao: str | None = None
    capital_social: float | None = None
    data_abertura: date | None = None
    identificador_matriz_filial: int | None = None

    model_config = ConfigDict(from_attributes=True)


class EmpresaDetalheSchema(BaseModel):
    """Detalhe completo de um CNPJ (estabelecimento + empresa + sócios)."""

    cnpj: str
    cnpj_basico: str
    cnpj_ordem: str
    cnpj_dv: str
    razao_social: str | None = None
    nome_fantasia: str | None = None
    situacao_cadastral: str | None = None
    situacao_cadastral_descricao: str | None = None
    data_situacao_cadastral: date | None = None
    data_abertura: date | None = None
    natureza_juridica: CodigoDescricao | None = None
    capital_social: float | None = None
    porte: CodigoDescricao | None = None
    cnae_principal: CodigoDescricao | None = None
    cnaes_secundarios: list[CodigoDescricao] = Field(default_factory=list)
    endereco: EnderecoSchema | None = None
    contato: ContatoSchema | None = None
    identificador_matriz_filial: int | None = None
    identificador_matriz_filial_descricao: str | None = None
    socios: list[SocioResumoSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class EmpresaFiltros(BaseModel):
    """Filtros opcionais para busca de empresas."""

    nome: str | None = None
    nome_fantasia: str | None = None
    cidade: str | None = None
    uf: str | None = None
    cnae: str | None = None
    situacao: str | None = None
    natureza_juridica: str | None = None
    porte: str | None = None
    capital_minimo: float | None = None
    capital_maximo: float | None = None
    apenas_matriz: bool = True
    busca_contem: bool = False
