"""Fixtures e helpers para testes da API."""

from __future__ import annotations

from collections.abc import Generator
from datetime import date
from uuid import uuid5, NAMESPACE_DNS

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.main import create_app
from app.models.empresa import Empresa, Estabelecimento
from app.models.referencia import Cnae, Municipio, NaturezaJuridica, QualificacaoSocio
from app.models.socio import Socio


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestingSession()
    _seed(session)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def _override_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _seed(session: Session) -> None:
    session.add_all(
        [
            Cnae(codigo="6201501", descricao="Desenvolvimento de programas de computador sob encomenda"),
            Cnae(codigo="6202300", descricao="Desenvolvimento e licenciamento de programas de computador customizáveis"),
            Municipio(codigo="7107", descricao="SAO PAULO"),
            Municipio(codigo="6001", descricao="RIO DE JANEIRO"),
            NaturezaJuridica(codigo="2062", descricao="Sociedade Empresária Limitada"),
            QualificacaoSocio(codigo="49", descricao="Sócio-Administrador"),
        ]
    )

    session.add(
        Empresa(
            cnpj_basico="12345678",
            razao_social="EMPRESA TESTE LTDA",
            natureza_juridica="2062",
            qualificacao_responsavel="49",
            capital_social=100000.0,
            porte="03",
        )
    )
    session.add(
        Empresa(
            cnpj_basico="87654321",
            razao_social="OUTRA EMPRESA SA",
            natureza_juridica="2062",
            capital_social=50000.0,
            porte="01",
        )
    )

    session.add(
        Estabelecimento(
            cnpj_basico="12345678",
            cnpj_ordem="0001",
            cnpj_dv="90",
            identificador_matriz_filial=1,
            nome_fantasia="TESTE TECH",
            situacao_cadastral="02",
            data_inicio_atividade=date(2010, 1, 15),
            cnae_fiscal_principal="6201501",
            cnae_fiscal_secundaria="6202300",
            tipo_logradouro="RUA",
            logradouro="DAS FLORES",
            numero="100",
            bairro="CENTRO",
            cep="01001000",
            uf="SP",
            municipio="7107",
            ddd_1="11",
            telefone_1="99999999",
            correio_eletronico="contato@teste.com.br",
        )
    )
    session.add(
        Estabelecimento(
            cnpj_basico="87654321",
            cnpj_ordem="0001",
            cnpj_dv="00",
            identificador_matriz_filial=1,
            nome_fantasia="OUTRA FANTASIA",
            situacao_cadastral="08",
            data_inicio_atividade=date(2015, 5, 20),
            cnae_fiscal_principal="6201501",
            uf="RJ",
            municipio="6001",
        )
    )

    session.add(
        Socio(
            socio_id=uuid5(NAMESPACE_DNS, "socio-1"),
            cnpj_basico="12345678",
            identificador_de_socio="2",
            nome_socio="JOAO DA SILVA",
            cnpj_cpf_do_socio="***123456**",
            qualificacao_do_socio="49",
            data_entrada_sociedade=date(2010, 1, 15),
            faixa_etaria="5",
        )
    )
    session.commit()
