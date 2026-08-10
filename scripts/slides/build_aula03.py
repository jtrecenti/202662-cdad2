"""
Monta os slides da Aula 3: filtrar e resumir.

Deck curto de proposito. A aula tem pouco tempo: boa parte dela e o notebook
(notebooks/aula03_*.ipynb) e o lancamento do Projeto 1.

Uso:
    python build_aula03.py
"""

from __future__ import annotations

import os

from pptx.enum.text import PP_ALIGN
from pptx.util import Inches

from insper import (
    AMARELO, BRANCO, CINZA, CINZA_CLARO, CINZA_ESCURO, DISPLAY, FAIXA, LARANJA,
    MARGEM, PRETO, QUASE_BRANCO, ROXO, TURQUESA, VERMELHO, caixa, celula,
    deck_limpo, escrever, gravar, layouts, lista_com_barras, slide_capa,
    slide_com_titulo, slide_secao, tabela_sem_estilo, texto_livre,
)

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "aula03.pptx")

EYEBROW = "Ciência de Dados Aplicada ao Direito II  ·  Aula 3  ·  Filtrar e resumir"
TITULO_DECK = "Aula 3: filtrar e resumir"

COR_NUMERICA = TURQUESA
COR_CATEGORICA = ROXO


def s01_capa(prs, lays):
    return slide_capa(
        prs, lays,
        subtitulo="Aula 3: filtrar e resumir",
        subtema="Medidas de posição e de dispersão",
    )


def s02_secao(prs, lays):
    return slide_secao(prs, lays, "Resumir uma coluna em um número")


def s03_posicao(prs, lays):
    slide = slide_com_titulo(prs, lays, "Posição: onde fica o centro", EYEBROW)

    tb = texto_livre(slide, MARGEM, Inches(2.02), FAIXA, Inches(0.32))
    escrever(tb.text_frame, [
        {"texto": "Indenizações por dano moral arbitradas pelo TJSP, em 303 "
                  "acórdãos com valor na ementa.",
         "tamanho": 14, "cor": CINZA_ESCURO, "depois": 0},
    ])

    numeros = [
        ("média", "R$ 7.935", LARANJA, "somar tudo e dividir pelo número de casos"),
        ("mediana", "R$ 5.000", TURQUESA, "o valor do meio, com metade abaixo e "
                                          "metade acima"),
        ("maior valor", "R$ 90.000", CINZA, "um único acórdão"),
    ]
    largura = Inches(3.62)
    vao = Inches(0.32)
    y = Inches(2.52)
    altura = Inches(1.72)
    for i, (rotulo, valor, cor, detalhe) in enumerate(numeros):
        x = MARGEM + i * (largura + vao)
        caixa(slide, x, y, largura, altura, preenchimento=QUASE_BRANCO)
        caixa(slide, x, y, largura, Inches(0.09), preenchimento=cor)
        tb = texto_livre(slide, x + Inches(0.26), y + Inches(0.30),
                         largura - Inches(0.52), altura - Inches(0.45))
        escrever(tb.text_frame, [
            {"texto": rotulo, "tamanho": 13, "cor": CINZA_ESCURO, "depois": 2},
            {"texto": valor, "fonte": DISPLAY, "tamanho": 28, "bold": True,
             "depois": 6},
            {"texto": detalhe, "tamanho": 12, "cor": CINZA_ESCURO,
             "entrelinhas": 1.1, "depois": 0},
        ])

    caixa(slide, MARGEM, Inches(4.55), FAIXA, Inches(1.05),
          preenchimento=QUASE_BRANCO)
    caixa(slide, MARGEM, Inches(4.55), Inches(0.09), Inches(1.05),
          preenchimento=VERMELHO)
    tb = texto_livre(slide, Inches(1.48), Inches(4.72), Inches(10.9), Inches(0.78))
    escrever(tb.text_frame, [
        {"texto": "A média é 59% maior que a mediana",
         "tamanho": 15, "bold": True, "depois": 3},
        {"texto": "Poucos valores muito altos puxam a média para cima, e a "
                  "mediana não se move. Tirar o maior acórdão da base derruba a "
                  "média em R$ 272 e deixa a mediana exatamente onde estava.",
         "tamanho": 13, "cor": CINZA_ESCURO, "entrelinhas": 1.12, "depois": 0},
    ])

    tb = texto_livre(slide, MARGEM, Inches(5.85), FAIXA, Inches(0.80))
    escrever(tb.text_frame, [
        {"texto": "Em valores monetários no Direito, a distribuição quase sempre "
                  "é assimétrica à direita. Por isso o valor típico de uma "
                  "indenização se reporta com a mediana, e a média sozinha, sem "
                  "acompanhamento, tende a enganar quem lê.",
         "tamanho": 13, "cor": CINZA_ESCURO, "entrelinhas": 1.15, "depois": 0},
    ])
    return slide


