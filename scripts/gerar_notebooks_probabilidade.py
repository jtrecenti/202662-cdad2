"""Notebooks das aulas 7 a 11 (probabilidade, variáveis aleatórias e inferência).

Sai daqui:
    notebooks/aula07_professor.ipynb   probabilidade condicional e independência
    notebooks/aula07_aluno.ipynb
    notebooks/aula08_professor.ipynb   condicional, independência e Bayes
    notebooks/aula08_aluno.ipynb
    notebooks/aula09_professor.ipynb   variável aleatória discreta, esperança e risco
    notebooks/aula09_aluno.ipynb
    notebooks/aula10_professor.ipynb   catálogo de distribuições
    notebooks/aula10_aluno.ipynb
    notebooks/aula11_professor.ipynb   amostra, TCL e intervalo de confiança
    notebooks/aula11_aluno.ipynb

Estes são propositalmente CURTOS, na casa de vinte células, e não os
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
            "montar a tabela de dupla entrada e separar conjunta de marginal;",
            "calcular uma probabilidade condicional filtrando e recontando;",
            "verificar independência comparando o observado com o esperado;",
            "aplicar o teorema de Bayes para inverter uma condicional.",
        ],
        abertura="""
Este notebook é curto de propósito. Tudo que está aqui já foi feito na lousa
hoje.

Uma diferença em relação ao slide: lá a tabela de 400 sentenças era
**ilustrativa**, com números escolhidos para fechar de cabeça. Aqui a base é
**real**, e por isso as divisões não dão números redondos. É assim que a conta
aparece na vida.
""",
    )

    nb.indice([
        ("A base de hoje", "dados"),
        ("Probabilidade é uma proporção", "proporcao"),
        ("A tabela de dupla entrada", "tabela"),
        ("Probabilidade condicional", "condicional"),
        ("Independência: o teste", "independencia"),
        ("Teorema de Bayes", "bayes"),
        ("RESUMO", "resumo"),
    ])

    # ---------------------------------------------------------------- base
    nb.secao("dados", "A base de hoje", """
Acórdãos do TJSP em ações contra planos de saúde. Uma linha por acórdão.
""")
    nb.code(f'''
import pandas as pd

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)

URL = "{URL}"

saude = pd.read_csv(f"{{URL}}/tjsp_cjsg_plano_saude.csv")

saude.shape
''')

    nb.md("""
Duas colunas de sim ou não interessam hoje:

- `tem_dano_moral`: o acórdão reconheceu dano moral;
- `houve_majoracao`: o valor da indenização foi majorado.
""")
    nb.code('saude[["tem_dano_moral", "houve_majoracao"]].head()')

    nb.volta()

    # ----------------------------------------------------------- proporcao
    nb.secao("proporcao", "Probabilidade é uma proporção", """
$P(A)$ é o número de casos em $A$ dividido pelo total. No pandas, uma coluna de
`True` e `False` já sabe fazer essa conta: a média de uma coluna booleana **é**
a proporção de `True`.
""")

    nb.code('''
dano = saude["tem_dano_moral"]

dano.mean()
''')

    nb.md("""
Por que a média funciona: `True` vale 1 e `False` vale 0, então somar a coluna
conta os casos e dividir pelo tamanho dá a proporção.
""")

    nb.faca(
        "Calcule $P(\\text{houve majoração})$. Mesma ideia, outra coluna.",
        '''
majorou = saude["houve_majoracao"]

majorou.mean()
''',
        '''
majorou = saude["________"]

majorou.________()
''',
    )

    nb.volta()

    # -------------------------------------------------------------- tabela
    nb.secao("tabela", "A tabela de dupla entrada", """
`pd.crosstab` cruza duas colunas e conta quantos casos caem em cada combinação.

Os dois nomes da aula aparecem aqui:

- o **miolo** é a distribuição **conjunta**, e cada célula responde por duas
  variáveis ao mesmo tempo;
- a última linha e a última coluna são as **marginais**, e cada valor delas
  responde por uma variável só.
""")

    nb.operacao(
        "pd.crosstab",
        "pd.crosstab(coluna_das_linhas, coluna_das_colunas, margins=True)",
        "https://pandas.pydata.org/docs/reference/api/pandas.crosstab.html",
    )

    nb.code('''
pd.crosstab(
    saude["tem_dano_moral"],
    saude["houve_majoracao"],
    margins=True,
    margins_name="total",
)
''')

    nb.md("""
✔️ **A mesma tabela em proporções.** `normalize="all"` divide tudo pelo total
geral, e é a versão do slide em que o canto vale 1.
""")

    nb.code('''
pd.crosstab(
    saude["tem_dano_moral"],
    saude["houve_majoracao"],
    margins=True,
    margins_name="total",
    normalize="all",
).round(3)
''')

    nb.volta()

    # ---------------------------------------------------------- condicional
    nb.secao("condicional", "Probabilidade condicional", """
Condicionar é trocar o denominador: em vez de dividir pelo total, dividimos só
pelo grupo que interessa. No pandas isso é **filtrar e recontar**.
""")

    nb.code('''
# Só os acórdãos que reconheceram dano moral
com_dano = saude.query("tem_dano_moral")

len(com_dano)
''')

    nb.code('''
# P(majoração | tem dano moral)
com_dano["houve_majoracao"].mean()
''')

    nb.md("""
Compare com a proporção de majoração na base inteira. Saber que houve dano
moral **muda** o número, e é isso que significa dizer que as duas variáveis têm
relação.
""")

    nb.faca(
        "Agora o outro lado: $P(\\text{majoração} \\mid \\text{sem dano moral})$.",
        '''
sem_dano = saude.query("~tem_dano_moral")

sem_dano["houve_majoracao"].mean()
''',
        '''
sem_dano = saude.query("~________")

sem_dano["________"].mean()
''',
    )

    nb.md("""
⚠️ **Cuidado com o `normalize`.** `"index"` divide por linha, `"columns"` por
coluna e `"all"` pelo total. As três dão números diferentes e respondem a
perguntas diferentes. Errar aqui é o mesmo erro de dividir pelo total em vez de
pelo grupo.
""")

    nb.code('''
pd.crosstab(
    saude["tem_dano_moral"],
    saude["houve_majoracao"],
    normalize="index",
).round(3)
''')

    nb.volta()

    # ------------------------------------------------------- independencia
    nb.secao("independencia", "Independência: o teste", """
Se dois eventos fossem independentes, a probabilidade dos dois juntos seria o
produto das marginais. O teste é comparar esse produto com o que a base tem.
""")

    nb.code('''
esperado = dano.mean() * majorou.mean() * len(saude)
observado = (dano & majorou).sum()

print("esperado sob independência:", round(esperado, 1))
print("observado                 :", observado)
''')

    nb.md("""
