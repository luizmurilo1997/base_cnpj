"""Testes de consulta por CNPJ, busca, paginação, filtros e erros."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_consultar_cnpj_sucesso(client: TestClient) -> None:
    with patch("app.services.empresa_service.cache_get", return_value=None), patch(
        "app.services.empresa_service.cache_set"
    ):
        response = client.get("/cnpj/12345678000190")

    assert response.status_code == 200
    body = response.json()
    assert body["cnpj"] == "12345678000190"
    assert body["razao_social"] == "EMPRESA TESTE LTDA"
    assert body["nome_fantasia"] == "TESTE TECH"
    assert body["situacao_cadastral"] == "02"
    assert body["situacao_cadastral_descricao"] == "Ativa"
    assert body["capital_social"] == 100000.0
    assert body["cnae_principal"]["codigo"] == "6201501"
    assert body["endereco"]["uf"] == "SP"
    assert body["contato"]["email"] == "contato@teste.com.br"
    assert len(body["socios"]) == 1
    assert body["socios"][0]["nome_socio"] == "JOAO DA SILVA"


def test_consultar_cnpj_com_mascara(client: TestClient) -> None:
    with patch("app.services.empresa_service.cache_get", return_value=None), patch(
        "app.services.empresa_service.cache_set"
    ):
        response = client.get("/cnpj/12.345.678/0001-90")

    assert response.status_code == 200
    assert response.json()["cnpj"] == "12345678000190"


def test_consultar_cnpj_nao_encontrado(client: TestClient) -> None:
    with patch("app.services.empresa_service.cache_get", return_value=None):
        response = client.get("/cnpj/00000000000000")

    assert response.status_code == 404
    assert "não encontrado" in response.json()["error"]


def test_consultar_cnpj_invalido(client: TestClient) -> None:
    response = client.get("/cnpj/123")
    assert response.status_code == 422
    assert "inválido" in response.json()["error"].lower() or "CNPJ" in response.json()["error"]


def test_buscar_por_nome(client: TestClient) -> None:
    response = client.get("/empresas", params={"nome": "EMPRESA"})
    assert response.status_code == 200
    body = response.json()
    assert body["has_more"] is False
    assert any(item["razao_social"] == "EMPRESA TESTE LTDA" for item in body["items"])


def test_buscar_sem_filtro(client: TestClient) -> None:
    response = client.get("/empresas", params={"page": 1, "size": 1})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["has_more"] is True


def test_paginacao(client: TestClient) -> None:
    response_p1 = client.get(
        "/empresas",
        params={"cnae": "6201501", "page": 1, "size": 1, "apenas_matriz": False},
    )
    assert response_p1.status_code == 200
    assert len(response_p1.json()["items"]) == 1
    assert response_p1.json()["has_more"] is True

    response_p2 = client.get(
        "/empresas",
        params={"cnae": "6201501", "page": 2, "size": 1, "apenas_matriz": False},
    )
    assert response_p2.status_code == 200
    assert len(response_p2.json()["items"]) == 1
    assert response_p2.json()["items"][0]["cnpj"] != response_p1.json()["items"][0]["cnpj"]


def test_filtros_uf_e_situacao(client: TestClient) -> None:
    response = client.get(
        "/empresas",
        params={"uf": "SP", "situacao": "02", "apenas_matriz": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["uf"] == "SP"
    assert body["items"][0]["situacao_cadastral"] == "02"


def test_filtro_capital(client: TestClient) -> None:
    response = client.get(
        "/empresas",
        params={
            "capital_minimo": 80000,
            "capital_maximo": 150000,
            "apenas_matriz": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["cnpj_basico"] == "12345678"


def test_filtro_cnae_endpoint(client: TestClient) -> None:
    response = client.get("/cnae/6201501", params={"page": 1, "size": 10})
    assert response.status_code == 200
    # endpoint defaults to matriz ativa - both seed rows are matriz; RJ is baixada (08)
    assert len(response.json()["items"]) == 1
    assert response.json()["has_more"] is False


def test_empresas_por_estado(client: TestClient) -> None:
    response = client.get("/estados/SP")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["uf"] == "SP"


def test_empresas_por_municipio(client: TestClient) -> None:
    response = client.get("/municipios/7107")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


def test_buscar_socios_por_nome(client: TestClient) -> None:
    response = client.get("/socios", params={"nome": "JOAO"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["nome_socio"] == "JOAO DA SILVA"


def test_buscar_socios_por_cpf_parcial(client: TestClient) -> None:
    response = client.get("/socios", params={"cpf": "123456"})
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


def test_estatisticas(client: TestClient) -> None:
    response = client.get("/estatisticas")
    assert response.status_code == 200
    body = response.json()
    assert body["total_empresas"] == 2
    assert body["empresas_ativas"] == 1
    assert body["empresas_baixadas"] == 1
    assert "SP" in body["empresas_por_uf"]


def test_pagina_invalida(client: TestClient) -> None:
    response = client.get("/empresas", params={"page": 0})
    assert response.status_code == 422
