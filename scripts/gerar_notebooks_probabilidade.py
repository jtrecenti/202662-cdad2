"""Notebooks das aulas 7, 8 e 9 (probabilidade, distribuições e inferência).

Sai daqui:
    notebooks/aula07_professor.ipynb   probabilidade condicional e independência
    notebooks/aula07_aluno.ipynb
    notebooks/aula08_professor.ipynb   distribuições de probabilidade
    notebooks/aula08_aluno.ipynb
    notebooks/aula09_professor.ipynb   amostra, TCL e intervalo de confiança
    notebooks/aula09_aluno.ipynb

Estes três são propositalmente CURTOS, na casa de vinte células, e não os
oitenta das aulas 2 a 6. O motivo é o formato da aula: a conta é feita na
lousa, com a turma junto, e o notebook vem depois só para conferir na máquina
o que já foi entendido no papel. Notebook comprido aqui competiria com a lousa
e perderia.

Daí três regras de corte:

1. **Nada de conta que a lousa não tenha feito antes.** O notebook confere, não
   ensina.
2. **Uma ideia por seção, um exercício por ideia.** Sem apêndice, sem "para
   quem quiser ver mais".
3. **A base é a mesma das aulas 4 a 6.** Trocar de base custaria metade do
   notebook em reapresentação, e não é disso que se trata.

A classe `Caderno` vem do gerar_notebooks.py: mesma formatação, mesmo par
professor/aluno, mesma convenção de lacuna com `________`.

Uso:
    python scripts/gerar_notebooks_probabilidade.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from gerar_notebooks import URL, Caderno  # noqa: E402

# A base criminal, montada igual em todas as três aulas. Sai de uma constante
# porque repetir isso em três lugares é como as versões saem de sincronia.
ABERTURA_CRIMINAL = f'''
import pandas as pd

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)

URL = "{URL}"

criminal = pd.read_csv(f"{{URL}}/tjsp_cjsg_criminal.csv")

# Fora as linhas sem regime: não dá para calcular proporção de regime
# em acórdão que não informou regime nenhum.
penas = criminal.dropna(subset=["regime_inicial"])

penas.shape
'''


# ====================================================== AULA 7


def montar_aula07() -> Caderno:
    nb = Caderno("aula07")

    nb.cabecalho(
        "Probabilidade e incerteza",
        "Aula 07",
        [
            "calcular a probabilidade de um evento como proporção na base;",
            "calcular uma probabilidade condicional filtrando e recontando;",
            "montar a tabela de duas variáveis e ler as contagens dela;",
            "verificar se dois eventos são independentes comparando o observado "
            "com o que a independência preveria.",
        ],
        abertura="""
Este notebook é curto de propósito. Tudo que está aqui já foi feito na lousa
hoje: o que muda é que agora o computador faz a divisão, e você confere se o
número bate com o que você calculou à mão.
""",
    )

    nb.indice([
        ("A base de hoje", "dados"),
        ("Probabilidade é uma proporção", "proporcao"),
        ("A tabela de dupla entrada", "tabela"),
        ("Probabilidade condicional", "condicional"),
        ("Independência: o teste", "independencia"),
        ("RESUMO", "resumo"),
    ])

    # ---------------------------------------------------------------- base
    nb.secao("dados", "A base de hoje", """
A mesma base de apelações criminais das aulas 4 a 6. Uma linha por acórdão.
""")
    nb.code(ABERTURA_CRIMINAL)

    nb.md("""
Duas colunas interessam hoje:

- `regime_inicial`: aberto, semiaberto ou fechado;
- `houve_reincidencia`: `True` ou `False`.
""")
    nb.code('penas[["regime_inicial", "houve_reincidencia"]].head()')

    nb.volta()

    # ----------------------------------------------------------- proporcao
    nb.secao("proporcao", "Probabilidade é uma proporção", """
$P(A)$ é o número de casos em $A$ dividido pelo total. No pandas, uma coluna de
`True` e `False` já sabe fazer essa conta sozinha: a média de uma coluna
booleana **é** a proporção de `True`.
""")

    nb.code('''
# O evento "o regime foi fechado", caso a caso
fechado = penas["regime_inicial"] == "fechado"

fechado.head()
''')

    nb.code('''
# P(fechado): quantos True, dividido pelo total
fechado.mean()
''')

    nb.md("""
