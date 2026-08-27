"""Monta os slides da Aula 6: graficos de duas variaveis.

O deck e curto de proposito: sao 18 minutos de exposicao, porque a segunda hora
da aula inteira e o Projeto 02. Os slides existem para instalar uma frase, "o
par de tipos escolhe a geometria", e para mostrar as tres formas do `position`
lado a lado, que e a unica ideia da aula que nao cabe numa tabela.

As figuras vem de `graficos_aula06.py`, e saem da mesma tabela do notebook.

Uso:
    python graficos_aula06.py && python build_aula06.py
"""

from __future__ import annotations

import os
import sys

from pptx.util import Inches

from insper import (
    BRANCO, CINZA, CINZA_CLARO, CINZA_ESCURO, FAIXA, LARANJA, MARGEM, PRETO,
    QUASE_BRANCO, ROXO, TURQUESA, VERDE, VERMELHO, caixa, celula, deck_limpo,
    escrever, gravar, imagem_ajustada, layouts, slide_capa, slide_com_titulo,
    tabela_sem_estilo, texto_livre,
)

AQUI = os.path.dirname(os.path.abspath(__file__))
FIGURAS = os.path.join(AQUI, "assets", "aula06")
SAIDA = os.path.join(AQUI, "aula06.pptx")

EYEBROW = ("Ciência de Dados Aplicada ao Direito II  ·  Aula 6  ·  "
           "Gráficos de duas variáveis")

MONO = "Consolas"


# ------------------------------------------------------------------ utilidades

def bloco_codigo(slide, x, y, cx, cy, linhas, *, tamanho=13, barra=None):
    caixa(slide, x, y, cx, cy, preenchimento=QUASE_BRANCO)
    if barra is not None:
        caixa(slide, x, y, Inches(0.07), cy, preenchimento=barra)
    tb = texto_livre(slide, x + Inches(0.26), y + Inches(0.13),
                     cx - Inches(0.42), cy - Inches(0.22))
    escrever(tb.text_frame, linhas, fonte=MONO, tamanho=tamanho, cor=PRETO,
             entrelinhas=1.16, espaco_depois=0)
    return tb


def legenda(slide, x, y, cx, texto, *, cor=CINZA_ESCURO, tamanho=13):
    tb = texto_livre(slide, x, y, cx, Inches(0.3))
    escrever(tb.text_frame, [texto], tamanho=tamanho, cor=cor, espaco_depois=0)
    return tb


def painel(slide, x, y, cx, cy, linhas, *, inverso=False, recuo=0.30):
    """Caixa de destaque, clara ou invertida, com paragrafos ja formatados."""
    fundo = PRETO if inverso else QUASE_BRANCO
    base = BRANCO if inverso else PRETO
    caixa(slide, x, y, cx, cy, preenchimento=fundo)
    tb = texto_livre(slide, x + Inches(recuo), y + Inches(0.16),
                     cx - Inches(recuo * 2), cy - Inches(0.24))
    escrever(tb.text_frame, [{**item, "cor": item.get("cor", base)}
                             for item in linhas])
    return tb


def tabela(slide, x, y, cx, cy, cabecalho, linhas, larguras, alt_linha):
    """Tabela no estilo do deck: cabecalho preto e altura fixa por linha."""
    shape = slide.shapes.add_table(len(linhas) + 1, len(cabecalho), x, y, cx, cy)
    tab = shape.table
    tabela_sem_estilo(tab)
    for larg, i in zip(larguras, range(len(cabecalho))):
        tab.columns[i].width = larg
    tab.rows[0].height = Inches(0.32)
    for r in range(1, len(linhas) + 1):
        tab.rows[r].height = alt_linha
    for c, texto in enumerate(cabecalho):
        celula(tab, 0, c, texto, tamanho=11, bold=True, cor=BRANCO, fundo=PRETO)
    return tab


def etiqueta(slide, x, y, cx, cy, texto, cor, *, tamanho=11.5):
    sh = caixa(slide, x, y, cx, cy, preenchimento=cor)
    escrever(sh.text_frame, [texto], tamanho=tamanho, cor=BRANCO, bold=True,
             espaco_depois=0)
    return sh


# ---------------------------------------------------------------------- slides

def s01_capa(prs, lays):
    return slide_capa(
        prs, lays,
        subtitulo="Aula 6: gráficos de duas variáveis",
        subtema="O par de tipos escolhe a geometria",
    )


def s02_plano(prs, lays):
    slide = slide_com_titulo(prs, lays, "O plano de hoje", EYEBROW)

    legenda(slide, MARGEM, Inches(1.98), FAIXA,
            "Aula curta de propósito: a segunda hora inteira é o projeto "
            "aplicado, em grupo e valendo nota.")

    itens = [
        ("25 min", "Slides", "o que ficou da gincana, e de uma variável "
         "para duas.", VERMELHO),
        ("25 min", "Notebook", "as geometrias novas e as três operações de "
         "pandas que o projeto usa.", ROXO),
        ("60 min", "Projeto 02", "no app da disciplina. Você organiza blocos de "
         "pandas e de plotnine na ordem em que devem rodar.", TURQUESA),
        ("5 min", "Fechamento", "entrega e o que vem na aula 7.", CINZA_ESCURO),
    ]
    y = Inches(2.62)
    for tempo, titulo, texto, cor in itens:
        etiqueta(slide, MARGEM, y, Inches(1.05), Inches(0.42), tempo, cor)
        tb = texto_livre(slide, MARGEM + Inches(1.30), y - Inches(0.02),
                         FAIXA - Inches(1.30), Inches(0.9))
        escrever(tb.text_frame, [
            {"texto": titulo, "tamanho": 17, "bold": True, "depois": 1},
            {"texto": texto, "tamanho": 13, "cor": CINZA_ESCURO, "depois": 0},
        ])
        y += Inches(1.02)
    return slide


