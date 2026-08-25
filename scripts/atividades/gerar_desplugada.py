"""Gera o material impresso da dinamica desplugada de manipulacao de dados.

Sai em _saida/:

    baralho.pdf              2 folhas, 24 cartas de acordao    -> 1 por grupo
    tiras_e_fichas.pdf       1 folha, 6 tiras e 4 fichas       -> 1 por grupo
    tabuleiro.pdf            1 folha, o encadeamento em branco -> 1 por grupo
    folha_resposta.pdf       2 folhas                          -> 1 por grupo
    gabarito_desplugada.pdf  2 folhas                          -> so do professor

Uso:
    python atividades/gerar_desplugada.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from base_cartas import CARTAS, pena_br, sim_nao

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "_saida" / "alternativas"
FONTES = AQUI.parent / "listas" / "fontes"

TIRAS = [
    '.query("trafico == \'não\'")',
    '.sort_values("pena", ascending=False)',
    ".head(3)",
    '[["id", "comarca", "pena"]]',
    '.groupby("regime")',
    '.agg(n=("id", "size"))',
]

PREAMBULO = """#import "../../estilo.typ": *
#set page(paper: "a4", margin: (x: 16mm, y: 13mm), footer: rodape)
#set text(font: body-font, size: 9pt, fill: ink)
#set par(leading: 0.62em, spacing: 0.8em)
"""


def esc(texto: str) -> str:
    """Escapa uma string para virar literal de texto no typst."""
    return texto.replace("\\", "\\\\").replace('"', '\\"')


# --------------------------------------------------------------- baralho


def typ_baralho() -> str:
    partes = [
        '#import "../../estilo.typ": *',
        '#set page(paper: "a4", margin: (x: 10mm, y: 10mm))',
        "#set text(font: body-font, size: 9pt)",
        "",
    ]
    for inicio in (0, 12):
        cartas = ",\n".join(
            f'  carta-acordao("{i}", "{esc(comarca)}", "{regime}", '
            f'"{pena_br(pena)} anos", "{sim_nao(reinc)}", "{sim_nao(traf)}")'
            for i, comarca, regime, pena, reinc, traf in CARTAS[inicio:inicio + 12]
        )
        partes.append("#pagina-de-cartas((\n" + cartas + ",\n))")
        if inicio == 0:
            partes.append("#pagebreak()")
    return "\n".join(partes) + "\n"


# --------------------------------------------------- tiras e fichas-resumo


def typ_tiras() -> str:
    tiras = ",\n".join(f'  tira("{esc(t)}")' for t in TIRAS)
    corpo = """
#folha-titulo(
  "Dinâmica 1 · recortar",
  "Tiras de operação e fichas-resumo",
  subtitulo: [Recorte as seis tiras e as quatro fichas. Duas tiras não entram no
  encadeamento de hoje: descobrir quais é parte da tarefa.],
)

#v(10pt)
#eyebrow("As seis tiras", cor: ink)
#v(7pt)

#block(width: 100%, height: 96mm, grid(
  columns: (1fr,),
  rows: (1fr,) * 6,
  row-gutter: 4mm,
__TIRAS__,
))

#v(14pt)
#eyebrow("As quatro fichas-resumo", cor: ink)
#v(5pt)
#text(size: 8.5pt, fill: ink-soft)[Cada pilha de cartas vira uma ficha só. É
exatamente isso que `.groupby()` seguido de `.agg()` faz com uma tabela.]
#v(8pt)

#block(width: 100%, height: 92mm, grid(
  columns: (1fr, 1fr),
  rows: (1fr, 1fr),
  column-gutter: 5mm,
  row-gutter: 5mm,
  ..((ficha-resumo(("regime", "quantas cartas", "quantas com reincidência",
                    "proporção", "pena mediana")),) * 4),
))
"""
    return PREAMBULO + corpo.replace("__TIRAS__", tiras)


# --------------------------------------------------------------- tabuleiro


def typ_tabuleiro() -> str:
    return PREAMBULO + """
