"""Gera o material impresso da dinamica de match entre codigo e grafico.

Oito codigos e oito graficos. Os pares foram escolhidos para que nenhuma carta
possa ser identificada pela variavel: quatro usam `regime_inicial` e quatro usam
`pena_anos`. O que separa uma da outra e sempre um elemento da gramatica.

    1 e 2   a mesma geometria, com e sem `coord_flip()`
    3 e 4   `fill` fora do `aes()` contra `fill` dentro do `aes()`
    5 e 6   o mesmo histograma com 10 e com 40 caixas
    7       outra geometria para a mesma variavel numerica
    8       o mesmo histograma repartido em facetas

Sai em _saida/:

    cartas_codigo.pdf    1 folha, 8 cartas   -> 1 por grupo
    cartas_grafico.pdf   1 folha, 8 cartas   -> 1 por grupo, de preferencia
                                                colorida (em preto e branco
                                                tambem funciona: as cores das
                                                cartas 3 e 4 foram escolhidas
                                                para sobreviver a escala de
                                                cinza)
    folha_match.pdf      1 folha             -> 1 por grupo
    gabarito_match.pdf   2 folhas            -> so do professor

Uso:
    python atividades/gerar_match_plotnine.py
"""

from __future__ import annotations

import subprocess
import sys
import warnings
from pathlib import Path

import pandas as pd
from plotnine import (aes, coord_flip, facet_wrap, geom_bar, geom_density,
                      geom_histogram, ggplot, theme, theme_minimal)

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "_saida" / "alternativas"
FIGURAS = SAIDA / "figuras_match"
FONTES = AQUI.parent / "listas" / "fontes"
BASE = AQUI.parent / "dados" / "tjsp_cjsg_criminal.csv"

# codigo mostrado na carta (quebrado por elemento da gramatica) e a receita
CARTAS = [
    (
        'ggplot(penas)\n  + aes(x="regime_inicial")\n  + geom_bar()',
        lambda d: ggplot(d) + aes(x="regime_inicial") + geom_bar(),
    ),
    (
        'ggplot(penas)\n  + aes(x="regime_inicial")\n  + geom_bar()\n  + coord_flip()',
        lambda d: ggplot(d) + aes(x="regime_inicial") + geom_bar() + coord_flip(),
    ),
    (
        'ggplot(penas)\n  + aes(x="regime_inicial")\n  + geom_bar(fill="#3ACC9F")',
        lambda d: ggplot(d) + aes(x="regime_inicial") + geom_bar(fill="#3ACC9F"),
    ),
    (
        'ggplot(penas)\n  + aes(x="regime_inicial",\n        fill="houve_reincidencia")\n  + geom_bar()',
        lambda d: (ggplot(d)
                   + aes(x="regime_inicial", fill="houve_reincidencia")
                   + geom_bar()),
    ),
    (
        'ggplot(penas)\n  + aes(x="pena_anos")\n  + geom_histogram(bins=10)',
        lambda d: ggplot(d) + aes(x="pena_anos") + geom_histogram(bins=10),
    ),
    (
        'ggplot(penas)\n  + aes(x="pena_anos")\n  + geom_histogram(bins=40)',
        lambda d: ggplot(d) + aes(x="pena_anos") + geom_histogram(bins=40),
    ),
    (
        'ggplot(penas)\n  + aes(x="pena_anos")\n  + geom_density()',
        lambda d: ggplot(d) + aes(x="pena_anos") + geom_density(),
    ),
    (
        'ggplot(penas)\n  + aes(x="pena_anos")\n  + geom_histogram(bins=10)\n  + facet_wrap("regime_inicial")',
        lambda d: (ggplot(d) + aes(x="pena_anos") + geom_histogram(bins=10)
                   + facet_wrap("regime_inicial")),
    ),
]

# letra impressa na carta de grafico de cada codigo. Fixa, e de proposito fora
# de ordem: com a ordem natural o grupo acerta contando, e nao lendo.
LETRAS = {1: "E", 2: "H", 3: "B", 4: "F", 5: "A", 6: "D", 7: "G", 8: "C"}

PISTAS = {
    1: "barras verticais, uma cor só, sem legenda",
    2: "as mesmas barras deitadas: quem virou os eixos foi o `coord_flip()`",
    3: "barras todas verdes e sem legenda: `fill` está fora do `aes()`, então é "
       "decoração, e vale para todas as barras",
    4: "cada barra repartida em duas cores, com legenda: `fill` está dentro do "
       "`aes()`, então virou variável no gráfico",
    5: "histograma com caixas largas, poucas colunas",
    6: "o mesmo histograma esmigalhado em 40 caixas, com buracos entre elas",
    7: "uma curva contínua no lugar das colunas: `geom_density()`",
    8: "três painéis, um por regime: `facet_wrap()` reparte o mesmo gráfico",
}


def preparar() -> pd.DataFrame:
    criminal = pd.read_csv(BASE)
    return (
        criminal
        .dropna(subset=["regime_inicial", "pena_anos"])
        .query("pena_anos <= 30")
    )