Cerca de 15 contra 21. A diferença é o tamanho da associação entre reconhecer
dano moral e majorar o valor.

Na aula 17 vamos aprender a decidir se uma diferença dessas é grande o bastante
para não ser acaso. Aqui, com números pequenos, a cautela é ainda maior.
""")

    nb.volta()

    # --------------------------------------------------------------- bayes
    nb.secao("bayes", "Teorema de Bayes", """
Bayes inverte a condicional:

$$P(A \\mid B) = \\frac{P(B \\mid A)\\,P(A)}{P(B)}$$

Vamos conferir que ele bate com a conta direta.
""")

    nb.code('''
p_dano = dano.mean()
p_maj = majorou.mean()
p_maj_dado_dano = com_dano["houve_majoracao"].mean()

# Bayes: P(dano | majorou)
bayes = p_maj_dado_dano * p_dano / p_maj

# a conta direta, filtrando
direto = saude.query("houve_majoracao")["tem_dano_moral"].mean()

print("por Bayes :", round(bayes, 4))
print("direto    :", round(direto, 4))
''')

    nb.md("""
Os dois dão o mesmo número, e é assim que tem que ser: Bayes não é uma conta
nova, é a regra do produto escrita de outro jeito.

Ele importa quando você **não tem a base inteira** para filtrar, e só conhece
$P(B \\mid A)$ e as marginais. É a situação da perícia: o laudo informa a
taxa de erro do exame, e ninguém tem a tabela do lote inteiro.
""")

    nb.exercicio(1, "ex1", """
A perícia grafotécnica da aula, agora em código.

Dois eventos, e só eles:

- $F$: a assinatura do contrato **é falsa**;
- $A$: a perícia **aponta** falsidade nesse contrato.

O enunciado da lousa dá três números:

- $P(F) = 0{,}01$, porque 1 em cada 100 contratos do lote tem assinatura falsa;
- $P(A \\mid F) = 0{,}99$, porque **entre os contratos falsos** a perícia aponta
  em 99% das vezes;
- $P(A \\mid F^c) = 0{,}01$, porque **entre os autênticos** ela aponta em 1% das
  vezes, por variação natural da assinatura.

E pede $P(F \\mid A)$: a perícia apontou este contrato, qual a probabilidade de
a assinatura ser mesmo falsa. É a inversão.

1. escreva os três números como variáveis;
2. calcule $P(A)$ pela lei da probabilidade total;
3. calcule $P(F \\mid A)$ por Bayes, e confira com os 50% da lousa;
4. refaça com $P(F) = 0{,}50$, como se a perícia só fosse pedida em contratos já
   sob suspeita. O que acontece com a resposta?
""")

    nb.code('''
def p_falso_dado_apontado(p_falso,
                          p_aponta_dado_falso=0.99,
                          p_aponta_dado_autentico=0.01):
    # lei da probabilidade total: os apontados saem dos falsos e dos autênticos
    p_aponta = (p_aponta_dado_falso * p_falso
                + p_aponta_dado_autentico * (1 - p_falso))
    # Bayes
    return p_aponta_dado_falso * p_falso / p_aponta

for antes in (0.01, 0.10, 0.50):
    print(f"P(F) = {antes:.0%}  ->  P(F | A) = {p_falso_dado_apontado(antes):.1%}")
''', '''
def p_falso_dado_apontado(p_falso,
                          p_aponta_dado_falso=0.99,
                          p_aponta_dado_autentico=0.01):
    # lei da probabilidade total: os apontados saem dos falsos e dos autênticos
    p_aponta = (p_aponta_dado_falso * p_falso
                + ________ * (1 - p_falso))
    # Bayes
    return p_aponta_dado_falso * p_falso / ________

for antes in (0.01, 0.10, 0.50):
    print(f"P(F) = {antes:.0%}  ->  P(F | A) = {p_falso_dado_apontado(antes):.1%}")
''')

    nb.md("""
💡 A perícia é a mesma nas três linhas, e o laudo diria exatamente a mesma
coisa. O que muda é **em que lote ela foi aplicada**. Por isso periciar o lote
inteiro e periciar só os contratos já sob suspeita são decisões diferentes, com
o mesmo perito e o mesmo equipamento.
""")

    nb.volta()

    nb.resumo("""
| ideia | no pandas |
|---|---|
| $P(A)$ | média de uma coluna booleana |
| tabela de dupla entrada | `pd.crosstab(a, b, margins=True)` |
| a mesma tabela em proporções | `normalize="all"` |
| $P(A \\mid B)$ | `.query()` no B, e a média de A dentro do filtro |
| todas as condicionais de uma vez | `normalize="index"` ou `"columns"` |
| independência | comparar $P(A)P(B)n$ com o observado |
| Bayes | $P(B \\mid A)P(A)/P(B)$, com $P(B)$ pela marginal |

**A frase para levar:** condicionar é trocar o denominador, e Bayes é o que
permite trocar de volta.
""")

    nb.volta()
    return nb


# ====================================================== AULA 8


def montar_aula08() -> Caderno:
    nb = Caderno("aula08")

    nb.cabecalho(
        "Condicional, independência e Bayes",
        "Aula 08",
        [
            "montar a tabela de dupla entrada e ler condicionais nela;",
            "calcular uma condicional filtrando e recontando;",
            "testar independência comparando o observado com o esperado;",
            "inverter uma condicional com o teorema de Bayes.",
        ],
        abertura="""
Curto, como sempre. Tudo que está aqui já foi feito na lousa hoje.

Uma diferença em relação ao slide: lá a tabela dos 400 processos era
**ilustrativa**, com números escolhidos para fechar de cabeça. Aqui a base é
**real**, e por isso as divisões não dão números redondos. É assim que a conta
aparece na vida.
""",
    )

    nb.indice([
        ("A base de hoje", "dados"),
        ("A tabela de dupla entrada", "tabela"),
        ("Probabilidade condicional", "condicional"),
        ("Independência: o teste", "independencia"),
        ("Teorema de Bayes", "bayes"),
        ("Variável aleatória e esperança", "esperanca"),
        ("Discreta, contínua e o que é um modelo", "continua"),
        ("RESUMO", "resumo"),
    ])

    # --------------------------------------------------------------- dados
    nb.secao("dados", "A base de hoje", """
Acórdãos criminais do TJSP. Uma linha por acórdão.
""")

    nb.code(ABERTURA_CRIMINAL)

    nb.md("""
Duas informações interessam hoje:

- `houve_reincidencia`: o acórdão registrou reincidência;
- `regime_inicial`: fechado, semiaberto ou aberto.