def s02b_retomada_pipeline(prs, lays):
    """Retomada da aula 5: a sequencia de operacoes."""
    slide = slide_com_titulo(prs, lays, "De onde viemos: o encadeamento",
                             EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "Uma análise é uma sequência de operações somadas com ponto. Cada "
            "uma recebe a tabela que a anterior devolveu.")

    linhas = [
        ('.query("coluna == \'valor\'")', "escolher linhas"),
        ('[["a", "b"]]', "escolher colunas: dois pares de colchetes"),
        ('.sort_values("a", ascending=False)', "ordenar"),
        ('.groupby("a").agg(nome=("b", "mean"))', "uma linha por grupo"),
        ('.assign(nova=tabela["b"] > 8)', "criar uma coluna"),
    ]
    y = Inches(2.50)
    for op, oque in linhas:
        caixa(slide, MARGEM, y, Inches(0.08), Inches(0.40),
              preenchimento=TURQUESA)
        tb = texto_livre(slide, MARGEM + Inches(0.24), y - Inches(0.05),
                         Inches(4.10), Inches(0.46))
        escrever(tb.text_frame, [{"texto": op, "fonte": MONO, "tamanho": 12,
                                  "bold": True, "depois": 0}])
        tb = texto_livre(slide, MARGEM + Inches(4.40), y - Inches(0.05),
                         Inches(2.40), Inches(0.46))
        escrever(tb.text_frame, [{"texto": oque, "tamanho": 12,
                                  "cor": CINZA_ESCURO, "depois": 0}])
        y += Inches(0.52)

    etiqueta(slide, MARGEM + Inches(6.85), Inches(2.42), Inches(3.20),
             Inches(0.40), "e sempre entre parênteses", CINZA_ESCURO)
    bloco_codigo(slide, MARGEM + Inches(6.85), Inches(2.94), Inches(4.65),
                 Inches(2.10), [
        "(",
        "    criminal",
        '    .query("eh_trafico")',
        '    .sort_values("pena_anos", ascending=False)',
        '    [["processo", "comarca", "pena_anos"]]',
        "    .head(5)",
        ")",
    ], tamanho=11, barra=TURQUESA)
    legenda(slide, MARGEM + Inches(6.85), Inches(5.20), Inches(4.65),
            "Os parênteses são o que permitem quebrar a linha e ler o "
            "encadeamento de cima para baixo, uma operação por linha.",
            tamanho=12)

    painel(slide, MARGEM, Inches(5.35), Inches(6.30), Inches(1.00), [
        {"texto": "A ordem é o conteúdo.", "tamanho": 15, "bold": True,
         "depois": 3},
        {"texto": "Filtrar antes ou depois de agrupar dá números diferentes, e "
                  "uma operação só usa coluna que já existe naquele ponto.",
         "tamanho": 12.5, "cor": CINZA_ESCURO, "depois": 0},
    ])
    return slide


def s02c_retomada_grafico(prs, lays):
    """Retomada da aula 5: a gramatica de graficos."""
    slide = slide_com_titulo(prs, lays, "De onde viemos: a gramática",
                             EYEBROW)

    painel(slide, MARGEM, Inches(1.94), FAIXA, Inches(0.80), [
        {"texto": "Um gráfico estatístico é um mapeamento de variáveis "
                  "(colunas) em aspectos estéticos de formas geométricas.",
         "tamanho": 17, "bold": True, "depois": 0},
    ], inverso=True, recuo=0.42)

    camadas = [
        ("1. os dados", "de qual tabela o gráfico sai", "ggplot(penas)",
         TURQUESA),
        ("2. a estética", "qual coluna vira qual aspecto do desenho",
         '+ aes(x="regime")', LARANJA),
        ("3. a geometria", "que forma ocupa essas posições", "+ geom_bar()",
         ROXO),
    ]
    y = Inches(3.05)
    for titulo, oque, codigo, cor in camadas:
        caixa(slide, MARGEM, y, Inches(0.09), Inches(0.78), preenchimento=cor)
        tb = texto_livre(slide, MARGEM + Inches(0.28), y - Inches(0.04),
                         Inches(3.30), Inches(0.84))
        escrever(tb.text_frame, [
            {"texto": titulo, "tamanho": 14, "bold": True, "depois": 2},
            {"texto": oque, "tamanho": 12, "cor": CINZA_ESCURO, "depois": 0},
        ])
        bloco_codigo(slide, MARGEM + Inches(3.80), y - Inches(0.02),
                     Inches(3.60), Inches(0.62), [codigo], tamanho=12,
                     barra=cor)
        y += Inches(0.95)

    imagem_ajustada(slide, os.path.join(FIGURAS, "retomada_bar.png"),
                    MARGEM + Inches(7.70), Inches(3.00), Inches(3.80),
                    Inches(2.40), moldura=False)

    painel(slide, MARGEM, Inches(6.00), FAIXA, Inches(0.85), [
        {"texto": "Dentro do aes(), nome de coluna. Fora do aes(), valor fixo.",
         "tamanho": 15, "bold": True, "depois": 3},
        {"texto": "É a distinção que mais gera erro, e ela vale para x, y, "
                  "fill, color, size e alpha.",
         "tamanho": 12.5, "cor": CINZA_ESCURO, "depois": 0},
    ])
    return slide


