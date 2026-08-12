"""Testes unitários dos utilitários de CNPJ."""

from __future__ import annotations

import pytest

from app.utils.cnpj import formatar_cnpj, limpar_cnpj, parse_cnpj, validar_cnpj


def test_limpar_e_validar() -> None:
    assert limpar_cnpj("12.345.678/0001-90") == "12345678000190"
    assert validar_cnpj("12345678000190")
    assert not validar_cnpj("123")


def test_parse_cnpj() -> None:
    assert parse_cnpj("12345678000190") == ("12345678", "0001", "90")


def test_parse_cnpj_invalido() -> None:
    with pytest.raises(ValueError):
        parse_cnpj("abc")


def test_formatar_cnpj() -> None:
    assert formatar_cnpj("12345678000190") == "12.345.678/0001-90"