#folha-titulo(
  "Dinâmica 1 · tabuleiro",
  "O encadeamento",
  subtitulo: [Ponha as tiras nas vagas, na ordem em que devem acontecer. Depois
  execute cada uma delas nas cartas, de cima para baixo, sem pular nenhuma.],
)

#v(8pt)
#block(width: 100%, fill: tint, inset: (x: 12pt, y: 11pt))[
  #eyebrow("A pergunta")
  #v(6pt)
  #text(size: 11pt, fill: ink)[Entre os acórdãos que *não* são de tráfico, quais
  são os três com a maior pena?]
]

#v(20pt)

#grid(
  columns: (14mm, 1fr),
  rows: (12mm, 12mm, 17mm, 17mm, 17mm, 17mm, 12mm),
  row-gutter: 4mm,
  align: left + horizon,

  text(font: mono-font, size: 24pt, fill: brand)[\\(], [],
  [], text(font: mono-font, size: 14pt)[acordaos],
  [], vaga(1),
  [], vaga(2),
  [], vaga(3),
  [], vaga(4),
  text(font: mono-font, size: 24pt, fill: brand)[\\)], [],
)

#v(22pt)
#block(width: 100%, stroke: (paint: brand, thickness: 1pt), inset: 12pt)[
  #eyebrow("Depois que funcionar")
  #v(7pt)
  #text(size: 10pt, fill: ink-soft)[
    Troque duas tiras de lugar: ponha `.head(3)` *antes* de `.sort_values(...)`.
    Devolva todas as cartas ao baralho e execute tudo de novo, do zero. Anote na
    folha de resposta o que mudou, e por quê.
  ]
]
"""


# ----------------------------------------------------------- folha resposta


def typ_resposta() -> str:
    return PREAMBULO + """
#folha-titulo(
  "Dinâmica 1 · resposta",
  "Folha do grupo",
  subtitulo: [
    Grupo #box(width: 30mm, line(length: 100%, stroke: 0.6pt + rule-col))
    #h(10pt) Quem escreveu
    #box(width: 60mm, line(length: 100%, stroke: 0.6pt + rule-col))
  ],
)

#v(10pt)
#eyebrow("Rodada 1 · um verbo de cada vez", cor: ink)
#v(10pt)

#resposta[*a.* Depois de `.query("regime == 'fechado'")`, quantas cartas sobraram na mesa?]

#resposta[*b.* Depois de `.sort_values("pena", ascending=False)`, qual carta ficou em primeiro lugar?]

#resposta(linhas: 2)[*c.* Olhe bem para essa carta. O número faz sentido? O que deve ter acontecido quando a pena foi lida do texto da ementa?]

#resposta(linhas: 2)[*d.* Depois de `.groupby("regime")`, quantas pilhas existem na mesa, e de que tamanho?]

#text(size: 9pt)[*e.* Preencha uma ficha-resumo por pilha e copie os números aqui:]
#v(8pt)

#table(
  columns: (1.3fr, 1fr, 1fr, 1fr, 1fr),
  inset: (x: 7pt, y: 11pt),
  stroke: (paint: rule-col, thickness: 0.5pt),
  fill: (x, y) => if y == 0 { tint } else { white },
  text(size: 7.5pt, weight: "bold")[regime],
  text(size: 7.5pt, weight: "bold")[n],
  text(size: 7.5pt, weight: "bold")[reincidentes],
  text(size: 7.5pt, weight: "bold")[proporção],
  text(size: 7.5pt, weight: "bold")[pena mediana],
  [aberto], [], [], [], [],
  [semiaberto], [], [], [], [],
  [fechado], [], [], [], [],
)

#v(16pt)
#resposta(linhas: 2)[*f.* A proporção de reincidência cresce, cai ou fica igual conforme o regime fica mais severo? O que isso tem a ver com o que a lei manda o juiz olhar?]

#pagebreak()

#eyebrow("Rodada 2 · o encadeamento", cor: ink)
#v(10pt)