def gerar_figuras(penas: pd.DataFrame) -> None:
    FIGURAS.mkdir(parents=True, exist_ok=True)
    for numero, (_, receita) in enumerate(CARTAS, start=1):
        grafico = receita(penas) + theme_minimal() + theme(figure_size=(4.4, 2.9))
        grafico.save(FIGURAS / f"g{numero}.png", dpi=200, verbose=False)
    print(f"  {len(CARTAS)} figuras em _saida/alternativas/figuras_match/")


# ------------------------------------------------------------------- cartas

PREAMBULO = """#import "../../estilo.typ": *
#set page(paper: "a4", margin: (x: 16mm, y: 13mm), footer: rodape)
#set text(font: body-font, size: 9pt, fill: ink)
#set par(leading: 0.62em, spacing: 0.8em)
"""


def esc(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def typ_cartas_codigo() -> str:
    cartas = ",\n".join(
        f'  carta-codigo({n}, "{esc(codigo)}")'
        for n, (codigo, _) in enumerate(CARTAS, start=1)
    )
    return f"""#import "../../estilo.typ": *
#set page(paper: "a4", margin: (x: 10mm, y: 10mm))
#set text(font: body-font, size: 9pt)

#block(width: 100%, height: 100%, grid(
  columns: (1fr, 1fr),
  rows: (1fr,) * 4,
  column-gutter: 4mm,
  row-gutter: 4mm,
{cartas},
))
"""


def typ_cartas_grafico() -> str:
    itens = ",\n".join(
        f'  carta-grafico("{LETRAS[n]}", "/_saida/alternativas/figuras_match/g{n}.png")'
        for n in sorted(LETRAS, key=lambda k: LETRAS[k])
    )
    return f"""#import "../../estilo.typ": *
#set page(paper: "a4", margin: (x: 10mm, y: 10mm))
#set text(font: body-font, size: 9pt)

#block(width: 100%, height: 100%, grid(
  columns: (1fr, 1fr),
  rows: (1fr,) * 4,
  column-gutter: 4mm,
  row-gutter: 4mm,
{itens},
))
"""


def typ_folha() -> str:
    linhas = "\n".join(
        f"  [{n}], [], [],"
        for n in range(1, len(CARTAS) + 1)
    )
    return PREAMBULO + f"""
#folha-titulo(
  "Dinâmica 2 · resposta",
  "Qual código fez qual gráfico?",
  subtitulo: [
    Grupo #box(width: 30mm, line(length: 100%, stroke: 0.6pt + rule-col))
    #h(10pt) Quem escreveu
    #box(width: 60mm, line(length: 100%, stroke: 0.6pt + rule-col))
  ],
)

#v(8pt)
#block(width: 100%, fill: tint, inset: (x: 12pt, y: 11pt))[
  #eyebrow("Antes de começar")
  #v(6pt)
  #text(size: 9.5pt, fill: ink-soft)[
    Todos os oito gráficos saem da mesma tabela, montada assim:
  ]
  #v(7pt)
  #codigo(
"penas = (
    criminal
    .dropna(subset=[\\"regime_inicial\\", \\"pena_anos\\"])
    .query(\\"pena_anos <= 30\\")
)", tamanho: 8.5pt)
  #v(8pt)
  #text(size: 9.5pt, fill: ink-soft)[
    Quatro cartas usam `regime_inicial` e quatro usam `pena_anos`. Ou seja:
    olhar só o nome do eixo resolve metade do problema e empata a outra metade.
    O que decide é o resto da gramática.
  ]
]

#v(12pt)
#text(size: 9pt)[Espalhem as dezesseis cartas na mesa. Para cada código, achem o
gráfico e escrevam *qual foi a pista*: a estética, a geometria, a faceta, um
argumento. Vale escrever pouco, desde que seja a razão de verdade.]
#v(10pt)

#table(
  columns: (0.6fr, 0.7fr, 3fr),
  inset: (x: 8pt, y: 12pt),
  stroke: (paint: rule-col, thickness: 0.5pt),
  fill: (x, y) => if y == 0 {{ tint }} else {{ white }},
  text(size: 7.5pt, weight: "bold")[código],
  text(size: 7.5pt, weight: "bold")[gráfico],
  text(size: 7.5pt, weight: "bold")[qual foi a pista],
{linhas}
)

#v(14pt)
#block(width: 100%, stroke: (paint: brand, thickness: 1pt), inset: 12pt)[
  #eyebrow("Desafio")
  #v(7pt)
  #text(size: 9.5pt, fill: ink-soft)[
    Um dos códigos pinta todas as barras da mesma cor. Outro reparte cada barra
    em duas cores e ganha uma legenda ao lado. A mesma palavra aparece nos dois,
    em lugares diferentes. Escreva aqui qual é a palavra, onde ela está em cada
    caso, e por que isso muda tanto o gráfico.
  ]
  #v(10pt)
  #line(length: 100%, stroke: (paint: rule-col, thickness: 0.6pt))
  #v(13pt)
  #line(length: 100%, stroke: (paint: rule-col, thickness: 0.6pt))
  #v(13pt)
  #line(length: 100%, stroke: (paint: rule-col, thickness: 0.6pt))
]
"""


def typ_gabarito() -> str:
    linhas = "\n".join(
        f"  [{n}], [{LETRAS[n]}], [{PISTAS[n]}],"
        for n in range(1, len(CARTAS) + 1)
    )
    return PREAMBULO + f"""
#folha-titulo(
  "Dinâmica 2 · uso do professor",
  "Gabarito e pontos de discussão",
)

#v(8pt)

#table(
  columns: (0.55fr, 0.6fr, 3fr),
  inset: (x: 8pt, y: 9pt),
  stroke: (paint: rule-col, thickness: 0.5pt),
  fill: (x, y) => if y == 0 {{ tint }} else {{ white }},
  text(size: 7.5pt, weight: "bold")[código],
  text(size: 7.5pt, weight: "bold")[gráfico],
  text(size: 7.5pt, weight: "bold")[a pista],
{linhas}
)

#v(14pt)
#eyebrow("Os três pares que carregam a aula", cor: ink)
#v(9pt)

*3 contra 4, o `fill`.* É o par mais importante da mesa, e o que os grupos mais
erram. Fora do `aes()`, `fill="#E50505"` é uma escolha de tinta: pinta tudo da
mesma cor e não aparece legenda nenhuma. Dentro do `aes()`, `fill="houve_reincidencia"`
é um mapeamento: a cor passa a representar uma variável, cada barra se reparte, e
o gráfico ganha uma legenda porque agora a cor significa alguma coisa. É a
resposta do desafio da folha, e a definição de estética em uma frase.

*5 contra 6, o `bins`.* Mesmos dados, mesma geometria, duas leituras. Com 10
caixas aparece uma massa concentrada nas penas curtas. Com 40, o gráfico fica
cheio de buracos e de picos que são só o tamanho da amostra. Vale perguntar:
qual dos dois está certo? Nenhum, e é por isso que o número de caixas é decisão
de quem analisa, e não um detalhe.

*1 contra 8, a faceta.* A faceta não muda o gráfico, repete o gráfico. O mesmo
histograma, os mesmos eixos, três pedaços da tabela. Quando alguém disser "são
três gráficos", vale corrigir com cuidado: é um gráfico só, com a tabela
repartida.

#pagebreak()

#eyebrow("Como conduzir", cor: ink)
#v(10pt)

#passo(1, "Montar a mesa (2 min)",
  [Cada grupo recebe as duas folhas de cartas e recorta. Dezesseis cartas
   viradas para cima, códigos de um lado, gráficos do outro. Diga que as letras
   estão fora de ordem de propósito.])

#passo(2, "Parear (8 min)",
  [A regra que faz a atividade funcionar: nenhum par vale sem a pista escrita.
   Sem isso o grupo casa por eliminação, acerta os oito e não aprende nada. Ao
   circular, a pergunta é sempre a mesma: "o que no código te fez escolher esse
   gráfico?".])

#passo(3, "Conferir em plenária (4 min)",
  [Não leia o gabarito. Chame um grupo por par, começando pelos fáceis (5 e 6),
   e deixe 3 e 4 por último. Peça a pista, não a resposta. Se dois grupos
   discordarem, melhor ainda: peça que cada um defenda e deixe a mesa decidir.])

#passo(4, "Fechar na gramática (3 min)",
  [Volte ao quadro com os cinco elementos e pergunte, para cada par, qual deles
   estava em jogo: dados, estética, geometria, escala, faceta. A turma acaba de
   usar quatro dos cinco sem escrever uma linha de código.])

#v(12pt)
#block(width: 100%, fill: tint, inset: (x: 12pt, y: 11pt))[
  #eyebrow("Se sobrar tempo")
  #v(6pt)
  #text(size: 9.5pt, fill: ink-soft)[
    Peça que cada grupo escreva no verso da folha o código de um nono gráfico,
    que não está na mesa, e que responda a alguma pergunta sobre a base. Os
    melhores viram exemplo no notebook logo em seguida.
  ]
]
"""


# ------------------------------------------------------------------ compilar


def compilar(nome: str, conteudo: str) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    fonte = SAIDA / f"{nome}.typ"
    fonte.write_text(conteudo, encoding="utf-8")
    subprocess.run(
        ["quarto", "typst", "compile", fonte.name, f"{nome}.pdf",
         "--font-path", str(FONTES), "--root", str(AQUI)],
        cwd=SAIDA, check=True, shell=True,
    )
    fonte.unlink()
    print(f"  _saida/{nome}.pdf")


def main() -> None:
    print("dinâmica de match:")
    gerar_figuras(preparar())
    compilar("cartas_codigo", typ_cartas_codigo())
    compilar("cartas_grafico", typ_cartas_grafico())
    compilar("folha_match", typ_folha())
    compilar("gabarito_match", typ_gabarito())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