def s09b_catalogo_uni(prs, lays):
    """Um exemplo desenhado para cada grafico de uma variavel."""
    slide = slide_com_titulo(prs, lays, "Uma variável: os três casos", EYEBROW)

    legenda(slide, MARGEM, Inches(1.90), FAIXA,
            "O tipo da variável escolhe a geometria. Estes são todos os casos "
            "de uma variável sozinha.")

    casos = [
        ("categórica · frequência", TURQUESA, "cat_freq",
         ['ggplot(penas, aes(x="regime"))', "+ geom_bar()"],
         "geom_bar() conta as linhas sozinho: não existe coluna y."),
        ("categórica · frequência relativa", TURQUESA, "cat_prop",
         ['ggplot(freq, aes(x="regime", y="prop"))', "+ geom_col()"],
         "A divisão é feita antes, no pandas. A altura já vem pronta na "
         "tabela, então o geom é geom_col()."),
        ("numérica · distribuição", ROXO, "num_hist",
         ['ggplot(penas, aes(x="pena_anos"))', "+ geom_histogram(bins=20)"],
         "Numérica não tem categoria para contar: o histograma corta em faixas "
         "e conta cada faixa."),
    ]

    largura = Inches(3.70)
    passo = largura + Inches(0.20)
    for i, (rotulo, cor, figura, codigo, nota) in enumerate(casos):
        x = MARGEM + i * passo
        etiqueta(slide, x, Inches(2.42), largura, Inches(0.38), rotulo, cor)
        bloco_codigo(slide, x, Inches(2.92), largura, Inches(0.78), codigo,
                     tamanho=10, barra=cor)
        imagem_ajustada(slide, os.path.join(FIGURAS, f"{figura}.png"),
                        x, Inches(3.82), largura, Inches(2.20), moldura=False)
        tb = texto_livre(slide, x, Inches(6.10), largura, Inches(0.90))
        escrever(tb.text_frame, [{"texto": nota, "tamanho": 11,
                                  "cor": CINZA_ESCURO, "depois": 0}])
    return slide


def s09c_catalogo_bi(prs, lays):
    """Um exemplo desenhado para cada grafico de duas variaveis."""
    slide = slide_com_titulo(prs, lays, "Duas variáveis: os quatro casos",
                             EYEBROW)

    legenda(slide, MARGEM, Inches(1.90), FAIXA,
            "Agora o par de tipos escolhe a geometria. E quando o eixo x é "
            "tempo, o par muda de nome: vira série.")

    casos = [
        ("categórica × categórica", ROXO, "fill",
         ['aes(x="regime", fill="houve_reincidencia")',
          '+ geom_bar(position="fill")'],
         "Barras repartidas. Em proporção com fill, em contagem com dodge."),
        ("categórica × numérica", LARANJA, "boxplot",
         ['aes(x="regime", y="pena_anos")', "+ geom_boxplot() + coord_flip()"],
         "Uma caixa por categoria, comparando a distribuição inteira."),
        ("numérica × numérica", TURQUESA, "pontos_smooth",
         ['aes(x="n_palavras_ementa", y="pena_anos")',
          "+ geom_point() + geom_smooth(method=\"lm\")"],
         "Um ponto por linha, e a reta resume a direção da nuvem."),
        ("numérica × tempo", VERMELHO, "serie",
         ['aes(x="mes", y="n")', "+ geom_line() + geom_point()"],
         "Com o tempo no eixo x, a linha liga os pontos e mostra a trajetória."),
    ]

    largura = Inches(2.75)
    passo = largura + Inches(0.18)
    for i, (rotulo, cor, figura, codigo, nota) in enumerate(casos):
        x = MARGEM + i * passo
        etiqueta(slide, x, Inches(2.42), largura, Inches(0.38), rotulo, cor,
                 tamanho=10.5)
        bloco_codigo(slide, x, Inches(2.92), largura, Inches(0.86), codigo,
                     tamanho=8.5, barra=cor)
        imagem_ajustada(slide, os.path.join(FIGURAS, f"{figura}.png"),
                        x, Inches(3.90), largura, Inches(2.10), moldura=False)
        tb = texto_livre(slide, x, Inches(6.08), largura, Inches(0.95))
        escrever(tb.text_frame, [{"texto": nota, "tamanho": 10.5,
                                  "cor": CINZA_ESCURO, "depois": 0}])
    return slide


def s09b_univariados(prs, lays):
    """Retomada: uma variavel sozinha, por tipo."""
    slide = slide_com_titulo(prs, lays, "Uma variável: qual gráfico", EYEBROW)

    legenda(slide, MARGEM, Inches(1.98), FAIXA,
            "Os mesmos casos, agora em tabela, para consultar depois. "
            "Entram também duas geometrias que só aparecem no notebook.")

    linhas = [
        ("categórica", "quantos casos em cada categoria", "geom_bar()",
         "conta sozinho: não existe coluna y", TURQUESA),
        ("categórica, altura já calculada", "um valor por categoria",
         "geom_col()", "usa a coluna que você mapeou em y", TURQUESA),
        ("numérica", "como os valores se distribuem", "geom_histogram(bins=)",
         "o número de faixas muda a leitura", ROXO),
        ("numérica", "a mesma distribuição, alisada", "geom_density()",
         "sem o degrau das faixas", ROXO),
        ("numérica", "mediana, quartis e pontos fora", "geom_boxplot()",
         "resume, e por isso esconde a forma", ROXO),
    ]

    tab = tabela(slide, MARGEM, Inches(2.55), FAIXA, Inches(3.30),
                 ["", "a variável", "a pergunta", "a geometria", "o detalhe"],
                 linhas, [Inches(0.14), Inches(3.05), Inches(3.15),
                          Inches(2.40), Inches(2.76)], Inches(0.58))
    for r, (var, perg, geom, det, cor) in enumerate(linhas, start=1):
        z = QUASE_BRANCO if r % 2 else BRANCO
        celula(tab, r, 0, "", fundo=cor)
        celula(tab, r, 1, var, tamanho=12, bold=True, cor=PRETO, fundo=z)
        celula(tab, r, 2, perg, tamanho=12, cor=PRETO, fundo=z)
        celula(tab, r, 3, geom, tamanho=12, bold=True, cor=PRETO, fundo=z)
        celula(tab, r, 4, det, tamanho=11.5, cor=CINZA_ESCURO, fundo=z)

    painel(slide, MARGEM, Inches(6.05), FAIXA, Inches(0.85), [
        {"texto": "A pergunta a fazer antes de escolher: a altura é uma "
                  "contagem, ou uma conta que eu já fiz?", "tamanho": 15,
         "bold": True, "depois": 3},
        {"texto": "Contagem é geom_bar(). Conta pronta é geom_col(). Todo o "
                  "resto decorre do tipo da variável.",
         "tamanho": 12.5, "cor": CINZA_ESCURO, "depois": 0},
    ])
    return slide


