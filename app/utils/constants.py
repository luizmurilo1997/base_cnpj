"""Constantes e mapas de domínio da Receita Federal."""

from __future__ import annotations

SITUACAO_CADASTRAL: dict[str, str] = {
    "01": "Nula",
    "02": "Ativa",
    "03": "Suspensa",
    "04": "Inapta",
    "05": "Ativa Não Regular",
    "08": "Baixada",
}

PORTE_EMPRESA: dict[str, str] = {
    "00": "Não informado",
    "01": "Microempresa",
    "03": "Empresa de Pequeno Porte",
    "05": "Demais",
}

IDENTIFICADOR_MATRIZ_FILIAL: dict[int, str] = {
    1: "Matriz",
    2: "Filial",
}

IDENTIFICADOR_SOCIO: dict[str, str] = {
    "1": "Pessoa Jurídica",
    "2": "Pessoa Física",
    "3": "Estrangeiro",
}

FAIXA_ETARIA: dict[str, str] = {
    "0": "Não se aplica",
    "1": "0-12 anos",
    "2": "13-20 anos",
    "3": "21-30 anos",
    "4": "31-40 anos",
    "5": "41-50 anos",
    "6": "51-60 anos",
    "7": "61-70 anos",
    "8": "71-80 anos",
    "9": "80+ anos",
}

SITUACAO_ATIVA = "02"
SITUACAO_BAIXADA = "08"
MATRIZ = 1
