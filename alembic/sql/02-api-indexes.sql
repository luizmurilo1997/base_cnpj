-- Índices adicionais para a API de consulta CNPJ
-- Aplicado automaticamente no primeiro docker compose up (initdb)

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