def s09c_datatoviz(prs, lays):
    """O data-to-viz, para quando a duvida aparecer fora da aula."""
    slide = slide_com_titulo(prs, lays, "From data to viz", EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "As tabelas destes slides cobrem o que a disciplina usa. Para o "
            "resto, existe uma árvore de decisão pronta: você diz que tipo de "
            "dado tem, e ela leva ao gráfico.")

    imagem_ajustada(slide, os.path.join(FIGURAS, "data_to_viz.png"),
                    MARGEM, Inches(2.50), Inches(8.10), Inches(3.95),
                    moldura=True)

    x2 = MARGEM + Inches(8.45)
    etiqueta(slide, x2, Inches(2.50), Inches(3.05), Inches(0.40),
             "data-to-viz.com", VERMELHO)
    tb = texto_livre(slide, x2, Inches(3.10), Inches(3.05), Inches(3.20))
    escrever(tb.text_frame, [
        {"texto": "Escolha o tipo de dado no alto (numérico, categórico, os "
                  "dois, mapa, rede, série temporal) e siga a árvore.",
         "tamanho": 12.5, "depois": 8},
        {"texto": "Cada gráfico do fim leva a uma página com o código, e a uma "
                  "lista do que costuma dar errado naquele tipo.",
         "tamanho": 12.5, "depois": 8},
        {"texto": "A seção CAVEATS é a melhor parte: é um catálogo de gráficos "
                  "que enganam, com o motivo.",
         "tamanho": 12.5, "cor": CINZA_ESCURO, "depois": 0},
    ])
    return slide


def s03_assign(prs, lays):
    """A rodada 3 da gincana, que a aula 5 nao alcancou."""
    slide = slide_com_titulo(prs, lays, "A coluna que não estava na tabela",
                             EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "Ficou faltando uma rodada da gincana, e ela é a mais usada hoje: "
            "a coluna que responde à pergunta nem sempre existe na base.")

    etiqueta(slide, MARGEM, Inches(2.42), Inches(4.10), Inches(0.40),
             "a coluna nasce no meio do caminho", TURQUESA)
    bloco_codigo(slide, MARGEM, Inches(2.90), Inches(6.30), Inches(1.95), [
        "(",
        "    criminal",
        '    .assign(eh_capital=criminal["comarca"] == "São Paulo")',
        '    .groupby("eh_capital")',
        '    .agg(n=("processo", "size"))',
        "    .reset_index()",
        ")",
    ], tamanho=12, barra=TURQUESA)

    itens = [
        ("A base tem comarca, e não tem eh_capital.",
         "Nenhuma coluna responde “capital ou interior”."),
        (".assign() cria a coluna sem quebrar o encadeamento.",
         "Por isso ele cabe no meio do pipeline."),
        ("Ele vem ANTES do .groupby() que usa a coluna.",
         "A coluna precisa existir para ser agrupada. É a única ordem que não "
         "pode trocar."),
    ]
    y = Inches(4.98)
    for titulo, texto in itens:
        caixa(slide, MARGEM, y, Inches(0.09), Inches(0.72), preenchimento=TURQUESA)
        tb = texto_livre(slide, MARGEM + Inches(0.28), y - Inches(0.06),
                         Inches(6.20), Inches(0.82))
        escrever(tb.text_frame, [
            {"texto": titulo, "tamanho": 12.5, "bold": True, "depois": 2},
            {"texto": texto, "tamanho": 11, "cor": CINZA_ESCURO, "depois": 0},
        ])
        y += Inches(0.84)

    # a tabela que ESTE pipeline produz, e não uma figura qualquer: o slide
    # existe para mostrar o que o código da esquerda devolve
    etiqueta(slide, MARGEM + Inches(6.85), Inches(2.42), Inches(2.60),
             Inches(0.40), "o que isso devolve", TURQUESA)
    linhas = [("False", "378"), ("True", "97")]
    tab = tabela(slide, MARGEM + Inches(6.85), Inches(2.96), Inches(4.00),
                 Inches(1.24), ["eh_capital", "n"], linhas,
                 [Inches(2.55), Inches(1.45)], Inches(0.44))
    for r, (v, n) in enumerate(linhas, start=1):
        z = QUASE_BRANCO if r % 2 else BRANCO
        celula(tab, r, 0, v, tamanho=13, bold=True, cor=PRETO, fundo=z)
        celula(tab, r, 1, n, tamanho=13, cor=PRETO, fundo=z)

    legenda(slide, MARGEM + Inches(6.85), Inches(4.50), Inches(4.65),
            "Duas linhas, porque a coluna nova só tem dois valores. O "
            ".reset_index() é o que traz eh_capital para dentro da tabela: sem "
            "ele, ela vira rótulo de linha e some do alcance do aes().",
            tamanho=12)
    return slide


