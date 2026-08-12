"""Utilitários de normalização e validação de CNPJ."""

from __future__ import annotations

import re

_CNPJ_ALNUM = re.compile(r"^[0-9A-Z]{12}\d{2}$")
_CNPJ_BASICO = re.compile(r"^[0-9A-Z]{8}$")


def limpar_cnpj(valor: str) -> str:
    """Remove máscara e normaliza para maiúsculas."""
    return re.sub(r"[^0-9A-Za-z]", "", valor).upper()


def validar_cnpj(valor: str) -> bool:
    """Valida CNPJ completo (14 caracteres alfanuméricos)."""
    limpo = limpar_cnpj(valor)
    return bool(_CNPJ_ALNUM.match(limpo))


def validar_cnpj_basico(valor: str) -> bool:
    """Valida os 8 primeiros caracteres do CNPJ."""
    limpo = limpar_cnpj(valor)
    return bool(_CNPJ_BASICO.match(limpo))


def parse_cnpj(valor: str) -> tuple[str, str, str]:
    """
    Separa CNPJ em (basico, ordem, dv).

    Raises:
        ValueError: se o CNPJ for inválido.
    """
    limpo = limpar_cnpj(valor)
    if not validar_cnpj(limpo):
        raise ValueError(f"CNPJ inválido: {valor}")
    return limpo[:8], limpo[8:12], limpo[12:14]


def montar_cnpj(basico: str, ordem: str, dv: str) -> str:
    """Concatena as partes do CNPJ."""
    return f"{basico}{ordem}{dv}"


def formatar_cnpj(valor: str) -> str:
    """Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX (apenas dígitos numéricos)."""
    limpo = limpar_cnpj(valor)
    if len(limpo) != 14:
        return limpo
    if not limpo.isdigit():
        return limpo
    return f"{limpo[:2]}.{limpo[2:5]}.{limpo[5:8]}/{limpo[8:12]}-{limpo[12:14]}"