O regime tem três valores, e a aula toda foi sobre eventos de sim ou não. Então
a primeira coisa é transformar "regime" no evento **"o regime é fechado"**.
""")

    nb.code('''
penas = penas.assign(fechado=penas["regime_inicial"] == "fechado")

penas[["houve_reincidencia", "regime_inicial", "fechado"]].head()
''')

    nb.volta()

    # -------------------------------------------------------------- tabela
    nb.secao("tabela", "A tabela de dupla entrada", """
`pd.crosstab` cruza duas colunas e conta quantos casos caem em cada combinação.
É a mesma tabela do slide, agora com os números da base.

- o **miolo** é a distribuição **conjunta**;
- a última linha e a última coluna são as **marginais**.
""")

    nb.code('''
pd.crosstab(
    penas["houve_reincidencia"],
    penas["fechado"],
    margins=True,
    margins_name="total",
)
''')

    nb.md("""
✔️ **A mesma tabela em proporções.** `normalize="all"` divide tudo pelo total
geral, e é a versão em que o canto vale 1.
""")

    nb.code('''
pd.crosstab(
    penas["houve_reincidencia"],
    penas["fechado"],
    margins=True,
    margins_name="total",
    normalize="all",
).round(3)
''')

    nb.md("""
**✍️ Agora você.** Nessa tabela de proporções, aponte:

1. a **conjunta** de "reincidente e regime fechado";
2. a **marginal** de "regime fechado".
""")

    nb.md("""
**Interseção, união e marginal**, os três nomes do slide, saem todos daqui. No
pandas, `&` é "e", `|` é "ou", e a média de uma coluna de sim ou não é a
probabilidade dela.
""")

    nb.code('''
A = penas["fechado"]
B = penas["houve_reincidencia"]

print("P(A)        ", round(A.mean(), 4))            # marginal
print("P(B)        ", round(B.mean(), 4))            # marginal
print("P(A e B)    ", round((A & B).mean(), 4))      # interseção
print("P(A ou B)   ", round((A | B).mean(), 4))      # união
''')

    nb.md("""
**✍️ Agora você.** A união também sai da fórmula do slide:

$$P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$$

Confira que ela dá o mesmo número da conta direta acima.
""")

    nb.code('''
pela_formula = A.mean() + B.mean() - (A & B).mean()

print("pela fórmula:", round(pela_formula, 4))
print("direto      :", round((A | B).mean(), 4))
''', '''
pela_formula = A.mean() + B.mean() - ________

print("pela fórmula:", round(pela_formula, 4))
print("direto      :", round((A | B).mean(), 4))
''')

    nb.md("""
Se você tivesse somado só $P(A) + P(B)$, teria contado duas vezes quem tem as
duas coisas. Subtrair a interseção é exatamente o que devolve o canto contado a
mais.
""")

    nb.volta()

    # ---------------------------------------------------------- condicional
    nb.secao("condicional", "Probabilidade condicional", """
Condicionar é trocar o denominador: em vez de dividir pelo total, dividimos só
pelo grupo que interessa. No pandas isso é **filtrar e recontar**.

Comece pela probabilidade sem condicionar. A média de uma coluna booleana **é**
a proporção de `True`, porque `True` vale 1 e `False` vale 0.
""")

    nb.code('''
# P(fechado), sem condicionar
penas["fechado"].mean()
''')

    nb.code('''
# P(fechado | reincidente): filtra, e recalcula a média dentro do filtro
reincidentes = penas.query("houve_reincidencia")

reincidentes["fechado"].mean()
''')

    nb.md("""
**✍️ Agora você.** O outro lado:
$P(\\text{fechado} \\mid \\text{não reincidente})$.
""")

    nb.code('''
nao_reincidentes = penas.query("~houve_reincidencia")

nao_reincidentes["fechado"].mean()
''', '''
nao_reincidentes = penas.query("~houve_reincidencia")

nao_reincidentes["________"].mean()
''')

    nb.md("""
Três números: cerca de 0,46 sem condicionar, 0,61 entre reincidentes e 0,35
entre não reincidentes. **Saber sobre a reincidência muda a probabilidade**, e é
isso que significa dizer que as duas variáveis têm relação.

⚠️ **Cuidado com o `normalize`.** `"index"` divide por linha, `"columns"` por
coluna e `"all"` pelo total. As três dão números diferentes e respondem a
perguntas diferentes. Errar aqui é o mesmo erro de dividir pelo total em vez de
pelo grupo.
""")

    nb.code('''
# todas as condicionais de uma vez: cada linha soma 1
pd.crosstab(
    penas["houve_reincidencia"],
    penas["fechado"],
    normalize="index",
).round(3)
''')

    nb.volta()

    # ------------------------------------------------------- independencia
    nb.secao("independencia", "Independência: o teste", """
Se dois eventos fossem independentes, a probabilidade dos dois juntos seria o
produto das marginais. O teste é comparar esse produto com o que a base tem.
""")

    nb.code('''
esperado = penas["fechado"].mean() * penas["houve_reincidencia"].mean() * len(penas)
observado = (penas["fechado"] & penas["houve_reincidencia"]).sum()

print("esperado sob independência:", round(esperado, 1))
print("observado                 :", observado)
''')

    nb.md("""
Cerca de 62 contra 83. O observado é bem maior que o esperado, então os eventos
**não** são independentes.

💡 E, como na aula: isso é **associação**, não causa. Reincidência e regime
fechado andam juntos, e a lei explica boa parte disso. O número sozinho não diz
qual é a explicação.
""")

    nb.volta()

    # --------------------------------------------------------------- bayes
    nb.secao("bayes", "Teorema de Bayes", """
Bayes inverte a condicional:

$$P(A \\mid B) = \\frac{P(B \\mid A)\\,P(A)}{P(B)}$$

Com a base inteira na mão, dá para conferir que ele bate com a conta direta.
""")

    nb.code('''
p_reincidencia = penas["houve_reincidencia"].mean()
p_fechado = penas["fechado"].mean()
p_fechado_dado_reincidencia = reincidentes["fechado"].mean()

# Bayes: P(reincidente | fechado)
bayes = p_fechado_dado_reincidencia * p_reincidencia / p_fechado

# a conta direta, filtrando
direto = penas.query("fechado")["houve_reincidencia"].mean()

print("por Bayes :", round(bayes, 4))
print("direto    :", round(direto, 4))
''')

    nb.md("""
Os dois dão o mesmo número, e é assim que tem que ser: Bayes não é uma conta
nova, é a regra do produto escrita de outro jeito.

Repare que $P(\\text{fechado} \\mid \\text{reincidente}) \\approx 0,61$ e
$P(\\text{reincidente} \\mid \\text{fechado}) \\approx 0,55$ são **números
diferentes**. Trocar um pelo outro é o erro do promotor, e aqui a troca custaria
seis pontos percentuais.