def s04_proporcao(prs, lays):
    """A rodada 6: media de verdadeiro/falso e proporcao, e geom_col."""
    slide = slide_com_titulo(prs, lays, "Contagem vs proporção", EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "A outra rodada que ficou. Duas perguntas parecidas, dois gráficos "
            "diferentes, e a diferença está em quem faz a conta.")

    # esquerda: contar
    etiqueta(slide, MARGEM, Inches(2.42), Inches(3.60), Inches(0.40),
             "quantos acórdãos em cada regime?", CINZA_ESCURO)
    bloco_codigo(slide, MARGEM, Inches(2.94), Inches(5.30), Inches(1.20), [
        'ggplot(penas, aes(x="regime"))',
        "+ geom_bar()",
    ], tamanho=12, barra=CINZA_ESCURO)
    imagem_ajustada(slide, os.path.join(FIGURAS, "retomada_bar.png"),
                    MARGEM, Inches(4.30), Inches(5.30), Inches(2.10),
                    moldura=False)
    legenda(slide, MARGEM, Inches(6.52), Inches(5.30),
            "geom_bar() conta as linhas sozinho. A altura sai da contagem, e "
            "não existe coluna y.", tamanho=11.5)

    # direita: medir
    x2 = MARGEM + Inches(5.75)
    etiqueta(slide, x2, Inches(2.42), Inches(4.30), Inches(0.40),
             "que proporção é reincidente?", VERMELHO)
    bloco_codigo(slide, x2, Inches(2.94), Inches(5.75), Inches(1.20), [
        "resumo = (",
        '    penas.groupby("regime", as_index=False)',
        '    .agg(prop=("houve_reincidencia", "mean"))',
        ")",
    ], tamanho=10.5, barra=VERMELHO)
    imagem_ajustada(slide, os.path.join(FIGURAS, "retomada_col.png"),
                    x2, Inches(4.30), Inches(5.30), Inches(2.10),
                    moldura=False)
    legenda(slide, x2, Inches(6.52), Inches(5.75),
            "Depois vem ggplot(resumo) + aes(x=\"regime\", y=\"prop\") + "
            "geom_col(). A altura já está na tabela, e a média de uma coluna "
            "de verdadeiro/falso é a proporção de verdadeiros.", tamanho=11.5)
    return slide


def s03_ideia(prs, lays):
    slide = slide_com_titulo(prs, lays, "De uma variável para duas", EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "Na aula 5 todo gráfico tinha uma coluna só. Hoje entram duas, e a "
            "gramática não muda: o aes() passa a receber dois nomes.")

    caixa(slide, MARGEM, Inches(2.50), FAIXA, Inches(1.15), preenchimento=PRETO)
    tb = texto_livre(slide, MARGEM + Inches(0.40), Inches(2.76),
                     FAIXA - Inches(0.8), Inches(0.85))
    escrever(tb.text_frame, [
        {"texto": "O par de tipos escolhe a geometria.",
         "tamanho": 26, "bold": True, "cor": BRANCO, "depois": 5},
        {"texto": "Antes de escrever qualquer coisa, diga em voz alta o tipo "
                  "das duas variáveis.",
         "tamanho": 14, "cor": BRANCO, "depois": 0},
    ])

    pares = [
        ("numérica  ×  numérica", "quando uma cresce, o que a outra faz",
         "geom_point()", TURQUESA),
        ("numérica  ×  categórica", "a distribuição muda entre as categorias",
         "geom_boxplot()", LARANJA),
        ("categórica  ×  categórica", "a composição muda entre as categorias",
         'geom_bar(position="fill")', ROXO),
    ]
    y = Inches(4.05)
    for par, pergunta, geom, cor in pares:
        caixa(slide, MARGEM, y, Inches(0.09), Inches(0.72), preenchimento=cor)
        tb = texto_livre(slide, MARGEM + Inches(0.28), y - Inches(0.02),
                         Inches(3.60), Inches(0.4))
        escrever(tb.text_frame, [
            {"texto": par, "tamanho": 16, "bold": True, "depois": 0}])
        tb = texto_livre(slide, MARGEM + Inches(4.00), y + Inches(0.02),
                         Inches(4.20), Inches(0.4))
        escrever(tb.text_frame, [
            {"texto": pergunta, "tamanho": 13, "cor": CINZA_ESCURO,
             "depois": 0}])
        tb = texto_livre(slide, MARGEM + Inches(8.40), y + Inches(0.02),
                         Inches(3.10), Inches(0.4))
        escrever(tb.text_frame, [
            {"texto": geom, "fonte": MONO, "tamanho": 13, "depois": 0}])
        y += Inches(0.82)
    return slide


def s04_forma_curta(prs, lays):
    slide = slide_com_titulo(prs, lays, "Uma forma mais curta de escrever",
                             EYEBROW)

    legenda(slide, MARGEM, Inches(1.98), FAIXA,
            "O aes() pode ir dentro do ggplot(), como segundo argumento. "
            "As duas células produzem exatamente o mesmo gráfico.")

    largura = Inches(5.55)
    x2 = MARGEM + largura + Inches(0.40)

    etiqueta(slide, MARGEM, Inches(2.55), Inches(3.10), Inches(0.36),
             "a forma da aula 5", CINZA_ESCURO)
    bloco_codigo(slide, MARGEM, Inches(3.03), largura, Inches(1.45), [
        "(",
        "    ggplot(penas)",
        '    + aes(x="regime")',
        "    + geom_bar()",
        ")",
    ], barra=CINZA)
    legenda(slide, MARGEM, Inches(4.62), largura,
            "Separa as camadas, e é melhor para aprender.", tamanho=12)

    etiqueta(slide, x2, Inches(2.55), Inches(3.55), Inches(0.36),
             "a forma curta", VERMELHO)
    bloco_codigo(slide, x2, Inches(3.03), largura, Inches(1.45), [
        "(",
        '    ggplot(penas, aes(x="regime"))',
        "    + geom_bar()",
        ")",
    ], barra=VERMELHO)
    legenda(slide, x2, Inches(4.62), largura,
            "É a mais comum na prática, e a que você vai achar na internet e "
            "nos exercícios.", tamanho=12)

    caixa(slide, MARGEM, Inches(5.35), FAIXA, Inches(1.05),
          preenchimento=QUASE_BRANCO)
    tb = texto_livre(slide, MARGEM + Inches(0.30), Inches(5.52),
                     FAIXA - Inches(0.6), Inches(0.8))
    escrever(tb.text_frame, [
        {"texto": "A regra da aula 5 continua valendo, sem exceção.",
         "tamanho": 15, "bold": True, "depois": 3},
        {"texto": "Nome de coluna dentro do aes(), valor fixo fora dele. "
                  "Mudou onde o aes() está escrito, não o que ele faz.",
         "tamanho": 13, "cor": CINZA_ESCURO, "depois": 0},
    ])
    return slide


