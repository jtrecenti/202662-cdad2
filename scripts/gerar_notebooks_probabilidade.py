"""Notebooks das aulas 7, 8 e 9 (probabilidade, distribuições e inferência).

Sai daqui:
    notebooks/aula07_professor.ipynb   probabilidade condicional e independência
    notebooks/aula07_aluno.ipynb
    notebooks/aula08_professor.ipynb   condicional, independência e Bayes
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