Bayes importa quando você **não tem a base inteira** para filtrar, e só conhece
$P(B \\mid A)$ e as marginais. É a situação da perícia: o laudo informa a taxa
de erro do exame, e ninguém tem a tabela do lote inteiro.
""")

    nb.exercicio(1, "ex1", """
A perícia grafotécnica da aula, agora em código.

Dois eventos, e só eles:

- $F$: a assinatura do contrato **é falsa**;
- $A$: a perícia **aponta** falsidade nesse contrato.

O enunciado da lousa dá três números: $P(F) = 0{,}01$,
$P(A \\mid F) = 0{,}99$ e $P(A \\mid F^c) = 0{,}01$. E pede $P(F \\mid A)$.

1. calcule $P(A)$ pela lei da probabilidade total;
2. calcule $P(F \\mid A)$ por Bayes, e confira com os 50% da lousa;
3. refaça com $P(F) = 0{,}50$, como se a perícia só fosse pedida em contratos já
   sob suspeita. O que acontece com a resposta?
""")

    nb.code('''
def p_falso_dado_apontado(p_falso,
                          p_aponta_dado_falso=0.99,
                          p_aponta_dado_autentico=0.01):
    # lei da probabilidade total: os apontados saem dos falsos e dos autênticos
    p_aponta = (p_aponta_dado_falso * p_falso
                + p_aponta_dado_autentico * (1 - p_falso))
    # Bayes
    return p_aponta_dado_falso * p_falso / p_aponta

for antes in (0.01, 0.10, 0.50):
    print(f"P(F) = {antes:.0%}  ->  P(F | A) = {p_falso_dado_apontado(antes):.1%}")
''', '''
def p_falso_dado_apontado(p_falso,
                          p_aponta_dado_falso=0.99,
                          p_aponta_dado_autentico=0.01):
    # lei da probabilidade total: os apontados saem dos falsos e dos autênticos
    p_aponta = (p_aponta_dado_falso * p_falso
                + ________ * (1 - p_falso))
    # Bayes
    return p_aponta_dado_falso * p_falso / ________

for antes in (0.01, 0.10, 0.50):
    print(f"P(F) = {antes:.0%}  ->  P(F | A) = {p_falso_dado_apontado(antes):.1%}")
''')

    nb.md("""
💡 A perícia é a mesma nas três linhas, e o laudo diria exatamente a mesma
coisa. O que muda é **em que lote ela foi aplicada**.
""")

    nb.volta()

    # ----------------------------------------------------------- esperanca
    nb.secao("esperanca", "Variável aleatória e esperança", """
Uma **variável aleatória** é uma função que leva elementos do espaço amostral em
valores numéricos, e para cada valor sabemos atribuir uma probabilidade. Essa
lista de valores com as probabilidades deles é a **distribuição**.

No caso dos honorários de êxito, visto no fim da aula: duas audiências por dia,
20% de chance de acordo em cada uma, e R$ 500 por acordo fechado.

| $x$ | $P(X = x)$ |
|---|---|
| 0 | 0,64 |
| 500 | 0,32 |
| 1000 | 0,04 |

A **esperança** é a média dos valores possíveis, cada um pesado pela sua
probabilidade.
""")

    nb.code('''
import numpy as np

valores = np.array([0, 500, 1000])          # honorários do dia, em reais
probabilidades = np.array([0.64, 0.32, 0.04])

esperanca = (valores * probabilidades).sum()

print("as probabilidades somam:", probabilidades.sum())
print("honorário esperado por dia:", esperanca, "reais")
''')

    nb.md("""
200 reais **não é um resultado possível**: num dia ela ganha 0, 500 ou 1000. A
esperança é o que sai na média ao longo de muitos dias.

E a Bernoulli fecha o círculo: quando $X$ vale 1 ou 0, a esperança é $p$. Por
isso a média de uma coluna booleana, que usamos a aula inteira, **é** uma
esperança.
""")

    nb.code('''
# a media de uma coluna booleana E a esperanca de uma Bernoulli
penas["fechado"].mean()
''')

    nb.volta()

    # ------------------------------------------------------------ continua
    nb.secao("continua", "Discreta, contínua e o que é um modelo", """
`houve_reincidencia` é **discreta**: só assume 0 e 1, e a distribuição dela cabe
em duas linhas. É uma Bernoulli.

`pena_anos` é **contínua**: assume qualquer valor de um intervalo. Aqui
$P(X = 5{,}66)$ não faz sentido, e a pergunta que faz sentido é por **faixa**.
""")

    nb.code('''
penas_anos = criminal["pena_anos"].dropna()

print("quantos acórdãos informam pena:", len(penas_anos))
print("média  :", round(penas_anos.mean(), 2), "anos")
print("desvio :", round(penas_anos.std(), 2), "anos")
''')

    nb.md("""
**✍️ Agora você.** Calcule a probabilidade de a pena estar **entre 2 e 8 anos**.
A conta é a mesma de sempre: uma condição vira coluna de `True` e `False`, e a
média dela é a probabilidade.
""")

    nb.code('''
entre_2_e_8 = (penas_anos >= 2) & (penas_anos <= 8)

entre_2_e_8.mean()
''', '''
entre_2_e_8 = (penas_anos >= 2) & (penas_anos <= ________)

entre_2_e_8.________()
''')

    nb.md("""
### A pena é normal?

Na aula usamos a regra dos desvios: numa **normal**, cerca de 68% da área cai
entre $\\mu - \\sigma$ e $\\mu + \\sigma$, e cerca de 95% entre $\\mu - 2\\sigma$ e
$\\mu + 2\\sigma$.

Isso é uma afirmação **testável**. Vamos contar.
""")

    nb.code('''
media = penas_anos.mean()
desvio = penas_anos.std()

for k in (1, 2):
    dentro = ((penas_anos >= media - k * desvio)
              & (penas_anos <= media + k * desvio)).mean()
    esperado = {1: 0.68, 2: 0.95}[k]
    print(f"media +- {k} desvio: {dentro:.1%} dos casos   "
          f"(numa normal seria {esperado:.0%})")
''')

    nb.md("""
Não bate, e não é por pouco: **96% contra 68%**.

O motivo aparece no histograma. A pena é um valor que não pode ser negativo, se
acumula em poucos anos e tem uma cauda longa de penas altas. Isso a torna
fortemente assimétrica, e a normal é simétrica.
""")

    nb.code('''
from plotnine import ggplot, aes, geom_histogram, geom_vline, labs, theme_minimal

(
    ggplot(penas_anos.to_frame("pena_anos"))
    + aes(x="pena_anos")
    + geom_histogram(bins=40, fill="#12996f")
    + geom_vline(xintercept=media, color="#e50505", linetype="dashed")
    + labs(x="pena em anos", y="acórdãos",
           title="A média (linha vermelha) não fica no meio")
    + theme_minimal()
)
''')

    nb.md("""