Por que a média funciona: `True` vale 1 e `False` vale 0, então somar a coluna
conta os casos e dividir pelo tamanho dá a proporção. É a definição de
probabilidade que usamos na lousa, escrita em uma linha.
""")

    nb.faca(
        "Calcule $P(\\text{réu reincidente})$. É a mesma ideia, em outra coluna.",
        '''
reincidente = penas["houve_reincidencia"]

reincidente.mean()
''',
        '''
reincidente = penas["________"]

reincidente.________()
''',
    )

    nb.volta()

    # -------------------------------------------------------------- tabela
    nb.secao("tabela", "A tabela de dupla entrada", """
`pd.crosstab` cruza duas colunas e conta quantos casos caem em cada
combinação. É exatamente a tabela que estava no slide.

Vale reter os dois nomes, porque eles aparecem juntos o tempo todo:

- o **miolo** da tabela é a distribuição **conjunta**, e cada célula responde
  por duas variáveis ao mesmo tempo;
- a última linha e a última coluna são as distribuições **marginais**, e cada
  valor delas responde por uma variável só.
""")

    nb.operacao(
        "pd.crosstab",
        "pd.crosstab(coluna_das_linhas, coluna_das_colunas, margins=True)",
        "https://pandas.pydata.org/docs/reference/api/pandas.crosstab.html",
    )

    nb.code('''
pd.crosstab(
    penas["regime_inicial"],
    penas["houve_reincidencia"],
    margins=True,
    margins_name="total",
)
''')

    nb.md("""
Todos os números da aula estão aí: 83 é a conjunta de fechado com reincidente,
135 é a marginal dos reincidentes e 333 é o total.
""")

    nb.volta()

    # ---------------------------------------------------------- condicional
    nb.secao("condicional", "Probabilidade condicional", """
Condicionar é trocar o denominador: em vez de dividir pelos 333, dividimos só
pelo grupo que interessa. No pandas isso é **filtrar e recontar**.
""")

    nb.code('''
# Só os reincidentes. Depois do filtro, o total já é outro.
so_reincidentes = penas.query("houve_reincidencia == True")

len(so_reincidentes)
''')

    nb.code('''
# P(fechado | reincidente): a mesma média de antes, dentro do filtro
(so_reincidentes["regime_inicial"] == "fechado").mean()
''')

    nb.md("""
Compare com $P(\\text{fechado}) = 0{,}456$ na base inteira. Saber que o réu é
reincidente mudou o número, e é isso que significa dizer que as duas variáveis
têm relação.
""")

    nb.faca(
        "Agora o outro lado: $P(\\text{fechado} \\mid \\text{NÃO reincidente})$. "
        "Troque o filtro e refaça a média.",
        '''
so_primarios = penas.query("houve_reincidencia == False")

(so_primarios["regime_inicial"] == "fechado").mean()
''',
        '''
so_primarios = penas.query("houve_reincidencia == ________")

(so_primarios["regime_inicial"] == "________").mean()
''',
    )

    nb.md("""
✔️ **Um atalho.** `normalize="columns"` faz o crosstab dividir cada coluna pelo
próprio total, que é a mesma conta condicional de uma vez só.
""")

    nb.code('''
pd.crosstab(
    penas["regime_inicial"],
    penas["houve_reincidencia"],
    normalize="columns",
).round(3)
''')

    nb.md("""
⚠️ **Cuidado com o `normalize`.** `"columns"` divide por coluna, `"index"`
divide por linha e `"all"` divide pelo total geral. As três dão números
diferentes e respondem a perguntas diferentes. Errar aqui é o mesmo erro de
dividir por 333 em vez de 135.
""")

    nb.volta()

    # ------------------------------------------------------- independencia
    nb.secao("independencia", "Independência: o teste", """
Se dois eventos fossem independentes, a probabilidade dos dois juntos seria o
produto das duas. O teste é comparar esse produto com o que a base tem de
verdade.
""")

    nb.code('''
p_fechado = fechado.mean()
p_reincidente = reincidente.mean()

# O que a independência preveria, em número de acórdãos
esperado = p_fechado * p_reincidente * len(penas)

round(esperado, 1)
''')

    nb.code('''
# O que a base tem de verdade
observado = (fechado & reincidente).sum()

observado
''')

    nb.md("""
