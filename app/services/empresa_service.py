"""Serviço de consulta e detalhe de empresas/CNPJ."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.cache import cache_get, cache_set
from app.core.exceptions import NotFoundError, ValidationAppError
from app.repositories.empresa_repository import EmpresaLookupRow, EmpresaRepository
from app.schemas.empresa import EmpresaDetalheSchema, EmpresaFiltros, EmpresaResumoSchema
from app.schemas.responses import (
    CodigoDescricao,
    ContatoSchema,
    EnderecoSchema,
    PaginatedResponse,
)
from app.schemas.socio import SocioResumoSchema
from app.utils.cnpj import montar_cnpj, parse_cnpj
from app.utils.constants import (
    IDENTIFICADOR_MATRIZ_FILIAL,
    IDENTIFICADOR_SOCIO,
    FAIXA_ETARIA,
    PORTE_EMPRESA,
    SITUACAO_CADASTRAL,
)

logger = logging.getLogger(__name__)


class EmpresaService:
    """Regras de negócio para consulta de empresas."""

    def __init__(self, db: Session) -> None:
        self.repo = EmpresaRepository(db)

    def consultar_cnpj(self, cnpj: str) -> EmpresaDetalheSchema:
        """Consulta detalhada por CNPJ com cache Redis."""
        try:
            basico, ordem, dv = parse_cnpj(cnpj)
        except ValueError as exc:
            raise ValidationAppError(str(exc)) from exc

        cache_key = f"cnpj:{basico}{ordem}{dv}"
        cached = cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache hit para %s", cache_key)
            return EmpresaDetalheSchema.model_validate(cached)

        row = self.repo.get_by_cnpj(basico, ordem, dv)
        if row is None:
            raise NotFoundError(f"CNPJ {basico}{ordem}{dv} não encontrado")

        detalhe = self._to_detalhe(row)
        cache_set(cache_key, detalhe.model_dump(mode="json"))
        return detalhe

    def buscar(
        self,
        filtros: EmpresaFiltros,
        *,
        page: int,
        size: int,
    ) -> PaginatedResponse[EmpresaResumoSchema]:
        """Busca paginada de empresas."""
        self._validar_filtros(filtros)
        resultado = self.repo.buscar(filtros, page=page, size=size)
        items = [
            self._to_resumo(est, emp, mun, cnae) for est, emp, mun, cnae in resultado.rows
        ]
        return PaginatedResponse(
            items=items,
            page=page,
            size=size,
            has_more=resultado.has_more,
            total=None,
            pages=None,
        )

    def por_municipio(
        self, codigo: str, *, page: int, size: int
    ) -> PaginatedResponse[EmpresaResumoSchema]:
        """Empresas por município."""
        return self.buscar(
            EmpresaFiltros(cidade=codigo, apenas_matriz=True),
            page=page,
            size=size,
        )

    def por_uf(
        self, uf: str, *, page: int, size: int
    ) -> PaginatedResponse[EmpresaResumoSchema]:
        """Empresas por UF (matrizes ativas)."""
        if len(uf) != 2:
            raise ValidationAppError("UF deve ter 2 caracteres")
        return self.buscar(
            EmpresaFiltros(uf=uf.upper(), apenas_matriz=True, situacao="02"),
            page=page,
            size=size,
        )

    def por_cnae(
        self, codigo: str, *, page: int, size: int
    ) -> PaginatedResponse[EmpresaResumoSchema]:
        """Empresas por CNAE (matrizes ativas)."""
        return self.buscar(
            EmpresaFiltros(cnae=codigo, apenas_matriz=True, situacao="02"),
            page=page,
            size=size,
        )

    def _validar_filtros(self, filtros: EmpresaFiltros) -> None:
        if filtros.nome and len(filtros.nome.strip()) < 3:
            raise ValidationAppError("nome deve ter ao menos 3 caracteres")
        if filtros.nome_fantasia and len(filtros.nome_fantasia.strip()) < 3:
            raise ValidationAppError("nome_fantasia deve ter ao menos 3 caracteres")
        if filtros.busca_contem and not filtros.uf:
            raise ValidationAppError(
                "busca_contem=true exige o filtro uf para evitar full scan"
            )

    def _to_detalhe(self, row: EmpresaLookupRow) -> EmpresaDetalheSchema:
        est = row.estabelecimento
        emp = row.empresa
        cnpj = montar_cnpj(est.cnpj_basico, est.cnpj_ordem, est.cnpj_dv)

        telefone = None
        if est.ddd_1 and est.telefone_1:
            telefone = f"({est.ddd_1}) {est.telefone_1}"
        elif est.telefone_1:
            telefone = est.telefone_1

        telefone_2 = None
        if est.ddd_2 and est.telefone_2:
            telefone_2 = f"({est.ddd_2}) {est.telefone_2}"
        elif est.telefone_2:
            telefone_2 = est.telefone_2

        fax = None
        if est.ddd_fax and est.fax:
            fax = f"({est.ddd_fax}) {est.fax}"
        elif est.fax:
            fax = est.fax

        socios = [
            SocioResumoSchema(
                socio_id=s.socio_id,
                nome_socio=s.nome_socio,
                cnpj_cpf_do_socio=s.cnpj_cpf_do_socio,
                identificador_de_socio=s.identificador_de_socio,
                identificador_de_socio_descricao=IDENTIFICADOR_SOCIO.get(
                    s.identificador_de_socio
                ),
                qualificacao_do_socio=s.qualificacao_do_socio,
                qualificacao_do_socio_descricao=(
                    row.qualificacoes.get(s.qualificacao_do_socio)
                    if s.qualificacao_do_socio
                    else None
                ),
                data_entrada_sociedade=s.data_entrada_sociedade,
                faixa_etaria=s.faixa_etaria,
                faixa_etaria_descricao=FAIXA_ETARIA.get(s.faixa_etaria or ""),
                pais=s.pais,
                representante_legal=s.representante_legal,
                nome_do_representante=s.nome_do_representante,
            )
            for s in row.socios
        ]

        return EmpresaDetalheSchema(
            cnpj=cnpj,
            cnpj_basico=est.cnpj_basico,
            cnpj_ordem=est.cnpj_ordem,
            cnpj_dv=est.cnpj_dv,
            razao_social=emp.razao_social,
            nome_fantasia=est.nome_fantasia,
            situacao_cadastral=est.situacao_cadastral,
            situacao_cadastral_descricao=SITUACAO_CADASTRAL.get(est.situacao_cadastral or ""),
            data_situacao_cadastral=est.data_situacao_cadastral,
            data_abertura=est.data_inicio_atividade,
            natureza_juridica=CodigoDescricao(
                codigo=emp.natureza_juridica,
                descricao=row.natureza_descricao,
            ),
            capital_social=emp.capital_social,
            porte=CodigoDescricao(
                codigo=emp.porte,
                descricao=PORTE_EMPRESA.get(emp.porte or ""),
            ),
            cnae_principal=CodigoDescricao(
                codigo=est.cnae_fiscal_principal,
                descricao=row.cnae_descricao,
            ),
            cnaes_secundarios=[
                CodigoDescricao(codigo=c, descricao=d) for c, d in row.cnaes_secundarios
            ],
            endereco=EnderecoSchema(
                tipo_logradouro=est.tipo_logradouro,
                logradouro=est.logradouro,
                numero=est.numero,
                complemento=est.complemento,
                bairro=est.bairro,
                cep=est.cep,
                municipio=est.municipio,
                municipio_nome=row.municipio_nome,
                uf=est.uf,
                pais=est.pais,
                nome_cidade_exterior=est.nome_cidade_exterior,
            ),
            contato=ContatoSchema(
                telefone=telefone,
                telefone_2=telefone_2,
                fax=fax,
                email=est.correio_eletronico,
            ),
            identificador_matriz_filial=est.identificador_matriz_filial,
            identificador_matriz_filial_descricao=IDENTIFICADOR_MATRIZ_FILIAL.get(
                est.identificador_matriz_filial or 0
            ),
            socios=socios,
        )

    def _to_resumo(
        self,
        est,
        emp,
        municipio_nome: str | None,
        cnae_descricao: str | None,
    ) -> EmpresaResumoSchema:
        return EmpresaResumoSchema(
            cnpj=montar_cnpj(est.cnpj_basico, est.cnpj_ordem, est.cnpj_dv),
            cnpj_basico=est.cnpj_basico,
            razao_social=emp.razao_social,
            nome_fantasia=est.nome_fantasia,
            situacao_cadastral=est.situacao_cadastral,
            situacao_cadastral_descricao=SITUACAO_CADASTRAL.get(est.situacao_cadastral or ""),
            uf=est.uf,
            municipio=est.municipio,
            municipio_nome=municipio_nome,
            cnae_principal=est.cnae_fiscal_principal,
            cnae_principal_descricao=cnae_descricao,
            porte=emp.porte,
            porte_descricao=PORTE_EMPRESA.get(emp.porte or ""),
            capital_social=emp.capital_social,
            data_abertura=est.data_inicio_atividade,
            identificador_matriz_filial=est.identificador_matriz_filial,
        )
