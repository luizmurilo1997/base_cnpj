"""Índices de performance para a API de consulta.

Revision ID: 001_api_indexes
Revises:
Create Date: 2026-07-10
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "001_api_indexes"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_empresas_razao_social
            ON empresas (razao_social text_pattern_ops);
        CREATE INDEX IF NOT EXISTS idx_empresas_natureza
            ON empresas (natureza_juridica);
        CREATE INDEX IF NOT EXISTS idx_empresas_porte
            ON empresas (porte);
        CREATE INDEX IF NOT EXISTS idx_empresas_capital
            ON empresas (capital_social);
        CREATE INDEX IF NOT EXISTS idx_estabelecimentos_nome_fantasia
            ON estabelecimentos (nome_fantasia text_pattern_ops);
        CREATE INDEX IF NOT EXISTS idx_estabelecimentos_uf_situacao
            ON estabelecimentos (uf, situacao_cadastral);
        CREATE INDEX IF NOT EXISTS idx_estabelecimentos_uf_cnae
            ON estabelecimentos (uf, cnae_fiscal_principal);
        CREATE INDEX IF NOT EXISTS idx_estabelecimentos_municipio_situacao
            ON estabelecimentos (municipio, situacao_cadastral);
        CREATE INDEX IF NOT EXISTS idx_socios_nome
            ON socios (nome_socio text_pattern_ops);
        CREATE INDEX IF NOT EXISTS idx_socios_cpf
            ON socios (cnpj_cpf_do_socio);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS idx_socios_cpf;
        DROP INDEX IF EXISTS idx_socios_nome;
        DROP INDEX IF EXISTS idx_estabelecimentos_municipio_situacao;
        DROP INDEX IF EXISTS idx_estabelecimentos_uf_cnae;
        DROP INDEX IF EXISTS idx_estabelecimentos_uf_situacao;
        DROP INDEX IF EXISTS idx_estabelecimentos_nome_fantasia;
        DROP INDEX IF EXISTS idx_empresas_capital;
        DROP INDEX IF EXISTS idx_empresas_porte;
        DROP INDEX IF EXISTS idx_empresas_natureza;
        DROP INDEX IF EXISTS idx_empresas_razao_social;
        """
    )