Cerca de 62 contra 83. A diferença é o tamanho da relação entre reincidência e
regime fechado: 21 acórdãos que a independência não explica.

Na aula 17 vamos aprender a decidir se uma diferença dessas é grande o
bastante para não ser acaso. Por enquanto basta saber olhar para ela.
""")

    nb.exercicio(1, "ex1", """
Refaça a comparação para o par **regime aberto** e **reincidência**.

1. calcule $P(\\text{aberto})$ e $P(\\text{aberto} \\mid \\text{reincidente})$;
2. calcule quantos acórdãos a independência preveria e compare com o observado;
3. em uma frase: a relação vai na mesma direção da de regime fechado, ou na
   direção contrária?
""")

    nb.code('''
aberto = penas["regime_inicial"] == "aberto"

print("P(aberto)              =", round(aberto.mean(), 3))
print("P(aberto | reincidente) =",
      round((so_reincidentes["regime_inicial"] == "aberto").mean(), 3))
print("esperado sob independência =",
      round(aberto.mean() * p_reincidente * len(penas), 1))
print("observado                  =", (aberto & reincidente).sum())
''', '''
aberto = penas["regime_inicial"] == "________"

print("P(aberto)              =", round(aberto.________(), 3))
print("P(aberto | reincidente) =",
      round((so_reincidentes["regime_inicial"] == "________").mean(), 3))
print("esperado sob independência =",
      round(aberto.mean() * ________ * len(penas), 1))
print("observado                  =", (aberto & ________).sum())
''')

    nb.volta()

    nb.resumo("""
| ideia | no pandas |
|---|---|
| $P(A)$ | média de uma coluna booleana |
| tabela de dupla entrada (conjunta e marginais) | `pd.crosstab(a, b, margins=True)` |
| $P(A \\mid B)$ | `.query()` no B, e a média de A dentro do filtro |
| todas as condicionais de uma vez | `pd.crosstab(a, b, normalize="columns")` |
| independência | comparar $P(A) \\times P(B) \\times n$ com o observado |

**A frase para levar:** condicionar é trocar o denominador. Todo erro de
probabilidade que vimos hoje, inclusive os que prenderam gente inocente, é
alguma versão de dividir pelo número errado.
""")

    nb.volta()
    return nb


# ====================================================== AULA 8


def montar_aula08() -> Caderno:
    nb = Caderno("aula08")

    nb.cabecalho(
        "Distribuições de probabilidade",
        "Aula 08",
        [
            "reconhecer qual distribuição descreve um fenômeno jurídico a partir "
            "do enunciado;",
            "calcular probabilidades com a binomial e com a Poisson no scipy;",
            "distinguir contagem (discreta) de tempo de espera (contínua);",
            "ler um histograma da base como uma distribuição observada.",
        ],
        abertura="""
Curto, como o de terça. A escolha da distribuição foi feita na lousa; aqui você
confere as contas e vê o formato de cada uma.
""",
    )

    nb.indice([
        ("O que muda de ontem para hoje", "ideia"),
        ("Contar sucessos: a binomial", "binomial"),
        ("Contar chegadas: a Poisson", "poisson"),
        ("Esperar: a exponencial", "exponencial"),
        ("A distribuição que a base mostra", "base"),
        ("RESUMO", "resumo"),
    ])

    # --------------------------------------------------------------- ideia
    nb.secao("ideia", "O que muda de ontem para hoje", """
Na terça calculamos a probabilidade de **um** evento por vez. Uma distribuição
responde de uma vez só para **todos** os resultados possíveis: qual a chance de
0, de 1, de 2, de 3, e assim por diante.

O `scipy.stats` tem uma função por distribuição, e todas se usam do mesmo jeito.
""")

    nb.code('''
import numpy as np
import pandas as pd
from plotnine import *
from scipy import stats

pd.set_option("display.max_columns", 30)
''')

    nb.md("""
✔️ **O padrão do scipy**, igual para todas as distribuições:

