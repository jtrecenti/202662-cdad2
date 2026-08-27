"""Gera as figuras da Aula 6 (graficos de duas variaveis).

Todas saem da mesma base e da mesma tabela `penas` do notebook da aula, para que
o grafico do slide seja identicamente o grafico que o aluno obtem rodando o
codigo. Nenhuma figura e desenhada a mao.

Uso:
    python graficos_aula06.py
"""

from __future__ import annotations

import os
import warnings

import matplotlib

matplotlib.use("Agg")

import pandas as pd
from plotnine import (aes, coord_flip, geom_bar, geom_boxplot, geom_col,
                      geom_line,
                      geom_histogram, scale_x_datetime,
                      geom_point, geom_smooth, ggplot, labs, theme,
                      theme_minimal)

warnings.filterwarnings("ignore")

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(AQUI, "..", "dados", "tjsp_cjsg_criminal.csv")
SAIDA = os.path.join(AQUI, "assets", "aula06")


def preparar() -> pd.DataFrame:
    criminal = pd.read_csv(BASE)
    criminal["regime"] = pd.Categorical(
        criminal["regime_inicial"],
        categories=["aberto", "semiaberto", "fechado"],
        ordered=True,
    )
    return (
        criminal
        .dropna(subset=["regime", "pena_anos"])
        .query("pena_anos <= 30")
    )


def figuras(penas: pd.DataFrame) -> dict:
    resumo_comarca = (
        penas
        .groupby("comarca", as_index=False)
        .agg(pena_mediana=("pena_anos", "median"), n=("processo", "size"))
        .query("n >= 5")
    )

    # A gincana parou antes das rodadas 3 e 6, e e de la que a aula 6 recomeca.
    # Estas tres figuras existem so para retomar aquilo: o que a turma nao viu
    # nao pode aparecer pela primeira vez dentro do projeto que vale nota.
    resumo_regime = (
        penas
        .groupby("regime", as_index=False)
        .agg(prop_reincidencia=("houve_reincidencia", "mean"))
    )

    # ---- o catalogo de exemplos, um por tipo de grafico -------------------
    # frequencia relativa de uma categorica: o pandas faz a divisao e o
    # plotnine so desenha. Sem lambda, que a turma nao viu.
    freq = penas.groupby("regime", as_index=False, observed=True).agg(
        n=("processo", "size"))
    freq["prop"] = freq["n"] / freq["n"].sum()

    # serie temporal: a base criminal tem quatro dias de julgamento, e nao da
    # serie nenhuma. Esta e a base de saude da aula 2, por mes de ajuizamento.
    saude = pd.read_csv(os.path.join(AQUI, "..", "dados",
                                     "tjsp_datajud_saude.csv"))
    saude["mes"] = (pd.to_datetime(saude["data_ajuizamento"], errors="coerce")
                    .dt.to_period("M").dt.to_timestamp())
    por_mes = saude.groupby("mes", as_index=False).agg(
        n=("numero_processo", "size"))

    return {
        # o catalogo
        "cat_freq": (
            ggplot(penas, aes(x="regime"))
            + geom_bar()
            + labs(x="Regime inicial", y="Acórdãos")),
        "cat_prop": (
            ggplot(freq, aes(x="regime", y="prop"))
            + geom_col()
            + labs(x="Regime inicial", y="Proporção")),
        "num_hist": (
            ggplot(penas, aes(x="pena_anos"))
            + geom_histogram(bins=20)
            + labs(x="Pena (anos)", y="Acórdãos")),
        "serie": (
            ggplot(por_mes, aes(x="mes", y="n"))
            + geom_line()
            + geom_point(size=1.2)
            # sem isto o eixo x escreve a data inteira em cada ponto e os
            # rotulos se empilham uns sobre os outros
            + scale_x_datetime(date_breaks="1 year", date_labels="%Y")
            + labs(x="Mês de ajuizamento", y="Processos")),
        # a retomada da gincana
        "retomada_col": (
            ggplot(resumo_regime,
                   aes(x="regime", y="prop_reincidencia"))
            + geom_col(fill="#E50505")
            + labs(x="Regime inicial", y="Proporção com reincidência")),
        "retomada_bar": (
            ggplot(penas, aes(x="regime"))
            + geom_bar(fill="#9A9A9A")
            + labs(x="Regime inicial", y="Acórdãos")),
        # uma numerica sozinha: a rodada bonus nao foi feita, e o boxplot da
        # aula de hoje pressupoe justamente esta intuicao de distribuicao
        "histograma": (
            ggplot(penas, aes(x="pena_anos"))
            + geom_histogram(bins=20, fill="#9A9A9A", color="white")
            + labs(x="Pena (anos)", y="Acórdãos")),
        # duas numericas
        "pontos": (
            ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos"))
            + geom_point(alpha=0.4)
            + labs(x="Palavras na ementa", y="Pena (anos)")),
        "pontos_smooth": (
            ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos"))
            + geom_point(alpha=0.4)
            + geom_smooth(method="lm", color="#E50505")
            + labs(x="Palavras na ementa", y="Pena (anos)")),
        "pontos_cor": (
            ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos",
                              color="regime"))
            + geom_point(alpha=0.6)
            + geom_smooth(method="lm", se=False)
            + labs(x="Palavras na ementa", y="Pena (anos)",
                   color="Regime inicial")),
        # numerica x categorica
        "boxplot": (
            ggplot(penas, aes(x="regime", y="pena_anos"))
            + geom_boxplot()
            + coord_flip()
            + labs(x="Regime inicial", y="Pena (anos)")),
        # duas categoricas: os tres position
        "stack": (
            ggplot(penas, aes(x="regime", fill="houve_reincidencia"))
            + geom_bar()
            + labs(x="Regime inicial", y="Acórdãos", fill="Reincidência")),
        "fill": (
            ggplot(penas, aes(x="regime", fill="houve_reincidencia"))
            + geom_bar(position="fill")
            + labs(x="Regime inicial", y="Proporção", fill="Reincidência")),
        "dodge": (
            ggplot(penas, aes(x="regime", fill="houve_reincidencia"))
            + geom_bar(position="dodge")
            + labs(x="Regime inicial", y="Acórdãos", fill="Reincidência")),
        # tabela preparada antes do grafico
        "reorder": (
            ggplot(resumo_comarca,
                   aes(x="reorder(comarca, pena_mediana)", y="pena_mediana"))
            + geom_col(fill="#E50505")
            + coord_flip()
            + labs(x="Comarca", y="Pena mediana (anos)")),
    }