💡 **E é isso que significa escolher um modelo.** Dizer "a pena é normal" seria
uma **suposição sobre a variável**, não um fato lido dos dados, e aqui ela seria
uma suposição ruim: a conta dos desvios já a desmente.

Na aula 9 vamos supor uma normal, mas não para a coluna: para a **média de uma
amostra**. E aí a suposição se sustenta, por um motivo que é o assunto da aula.
""")

    nb.volta()

    nb.resumo("""
| ideia | no pandas |
|---|---|
| $P(A)$ | média de uma coluna booleana |
| $P(A \\cap B)$ e $P(A \\cup B)$ | `(A & B).mean()` e `(A \| B).mean()` |
| tabela de dupla entrada | `pd.crosstab(a, b, margins=True)` |
| a mesma tabela em proporções | `normalize="all"` |
| $P(A \\mid B)$ | `.query()` no B, e a média de A dentro do filtro |
| todas as condicionais de uma vez | `normalize="index"` ou `"columns"` |
| independência | comparar $P(A)P(B)n$ com o observado |
| Bayes | $P(B \\mid A)P(A)/P(B)$, com $P(B)$ pela marginal |
| esperança | soma de valor vezes probabilidade |
| probabilidade por faixa | média de uma condição, como `(x >= 2) & (x <= 8)` |

**A frase para levar:** condicionar é trocar o denominador, e Bayes é o que
permite trocar de volta. E dizer que uma variável segue uma distribuição
conhecida é uma **suposição**, que dá para conferir nos dados.
""")

    nb.volta()
    return nb


# ====================================================== AULA 9


def montar_aula09() -> Caderno:
    nb = Caderno("aula09")

    nb.cabecalho(
        "A distribuição, a média e o risco",
        "Aula 09",
        [
            "montar a distribuição de uma variável aleatória discreta numa tabela;",
            "calcular esperança, variância e desvio padrão a partir dessa tabela;",
            "conferir no código o que somar um fixo e o que multiplicar fazem com "
            "a média e com o risco;",
            "decidir entre duas propostas usando os dois números, e não só a média.",
        ],
        abertura="""
Na lousa fizemos as contas do exemplo das audiências no braço. Aqui elas viram
três linhas de código, e é isso que libera espaço para a pergunta que importa:
o que muda quando a regra do jogo muda.
""",
    )

    nb.indice([
        ("A distribuição numa tabela", "distribuicao"),
        ("Esperança", "esperanca"),
        ("Variância e desvio padrão", "variancia"),
        ("As duas propostas", "propostas"),
        ("O caso do acordo", "acordo"),
        ("De onde vem uma distribuição de verdade", "real"),
        ("RESUMO", "resumo"),
    ])

    # ------------------------------------------------------- distribuicao
    nb.secao("distribuicao", "A distribuição numa tabela", """
O exemplo da aula: a advogada atende **duas audiências por dia**, cada acordo
rende **R$ 500**, e a chance de acordo em cada audiência é **0,20**.

A distribuição que montamos na lousa cabe num `DataFrame` de três linhas. A
coluna `x` traz os valores possíveis, e a coluna `p` a probabilidade de cada um.
""")

    nb.code('''
import pandas as pd

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)

X = pd.DataFrame({
    "x": [0, 500, 1000],
    "p": [0.64, 0.32, 0.04],
})

X
''')

    nb.md("""
A primeira conferência é sempre a mesma: **a coluna `p` soma 1?** Se não somar,
faltou um caminho da árvore ou sobrou um.
""")

    nb.code('''
X["p"].sum()
''')

    nb.faca(
        "De onde saiu o 0,32? Escreva a conta que produz a probabilidade de sair "
        "exatamente um acordo no dia, usando 0,20 e 0,80.",
        '''
# sai de dois caminhos: acordo na primeira e não na segunda, ou o contrário
0.20 * 0.80 + 0.80 * 0.20
''',
        '''
# sai de dois caminhos: acordo na primeira e não na segunda, ou o contrário
________ * ________ + ________ * ________
''',
    )

    nb.volta()

    # ---------------------------------------------------------- esperanca
    nb.secao("esperanca", "Esperança", """
$$E(X) = x_1 \\, P(X = x_1) + x_2 \\, P(X = x_2) + \\cdots + x_k \\, P(X = x_k)$$

Cada valor vezes a sua probabilidade, tudo somado. Em pandas isso é uma
multiplicação de colunas seguida de um `.sum()`.
""")

    nb.code('''
esperanca = (X["x"] * X["p"]).sum()

esperanca
''')

    nb.md("""
R$ 200. Vale repetir o que a lousa disse: **200 não é um valor possível**. Num
dia ela recebe 0, 500 ou 1.000, nunca 200. É o que entra em média ao longo de
muitos dias.
""")

    nb.faca(
        "Na atividade em duplas, o lucro da semana valia 2.600 com probabilidade "
        "0,16, 1.100 com 0,48 e −400 com 0,36. Monte a tabela e calcule a "
        "esperança. Confira que ela bate com os R$ 800 do quadro.",
        '''
L = pd.DataFrame({
    "x": [2600, 1100, -400],
    "p": [0.16, 0.48, 0.36],
})

print("soma das probabilidades:", L["p"].sum())
print("esperança:", (L["x"] * L["p"]).sum())
''',
        '''
L = pd.DataFrame({
    "x": [________, ________, ________],
    "p": [________, ________, ________],
})

print("soma das probabilidades:", L["p"].sum())
print("esperança:", (L["________"] * L["________"]).sum())
''',
    )

    nb.md("""
E a probabilidade de a semana dar prejuízo é a soma das probabilidades dos
valores negativos. Aqui só há um.
""")

    nb.code('''
L.loc[L["x"] < 0, "p"].sum()
''')

    nb.volta()

    # ---------------------------------------------------------- variancia
    nb.secao("variancia", "Variância e desvio padrão", """
$$Var(X) = [x_1 - E(X)]^2 \\, P(X = x_1) + \\cdots + [x_k - E(X)]^2 \\, P(X = x_k)$$

O desvio de cada valor até a esperança, ao quadrado, pesado pela probabilidade.
""")

    nb.code('''
variancia = (((X["x"] - esperanca) ** 2) * X["p"]).sum()

print("variância:", variancia)
print("desvio padrão:", variancia ** 0.5)
''')

    nb.md("""
A variância sai em **reais ao quadrado**, que não quer dizer nada para ninguém.
O desvio padrão volta para reais, e é ele que se lê ao lado da esperança: um dia
típico fica em torno de R$ 200, oscilando algo como R$ 283 para cada lado.