#text(size: 9pt)[*a.* Copie as tiras que você usou, na ordem em que ficaram no tabuleiro:]
#v(8pt)
#quadro(42mm)

#resposta(linhas: 2)[*b.* Quais foram as duas tiras que sobraram, e por que elas não servem para esta pergunta?]

#resposta(linhas: 2)[*c.* Quais são os três acórdãos da resposta? Algum deles é estranho?]

#resposta(linhas: 2)[*d.* Agora com `.head(3)` antes de `.sort_values(...)`: quais acórdãos saem?]

#resposta(linhas: 4)[*e.* As duas versões usam exatamente as mesmas operações. Por que elas dão respostas diferentes?]

#v(6pt)
#block(width: 100%, fill: tint, inset: (x: 12pt, y: 11pt))[
  #eyebrow("Para quem terminou antes")
  #v(6pt)
  #text(size: 9.5pt, fill: ink-soft)[
    Escreva no verso a sequência de operações que responde a esta outra pergunta:
    _qual é a comarca com mais acórdãos nesta amostra, e qual a pena mediana dela?_
    Não precisa executar nas cartas, basta a ordem das operações.
  ]
]
"""


# ------------------------------------------------------------------ gabarito


def typ_gabarito() -> str:
    return PREAMBULO + """
#folha-titulo(
  "Dinâmica 1 · uso do professor",
  "Gabarito e pontos de discussão",
)

#v(8pt)
#eyebrow("Rodada 1", cor: ink)
#v(8pt)

*a.* 10 cartas de regime fechado.

*b.* A carta A10, com pena de 75,3 anos.

*c.* O número está errado. A pena foi lida do texto da ementa pegando o primeiro
número seguido da palavra "anos", e nesse acórdão o primeiro número que aparece
não é a pena. O mesmo acontece na base de verdade, em que a maior pena lida é de
75,3 anos. Vale insistir no ponto: o código fez exatamente o que foi pedido, e o
resultado é lixo. Conferir os extremos de uma variável é parte da análise, não
zelo excessivo.

*d.* Três pilhas: aberto com 6 cartas, semiaberto com 8, fechado com 10.

#v(10pt)

#table(
  columns: (1.2fr, 0.6fr, 1fr, 1fr, 1fr, 1fr),
  inset: (x: 7pt, y: 8pt),
  stroke: (paint: rule-col, thickness: 0.5pt),
  fill: (x, y) => if y == 0 { tint } else { white },
  text(size: 7.5pt, weight: "bold")[regime],
  text(size: 7.5pt, weight: "bold")[n],
  text(size: 7.5pt, weight: "bold")[reincidentes],
  text(size: 7.5pt, weight: "bold")[proporção],
  text(size: 7.5pt, weight: "bold")[pena mediana],
  text(size: 7.5pt, weight: "bold")[pena média],
  [aberto], [6], [1], [0,17], [1,25], [1,28],
  [semiaberto], [8], [3], [0,38], [4,00], [4,04],
  [fechado], [10], [7], [0,70], [8,75], [15,24],
)

#v(12pt)

*f.* Cresce. É o mesmo resultado da base real, e não é descoberta nenhuma:
reincidência é um dos critérios legais de fixação do regime. Serve para conferir
que a leitura das variáveis está coerente.

*A última coluna é de brinde.* No regime fechado, mediana 8,75 e média 15,24.
Uma carta só, a A10, empurra a média em quase sete anos e não mexe na mediana.
É a aula 3 voltando, agora com a carta na mão.

#v(14pt)
#eyebrow("Rodada 2", cor: ink)
#v(8pt)

#codigo(
"(
    acordaos
    .query(\\"trafico == 'não'\\")
    .sort_values(\\"pena\\", ascending=False)
    .head(3)
    [[\\"id\\", \\"comarca\\", \\"pena\\"]]
)"
)

#v(12pt)