| método | o que devolve |
|---|---|
| `.pmf(k)` | chance de sair **exatamente** k (só nas discretas) |
| `.pdf(x)` | altura da curva em x (só nas contínuas) |
| `.cdf(k)` | chance de sair **k ou menos** |
| `.rvs(n)` | sorteia n valores |
""")

    nb.volta()

    # ------------------------------------------------------------ binomial
    nb.secao("binomial", "Contar sucessos: a binomial", """
**O escritório vai interpor 10 recursos. Cada um tem 30% de chance de ser
provido, e um não interfere no outro. Quantos serão providos?**

Número fixo de tentativas, mesma chance em cada uma, independentes: binomial.
""")

    nb.code('''
n, p = 10, 0.30

# A chance de exatamente 3 serem providos
stats.binom.pmf(3, n, p)
''')

    nb.code('''
# A distribuição inteira, de 0 a 10
quantos = np.arange(0, n + 1)

dist = pd.DataFrame({
    "providos": quantos,
    "chance": stats.binom.pmf(quantos, n, p),
})

dist.round(4)
''')

    nb.code('''
(
    ggplot(dist)
    + aes(x="providos", y="chance")
    + geom_col(fill="#3ACC9F")
    + scale_x_continuous(breaks=quantos)
    + labs(x="recursos providos em 10", y="probabilidade",
           title="Binomial com n = 10 e p = 0,30")
    + theme_minimal()
)
''')

    nb.md("""
O pico está em 3, que é $10 \\times 0{,}30$. Mas repare no resto: sair 1 ou sair
5 é perfeitamente possível. **Um resultado longe da média não é prova de que a
chance estava errada.**
""")

    nb.faca(
        'A pergunta do enunciado era "pelo menos 4". Como `.cdf(3)` dá a chance '
        "de 3 ou menos, a chance de 4 ou mais é o complementar.",
        '''
1 - stats.binom.cdf(3, n, p)
''',
        '''
1 - stats.binom.cdf(________, n, p)
''',
    )

    nb.volta()

    # ------------------------------------------------------------- poisson
    nb.secao("poisson", "Contar chegadas: a Poisson", """
**Uma vara recebe em média 7 processos novos por dia útil. Qual a chance de
chegarem mais de 15 num dia?**

Aqui não existem "10 tentativas": poderiam chegar 40. Contagem num intervalo de
tempo, sem teto natural, é Poisson. O único parâmetro é a média, $\\lambda$.
""")

    nb.code('''
lam = 7

# Mais de 15 é o complementar de "15 ou menos"
1 - stats.poisson.cdf(15, lam)
''')

    nb.code('''
chegadas = np.arange(0, 21)

poisson = pd.DataFrame({
    "processos": chegadas,
    "chance": stats.poisson.pmf(chegadas, lam),
})

(
    ggplot(poisson)
    + aes(x="processos", y="chance")
    + geom_col(fill="#730D9F")
    + labs(x="processos que chegam num dia", y="probabilidade",
           title="Poisson com média 7")
    + theme_minimal()
)
''')

    nb.md("""
Menos de 1% dos dias teriam mais de 15 chegadas. Isso é o que permite
dimensionar equipe: não pelo dia médio, e sim pelo dia ruim.
""")

    nb.volta()

    # --------------------------------------------------------- exponencial
    nb.secao("exponencial", "Esperar: a exponencial", """
**Quanto tempo entre a distribuição do recurso e o julgamento?**

Tempo não é contagem: pode ser 2,4 anos. É uma variável contínua, sempre
positiva, com muitos casos rápidos e uma minoria muito lenta. Esse formato é o
da exponencial.

Aqui vamos usar dados de verdade, e comparar o modelo com eles.
""")

    nb.code('''
# A base de câmaras, a mesma do Projeto 2. A coluna `tempo` traz os anos
# entre a distribuição do recurso e o julgamento.
CAMARAS = "https://jtrecenti.github.io/cdad2-202662/_shared/dados/camaras.csv"

camaras = pd.read_csv(CAMARAS)
tempo = camaras["tempo"].dropna()

tempo.describe().round(2)
''')

    nb.code('''
media = tempo.mean()

# A chance de o recurso passar de 5 anos, pelo modelo exponencial
1 - stats.expon.cdf(5, scale=media)
''')

    nb.md("""
E na base de verdade, quantos passaram de 5 anos?
""")

    nb.code('''
(tempo > 5).mean()
''')

    nb.md("""
