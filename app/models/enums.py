"""Enums usados nos modelos de dados."""

from enum import Enum


class TributoAlvo(str, Enum):
    PIS = "PIS"
    COFINS = "COFINS"
    CSLL = "CSLL"
    IRPJ = "IRPJ"
    IRPJ_ADICIONAL = "IRPJ_ADICIONAL"
    ISS = "ISS"


class TipoAjuste(str, Enum):
    ADICAO = "ADICAO"
    REDUCAO = "REDUCAO"


class StatusObrigacao(str, Enum):
    EM_ABERTO = "EM_ABERTO"
    PAGO = "PAGO"
    VENCIDO = "VENCIDO"
    CANCELADO = "CANCELADO"
    NAO_APLICAVEL = "NAO_APLICAVEL"
