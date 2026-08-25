"""Mini-base de 24 acordaos usada na dinamica desplugada da aula 5.

Nao e uma amostra aleatoria da base real. E um recorte desenhado para que:

  * a proporcao de reincidencia cresca com a severidade do regime, como acontece
    na base de verdade (1 em 6, 3 em 8, 7 em 10);
  * a pena mediana cresca junto (1,25 / 4,0 / 8,75 anos);
  * exista um valor implausivel (A10, 75,3 anos, que existe mesmo na base) para
    que o grupo tropece nele ao ordenar e discuta media contra mediana: no
    regime fechado a media da pena e 15,24 e a mediana e 8,75;
  * a ordem do baralho nao seja a ordem de nenhuma coluna, para que agrupar e
    ordenar sejam trabalho de verdade.

As comarcas sao as que mais aparecem na base real de apelacoes criminais do
TJSP. Os identificadores A01 a A24 substituem o numero do processo, que nao
caberia na carta.

Respostas de referencia estao em `GABARITO`, e o script de conferencia no fim do
arquivo recalcula todas elas a partir das cartas.
"""

from __future__ import annotations

import pandas as pd

# id, comarca, regime, pena (anos), reincidencia, trafico
CARTAS = [
    ("A01", "São Paulo",             "fechado",    8.0,  True,  True),
    ("A02", "Campinas",              "aberto",     1.2,  False, False),
    ("A03", "Guarulhos",             "semiaberto", 4.5,  True,  True),
    ("A04", "São Paulo",             "fechado",   12.0,  True,  False),
    ("A05", "Sorocaba",              "aberto",     0.7,  False, False),
    ("A06", "São Paulo",             "semiaberto", 2.7,  False, True),
    ("A07", "Praia Grande",          "fechado",    6.8,  True,  True),
    ("A08", "São Paulo",             "aberto",     1.5,  False, False),
    ("A09", "Araraquara",            "semiaberto", 5.3,  False, False),
    ("A10", "São Paulo",             "fechado",   75.3,  True,  False),
    ("A11", "São Vicente",           "fechado",    5.8,  False, True),
    ("A12", "Campinas",              "semiaberto", 3.5,  True,  False),
    ("A13", "São Paulo",             "aberto",     2.0,  True,  False),
    ("A14", "Garça",                 "fechado",    9.5,  True,  False),
    ("A15", "São Paulo",             "semiaberto", 2.5,  False, True),
    ("A16", "Araras",                "aberto",     1.0,  False, False),
    ("A17", "São Paulo",             "fechado",    7.5,  True,  True),
    ("A18", "São José dos Campos",   "semiaberto", 5.0,  True,  False),
    ("A19", "Francisco Morato",      "fechado",   11.5,  False, False),
    ("A20", "São Paulo",             "aberto",     1.3,  False, False),
    ("A21", "Guarulhos",             "semiaberto", 3.0,  False, False),
    ("A22", "São Paulo",             "fechado",    6.0,  False, True),
    ("A23", "São José do Rio Preto", "fechado",   10.0,  True,  False),
    ("A24", "Santos",                "semiaberto", 5.8,  False, False),
]

COLUNAS = ["id", "comarca", "regime", "pena", "reincidencia", "trafico"]

ORDEM_REGIME = ["aberto", "semiaberto", "fechado"]


def baralho() -> pd.DataFrame:
    """As 24 cartas na ordem em que sao entregues ao grupo."""
    return pd.DataFrame(CARTAS, columns=COLUNAS)


def sim_nao(valor: bool) -> str:
    return "sim" if valor else "não"


def pena_br(valor: float) -> str:
    """8.0 -> '8', 8.5 -> '8,5'."""
    texto = f"{valor:.1f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


# ---------------------------------------------------------------- conferencia

if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")

    df = baralho()
    df["regime"] = pd.Categorical(df["regime"], ORDEM_REGIME, ordered=True)

    print("cartas:", len(df))
    print()
    print("--- rodada 1: um verbo de cada vez ---")
    print("query regime == 'fechado':", int((df["regime"] == "fechado").sum()), "cartas")
    print("sort_values pena desc, 3 primeiras:",
          list(df.sort_values("pena", ascending=False).head(3)["id"]))
    print()
    print(df.groupby("regime", observed=True).agg(
        n=("id", "size"),
        reincidentes=("reincidencia", "sum"),
        prop_reincidencia=("reincidencia", "mean"),
        pena_mediana=("pena", "median"),
        pena_media=("pena", "mean"),
    ).round(2))
    print()
    print("--- rodada 2: encadeamento (não-tráfico, 3 maiores penas) ---")
    certo = (
        df
        .query("trafico == False")
        .sort_values("pena", ascending=False)
        .head(3)
        [["id", "comarca", "pena"]]
    )
    print(certo.to_string(index=False))
    print()
    print("--- rodada 2b: head(3) antes de sort_values ---")
    errado = (
        df
        .query("trafico == False")
        .head(3)
        .sort_values("pena", ascending=False)
        [["id", "comarca", "pena"]]
    )
    print(errado.to_string(index=False))