def s05_pontos(prs, lays):
    slide = slide_com_titulo(prs, lays, "Duas numéricas: pontos", EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "Um ponto por linha da tabela, com a posição dada pelas duas "
            "colunas. geom_smooth() acrescenta a reta que resume a nuvem.")

    bloco_codigo(slide, MARGEM, Inches(2.48), Inches(6.30), Inches(1.60), [
        "(",
        '    ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos"))',
        "    + geom_point(alpha=0.4)",
        '    + geom_smooth(method="lm", color="#E50505")',
        ")",
    ], tamanho=12, barra=TURQUESA)

    legenda(slide, MARGEM, Inches(4.30), Inches(6.30),
            "alpha vai fora do aes(): é um valor fixo, e serve para enxergar "
            "os pontos empilhados uns sobre os outros.", tamanho=12)

    imagem_ajustada(slide, os.path.join(FIGURAS, "pontos_smooth.png"),
                    MARGEM + Inches(6.85), Inches(2.30), Inches(4.65),
                    Inches(3.20), moldura=False)

    caixa(slide, MARGEM, Inches(5.10), Inches(6.30), Inches(1.35),
          preenchimento=PRETO)
    tb = texto_livre(slide, MARGEM + Inches(0.28), Inches(5.28), Inches(5.75),
                     Inches(1.1))
    escrever(tb.text_frame, [
        {"texto": "A reta é quase plana, e isso é uma resposta.",
         "tamanho": 15, "bold": True, "cor": BRANCO, "depois": 4},
        {"texto": "O tamanho da ementa não diz quase nada sobre a pena. "
                  "Gráfico que não mostra relação também responde à pergunta.",
         "tamanho": 12.5, "cor": BRANCO, "depois": 0},
    ])
    return slide


def s06_nao_diz(prs, lays):
    slide = slide_com_titulo(prs, lays, "O que a reta não diz", EYEBROW)

    legenda(slide, MARGEM, Inches(1.98), FAIXA,
            "Duas leituras que o gráfico anterior não autoriza, e que vão "
            "aparecer no relatório de vocês se ninguém avisar.")

    itens = [
        ("Reta plana não prova que não há relação",
         "Prova que não há relação linear nestes 197 acórdãos, que são os que "
         "tinham regime e pena legíveis na ementa. Mais da metade da base "
         "ficou de fora, e ela não saiu por sorteio."),
        ("Reta inclinada não provaria causa",
         "Se ementas longas viessem com penas altas, o mais provável seria que "
         "caso grave gera ementa longa e pena alta. A reta mede associação, e "
         "associação não é causa."),
    ]
    y = Inches(2.60)
    for titulo, texto in itens:
        caixa(slide, MARGEM, y, Inches(0.09), Inches(1.35),
              preenchimento=VERMELHO)
        tb = texto_livre(slide, MARGEM + Inches(0.30), y - Inches(0.02),
                         FAIXA - Inches(0.5), Inches(1.4))
        escrever(tb.text_frame, [
            {"texto": titulo, "tamanho": 18, "bold": True, "depois": 4},
            {"texto": texto, "tamanho": 13.5, "cor": CINZA_ESCURO, "depois": 0},
        ])
        y += Inches(1.70)

    caixa(slide, MARGEM, Inches(6.00), FAIXA, Inches(0.80),
          preenchimento=QUASE_BRANCO)
    tb = texto_livre(slide, MARGEM + Inches(0.30), Inches(6.18),
                     FAIXA - Inches(0.6), Inches(0.55))
    escrever(tb.text_frame, [
        {"texto": "No exercício 3 do notebook vocês escrevem as duas linhas: "
                  "o que o gráfico mostra, e o que ele não permite concluir.",
         "tamanho": 14, "bold": True, "depois": 0},
    ])
    return slide


def s07_boxplot(prs, lays):
    slide = slide_com_titulo(prs, lays, "Numérica e categórica: caixas",
                             EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "Uma caixa por categoria. Cada caixa é o resumo da aula 3, "
            "desenhado.")

    bloco_codigo(slide, MARGEM, Inches(2.48), Inches(6.30), Inches(1.55), [
        "(",
        '    ggplot(penas, aes(x="regime", y="pena_anos"))',
        "    + geom_boxplot()",
        "    + coord_flip()",
        ")",
    ], tamanho=12, barra=LARANJA)

    partes = [
        ("a linha do meio", "a mediana"),
        ("a caixa", "do primeiro ao terceiro quartil"),
        ("os fios", "até os valores ainda típicos"),
        ("os pontos soltos", "os distantes do resto"),
    ]
    y = Inches(4.25)
    for nome, oque in partes:
        tb = texto_livre(slide, MARGEM, y, Inches(2.30), Inches(0.32))
        escrever(tb.text_frame, [
            {"texto": nome, "tamanho": 13, "bold": True, "depois": 0}])
        tb = texto_livre(slide, MARGEM + Inches(2.40), y, Inches(3.90),
                         Inches(0.32))
        escrever(tb.text_frame, [
            {"texto": oque, "tamanho": 13, "cor": CINZA_ESCURO, "depois": 0}])
        y += Inches(0.42)

    imagem_ajustada(slide, os.path.join(FIGURAS, "boxplot.png"),
                    MARGEM + Inches(6.85), Inches(2.30), Inches(4.65),
                    Inches(3.60), moldura=False)
    return slide