Repare que a conta tem a mesma forma da esperança: cada linha da tabela entra
com o seu peso `p`. O que muda é o que está sendo pesado, o desvio até a média
em vez do próprio valor.
""")

    nb.volta()

    # ---------------------------------------------------------- propostas
    nb.secao("propostas", "As duas propostas", """
O escritório vai mudar a remuneração:

- **proposta A**: um fixo de R$ 300 por dia, mais os honorários de sempre,
  ou seja $Y = X + 300$;
- **proposta B**: nenhum fixo, e os honorários triplicados, ou seja $W = 3X$.

Repare no que muda na tabela: **a coluna `p` é a mesma nas três**. O que a
transformação mexe é só na coluna `x`.
""")

    nb.code('''
def resumir(tabela, nome):
    """Esperança, variância e desvio padrão de uma distribuição em tabela."""
    E = (tabela["x"] * tabela["p"]).sum()
    V = (((tabela["x"] - E) ** 2) * tabela["p"]).sum()
    return {"quem": nome, "E": E, "Var": V, "DP": round(V ** 0.5, 2)}


Y = X.assign(x=X["x"] + 300)
W = X.assign(x=X["x"] * 3)

pd.DataFrame([
    resumir(X, "X: hoje"),
    resumir(Y, "Y = X + 300"),
    resumir(W, "W = 3X"),
])
''')

    nb.md("""
Agora as propriedades da lousa, conferidas contra a tabela acima:

| propriedade | conta | resultado |
|---|---|---|
| $E(X + d) = E(X) + d$ | $200 + 300$ | 500 |
| $E(cX) = c \\, E(X)$ | $3 \\times 200$ | 600 |
| $Var(X + d) = Var(X)$ | 80.000 | 80.000 |
| $Var(cX) = c^2 \\, Var(X)$ | $9 \\times 80.000$ | 720.000 |

O fixo empurra a média e **não toca no risco**: somar 300 a todos os dias
desloca a distribuição inteira e não muda a distância de um dia para o outro.
Triplicar estica essas distâncias, e o quadrado da definição transforma o 3 em 9.
""")

    nb.faca(
        "B paga R$ 100 a mais por dia em média e oscila três vezes mais. Onde isso "
        "aparece: calcule, nas duas propostas, a probabilidade de o dia render "
        "MENOS de R$ 300.",
        '''
for tabela, nome in [(Y, "Y = X + 300"), (W, "W = 3X")]:
    print(nome, ":", tabela.loc[tabela["x"] < 300, "p"].sum())
''',
        '''
for tabela, nome in [(Y, "Y = X + 300"), (W, "W = 3X")]:
    print(nome, ":", tabela.loc[tabela["________"] < ________, "p"].sum())
''',
    )

    nb.md("""
Zero contra 0,64. O fixo da proposta A garante R$ 300 todo dia, e a B deixa a
advogada **sem nada em quase dois terços dos dias**, em troca de R$ 100 a mais
em média. Não há resposta certa: quem tem pouco caixa escolhe A, quem tem muito
escolhe B.
""")

    nb.volta()

    # ------------------------------------------------------------- acordo
    nb.secao("acordo", "O caso do acordo", """
O caso que abriu a aula: 30% de chance de receber R$ 200.000, 70% de pagar
R$ 20.000, contra um acordo de R$ 40.000 na mesa.
""")

    nb.code('''
litigio = pd.DataFrame({
    "x": [200_000, -20_000],
    "p": [0.30, 0.70],
})

resumir(litigio, "ir a julgamento")
''')

    nb.md("""
O julgamento vale R$ 46.000 em média, contra os R$ 40.000 do acordo. Pelo valor
esperado, ir a julgamento.

E o desvio padrão é de uns R$ 100.000, **mais que o dobro da própria média**. Em
70% dos cenários o cliente sai devendo. Aceitar menos que o valor esperado em
troca de certeza tem nome, **aversão ao risco**, e é o que explica a maior parte
dos acordos que fecham abaixo do valor esperado do julgamento.
""")

    nb.faca(
        "Qual o menor acordo que ainda empata com o julgamento no valor esperado? "
        "E se a chance de procedência caísse de 30% para 20%, quanto passaria a "
        "valer o julgamento?",
        '''
print("empata em:", (litigio["x"] * litigio["p"]).sum())

pessimista = pd.DataFrame({"x": [200_000, -20_000], "p": [0.20, 0.80]})
print("com 20% de chance:", (pessimista["x"] * pessimista["p"]).sum())
''',
        '''
print("empata em:", (litigio["x"] * litigio["p"]).sum())

pessimista = pd.DataFrame({"x": [200_000, -20_000], "p": [________, ________]})
print("com 20% de chance:", (pessimista["x"] * pessimista["p"]).sum())
''',
    )

    nb.md("""
Com 20% de chance o julgamento passa a valer R$ 24.000, e o acordo de R$ 40.000
vira o melhor negócio até pelo valor esperado. **Dez pontos de probabilidade
viraram a decisão**, e é por isso que a avaliação de chance de êxito não é
detalhe de petição.
""")

    nb.volta()

    # --------------------------------------------------------------- real
    nb.secao("real", "De onde vem uma distribuição de verdade", """
Até aqui as probabilidades vieram do enunciado. Na prática elas vêm de uma base:
a frequência com que cada valor apareceu é a estimativa da probabilidade dele.
""")

    nb.code(ABERTURA_CRIMINAL)

    nb.code('''
# a distribuição do regime inicial, lida direto da base
regime = (
    penas["regime_inicial"]
    .value_counts(normalize=True)
    .rename("p")
    .reset_index()
)

regime
''')

    nb.md("""
Isso é uma distribuição: valores possíveis e a probabilidade de cada um, somando
1. A diferença é que aqui ela foi **estimada**, e não suposta.

Para calcular esperança precisamos de números, e regime é uma categoria. Então
vamos supor uma consequência: cada regime custa um valor diferente de honorários
de defesa.
""")

    nb.faca(
        "Suponha que a defesa cobre R$ 12.000 quando o regime é fechado, R$ 8.000 "
        "no semiaberto e R$ 5.000 no aberto. Qual o honorário esperado de um caso "
        "sorteado ao acaso na base?",
        '''
honorario = {"fechado": 12_000, "semiaberto": 8_000, "aberto": 5_000}

tabela = regime.assign(x=regime["regime_inicial"].map(honorario))

(tabela["x"] * tabela["p"]).sum()
''',
        '''
honorario = {"fechado": ________, "semiaberto": ________, "aberto": ________}

tabela = regime.assign(x=regime["regime_inicial"].map(honorario))

(tabela["________"] * tabela["________"]).sum()
''',
    )

    nb.md("""