def s04_dispersao(prs, lays):
    slide = slide_com_titulo(prs, lays, "Dispersão: quanto os casos variam", EYEBROW)

    tb = texto_livre(slide, MARGEM, Inches(2.02), FAIXA, Inches(0.32))
    escrever(tb.text_frame, [
        {"texto": "Duas medidas, e elas respondem a perguntas diferentes.",
         "tamanho": 14, "cor": CINZA_ESCURO, "depois": 0},
    ])

    colunas = [
        ("Intervalo interquartílico", TURQUESA, "IQR = Q3 menos Q1",
         "A largura da metade central dos dados. Vai do valor que deixa 25% "
         "abaixo até o que deixa 75% abaixo.",
         "Acompanha a mediana. Dois casos extremos não mexem nele."),
        ("Desvio padrão", LARANJA, "divide por n menos 1",
         "O afastamento típico em relação à média, na mesma unidade da "
         "variável.",
         "Acompanha a média. É a base de quase toda a inferência que vem depois."),
    ]
    largura = Inches(5.59)
    vao = Inches(0.32)
    y = Inches(2.50)
    altura = Inches(2.55)
    for i, (titulo, cor, formula, oque, quando) in enumerate(colunas):
        x = MARGEM + i * (largura + vao)
        caixa(slide, x, y, largura, altura, preenchimento=QUASE_BRANCO)
        caixa(slide, x, y, largura, Inches(0.09), preenchimento=cor)
        tb = texto_livre(slide, x + Inches(0.28), y + Inches(0.30),
                         largura - Inches(0.56), altura - Inches(0.48))
        escrever(tb.text_frame, [
            {"texto": titulo, "fonte": DISPLAY, "tamanho": 20, "bold": True,
             "depois": 2},
            {"texto": formula, "tamanho": 13, "cor": CINZA_ESCURO, "depois": 10},
            {"texto": oque, "tamanho": 13.5, "entrelinhas": 1.15, "depois": 8},
            {"texto": quando, "tamanho": 12.5, "cor": CINZA_ESCURO,
             "entrelinhas": 1.12, "depois": 0},
        ])

    caixa(slide, MARGEM, Inches(5.32), FAIXA, Inches(1.32),
          preenchimento=QUASE_BRANCO)
    caixa(slide, MARGEM, Inches(5.32), Inches(0.09), Inches(1.32),
          preenchimento=VERMELHO)
    tb = texto_livre(slide, Inches(1.48), Inches(5.50), Inches(10.9), Inches(1.02))
    escrever(tb.text_frame, [
        {"texto": "Nas indenizações: IQR de R$ 5.000 e desvio padrão de R$ 8.388",
         "tamanho": 15, "bold": True, "depois": 3},
        {"texto": "A metade central está espremida entre R$ 5.000 e R$ 10.000, e "
                  "mesmo assim o desvio padrão passa da média. Isso é o que a "
                  "cauda longa faz. O coeficiente de variação, que é o desvio "
                  "padrão dividido pela média, dá 1,06: acima de 1, os valores "
                  "estão espalhados demais para que a média resuma alguma coisa.",
         "tamanho": 13, "cor": CINZA_ESCURO, "entrelinhas": 1.12, "depois": 0},
    ])
    return slide


def s05_tipo_e_estatistica(prs, lays):
    slide = slide_com_titulo(prs, lays, "Que conta cabe em cada tipo", EYEBROW)

    dados = [
        ("numérica contínua", COR_NUMERICA, "média, mediana, quantis",
         "desvio padrão, IQR"),
        ("numérica discreta", COR_NUMERICA, "média, mediana, moda",
         "desvio padrão, IQR"),
        ("categórica ordinal", COR_CATEGORICA, "mediana, moda",
         "amplitude de postos"),
        ("categórica nominal", COR_CATEGORICA, "moda", "nenhuma clássica"),
        ("categórica binária", COR_CATEGORICA, "proporção, que é a média",
         "raiz de p(1 - p)"),
        ("identificador", CINZA, "nenhuma", "nenhuma"),
    ]

    tabela_shape = slide.shapes.add_table(
        len(dados) + 1, 4, MARGEM, Inches(2.10), FAIXA, Inches(2.62)
    )
    tabela = tabela_shape.table
    tabela_sem_estilo(tabela)
    for largura, i in zip(
        (Inches(0.13), Inches(3.37), Inches(4.20), Inches(3.80)), range(4)
    ):
        tabela.columns[i].width = largura
    tabela.rows[0].height = Inches(0.28)
    for r in range(1, len(dados) + 1):
        tabela.rows[r].height = Inches(0.36)

    for c, titulo in enumerate(("", "tipo", "posição", "dispersão")):
        celula(tabela, 0, c, titulo, tamanho=11, bold=True, cor=BRANCO, fundo=PRETO)
    for r, (tipo, cor, posicao, dispersao) in enumerate(dados, start=1):
        zebra = QUASE_BRANCO if r % 2 == 0 else None
        celula(tabela, r, 0, "", fundo=cor)
        celula(tabela, r, 1, tipo, tamanho=12, bold=True, fundo=zebra)
        celula(tabela, r, 2, posicao, tamanho=12, fundo=zebra)
        celula(tabela, r, 3, dispersao, tamanho=12, fundo=zebra, cor=CINZA_ESCURO)

    caixa(slide, MARGEM, Inches(5.05), FAIXA, Inches(1.28),
          preenchimento=QUASE_BRANCO)
    caixa(slide, MARGEM, Inches(5.05), Inches(0.09), Inches(1.28),
          preenchimento=TURQUESA)
    tb = texto_livre(slide, Inches(1.48), Inches(5.24), Inches(10.9), Inches(0.98))
    escrever(tb.text_frame, [
        {"texto": "A média de uma binária é a proporção",
         "tamanho": 15, "bold": True, "depois": 3},
        {"texto": "Guardada como sim ou não, a variável vale 1 e 0. Somar dá "
                  "quantos sim, e dividir pelo total dá a fração de sim. É por "
                  "isso que .mean() numa coluna de verdadeiro e falso devolve a "
                  "proporção, e é a conta que mais vai aparecer daqui em diante.",
         "tamanho": 13, "cor": CINZA_ESCURO, "entrelinhas": 1.12, "depois": 0},
    ])
    return slide


