"""
Gera as figuras da Aula 3 (medidas de posicao e de variabilidade).

Todas saem da mesma base do notebook da aula, `dados/tjsp_cjsg_dano_moral.csv`,
para que o numero do slide seja o mesmo numero que o aluno obtem rodando o
codigo. Nenhum valor aqui e digitado a mao.

Uso:
    python graficos_aula03.py
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.ticker import FuncFormatter

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(os.path.dirname(AQUI), "dados", "tjsp_cjsg_dano_moral.csv")
SAIDA = os.path.join(AQUI, "assets", "aula03")

VERMELHO = "#E50505"
TURQUESA = "#3ACC9F"
LARANJA = "#F89D49"
ROXO = "#730D9F"
AMARELO = "#FFCC00"
GRAFITE = "#3F3F3F"
CINZA = "#ABABAB"
CINZA_CLARO = "#DCDCDC"
CINZA_ESCURO = "#5B5B5B"
QUASE_BRANCO = "#F7F7F7"

# A Inter nao esta instalada no Windows, mas os .ttf estao no repositorio (sao
# os mesmos que o site da pesquisa de campo usa). Registrando aqui, a figura sai
# na mesma fonte do corpo do slide, em vez de uma sosia.
FONTES = os.path.join(os.path.dirname(AQUI), "pesquisa_campo", "fonts")


def registrar_inter() -> str:
    """Devolve o nome da familia a usar: Inter se der, Segoe UI se nao der."""
    if not os.path.isdir(FONTES):
        return "Segoe UI"
    familia = None
    for arquivo in sorted(os.listdir(FONTES)):
        if not (arquivo.startswith("Inter-") and arquivo.endswith(".ttf")):
            continue
        caminho = os.path.join(FONTES, arquivo)
        fm.fontManager.addfont(caminho)
        # o arquivo se chama Inter-Regular, mas a familia declarada la dentro e
        # "Inter 18pt"; pedir "Inter" nao encontra nada
        familia = fm.FontProperties(fname=caminho).get_name()
    return familia or "Segoe UI"


FAMILIA = registrar_inter()

plt.rcParams.update({
    "font.family": FAMILIA,
    "font.size": 12.5,
    "axes.edgecolor": CINZA,
    "axes.linewidth": 0.8,
    "axes.labelcolor": CINZA_ESCURO,
    "text.color": "#1A1A1A",
    "xtick.color": CINZA_ESCURO,
    "ytick.color": CINZA_ESCURO,
    "xtick.labelsize": 11.5,
    "ytick.labelsize": 11.5,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})


def reais(v, _=None):
    """Rotulo curto do eixo: 5000 vira '5 mil'."""
    if v >= 1000:
        n = v / 1000
        return f"{n:.0f} mil" if n == int(n) else f"{n:.1f} mil".replace(".", ",")
    return f"{v:.0f}"


def brl(v: float, casas: int = 0) -> str:
    texto = f"{v:,.{casas}f}".replace(",", "@").replace(".", ",").replace("@", ".")
    return f"R$ {texto}"


def limpar_eixo(ax, *, esquerda=False, baixo=True):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_visible(esquerda)
    ax.spines["bottom"].set_visible(baixo)
    ax.tick_params(length=3)


def salvar(fig, nome):
    fig.savefig(os.path.join(SAIDA, nome), dpi=200, bbox_inches="tight",
                pad_inches=0.06)
    plt.close(fig)
    print("  ", nome)


def carregar():
    d = pd.read_csv(BASE)
    v = d["valor_indenizacao"].dropna().sort_values().reset_index(drop=True)
    return d, v


def histograma(ax, v, *, cor=CINZA_CLARO):
    """A distribuicao inteira, fundo comum de varias figuras."""
    ax.hist(v, bins=np.arange(0, 92500, 2500), color=cor, edgecolor="white",
            linewidth=0.6)
    ax.xaxis.set_major_formatter(FuncFormatter(reais))
    ax.set_xlim(-1500, 92500)
    limpar_eixo(ax)
    ax.set_yticks([])
    return ax


def marcar(ax, x, cor, *, largura=2.2):
    ax.axvline(x, color=cor, linewidth=largura, zorder=5)


def anotar(ax, x, y, rotulo, cor, *, x_texto, ha="left", peso="bold", tamanho=13):
    """Rotulo fora da mancha do grafico, ligado ao ponto por uma perna fina.

    Com media, mediana e quartis todos entre R$ 5 mil e R$ 10 mil, rotulo colado
    na linha vira sopa. O texto vai para a area vazia da cauda, e a perna de
    ligacao diz de quem ele e.
    """
    ax.annotate(rotulo, xy=(x, y), xytext=(x_texto, y), ha=ha, va="center",
                fontsize=tamanho, fontweight=peso, color=cor, zorder=6,
                arrowprops=dict(arrowstyle="-", color=cor, linewidth=0.8,
                                alpha=0.5, shrinkA=0, shrinkB=2))


def fig_media(v):
    fig, ax = plt.subplots(figsize=(13.4, 2.05))
    histograma(ax, v)
    topo = ax.get_ylim()[1]
    marcar(ax, v.mean(), VERMELHO)
    anotar(ax, v.mean(), topo * 0.88, f"média  {brl(v.mean())}", VERMELHO,
           x_texto=30000)
    ax.set_xlabel("valor da indenização arbitrada, em reais")
    salvar(fig, "media.png")


def fig_mediana(v):
    fig, ax = plt.subplots(figsize=(13.4, 2.05))
    histograma(ax, v)
    topo = ax.get_ylim()[1]
    marcar(ax, v.median(), TURQUESA)
    marcar(ax, v.mean(), CINZA, largura=1.8)
    anotar(ax, v.median(), topo * 0.88, f"mediana  {brl(v.median())}", TURQUESA,
           x_texto=30000)
    anotar(ax, v.mean(), topo * 0.58, f"média  {brl(v.mean())}", CINZA_ESCURO,
           x_texto=30000, peso="normal", tamanho=11)
    ax.set_xlabel("valor da indenização arbitrada, em reais")
    salvar(fig, "mediana.png")


def fig_moda(v):
    contagem = v.value_counts().head(8).sort_values()
    fig, ax = plt.subplots(figsize=(5.35, 2.95))
    cores = [ROXO if i == len(contagem) - 1 else CINZA_CLARO
             for i in range(len(contagem))]
    ax.barh([brl(x) for x in contagem.index], contagem.values, color=cores,
            height=0.72)
    for y, n in enumerate(contagem.values):
        ax.text(n + 1.5, y, str(n), va="center", fontsize=10, color=CINZA_ESCURO)
    limpar_eixo(ax, baixo=False)
    ax.set_xticks([])
    ax.set_xlim(0, contagem.max() * 1.18)
    ax.set_xlabel("acórdãos com esse valor exato", labelpad=8)
    salvar(fig, "moda.png")


def fig_extremo(v, *, qual):
    """Os seis extremos de um lado. O valor de interesse fica sempre no topo.

    Cuidado com o eixo: `barh` desenha o indice 0 embaixo, entao o destaque e
    sempre o ultimo item da lista, e nao o primeiro.
    """
    if qual == "minimo":
        alvo = v.head(6).sort_values(ascending=False)
        cor, titulo = LARANJA, "os seis menores valores da base"
    else:
        alvo = v.tail(6).sort_values()
        cor, titulo = VERMELHO, "os seis maiores valores da base"
    destaque = len(alvo) - 1

    fig, ax = plt.subplots(figsize=(5.35, 2.95))
    cores = [cor if i == destaque else CINZA_CLARO for i in range(len(alvo))]
    ax.barh(range(len(alvo)), alvo.values, color=cores, height=0.7)
    ax.set_yticks(range(len(alvo)))
    ax.set_yticklabels([brl(x, 2 if x < 1000 else 0) for x in alvo.values])
    # a barra do menor valor e um fio: quem marca o destaque e o rotulo
    rotulos = ax.get_yticklabels()
    rotulos[destaque].set_color(cor)
    rotulos[destaque].set_fontweight("bold")
    limpar_eixo(ax, baixo=False)
    ax.set_xticks([])
    ax.set_xlim(0, alvo.max() * 1.1)
    ax.set_xlabel(titulo, labelpad=8)
    salvar(fig, f"{qual}.png")


def fig_quartis(d):
    """Os tres cortes no tamanho da ementa, com as quatro partes marcadas.

    Duas escolhas deliberadas: nao ha boxplot, porque a turma so vai ver esse
    grafico mais para a frente, e a coluna nao e a do valor da indenizacao,
    porque nela 33% dos acordaos valem exatamente R$ 5.000 e o Q1 cai em cima
    da mediana. Aqui os tres cortes ficam visivelmente separados.
    """
    n = d["n_palavras_ementa"].dropna()
    q1, q2, q3 = n.quantile(.25), n.median(), n.quantile(.75)
    limite = int(n.max()) + 20

    fig, (ax, eixo_regua) = plt.subplots(
        2, 1, figsize=(13.4, 2.45), sharex=True,
        gridspec_kw={"height_ratios": [3.1, 1], "hspace": 0.12},
    )

    ax.hist(n, bins=np.arange(0, limite + 25, 25), color=CINZA_CLARO,
            edgecolor="white", linewidth=0.6)
    limpar_eixo(ax, baixo=False)
    ax.set_yticks([])
    ax.set_xlim(0, limite)
    topo = ax.get_ylim()[1]
    # rotulos empilhados na area vazia da cauda, com perna de ligacao, como
    # nas outras figuras do deck: os tres cortes sao proximos demais para
    # caberem lado a lado
    cortes = ((q1, f"Q1  {q1:.2f}".replace(".", ","), GRAFITE, 0.92),
              (q2, f"mediana  {q2:.1f}".replace(".", ","), VERMELHO, 0.66),
              (q3, f"Q3  {q3:.0f}", GRAFITE, 0.40))
    for x, nome, cor, altura in cortes:
        ax.axvline(x, color=cor, linewidth=2.2, zorder=5)
        anotar(ax, x, topo * altura, nome, cor, x_texto=330, tamanho=13)

    # a regua embaixo: quatro faixas com o mesmo numero de acordaos
    faixas = [(0, q1), (q1, q2), (q2, q3), (q3, limite)]
    tons = ["#EDEDED", "#DCDCDC", "#CBCBCB", "#BABABA"]
    for (esq, dir_), tom in zip(faixas, tons):
        eixo_regua.barh([0], [dir_ - esq], left=[esq], height=0.5, color=tom)
        eixo_regua.text((esq + dir_) / 2, 0, "25%", ha="center", va="center",
                        fontsize=12, fontweight="bold", color=GRAFITE)
    eixo_regua.set_ylim(-0.42, 0.42)
    eixo_regua.set_yticks([])
    eixo_regua.set_xlim(0, limite)
    limpar_eixo(eixo_regua)
    eixo_regua.set_xlabel("tamanho da ementa, em palavras · cada faixa tem o "
                          "mesmo número de acórdãos")
    salvar(fig, "quartis.png")


def fig_proporcao(d):
    """Duas proporcoes: uma de coluna binaria, outra de coluna categorica."""
    total = len(d)
    casos = [
        ("tem_dano_moral é verdadeiro", int(d["tem_dano_moral"].sum()), TURQUESA),
        ('comarca é "São Paulo"', int((d["comarca"] == "São Paulo").sum()), ROXO),
    ]
    fig, ax = plt.subplots(figsize=(13.4, 1.85))
    for i, (rotulo, parte, cor) in enumerate(casos):
        y = len(casos) - 1 - i
        p = parte / total
        ax.barh([y], [p], color=cor, height=0.46)
        ax.barh([y], [1 - p], left=[p], color=CINZA_CLARO, height=0.46)
        ax.text(0.012, y, f"{parte} / {total}  =  {p:.3f}".replace(".", ","),
                ha="left", va="center", fontsize=13, fontweight="bold",
                color="#FFFFFF")
        ax.text(1.0, y + 0.42, rotulo, ha="right", va="center", fontsize=11.5,
                color=CINZA_ESCURO)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.45, 1.62)
    ax.set_yticks([])
    ax.set_xticks([0, .25, .5, .75, 1])
    ax.set_xticklabels(["0", "0,25", "0,50", "0,75", "1"])
    limpar_eixo(ax)
    ax.set_xlabel(f"fração dos {total} acórdãos")
    salvar(fig, "proporcao.png")


def fig_desvio(v):
    m, s = v.mean(), v.std()
    fig, ax = plt.subplots(figsize=(13.4, 2.05))
    histograma(ax, v)
    topo = ax.get_ylim()[1]
    ax.axvspan(m - s, m + s, color=LARANJA, alpha=0.16, zorder=1)
    for x in (m - s, m + s):
        ax.axvline(x, color=LARANJA, linewidth=1.6, linestyle=(0, (4, 3)), zorder=4)
    marcar(ax, m, VERMELHO)
    anotar(ax, m, topo * 0.88, f"média  {brl(m)}", VERMELHO, x_texto=30000)
    anotar(ax, m + s, topo * 0.58,
           f"um desvio padrão para cada lado: {brl(s)}", LARANJA,
           x_texto=30000, peso="normal", tamanho=11)
    anotar(ax, m - s, topo * 0.30,
           f"do lado de baixo isso daria menos {brl(abs(m - s))}, que não existe",
           CINZA_ESCURO, x_texto=30000, peso="normal", tamanho=10.5)
    ax.set_xlabel("faixa de um desvio padrão em volta da média, em reais")
    salvar(fig, "desvio.png")


def fig_amplitude_iqr(v):
    q1, q3 = v.quantile(.25), v.quantile(.75)
    fig, ax = plt.subplots(figsize=(13.4, 1.95))
    ax.barh([1], [v.max() - v.min()], left=[v.min()], color=CINZA_CLARO, height=0.4)
    ax.barh([0], [q3 - q1], left=[q1], color=AMARELO, height=0.4)
    ax.set_yticks([1, 0])
    ax.set_yticklabels([f"amplitude\n{brl(v.max() - v.min(), 2)}",
                        f"intervalo interquartil\n{brl(q3 - q1)}"],
                       fontsize=10.5)
    ax.xaxis.set_major_formatter(FuncFormatter(reais))
    ax.set_xlim(-2500, 92500)
    ax.set_ylim(-0.62, 1.85)
    limpar_eixo(ax)
    ax.set_xlabel("valor da indenização arbitrada, em reais")
    ax.text(0, 1.60, "dois acórdãos, o mais barato e o mais caro, definem esta "
            "largura inteira", fontsize=10, color=CINZA_ESCURO, va="center")
    ax.annotate("a metade central dos 303 cabe aqui", xy=(q3, 0),
                xytext=(21000, -0.42), ha="left", va="center", fontsize=10,
                color=CINZA_ESCURO,
                arrowprops=dict(arrowstyle="->", color=CINZA, linewidth=0.9))
    salvar(fig, "amplitude_iqr.png")


def fig_resumo(v):
    fig, ax = plt.subplots(figsize=(13.4, 2.15))
    histograma(ax, v)
    topo = ax.get_ylim()[1]
    marcos = [
        (v.min(), f"mínimo  {brl(v.min(), 2)}", LARANJA, 0.94),
        (v.quantile(.25), f"Q1 e mediana  {brl(v.median())}", TURQUESA, 0.71),
        (v.mean(), f"média  {brl(v.mean())}", VERMELHO, 0.48),
        (v.quantile(.75), f"Q3  {brl(v.quantile(.75))}", ROXO, 0.25),
    ]
    for x, nome, cor, alt in marcos:
        marcar(ax, x, cor, largura=2.0)
        anotar(ax, x, topo * alt, nome, cor, x_texto=33000, tamanho=11)
    marcar(ax, v.max(), GRAFITE, largura=2.0)
    anotar(ax, v.max(), topo * 0.94, f"máximo  {brl(v.max())}", GRAFITE,
           x_texto=87000, ha="right", tamanho=11)
    ax.set_xlabel("valor da indenização arbitrada, em reais · 303 acórdãos")
    salvar(fig, "resumo.png")


def main():
    os.makedirs(SAIDA, exist_ok=True)
    d, v = carregar()
    print(f"base: {len(d)} acórdãos, {len(v)} com valor de indenização")
    fig_media(v)
    fig_mediana(v)
    fig_moda(v)
    fig_extremo(v, qual="minimo")
    fig_extremo(v, qual="maximo")
    fig_quartis(d)
    fig_proporcao(d)
    fig_desvio(v)
    fig_amplitude_iqr(v)
    fig_resumo(v)


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    main()