É a mesma conta das audiências, com as probabilidades vindas dos dados em vez do
enunciado. Todo o resto da aula funciona igual.
""")

    nb.volta()

    nb.resumo("""
1. **Distribuição** é a tabela inteira: valores possíveis e probabilidade de
   cada um. Conferir que `p` soma 1 é a primeira coisa a fazer.

2. **Esperança** é `(x * p).sum()`, e quase nunca é um valor possível.

3. **Variância** é `((x - E)**2 * p).sum()`, e o **desvio padrão** é a raiz dela,
   que é o número que se lê ao lado da esperança.

4. Somar um fixo mexe na média e **não** no risco. Multiplicar mexe nos dois, e
   no risco pelo quadrado.

5. Duas decisões com a mesma média podem ser muito diferentes. Quem só olha a
   média não vê a diferença.
""")

    nb.volta()
    return nb


# ====================================================== AULA 10


def montar_aula10() -> Caderno:
    nb = Caderno("aula10")

    nb.cabecalho(
        "Um catálogo de distribuições",
        "Aula 10",
        [
            "reconhecer se um fenômeno é contagem ou medida, e escolher entre "
            "discreta e contínua;",
            "dizer o que cada uma das seis distribuições da aula descreve;",
            "desenhar qualquer uma delas em Python, mexendo nos parâmetros;",
            "conferir contra o histograma da base se o modelo escolhido se "
            "sustenta.",
        ],
        abertura="""
Nada aqui pede fórmula decorada. O que este notebook treina é o olho: ver a
forma, associar ao fenômeno, e desconfiar quando o desenho não bate com os
dados.
""",
    )

    nb.indice([
        ("Contagem ou medida", "tipo"),
        ("As discretas", "discretas"),
        ("As contínuas", "continuas"),
        ("O modelo bate com a base?", "conferir"),
        ("Onde a suposição quebra", "quebra"),
        ("RESUMO", "resumo"),
    ])

    # --------------------------------------------------------------- tipo
    nb.secao("tipo", "Contagem ou medida", """
A primeira decisão é sempre a mesma, e não precisa de conta nenhuma:

| pergunta | tipo | gráfico |
|---|---|---|
| quantos? | **discreta** | barras separadas |
| quanto? | **contínua** | curva |

Cada barra de uma discreta é uma probabilidade de verdade, e as barras somam 1.
Numa contínua a altura não é probabilidade: **a probabilidade é a área**, e por
isso a pergunta é sempre por faixa.
""")

    nb.code('''
import numpy as np
import pandas as pd
from plotnine import *
from scipy import stats

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)
''')

    nb.volta()

    # ---------------------------------------------------------- discretas
    nb.secao("discretas", "As discretas", """
Três, na ordem em que aparecem na aula. Repare que o código é o mesmo nas três,
mudando só a distribuição do `scipy`.
""")

    nb.md("""
**Bernoulli.** Um sim ou não. Um recurso: provido ou não provido.
""")

    nb.code('''
p = 0.30

bernoulli = pd.DataFrame({"x": [0, 1], "prob": [1 - p, p]})

(
    ggplot(bernoulli, aes(x="factor(x)", y="prob"))
    + geom_col(fill="#12996f", width=0.5)
    + labs(x="provido (1) ou não (0)", y="probabilidade",
           title="Bernoulli com p = 0,30")
)
''')

    nb.md("""
**Binomial.** Quantos sucessos em `n` tentativas. O escritório interpõe 10
recursos: quantos serão providos?
""")

    nb.code('''
n, p = 10, 0.30

binomial = pd.DataFrame({"x": range(n + 1)})
binomial["prob"] = stats.binom.pmf(binomial["x"], n, p)

(
    ggplot(binomial, aes(x="x", y="prob"))
    + geom_col(fill="#12996f")
    + scale_x_continuous(breaks=range(n + 1))
    + labs(x="recursos providos", y="probabilidade",
           title="Binomial com n = 10 e p = 0,30")
)
''')

    nb.md("""
**Poisson.** Quantas ocorrências num período, sem teto natural. Quantas ações
novas chegam na vara hoje?
""")

    nb.code('''
lam = 4

poisson = pd.DataFrame({"x": range(15)})
poisson["prob"] = stats.poisson.pmf(poisson["x"], lam)

(
    ggplot(poisson, aes(x="x", y="prob"))
    + geom_col(fill="#12996f")
    + labs(x="ações novas no dia", y="probabilidade",
           title="Poisson com λ = 4")
)
''')

    nb.faca(
        "Mexa nos parâmetros e olhe o que muda de FORMA, não de números. Rode a "
        "binomial com p = 0,05 e depois com p = 0,50, e a Poisson com λ = 1 e "
        "depois com λ = 10. Onde fica o pico em cada caso?",
        '''
for parametro in [0.05, 0.50]:
    d = pd.DataFrame({"x": range(11)})
    d["prob"] = stats.binom.pmf(d["x"], 10, parametro)
    print(f"binomial p={parametro}: pico em {d.loc[d['prob'].idxmax(), 'x']}, "
          f"média {10 * parametro}")

for parametro in [1, 10]:
    d = pd.DataFrame({"x": range(25)})
    d["prob"] = stats.poisson.pmf(d["x"], parametro)
    print(f"poisson λ={parametro}: pico em {d.loc[d['prob'].idxmax(), 'x']}, "
          f"média {parametro}")
''',
        '''
for parametro in [________, ________]:
    d = pd.DataFrame({"x": range(11)})
    d["prob"] = stats.binom.pmf(d["x"], 10, parametro)
    print(f"binomial p={parametro}: pico em {d.loc[d['prob'].idxmax(), 'x']}, "
          f"média {10 * parametro}")

for parametro in [________, ________]:
    d = pd.DataFrame({"x": range(25)})
    d["prob"] = stats.poisson.pmf(d["x"], parametro)
    print(f"poisson λ={parametro}: pico em {d.loc[d['prob'].idxmax(), 'x']}, "
          f"média {parametro}")
''',
    )

    nb.md("""
O pico da binomial fica em torno de $n \\times p$, e o da Poisson em torno de
$\\lambda$. Nas duas, a média é onde a massa se concentra, e é só isso que
precisa ficar.
""")

    nb.volta()

    # ---------------------------------------------------------- continuas
    nb.secao("continuas", "As contínuas", """