*b.* Sobram `.groupby("regime")` e `.agg(n=("id", "size"))`. A pergunta quer
acórdãos, um por linha, e agrupar transformaria as 24 cartas em três fichas.
Agrupar é para pergunta sobre grupo, não sobre caso.

*c.* A10 (São Paulo, 75,3), A04 (São Paulo, 12,0) e A19 (Francisco Morato,
11,5). O dado sujo aparece no topo de novo, e agora atrapalha a resposta final.

*d.* Com `.head(3)` antes, sobram as três primeiras cartas não-tráfico na ordem
do baralho, A02, A04 e A05, e a ordenação devolve A04 (12,0), A02 (1,2) e A05
(0,7).

*e.* Porque `.head(3)` corta a tabela que existe naquele ponto da sequência.
Antes do `.sort_values`, as três primeiras são as três primeiras do baralho, e
não as três maiores penas. As operações são as mesmas, a ordem não é, e o
encadeamento executa de cima para baixo.

*Para quem terminou antes.* `.groupby("comarca")`, depois
`.agg(n=("id", "size"), pena_mediana=("pena", "median"))`, depois
`.reset_index()` e `.sort_values("n", ascending=False)`. Resposta: São Paulo,
com 10 acórdãos e pena mediana de 4,35 anos.

#pagebreak()

#eyebrow("Como conduzir", cor: ink)
#v(10pt)

#passo(1, "Distribuir e reconhecer (3 min)",
  [Cada grupo recebe um baralho, uma folha de tiras, um tabuleiro e uma folha de
   resposta. Antes de qualquer operação: espalhem as 24 cartas na mesa. Quantas
   linhas tem esta tabela? Quantas colunas? Qual o tipo de cada uma? É a aula 2
   em 90 segundos, e serve para todo mundo pegar numa carta.])

#passo(2, "Um verbo de cada vez (8 min)",
  [Você chama a operação em voz alta, todos executam ao mesmo tempo, e só então
   você pergunta o resultado. Filtrar é separar cartas para fora da mesa.
   Ordenar é enfileirar. Agrupar é fazer pilhas. Agregar é a pilha inteira virar
   uma ficha só. Guarde o item c para uma parada de verdade: a carta A10 na mão
   de alguém vale mais que dez avisos sobre qualidade de dado.])

#passo(3, "Montar o encadeamento (9 min)",
  [Agora os grupos trabalham sozinhos. Circule e não entregue a resposta: a
   pergunta útil é "o que a mesa tem depois desta tira?". Quando um grupo põe
   `[["id", "comarca", "pena"]]` no meio, funciona, e vale dizer que funciona.
   Quando põe `.head(3)` antes do `.sort_values`, não corrija: é justamente o
   experimento do passo seguinte.])

#passo(4, "A troca (4 min)",
  [Todos trocam a ordem das duas tiras e rodam de novo. Ninguém foi enganado,
   todo mundo fez o experimento. A pergunta de fechamento é a letra e: mesmas
   operações, respostas diferentes, por quê.])

#passo(5, "Fechar no código (3 min)",
  [Projete o encadeamento do gabarito e peça que apontem, linha por linha, o que
   cada uma foi na mesa. Daqui em diante o notebook não traz nada novo: escreve o
   que eles já fizeram com a mão.])

#v(10pt)
#block(width: 100%, fill: tint, inset: (x: 12pt, y: 11pt))[
  #eyebrow("Se o tempo apertar")
  #v(6pt)
  #text(size: 9.5pt, fill: ink-soft)[
    Corte o passo 3 pela metade: entregue as quatro tiras certas já separadas e
    peça só a ordem. O passo 4 é o que não pode cair, porque é ele que sustenta a
    ideia de sequência.
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
    print("dinâmica desplugada:")
    compilar("baralho", typ_baralho())
    compilar("tiras_e_fichas", typ_tiras())
    compilar("tabuleiro", typ_tabuleiro())
    compilar("folha_resposta", typ_resposta())
    compilar("gabarito_desplugada", typ_gabarito())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