Os dois números ficam próximos, mas não iguais. **A exponencial é um modelo do
formato, não uma cópia da base**: nenhum recurso é julgado no dia seguinte, e a
exponencial acha que isso seria o mais comum de todos.
""")

    nb.code('''
grade = np.linspace(0, tempo.max(), 300)

curva = pd.DataFrame({
    "anos": grade,
    "densidade": stats.expon.pdf(grade, scale=media),
})

(
    ggplot()
    + geom_histogram(aes(x="tempo", y="after_stat(density)"),
                     data=camaras.dropna(subset=["tempo"]),
                     bins=40, fill="#C9CCD2", color="white")
    + geom_line(aes(x="anos", y="densidade"), data=curva,
                color="#E50505", size=1.2)
    + labs(x="anos entre a distribuição e o julgamento", y="densidade",
           title="O que a base tem, e o modelo por cima")
    + theme_minimal()
)
''')

    nb.md("""
⚠️ **A altura da curva não é probabilidade.** Numa contínua, a chance de dar
*exatamente* 365,0 dias é zero: o que tem probabilidade é um intervalo, e ela é
a área embaixo da curva. Por isso a contínua usa `.pdf` e não `.pmf`, e por
isso a pergunta é sempre "mais que", "menos que" ou "entre".
""")

    nb.volta()

    # ---------------------------------------------------------------- base
    nb.secao("base", "A distribuição que a base mostra", """
Até aqui foram distribuições teóricas. A base também tem distribuições, e elas
são o histograma da aula 6.
""")

    nb.code(f'''
URL = "{URL}"

criminal = pd.read_csv(f"{{URL}}/tjsp_cjsg_criminal.csv")
penas = criminal.dropna(subset=["pena_anos"]).query("pena_anos <= 30")

(
    ggplot(penas)
    + aes(x="pena_anos")
    + geom_histogram(bins=25, fill="#F89D49", color="white")
    + labs(x="pena em anos", y="acórdãos",
           title="A distribuição observada das penas")
    + theme_minimal()
)
''')

    nb.exercicio(1, "ex1", """
Olhe o histograma e responda em uma frase cada:

1. essa distribuição parece mais com qual das que vimos hoje: a simétrica em
   torno da média, ou a de cauda longa para a direita?
2. a média é maior ou menor que o valor mais comum? Confira com
   `penas["pena_anos"].mean()` e `.mode()`.
3. por que usar a média da pena como "a pena típica" pode enganar num relatório?
""")

    nb.code('''
print("média :", round(penas["pena_anos"].mean(), 2))
print("mediana:", round(penas["pena_anos"].median(), 2))
print("moda   :", penas["pena_anos"].mode().iloc[0])
''')

    nb.volta()

    nb.resumo("""
| a pergunta do caso | distribuição | no scipy |
|---|---|---|
| deu certo ou não, uma vez só | Bernoulli | `stats.bernoulli` |
| quantos deram certo em n tentativas | binomial | `stats.binom` |
| quantos aconteceram no período | Poisson | `stats.poisson` |
| quantas tentativas até o primeiro | geométrica | `stats.geom` |
| quanto tempo até acontecer | exponencial | `stats.expon` |
| medida que se acumula em torno de um centro | normal | `stats.norm` |

**A frase para levar:** a distribuição não vem dos dados, vem do enunciado. Quem
escolhe é a pergunta: contagem com teto, contagem sem teto, ou tempo de espera.
""")

    nb.volta()
    return nb


# ====================================================== AULA 9


def montar_aula09() -> Caderno:
    nb = Caderno("aula09")

    nb.cabecalho(
        "Da amostra para a população",
        "Aula 09",
        [
            "separar parâmetro, estimador e estimativa num enunciado;",
            "simular o que acontece quando se sorteia uma amostra muitas vezes;",
            "reconhecer o teorema central do limite no resultado da simulação;",
            "calcular e interpretar um intervalo de confiança sem dizer o que ele "
            "não diz.",
        ],
        abertura="""