Aqui o gráfico é uma curva, e a altura dela **não** é probabilidade. Repare no
eixo y: em algumas curvas ele passa de 1, o que seria impossível se fosse
probabilidade.
""")

    nb.code('''
grade = pd.DataFrame({"x": np.linspace(0, 120, 400)})

curvas = pd.concat([
    grade.assign(dens=stats.uniform.pdf(grade["x"], 20, 60), qual="uniforme"),
    grade.assign(dens=stats.expon.pdf(grade["x"], scale=20), qual="exponencial"),
    grade.assign(dens=stats.norm.pdf(grade["x"], 60, 12), qual="normal"),
])

(
    ggplot(curvas, aes(x="x", y="dens"))
    + geom_area(fill="#bfe6d5")
    + geom_line(size=0.8)
    + facet_wrap("qual", scales="free_y")
    + labs(x="dias", y="densidade", title="As três contínuas da aula")
)
''')

    nb.md("""
- **uniforme**: um retângulo. Nenhum valor da faixa é mais provável que outro.
- **exponencial**: começa alta e cai. Muitos casos rápidos, uma cauda longa.
- **normal**: simétrica, com pico no meio.

A probabilidade de uma faixa é a **área** debaixo da curva, e o `scipy` já
entrega isso pronto com o `.cdf`.
""")

    nb.code('''
# P(o laudo sair entre 50 e 70 dias), na normal de média 60 e desvio 12
stats.norm.cdf(70, 60, 12) - stats.norm.cdf(50, 60, 12)
''')

    nb.faca(
        "Na mesma normal, calcule a probabilidade de o laudo sair em mais de 90 "
        "dias, e a de sair em exatamente 60 dias.",
        '''
print("mais de 90 dias:", 1 - stats.norm.cdf(90, 60, 12))
print("exatamente 60 dias:", stats.norm.cdf(60, 60, 12) - stats.norm.cdf(60, 60, 12))
''',
        '''
print("mais de 90 dias:", 1 - stats.norm.cdf(________, 60, 12))
print("exatamente 60 dias:", stats.norm.cdf(60, 60, 12) - stats.norm.cdf(________, 60, 12))
''',
    )

    nb.md("""
Zero. Não é um defeito da conta: em variável contínua, a probabilidade de
**qualquer** ponto isolado é zero mesmo. Por isso, aqui, `>` e `>=` dão o mesmo
número, e em discreta não dão.
""")

    nb.volta()

    # ---------------------------------------------------------- conferir
    nb.secao("conferir", "O modelo bate com a base?", """
Escolher uma distribuição é **supor** algo sobre o fenômeno, e suposição se
confere. O juiz é o histograma.
""")

    nb.code(ABERTURA_CRIMINAL)

    nb.code('''
penas["pena_anos"].describe()
''')

    nb.md("""
Média e mediana bem diferentes já avisam: a distribuição não é simétrica. Vamos
desenhar o histograma com a normal por cima, usando a média e o desvio da
própria base.
""")

    nb.code('''
media = penas["pena_anos"].mean()
desvio = penas["pena_anos"].std()

grade = pd.DataFrame({"x": np.linspace(0, penas["pena_anos"].max(), 300)})
grade["dens"] = stats.norm.pdf(grade["x"], media, desvio)

(
    ggplot()
    + geom_histogram(penas, aes(x="pena_anos", y="..density.."),
                     bins=30, fill="#dcdcdc", color="white")
    + geom_line(grade, aes(x="x", y="dens"), color="#e50505", size=1)
    + labs(x="pena (anos)", y="densidade",
           title="A pena segue uma normal?")
)
''')

    nb.md("""
**Não segue.** A normal é simétrica e desce para os dois lados; a pena tem um
piso em zero, uma concentração nos valores baixos e uma cauda comprida à
direita. A curva vermelha chega a prever pena negativa, que não existe.

É o mesmo desenho da **exponencial** da seção anterior, e é assim que quase todo
valor jurídico se comporta: pena, tempo de tramitação, indenização, honorários.
""")

    nb.faca(
        "Uma regra rápida para desconfiar: numa normal, cerca de 68% dos casos "
        "ficam a um desvio padrão da média. Calcule essa proporção na base e "
        "compare com os 68% que o modelo promete.",
        '''
dentro = penas["pena_anos"].between(media - desvio, media + desvio).mean()

print(f"o modelo promete: 68%")
print(f"a base entrega:   {dentro:.1%}")
''',
        '''
dentro = penas["pena_anos"].between(________, ________).mean()

print(f"o modelo promete: 68%")
print(f"a base entrega:   {dentro:.1%}")
''',
    )

    nb.md("""
A diferença é grande, e é uma **falsificação**: o modelo prometeu um número, os
dados entregaram outro. É assim que se descarta uma distribuição, e não por
opinião sobre a forma do gráfico.
""")

    nb.volta()

    # ------------------------------------------------------------- quebra
    nb.secao("quebra", "Onde a suposição quebra", """
A binomial exige três coisas: número fixo de tentativas, mesma probabilidade em
todas, e **independência**. A terceira é a que mais cai por terra em problema
jurídico.
""")

    nb.faca(
        "Escreva, numa frase de comentário, um caso jurídico em que contar "
        "sucessos em n tentativas NÃO é binomial porque as tentativas se "
        "influenciam.",
        '''
# Exemplo: dez recursos do mesmo escritório, sobre a mesma tese, julgados pela
# mesma câmara. Se o primeiro é provido, os outros passam a ter mais chance,
# porque o que decide não é o acaso e sim o entendimento da câmara sobre a tese.
# Usar binomial aqui subestima muito a chance dos extremos, dez providos ou
# nenhum, que são justamente os cenários que interessam a quem recorre.
''',
        '''
# ESCREVA SUA RESPOSTA AQUI
''',
    )

    nb.md("""
O mesmo raciocínio vale para as outras: a Poisson supõe que as ocorrências não
se aglomeram, e um mutirão de ações de um mesmo escritório quebra isso na hora.
""")

    nb.volta()

    nb.resumo("""
1. **Contagem** vira barra e é discreta; **medida** vira curva e é contínua.

2. Discretas: Bernoulli (um sim ou não), Binomial (quantos de `n`) e Poisson
   (quantos no período, sem teto).

3. Contínuas: uniforme (sem preferência), exponencial (tempo de espera, cauda
   longa) e normal (soma de muitas causas).

4. Em contínua a probabilidade é **área**, e a de um ponto é zero.

5. Escolher a distribuição é **supor**. O histograma da base é quem decide se a
   suposição fica de pé, e dinheiro e tempo quase nunca são normais.
""")

    nb.volta()
    return nb


# ====================================================== AULA 11


def montar_aula11() -> Caderno:
    nb = Caderno("aula11")

    nb.cabecalho(
        "Da amostra para a população",
        "Aula 11",
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
    for construir in (montar_aula07, montar_aula08, montar_aula09, montar_aula10,
                      montar_aula11):
        caderno = construir()
        print(f"{caderno.nome}:")
        caderno.gravar()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