def s08a_position_codigo(prs, lays):
    """Os tres codigos completos, nas mesmas colunas em que o slide seguinte
    poe os tres graficos. Ver o codigo e depois o desenho no mesmo lugar e o
    que deixa a comparacao imediata."""
    slide = slide_com_titulo(prs, lays, "Duas categóricas: o position",
                             EYEBROW)

    legenda(slide, MARGEM, Inches(1.90), FAIXA,
            "As mesmas duas variáveis, a mesma geometria, três gráficos "
            "diferentes. Só muda o argumento position.")

    casos = [
        ('position="stack"', TURQUESA, "stack",
         "o padrão: quantos casos, empilhados"),
        ('position="fill"', VERMELHO, "fill",
         "todas as barras com altura 1: proporção"),
        ('position="dodge"', LARANJA, "dodge",
         "lado a lado: contagem, sem empilhar"),
    ]

    largura = Inches(3.70)
    passo = largura + Inches(0.20)
    for i, (rotulo, cor, valor, oque) in enumerate(casos):
        x = MARGEM + i * passo
        etiqueta(slide, x, Inches(2.45), largura, Inches(0.40), rotulo, cor)
        bloco_codigo(slide, x, Inches(3.00), largura, Inches(2.05), [
            "(",
            "    ggplot(",
            "        penas,",
            '        aes(x="regime",',
            '            fill="houve_reincidencia")',
            "    )",
            f'    + geom_bar(position="{valor}")',
            ")",
        ], tamanho=10, barra=cor)
        tb = texto_livre(slide, x, Inches(5.20), largura, Inches(0.70))
        escrever(tb.text_frame, [{"texto": oque, "tamanho": 12.5,
                                  "cor": CINZA_ESCURO, "depois": 0}])
    return slide

def s08b_position_resultado(prs, lays):
    """Os tres resultados lado a lado."""
    slide = slide_com_titulo(prs, lays, "Os três, lado a lado", EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "A resposta é o fill: ele é o único em que a comparação entre "
            "regimes não é atrapalhada pelo tamanho de cada grupo.")

    largura = Inches(3.65)
    for i, (nome, rotulo, cor) in enumerate([
        ("stack", 'position="stack"', TURQUESA),
        ("fill", 'position="fill"', VERMELHO),
        ("dodge", 'position="dodge"', LARANJA),
    ]):
        x = MARGEM + i * (largura + Inches(0.28))
        etiqueta(slide, x, Inches(2.50), largura, Inches(0.40), rotulo, cor)
        imagem_ajustada(slide, os.path.join(FIGURAS, f"{nome}.png"),
                        x, Inches(3.02), largura, Inches(2.85), moldura=False)

    painel(slide, MARGEM, Inches(6.10), FAIXA, Inches(0.85), [
        {"texto": 'position="fill" esconde quanta gente tem em cada barra.',
         "tamanho": 15, "bold": True, "depois": 3},
        {"texto": "Uma barra com 4 casos e outra com 400 ficam do mesmo "
                  "tamanho. Quando a proporção interessa, ele é o certo; "
                  "quando o tamanho do grupo importa, ele mente por omissão.",
         "tamanho": 12.5, "cor": CINZA_ESCURO, "depois": 0},
    ])
    return slide

def s09_preparar(prs, lays):
    slide = slide_com_titulo(prs, lays, "Preparar a tabela antes do gráfico",
                             EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "Quando a altura da barra é uma conta, o pandas faz a conta e o "
            "plotnine só desenha. São três operações, e elas voltam sempre.")

    itens = [
        (".assign(nova=expressao)", "criar uma coluna sem quebrar o "
         "encadeamento", TURQUESA),
        (".groupby(col, as_index=False)", "agrupar já saindo com a coluna "
         "dentro da tabela, sem precisar do .reset_index()", TURQUESA),
        ('reorder("categoria", "valor")', "ordenar as barras, escrito dentro "
         "do aes(). Ordenar a tabela NÃO ordena as barras.", ROXO),
    ]
    y = Inches(2.50)
    for op, texto, cor in itens:
        caixa(slide, MARGEM, y, Inches(0.09), Inches(0.90), preenchimento=cor)
        tb = texto_livre(slide, MARGEM + Inches(0.28), y - Inches(0.02),
                         Inches(6.20), Inches(0.95))
        escrever(tb.text_frame, [
            {"texto": op, "fonte": MONO, "tamanho": 14, "bold": True,
             "depois": 3},
            {"texto": texto, "tamanho": 12.5, "cor": CINZA_ESCURO, "depois": 0},
        ])
        y += Inches(1.05)

    bloco_codigo(slide, MARGEM, Inches(5.75), Inches(6.30), Inches(0.98), [
        'ggplot(resumo, aes(x="reorder(comarca, pena_mediana)", '
        'y="pena_mediana"))',
        "+ geom_col(fill=\"#E50505\") + coord_flip()",
    ], tamanho=10.5, barra=ROXO)

    imagem_ajustada(slide, os.path.join(FIGURAS, "reorder.png"),
                    MARGEM + Inches(6.85), Inches(2.20), Inches(4.65),
                    Inches(4.35), moldura=False)
    return slide