def s06_do_texto_para_a_variavel(prs, lays):
    slide = slide_com_titulo(prs, lays, "Do texto para a variável", EYEBROW)

    tb = texto_livre(slide, MARGEM, Inches(2.02), FAIXA, Inches(0.52))
    escrever(tb.text_frame, [
        {"texto": "A decisão está na ementa: “fixo a indenização em R$ 8.000,00, "
                  "atento à capacidade econômica da ré”. Para virar coluna, "
                  "alguém precisa decidir três coisas.",
         "tamanho": 14, "cor": CINZA_ESCURO, "entrelinhas": 1.15, "depois": 0},
    ])

    decisoes = [
        (VERMELHO, "Onde a informação está",
         "O primeiro valor em reais da ementa nem sempre é o arbitrado: pode ser "
         "o pedido, o da sentença reformada, ou custas."),
        (LARANJA, "Que valores registrar",
         "Número em reais? Faixa? Indicador de houve ou não houve? Cada escolha "
         "responde a uma pergunta diferente."),
        (TURQUESA, "O que fazer quando falta",
         "Um terço das ementas não traz valor nenhum. Descartar essas linhas "
         "muda o universo sobre o qual a resposta vale."),
    ]
    lista_com_barras(slide, decisoes, topo=Inches(2.78), altura=Inches(0.86),
                     passo=Inches(0.94), tamanho_titulo=16, tamanho_detalhe=13)

    caixa(slide, MARGEM, Inches(5.68), FAIXA, Inches(0.96), borda=CINZA_CLARO)
    tb = texto_livre(slide, Inches(1.48), Inches(5.86), Inches(10.9), Inches(0.68))
    escrever(tb.text_frame, [
        {"texto": "Essa instrução tem nome: definição operacional",
         "tamanho": 14, "bold": True, "depois": 3},
        {"texto": "É o texto que faria duas pessoas lerem a mesma ementa e "
                  "registrarem o mesmo valor. Sem ela, a coluna não é "
                  "reproduzível, e o revisor não tem como conferir o que você "
                  "mediu.",
         "tamanho": 12.5, "cor": CINZA_ESCURO, "entrelinhas": 1.12, "depois": 0},
    ])
    return slide


def s07_projeto(prs, lays):
    slide = slide_com_titulo(prs, lays, "Projeto 1, hoje", EYEBROW)

    etapas = [
        (VERMELHO, "Escolher o tema e ler as sentenças",
         "cinco temas, cada um com uma pergunta de pesquisa e 10 sentenças reais "
         "de primeiro grau do TJSP."),
        (LARANJA, "Definir as variáveis",
         "nome, tipo, papel na pergunta e de onde tirar. O tipo declarado decide "
         "o formato do valor: numérica devolve número, categórica devolve uma "
         "das categorias listadas."),
        (AMARELO, "Rodar o modelo e dizer que estatísticas calcularia",
         "o modelo lê cada sentença e preenche as suas colunas. Depois você diz "
         "que contas faria com a tabela, e elas precisam caber nos tipos."),
        (TURQUESA, "Pedir feedback e entregar",
         "até três avaliações pela rubrica, que está visível desde o começo. "
         "Entrega no BlackBoard: a tabela em CSV e a documentação em JSON."),
    ]
    lista_com_barras(slide, etapas, topo=Inches(2.15), altura=Inches(0.98),
                     passo=Inches(1.06), tamanho_titulo=16, tamanho_detalhe=12.5)

    tb = texto_livre(slide, MARGEM, Inches(6.40), FAIXA, Inches(0.28))
    escrever(tb.text_frame, [
        {"texto": "Em grupo, com cópia e cola bloqueados. A rubrica avalia as "
                  "escolhas, e não a quantidade de variáveis.",
         "tamanho": 12, "cor": CINZA_ESCURO, "depois": 0},
    ])
    return slide


def main():
    prs = deck_limpo()
    lays = layouts(prs)

    for construir in (
        s01_capa, s02_secao, s03_posicao, s04_dispersao, s05_tipo_e_estatistica,
        s06_do_texto_para_a_variavel, s07_projeto,
    ):
        construir(prs, lays)

    gravar(prs, SAIDA, titulo=TITULO_DECK)


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    main()