Este notebook faz uma coisa que a lousa não faz: repete o sorteio dez mil vezes.
É essa repetição que torna visível a ideia central da aula.
""",
    )

    nb.indice([
        ("Três palavras que não são sinônimos", "palavras"),
        ("O sorteio, uma vez", "uma"),
        ("O sorteio, dez mil vezes", "muitas"),
        ("O intervalo de confiança", "intervalo"),
        ("O que o intervalo NÃO diz", "cuidado"),
        ("RESUMO", "resumo"),
    ])

    # ------------------------------------------------------------ palavras
    nb.secao("palavras", "Três palavras que não são sinônimos", """
| palavra | o que é | neste caso |
|---|---|---|
| **parâmetro** | o número da população, fixo e desconhecido | a proporção de regime fechado em todos os acórdãos do TJSP |
| **estimador** | a receita de cálculo | "a proporção na amostra" |
| **estimativa** | o número que saiu desta amostra | 0,456 |

A estatística inteira é a tentativa de falar do primeiro tendo só o terceiro.
""")

    nb.code(ABERTURA_CRIMINAL)

    nb.md("""
Para hoje vamos fingir que a nossa base de 333 acórdãos **é** a população
inteira. Assim conhecemos o parâmetro, o que na vida real nunca acontece, e
podemos conferir se o método funciona.
""")

    nb.code('''
import numpy as np
from plotnine import *

fechado = penas["regime_inicial"] == "fechado"

# O parâmetro. Na vida real este número não existe para você.
parametro = fechado.mean()

round(parametro, 4)
''')

    nb.volta()

    # ----------------------------------------------------------------- uma
    nb.secao("uma", "O sorteio, uma vez", """
Sorteamos 50 acórdãos e calculamos a proporção só neles.
""")

    nb.code('''
amostra = penas.sample(50, random_state=1)

(amostra["regime_inicial"] == "fechado").mean()
''')

    nb.faca(
        "Troque o `random_state` por outro número e rode de novo. Depois mais uma "
        "vez. O que acontece com a estimativa?",
        '''
amostra = penas.sample(50, random_state=7)

(amostra["regime_inicial"] == "fechado").mean()
''',
        '''
amostra = penas.sample(50, random_state=________)

(amostra["regime_inicial"] == "fechado").mean()
''',
    )

    nb.md("""
Cada sorteio dá um número diferente, e nenhum deles é o parâmetro. **A
estimativa é uma variável aleatória**: ela tem distribuição, como tudo que
vimos na quinta-feira.
""")

    nb.volta()

    # -------------------------------------------------------------- muitas
    nb.secao("muitas", "O sorteio, dez mil vezes", """
Se a estimativa tem distribuição, vamos olhar para ela. Sorteamos dez mil
amostras de 50 e guardamos a proporção de cada uma.
""")

    nb.code('''
estimativas = [
    (penas.sample(50, random_state=i)["regime_inicial"] == "fechado").mean()
    for i in range(10_000)
]

simulacao = pd.DataFrame({"estimativa": estimativas})

simulacao["estimativa"].describe().round(4)
''')

    nb.code('''
(
    ggplot(simulacao)
    + aes(x="estimativa")
    + geom_histogram(bins=30, fill="#3ACC9F", color="white")
    + geom_vline(xintercept=parametro, color="#E50505", size=1.2)
    + labs(x="proporção de regime fechado em amostras de 50",
           y="quantas amostras",
           title="A distribuição da estimativa (a linha vermelha é o parâmetro)")
    + theme_minimal()
)
''')

    nb.md("""
Três coisas para reparar, e são as três ideias da aula:

1. o monte está **centrado no parâmetro**: em média a estimativa acerta;
2. o formato é de **sino**, mesmo a variável original sendo só sim ou não. Isso
   é o teorema central do limite;
3. a **largura** do monte é o erro que se corre ao usar uma amostra só.
""")

    nb.faca(
        "Refaça com amostras de 200 em vez de 50 e compare o desvio-padrão das "
        "estimativas. Quadruplicar a amostra divide a largura por quanto?",
        '''
maiores = [
    (penas.sample(200, random_state=i)["regime_inicial"] == "fechado").mean()
    for i in range(10_000)
]

print("com  50:", round(np.std(estimativas), 4))
print("com 200:", round(np.std(maiores), 4))
''',
        '''
maiores = [
    (penas.sample(________, random_state=i)["regime_inicial"] == "fechado").mean()
    for i in range(10_000)
]

print("com  50:", round(np.std(estimativas), 4))
print("com 200:", round(np.std(________), 4))
''',
    )

    nb.volta()

    # ------------------------------------------------------------ intervalo
    nb.secao("intervalo", "O intervalo de confiança", """