def s10_tabela(prs, lays):
    slide = slide_com_titulo(prs, lays, "Que gráfico para que par", EYEBROW)

    linhas = [
        ("numérica × numérica", "quando uma cresce, o que a outra faz",
         "geom_point() + geom_smooth()", TURQUESA),
        ("numérica × numérica, x é tempo", "como evolui", "geom_line()",
         TURQUESA),
        ("numérica × categórica", "a distribuição muda entre as categorias",
         "geom_boxplot()", LARANJA),
        ("numérica × categórica, já resumida", "comparar um valor por categoria",
         "geom_col()", LARANJA),
        ("categórica × categórica", "a composição muda entre as categorias",
         'geom_bar(position="fill")', ROXO),
        ("categórica × categórica, contagem", "quantos casos em cada combinação",
         'geom_bar(position="dodge")', ROXO),
    ]

    tabela_shape = slide.shapes.add_table(
        len(linhas) + 1, 4, MARGEM, Inches(2.15), FAIXA, Inches(3.95))
    tabela = tabela_shape.table
    tabela_sem_estilo(tabela)
    for larg, i in zip([Inches(0.14), Inches(3.85), Inches(3.75),
                        Inches(3.76)], range(4)):
        tabela.columns[i].width = larg
    tabela.rows[0].height = Inches(0.32)
    for r in range(1, len(linhas) + 1):
        tabela.rows[r].height = Inches(0.60)

    for c, t in enumerate(["", "as duas variáveis", "a pergunta",
                           "a geometria"]):
        celula(tabela, 0, c, t, tamanho=11, bold=True, cor=BRANCO, fundo=PRETO)
    for r, (par, perg, geom, cor) in enumerate(linhas, start=1):
        zebra = QUASE_BRANCO if r % 2 == 0 else None
        celula(tabela, r, 0, "", fundo=cor)
        celula(tabela, r, 1, par, tamanho=12, bold=True, fundo=zebra)
        celula(tabela, r, 2, perg, tamanho=12, cor=CINZA_ESCURO, fundo=zebra)
        celula(tabela, r, 3, geom, tamanho=12, bold=True, fundo=zebra)

    caixa(slide, MARGEM, Inches(6.30), FAIXA, Inches(0.72),
          preenchimento=QUASE_BRANCO)
    tb = texto_livre(slide, MARGEM + Inches(0.30), Inches(6.45),
                     FAIXA - Inches(0.6), Inches(0.5))
    escrever(tb.text_frame, [
        {"texto": "A terceira variável, quando existe, entra em color ou fill "
                  "dentro do aes(), ou em facet_wrap() quando ficar carregado.",
         "tamanho": 13.5, "bold": True, "depois": 0},
    ])
    return slide


def s11_projeto(prs, lays):
    slide = slide_com_titulo(prs, lays, "Projeto 02", EYEBROW)

    legenda(slide, MARGEM, Inches(1.94), FAIXA,
            "Em grupo, valendo nota, uma hora. É a Gincana do Pipeline de "
            "terça-feira, no computador.")

    passos = [
        ("Seis desafios", "cada um com uma pergunta e a imagem do gráfico "
         "que vocês precisam produzir. Dá para avançar e voltar."),
        ("Valem 11 pontos", "o primeiro vale 1 e os outros 2. Cada tentativa "
         "errada desconta 0,25, e a nota para em 10."),
        ("Blocos fora de ordem", "de pandas e de plotnine. Você escolhe quais "
         "usar e em que ordem."),
        ("Tem bloco que não serve", "e o app explica por que, quando você usa. "
         "É o distrator da gincana."),
        ("Entrega hoje", "no fim da aula. Não há prazo no dia seguinte."),
    ]
    y = Inches(2.55)
    for titulo, texto in passos:
        caixa(slide, MARGEM, y, Inches(0.09), Inches(0.82),
              preenchimento=VERMELHO)
        tb = texto_livre(slide, MARGEM + Inches(0.28), y - Inches(0.02),
                         Inches(6.10), Inches(0.88))
        escrever(tb.text_frame, [
            {"texto": titulo, "tamanho": 15, "bold": True, "depois": 2},
            {"texto": texto, "tamanho": 12.5, "cor": CINZA_ESCURO, "depois": 0},
        ])
        y += Inches(0.98)

    return slide


def s12_fechamento(prs, lays):
    slide = slide_com_titulo(prs, lays, "Antes de sair", EYEBROW)

    itens = [
        ("Submeta pelo BlackBoard", "A entrega é hoje, no fim da aula. O app "
         "mostra o que foi registrado na sua sessão.", VERMELHO),
        ("Rode o notebook inteiro em casa", "Principalmente os exercícios 1 a "
         "3, que são os que pedem a leitura escrita do gráfico.", ROXO),
        ("Aula 7", "Probabilidade. Volta o papel e a caneta, e some o "
         "computador.", CINZA_ESCURO),
    ]
    y = Inches(2.40)
    for titulo, texto, cor in itens:
        caixa(slide, MARGEM, y, Inches(0.09), Inches(1.15), preenchimento=cor)
        tb = texto_livre(slide, MARGEM + Inches(0.32), y - Inches(0.02),
                         FAIXA - Inches(0.5), Inches(1.2))
        escrever(tb.text_frame, [
            {"texto": titulo, "tamanho": 19, "bold": True, "depois": 4},
            {"texto": texto, "tamanho": 14, "cor": CINZA_ESCURO, "depois": 0},
        ])
        y += Inches(1.45)
    return slide


# ---------------------------------------------------------------------- main

def main():
    prs = deck_limpo()
    lays = layouts(prs)

    # A aula abre retomando a 5 (o encadeamento e a gramatica), passa pelas
    # duas rodadas que a gincana nao alcancou, e so entao vai para duas
    # variaveis. Os graficos de UMA variavel voltam logo antes da tabela de
    # pares, junto com o data-to-viz: e ali que a pessoa decide o que usar.
    # O boxplot vem DEPOIS das barras: a aula sobe de uma variavel para duas
    # pelo caminho mais curto, que e acrescentar cor a um grafico de barras que
    # a turma ja sabe ler. A caixa e forma nova, e entra depois.
    #
    # Saiu o slide de `reorder()`: nao ha tempo para ele, e por isso ele
    # tambem saiu do Projeto 02 e virou material extra no notebook.
    for construir in (s01_capa,
                      s02b_retomada_pipeline, s02c_retomada_grafico,
                      s03_assign, s04_proporcao,
                      s03_ideia, s04_forma_curta,
                      s08a_position_codigo, s08b_position_resultado,
                      s07_boxplot,
                      s09b_catalogo_uni, s09c_catalogo_bi,
                      s09b_univariados, s10_tabela, s09c_datatoviz):
        construir(prs, lays)

    n = gravar(prs, SAIDA, titulo="Aula 6: gráficos de duas variáveis")
    print(f"{SAIDA}  ({n} slides)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