TAMANHO = {
    "cat_freq": (3.4, 2.6),
    "cat_prop": (3.4, 2.6),
    "num_hist": (3.4, 2.6),
    "serie": (3.4, 2.6),
    "retomada_col": (4.5, 2.9),
    "retomada_bar": (4.5, 2.9),
    "histograma": (4.8, 2.9),
    "pontos": (4.6, 3.0),
    "pontos_smooth": (4.6, 3.0),
    "pontos_cor": (5.6, 3.0),
    "boxplot": (5.0, 3.4),
    "stack": (3.5, 3.0),
    "fill": (3.5, 3.0),
    "dodge": (3.5, 3.0),
    "reorder": (5.2, 3.4),
}


# nos tres position a legenda vai para baixo: no slide eles ficam lado a lado em
# colunas estreitas, e a legenda a direita esmaga o eixo x ate os rotulos das
# categorias se encostarem.
LEGENDA_EMBAIXO = {"stack", "fill", "dodge"}


def main() -> None:
    os.makedirs(SAIDA, exist_ok=True)
    penas = preparar()
    for nome, g in figuras(penas).items():
        estilo = {"figure_size": TAMANHO[nome]}
        if nome in LEGENDA_EMBAIXO:
            estilo["legend_position"] = "bottom"
        (g + theme_minimal() + theme(**estilo)).save(
            os.path.join(SAIDA, f"{nome}.png"), dpi=200, verbose=False)
        print(f"  assets/aula06/{nome}.png")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()