Na vida real você tem **uma** amostra, e não dez mil. O intervalo de confiança
é o jeito de carregar a largura daquele monte junto com a estimativa.
""")

    nb.code('''
amostra = penas.sample(50, random_state=1)
p_chapeu = (amostra["regime_inicial"] == "fechado").mean()
n = len(amostra)

# O erro-padrão: a largura do monte, estimada a partir da própria amostra
erro_padrao = np.sqrt(p_chapeu * (1 - p_chapeu) / n)

# 1,96 é o que cobre 95% de uma normal
margem = 1.96 * erro_padrao

print("estimativa:", round(p_chapeu, 3))
print("intervalo :", round(p_chapeu - margem, 3), "a", round(p_chapeu + margem, 3))
print("parâmetro :", round(parametro, 3))
''')

    nb.md("""
Repare no $\\sqrt{n}$ na conta do erro-padrão. É dele que vem a regra da aula:
para estreitar o intervalo pela metade, é preciso **quatro vezes** mais
amostra. É por isso que pesquisa eleitoral para de crescer em 2.000
entrevistados.
""")

    nb.volta()

    # -------------------------------------------------------------- cuidado
    nb.secao("cuidado", "O que o intervalo NÃO diz", """
A leitura errada é dizer que "há 95% de chance de o parâmetro estar neste
intervalo". O parâmetro é fixo: ou está, ou não está.

Os 95% são uma propriedade do **método**. Vamos verificar isso construindo mil
intervalos e contando quantos pegaram o parâmetro.
""")

    nb.code('''
pegou = 0
for i in range(1_000):
    a = penas.sample(50, random_state=i)
    p = (a["regime_inicial"] == "fechado").mean()
    m = 1.96 * np.sqrt(p * (1 - p) / len(a))
    if p - m <= parametro <= p + m:
        pegou += 1

print(f"{pegou} de 1.000 intervalos contêm o parâmetro "
      f"({pegou / 10:.1f}%)")
''')

    nb.md("""
Perto de 95%. **Esse** é o sentido da confiança: se você repetisse o
procedimento a vida inteira, erraria em cerca de 5% das vezes.

Da amostra que você tem na mão, você não sabe se ela é uma das 95 ou uma das 5.
""")

    nb.exercicio(1, "ex1", """
Um relatório afirma: *"analisamos 400 sentenças e 62% foram procedentes, com
intervalo de confiança de 57% a 67%"*. Escreva, em uma frase cada:

1. qual é o parâmetro, qual é a estimativa;
2. uma leitura **correta** do intervalo, para colocar no relatório;
3. o que muda se as 400 sentenças não tiverem sido sorteadas, e sim escolhidas
   entre as que o escritório já tinha em pasta.
""")

    nb.md("""
💡 A terceira pergunta é a mais importante do dia. Todo este notebook depende de
`.sample()`, que sorteia. Amostra que não foi sorteada não tem intervalo de
confiança que a salve: o erro deixa de ser aleatório e vira viés, e viés não
diminui com mais dados.
""")

    nb.volta()

    nb.resumo("""
| ideia | o que fizemos |
|---|---|
| parâmetro | o número da população, fixo e desconhecido |
| estimativa | o que saiu desta amostra, e que muda a cada sorteio |
| distribuição da estimativa | dez mil sorteios, e o histograma deles |
| teorema central do limite | o histograma vira sino, mesmo com variável de sim ou não |
| erro-padrão | $\\sqrt{p(1-p)/n}$: a largura daquele histograma |
| intervalo de 95% | estimativa $\\pm$ 1,96 erros-padrão |

**A frase para levar:** o intervalo de confiança é uma declaração sobre o
método, não sobre este intervalo. E ele só vale se a amostra foi sorteada.
""")

    nb.volta()
    return nb


# ====================================================== main


def main() -> None:
    for construir in (montar_aula07, montar_aula08, montar_aula09):
        caderno = construir()
        print(f"{caderno.nome}:")
        caderno.gravar()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
