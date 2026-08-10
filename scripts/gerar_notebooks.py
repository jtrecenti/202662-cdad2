"""Gera os notebooks das aulas 2 e 3, e o material extra.

Sai daqui:
    notebooks/aula02_professor.ipynb   tipos de variaveis (DataJud)
    notebooks/aula02_aluno.ipynb
    notebooks/aula03_professor.ipynb   filtro e estatistica descritiva (CJSG)
    notebooks/aula03_aluno.ipynb
    notebooks/aula04_professor.ipynb   encadeamento de operacoes (CJSG criminal)
    notebooks/aula04_aluno.ipynb
    notebooks/extra_filtros_plano_saude.ipynb   material de estudo, completo

Duas regras que valem para tudo aqui:

1. Toda lacuna da versao do aluno repete uma operacao que aparece resolvida na
   celula imediatamente anterior, em outra coluna. Eles estao vendo pandas pela
   primeira vez: lacuna sobre coisa que nunca foi feita na frente deles nao e
   exercicio, e paralisia.
2. Nada de conteudo que o plano de aula coloca mais para a frente. Expressao
   regular e aula 12, e groupby/agg e aula 4. As colunas que sairiam do texto do
   acordao ja vem prontas na base.

Uso:
    python scripts/gerar_notebooks.py
"""

from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "notebooks"

URL = "https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/dados"


class Caderno:
    """Um notebook, com as duas versoes crescendo lado a lado."""

    def __init__(self, nome: str, *, so_completo: bool = False):
        self.nome = nome
        self.so_completo = so_completo
        self.celulas: list[tuple[str, str, str]] = []

    def md(self, texto: str) -> None:
        t = texto.strip("\n")
        self.celulas.append(("markdown", t, t))

    def code(self, professor: str, aluno: str | None = None) -> None:
        p = professor.strip("\n")
        self.celulas.append(("code", p, (aluno.strip("\n") if aluno else p)))

    def faca(self, enunciado: str, professor: str, aluno: str) -> None:
        """Bloco 'agora você': o enunciado curto mais a celula lacunada."""
        self.md(f"**Agora você.** {enunciado.strip()}")
        self.code(professor, aluno)

    def json(self, indice: int) -> dict:
        return {
            "cells": [
                {
                    "id": f"c{i:03d}",
                    "cell_type": tipo,
                    "metadata": {},
                    "source": (conteudo[indice] + "\n").splitlines(keepends=True),
                    **({"outputs": [], "execution_count": None} if tipo == "code" else {}),
                }
                for i, (tipo, *conteudo) in enumerate(self.celulas)
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {"name": "python", "version": "3.12"},
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }

    def gravar(self) -> None:
        SAIDA.mkdir(parents=True, exist_ok=True)
        versoes = [(0, "")] if self.so_completo else [(0, "_professor"), (1, "_aluno")]
        for indice, sufixo in versoes:
            caminho = SAIDA / f"{self.nome}{sufixo}.ipynb"
            caminho.write_text(
                json.dumps(self.json(indice), ensure_ascii=False, indent=1),
                encoding="utf-8",
            )
            lacunas = sum(
                c[1 + indice].count("________") for c in self.celulas if c[0] == "code"
            )
            print(f"  {caminho.name}: {len(self.celulas)} células, {lacunas} lacunas")


ABERTURA = f"""
import pandas as pd

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)

URL = "{URL}"
"""


# ====================================================== AULA 2


def montar_aula02() -> Caderno:
    nb = Caderno("aula02")

    nb.md("""
# Aula 2: tipos de variáveis

Uma pesquisa empírica em Direito termina numa tabela. Quem decide o que vira
coluna dessa tabela é você, e cada coluna é uma **variável**. Esta aula é sobre
dizer que tipo é cada variável, e sobre fazer o pandas concordar com você.

Como o notebook funciona: cada operação nova aparece primeiro resolvida, e logo
depois vem um bloco **Agora você**, que pede a mesma operação em outra coluna.
""")

    nb.code(ABERTURA)

    nb.md("""
## A pergunta de pesquisa

> Entre 2023 e 2025, como se distribuem no TJSP os processos com assunto de
> saúde (medicamento, tratamento médico-hospitalar, plano de saúde): em que grau
> tramitam, de que classe são, e quanto tempo passa entre o ajuizamento e a
> última movimentação registrada?

Repare que a pergunta já obriga a decidir coisas. "Quanto tempo" pede uma
variável numérica que **não existe** na base e vai precisar ser construída.
""")

    nb.md("""
### De onde vieram os dados

A base saiu da API pública do DataJud (CNJ), pelo juscraper. O código abaixo é o
que foi rodado uma vez, e está aqui só para você saber a origem da tabela. Não
precisa rodar.

```python
import juscraper as jus

datajud = jus.scraper("datajud")
processos = datajud.listar_processos(
    tribunal="TJSP",
    assuntos=[6064, 6233, 7775, 10064, 10356, 12484, 12487, 12489, 14760],
    ano_ajuizamento=2024,
    paginas=1,
)
```
""")

    nb.code("""
saude = pd.read_csv(f"{URL}/tjsp_datajud_saude.csv")
saude.head()
""")

    nb.code("""
saude.shape
""")

    nb.md("""
## Primeiro olhar: o que o pandas achou de cada coluna

`.info()` mostra, para cada coluna, quantos valores não são nulos e qual o
**dtype**, que é o tipo de armazenamento do pandas. Cuidado com a palavra
"tipo": o dtype é uma decisão que o pandas tomou ao ler o arquivo, e não a
natureza da variável.
""")

    nb.code("""
saude.info()
""")

    nb.md("""
`.nunique()` conta quantos valores distintos existem em cada coluna. É a segunda
coisa a olhar, e já adianta muito sobre o tipo de cada variável.
""")

    nb.code("""
saude.nunique()
""")

    nb.md("""
### O dtype não é o tipo da variável

Estas quatro colunas vieram todas como número:
""")

    nb.code("""
saude[["classe_codigo", "municipio_ibge", "nivel_sigilo", "n_assuntos"]].dtypes
""")

    nb.md("""
E o pandas deixa você fazer esta conta sem reclamar:
""")

    nb.code("""
saude["municipio_ibge"].mean()
""")

    nb.md("""
Saiu um número, e ele não significa nada: `municipio_ibge` é um **código**, um
rótulo que por acaso é escrito com dígitos. A média de um rótulo é um número sem
referente no mundo. O mesmo vale para `classe_codigo`.

Já `n_assuntos` é uma contagem de verdade, e a média dela responde a alguma
coisa: quantos assuntos, em média, um processo tem. Mesma aparência no arquivo,
natureza diferente.

> **Regra prática:** se somar dois valores da variável não produz nada com
> sentido, ela não é numérica, por mais que seja escrita com dígitos.
""")

    nb.md("""
### Exercício 1: classifique as variáveis

Os tipos são estes, com um exemplo desta base para cada um:

| tipo | é assim quando | nesta base |
|---|---|---|
| `identificador` | serve para achar o caso, não para medir | `numero_processo` |
| `categorica_nominal` | rótulos sem ordem entre si | `sistema` (SAJ, Projudi) |
| `categorica_ordinal` | rótulos com ordem natural | `grau` (G1 antes de G2) |
| `categorica_binaria` | só dois valores possíveis | `formato` (eletrônico, físico) |
| `numerica_discreta` | resultado de contar | `n_assuntos` |
| `numerica_continua` | resultado de medir numa escala | nenhuma ainda, vamos criar |
| `data` | matéria-prima para criar outras | `data_ajuizamento` |

Três já estão preenchidas como modelo. Complete o resto.
""")

    nb.code(
        """
tipos = {
    "numero_processo": "identificador",
    "sistema": "categorica_nominal",
    "n_assuntos": "numerica_discreta",
    "tribunal": "categorica_nominal",
    "grau": "categorica_ordinal",
    "classe": "categorica_nominal",
    "classe_codigo": "identificador",
    "assunto": "categorica_nominal",
    "orgao_julgador": "categorica_nominal",
    "municipio_ibge": "identificador",
    "formato": "categorica_binaria",
    "nivel_sigilo": "categorica_ordinal",
    "data_ajuizamento": "data",
    "data_ultima_atualizacao": "data",
}

pd.Series(tipos).value_counts()
""",
        """
tipos = {
    # os três primeiros são o modelo
    "numero_processo": "identificador",
    "sistema": "categorica_nominal",
    "n_assuntos": "numerica_discreta",
    # complete daqui para baixo
    "tribunal": "________",
    "grau": "________",
    "classe": "________",
    "classe_codigo": "________",
    "assunto": "________",
    "orgao_julgador": "________",
    "municipio_ibge": "________",
    "formato": "________",
    "nivel_sigilo": "________",
    "data_ajuizamento": "data",
    "data_ultima_atualizacao": "data",
}

pd.Series(tipos).value_counts()
""",
    )

    nb.md("""
### Variável que não varia

Antes de qualquer conta, veja quantos valores distintos cada coluna tem.
Variável com um valor só não explica nada: ela é constante no recorte.
""")

    nb.code("""
saude[["tribunal", "nivel_sigilo", "formato"]].nunique()
""")

    nb.code("""
saude["formato"].value_counts()
""")

    nb.md("""
`formato` é binária no papel, mas tem 3998 eletrônicos e 2 físicos.
Tecnicamente varia; na prática, não dá para comparar nada com dois casos de um
lado. Isso é decisão de pesquisa, não de programação.
""")

    # ------------------------------------------------ conversão para texto

    nb.md("""
## Converter: de número para texto

`.astype("string")` transforma a coluna em texto. Fazemos isso com códigos, para
que ninguém calcule média deles por acidente. Veja com `classe_codigo`:
""")

    nb.code("""
saude["classe_codigo"] = saude["classe_codigo"].astype("string")

saude["classe_codigo"].dtype
""")

    nb.md("""
Com `municipio_ibge` tem um passo a mais. Ela veio como `float64` (repare no
`.0` no fim de cada número), porque o pandas usa `float` para poder representar
o valor faltante. Converter direto para texto guardaria o `.0` junto:
""")

    nb.code("""
saude["municipio_ibge"].head(3)
""")

    nb.code("""
saude["municipio_ibge"].astype("string").head(3)
""")

    nb.md("""
A solução é passar antes por `"Int64"`, com I maiúsculo, que é o inteiro do
pandas que aceita valor faltante. Depois, sim, vira texto:
""")

    nb.code("""
saude["municipio_ibge"] = saude["municipio_ibge"].astype("Int64").astype("string")

saude["municipio_ibge"].head(3)
""")

    # ------------------------------------------------ datas

    nb.md("""
## Converter: de texto para data

No arquivo, data é texto. Enquanto for texto, `2024-03-15` é só uma sequência de
caracteres: não dá para subtrair, nem ordenar direito, nem pedir o ano.
`pd.to_datetime` faz a conversão.
""")

    nb.code("""
saude["data_ajuizamento"].head(3)
""")

    nb.code("""
saude["data_ajuizamento"] = pd.to_datetime(saude["data_ajuizamento"])

saude["data_ajuizamento"].head(3)
""")

    nb.md("""
Repare no que mudou: o dtype passou de `object` para `datetime64[ns]`.
""")

    nb.faca(
        "Converta `data_ultima_atualizacao` do mesmo jeito.",
        """
saude["data_ultima_atualizacao"] = pd.to_datetime(saude["data_ultima_atualizacao"])

saude[["data_ajuizamento", "data_ultima_atualizacao"]].dtypes
""",
        """
saude["data_ultima_atualizacao"] = pd.________(saude["data_ultima_atualizacao"])

saude[["data_ajuizamento", "data_ultima_atualizacao"]].dtypes
""",
    )

    nb.md("""
### O que se calcula a partir de uma data

Data não é bem um tipo da nossa lista: ela é matéria-prima. O que entra na
análise é o que se calcula a partir dela.

O acessador `.dt` dá acesso aos pedaços da data. `.dt.year` devolve o ano:
""")

    nb.code("""
saude["ano_ajuizamento"] = saude["data_ajuizamento"].dt.year

saude[["data_ajuizamento", "ano_ajuizamento"]].head(3)
""")

    nb.faca(
        "Crie `mes_ajuizamento` com `.dt.month`.",
        """
saude["mes_ajuizamento"] = saude["data_ajuizamento"].dt.month

saude[["data_ajuizamento", "ano_ajuizamento", "mes_ajuizamento"]].head(3)
""",
        """
saude["mes_ajuizamento"] = saude["data_ajuizamento"].dt.________

saude[["data_ajuizamento", "ano_ajuizamento", "mes_ajuizamento"]].head(3)
""",
    )

    nb.md("""
`ano_ajuizamento` sai como número inteiro, e é assim que ele fica. O que muda de
uma análise para outra não é o tipo da coluna, e sim o uso: às vezes ele entra
como número (diferença entre dois anos), às vezes como agrupador (comparar 2023,
2024 e 2025 entre si). Vale escrever qual dos dois usos você está fazendo.
""")

    nb.md("""
### Subtraindo duas datas

Subtrair duas datas devolve um `Timedelta`, que é uma duração. Para virar número
é preciso escolher a unidade, e `.dt.days` devolve a duração em dias.
""")

    nb.code("""
(saude["data_ultima_atualizacao"] - saude["data_ajuizamento"]).head(3)
""")

    nb.code("""
saude["dias_ate_atualizacao"] = (
    saude["data_ultima_atualizacao"] - saude["data_ajuizamento"]
).dt.days

saude[["data_ajuizamento", "data_ultima_atualizacao", "dias_ate_atualizacao"]].head(3)
""")

    nb.md("""
Pronto: a primeira variável numérica da base, e ela não existia no arquivo.
`.describe()` dá um resumo rápido de uma coluna numérica.
""")

    nb.code("""
saude["dias_ate_atualizacao"].describe()
""")

    # ------------------------------------------------ categorical

    nb.md("""
## `pd.Categorical`: o tipo que dá trabalho

Categórica é o tipo mais comum no Direito e o mais chato de representar. Por
padrão o pandas guarda texto (`object`), o que funciona, mas perde duas coisas:
**quais são as categorias possíveis** e **se existe ordem entre elas**.

`pd.Categorical` resolve isso. Veja com `assunto`:
""")

    nb.code("""
saude["assunto"] = pd.Categorical(saude["assunto"])

saude["assunto"].dtype
""")

    nb.md("""
A coluna agora carrega a lista de categorias, e o pandas passa a saber o
universo de valores que aquela variável pode assumir:
""")

    nb.code("""
saude["assunto"].cat.categories
""")

    nb.faca(
        "Faça o mesmo com a coluna `classe` e veja quantas categorias ela tem.",
        """
saude["classe"] = pd.Categorical(saude["classe"])

saude["classe"].cat.categories
""",
        """
saude["classe"] = pd.________(saude["classe"])

saude["classe"].cat.________
""",
    )

    nb.md("""
### Categórica ordinal

Quando existe ordem, ela precisa ser declarada, com `categories=` na ordem certa
e `ordered=True`. `grau` tem G1 (primeiro grau) e G2 (segundo grau), nessa
ordem:
""")

    nb.code("""
saude["grau_ordenado"] = pd.Categorical(
    saude["grau"], categories=["G1", "G2"], ordered=True
)

saude["grau_ordenado"].dtype
""")

    nb.md("""
Agora repare no efeito colateral. A base tem um terceiro valor, `JE` (juizado
especial), que ficou de fora da lista de categorias:
""")

    nb.code("""
saude["grau"].unique()
""")

    nb.code("""
saude["grau_ordenado"].isna().sum()
""")

    nb.md("""
> **Armadilha 1.** Todo valor fora da lista de categorias vira valor faltante,
> **em silêncio**. Isso é útil (declara o universo esperado) e perigoso (perde
> dado sem avisar). Confira sempre quantos viraram faltante depois de criar a
> categórica.

Aqui a perda é intencional: `JE` não fica nem antes nem depois de G1 e G2, é
outra coisa. Se quisermos manter o JE, o caminho é tratá-lo como categoria sem
ordem.
""")

    nb.md("""
### O que a ordem permite fazer

Com `ordered=True`, comparação e ordenação passam a funcionar. Dá para comparar
a coluna com o nome de uma categoria, usando `>`, `>=`, `<` e `<=`:
""")

    nb.code("""
(saude["grau_ordenado"] >= "G2").sum()
""")

    nb.code("""
saude.sort_values("grau_ordenado")[["numero_processo", "grau"]].head(3)
""")

    nb.md("""
Sem `ordered=True`, a mesma comparação levanta erro. Faça o teste:
""")

    nb.code("""
sem_ordem = pd.Categorical(saude["grau"], categories=["G1", "G2", "JE"])

try:
    sem_ordem >= "G2"
except TypeError as erro:
    print("TypeError:", erro)
""")

    nb.md("""
### Valor faltante e a categoria "Outros"

A coluna `assunto` tem dois processos sem assunto informado. Juntar esses casos
numa categoria explícita costuma ser melhor do que deixá-los faltantes: a
categoria aparece nas contagens e ninguém esquece que ela existe.
""")

    nb.code("""
saude["assunto"].isna().sum()
""")

    nb.md("""
A tentação é chamar `fillna("Outros")` direto. Não funciona, e o erro diz
exatamente por quê: `Outros` não está na lista de categorias declaradas.
""")

    nb.code("""
try:
    saude["assunto"].fillna("Outros")
except TypeError as erro:
    print("TypeError:", erro)
""")

    nb.md("""
O caminho é abrir espaço para a categoria antes, com `add_categories`, e só
depois preencher:
""")

    nb.code("""
saude["assunto"] = saude["assunto"].cat.add_categories(["Outros"]).fillna("Outros")

saude["assunto"].isna().sum()
""")

    nb.code("""
saude["assunto"].value_counts()
""")

    nb.md("""
> **Armadilha 2.** `value_counts()` em categórica mostra **todas** as categorias
> declaradas, inclusive as com zero ocorrências. Isso é ótimo para tabela (a
> linha existe mesmo com zero) e péssimo se você não esperava. Repare na última
> linha do resultado abaixo:
""")

    nb.code("""
segundo_grau = saude[saude["grau"] == "G2"]

segundo_grau["assunto"].value_counts()
""")

    # ------------------------------------------------ pd.cut

    nb.md("""
## `pd.cut`: de numérica para categórica ordinal

Transformar uma numérica em faixas é a conversão mais comum na outra direção.
`bins` são os pontos de corte e `labels` são os nomes das faixas. O resultado já
sai como categórica **ordenada**:
""")

    nb.code("""
saude["faixa_dias"] = pd.cut(
    saude["dias_ate_atualizacao"],
    bins=[-float("inf"), 30, 180, 365, float("inf")],
    labels=["até 1 mês", "1 a 6 meses", "6 a 12 meses", "mais de 1 ano"],
)

saude["faixa_dias"].dtype
""")

    nb.code("""
saude["faixa_dias"].value_counts(sort=False)
""")

    nb.md("""
`sort=False` mantém a ordem das faixas. Sem ele, o pandas ordenaria pela
contagem, e a tabela perderia a sequência que interessa.

Cortar em faixas **perde informação**: 31 dias e 179 dias viram a mesma coisa.
Faça isso quando a faixa for o que interessa para a pergunta, não por hábito.
""")

    nb.faca(
        "Como `faixa_dias` é ordenada, dá para comparar com o nome de uma faixa, do "
        "mesmo jeito que fizemos com `grau_ordenado >= \"G2\"`. Conte quantos "
        "processos demoraram mais de 6 meses.",
        """
(saude["faixa_dias"] > "1 a 6 meses").sum()
""",
        """
(saude["faixa_dias"] ________ "1 a 6 meses").sum()
""",
    )

    # ------------------------------------------------ fechamento

    nb.md("""
## Respondendo à pergunta

Com os tipos arrumados, as contas ficam curtas. Quantos processos por assunto:
""")

    nb.code("""
saude["assunto"].value_counts()
""")

    nb.md("""
E o tempo até a última movimentação, comparando primeiro e segundo grau. Por
enquanto fazemos isso separando a base em dois pedaços; na aula 4 você vai ver o
`groupby`, que faz esse tipo de comparação em uma linha só.
""")

    nb.code("""
primeiro_grau = saude[saude["grau"] == "G1"]

primeiro_grau["dias_ate_atualizacao"].median()
""")

    nb.faca(
        "Faça o mesmo para o segundo grau, usando a variável `segundo_grau` que já "
        "criamos lá em cima.",
        """
segundo_grau["dias_ate_atualizacao"].median()
""",
        """
segundo_grau["dias_ate_atualizacao"].________()
""",
    )

    nb.md("""
### Exercício 2

A coluna `orgao_julgador` tem mais de mil valores distintos. Ela é categórica
nominal, mas com tantas categorias não serve para comparar grupos. Escreva, em
duas ou três linhas, que variável derivada dela você criaria para que ela virasse
útil, e por quê. Não precisa programar.
""")

    nb.code("# exercício 2 (responda em célula de texto)")

    nb.md("""
### Exercício 3

Crie uma faixa nova, `faixa_assuntos`, que separe os processos com um assunto dos
processos com mais de um, usando `pd.cut` sobre `n_assuntos`. Depois conte
quantos caem em cada faixa.
""")

    nb.code(
        """
saude["faixa_assuntos"] = pd.cut(
    saude["n_assuntos"],
    bins=[0, 1, float("inf")],
    labels=["um assunto", "mais de um"],
)

saude["faixa_assuntos"].value_counts(sort=False)
""",
        """
saude["faixa_assuntos"] = pd.________(
    saude["n_assuntos"],
    bins=[0, 1, float("inf")],
    labels=["um assunto", "mais de um"],
)

saude["faixa_assuntos"].value_counts(sort=________)
""",
    )

    nb.md("""
## O que ficou

1. **dtype não é tipo de variável.** O pandas chuta pelo formato do arquivo; a
   natureza da variável é decisão sua, e ela decide que conta é possível.
2. **Converter é rotina.** `.astype("string")` para códigos, `"Int64"` no meio
   quando há faltantes, `pd.to_datetime` para datas.
3. **Data é matéria-prima.** O que entra na análise é o que se calcula dela, com
   `.dt.year`, `.dt.month` e subtração seguida de `.dt.days`.
4. **Categórica precisa ser declarada.** `pd.Categorical` guarda o universo de
   categorias e, com `ordered=True`, a ordem. O que fica fora vira faltante em
   silêncio, e faltante vira "Outros" com `add_categories` antes do `fillna`.
5. **`pd.cut`** faz o caminho de volta, de numérica para categórica ordenada.

Na aula 3 vamos usar esses tipos para escolher a estatística certa.
""")

    return nb


# ====================================================== AULA 3


def montar_aula03() -> Caderno:
    nb = Caderno("aula03")

    nb.md("""
# Aula 3: filtrar e resumir

Na aula 2 arrumamos os tipos de uma base. Agora vamos usar esses tipos para
duas coisas: **recortar** o que entra na análise e **resumir** a coluna em um
número.

O notebook segue o mesmo formato: cada operação aparece primeiro resolvida, e
depois vem um bloco **Agora você** com a mesma operação em outra coluna.
""")

    nb.code(ABERTURA)

    nb.md("""
## A pergunta de pesquisa

> Nos acórdãos do TJSP que arbitram indenização por dano moral, qual é o valor
> típico, e quanto ele varia?

"Valor típico" e "quanto varia" são as duas perguntas que a estatística
descritiva responde: uma medida de **posição** e uma medida de **dispersão**.
Escolher qual é o conteúdo da aula.
""")

    nb.md("""
### De onde vieram os dados

```python
import juscraper as jus

tjsp = jus.scraper("tjsp")
acordaos = tjsp.cjsg('"dano moral" E "arbitro a indenizacao"', paginas=range(1, 26))
```
""")

    nb.code("""
danos = pd.read_csv(f"{URL}/tjsp_cjsg_dano_moral.csv")
danos.head(3)
""")

    nb.code("""
danos.info()
""")

    nb.md("""
### As colunas que vieram do texto

Quatro colunas desta base não vieram prontas do tribunal: elas foram **lidas do
texto da ementa** antes de o arquivo ser publicado.

| coluna | como foi definida |
|---|---|
| `valor_indenizacao` | o primeiro valor em reais que aparece na ementa |
| `tem_dano_moral` | a ementa menciona a expressão "dano moral" |
| `houve_majoracao` | a ementa menciona alguma forma de "majorar" |
| `camara` e `secao` | o número e a seção lidos do nome do órgão julgador |

A ferramenta que faz essa leitura é a expressão regular, e ela é o assunto da
aula 12. Aqui interessa outra coisa: **as decisões que essas definições
embutem**, e o que elas custam.

Veja uma ementa e a linha correspondente da tabela:
""")

    nb.code("""
print(danos.loc[0, "ementa"][:700])
""")

    nb.code("""
danos.loc[[0], ["processo", "valor_indenizacao", "tem_dano_moral", "houve_majoracao"]]
""")

    nb.md("""
Duas limitações que precisam estar escritas em qualquer relatório que use estas
colunas:

- `valor_indenizacao` pega o **primeiro** valor em reais da ementa. Nem sempre é
  o valor arbitrado: pode ser o valor pedido, o da sentença reformada, ou custas;
- `tem_dano_moral` marca a ementa que **menciona** dano moral, inclusive para
  dizer que não é caso de indenizar.

Nenhuma das duas invalida o exercício. As duas mudam o que se pode concluir.
""")

    nb.md("""
**Exercício 1.** Escolha uma variável que você gostaria de ter nesta tabela e
que não está lá. Escreva o nome dela, o tipo, e a instrução que faria duas
pessoas lerem a mesma ementa e registrarem o mesmo valor. Não precisa programar.
Este é exatamente o trabalho que o Projeto 1 vai pedir hoje.
""")

    nb.code("# exercício 1 (responda em célula de texto)")

    nb.md("""
### Retomando: que tipo é cada coluna

Duas já estão preenchidas como modelo.
""")

    nb.code(
        """
tipos = {
    "processo": "identificador",
    "ementa": "texto",
    "comarca": "categorica_nominal",
    "camara": "categorica_nominal",
    "secao": "categorica_nominal",
    "data_julgamento": "data",
    "valor_indenizacao": "numerica_continua",
    "tem_dano_moral": "categorica_binaria",
    "n_palavras_ementa": "numerica_discreta",
}

pd.Series(tipos).value_counts()
""",
        """
tipos = {
    # modelo
    "processo": "identificador",
    "ementa": "texto",
    # complete
    "comarca": "________",
    "camara": "________",
    "secao": "________",
    "data_julgamento": "________",
    "valor_indenizacao": "________",
    "tem_dano_moral": "________",
    "n_palavras_ementa": "________",
}

pd.Series(tipos).value_counts()
""",
    )

    nb.md("""
`camara` merece atenção: ela é escrita com dígitos e mesmo assim é categórica
nominal. A 13ª câmara não é maior que a 2ª.
""")

    nb.md("""
### Convertendo as datas

Mesma operação da aula 2, com uma diferença: aqui a data vem no formato
brasileiro, `07/08/2026`, e o pandas precisa que você diga isso com `format=`.
`%d` é o dia, `%m` o mês e `%Y` o ano com quatro dígitos.
""")

    nb.code("""
danos["data_julgamento"] = pd.to_datetime(danos["data_julgamento"], format="%d/%m/%Y")

danos["data_julgamento"].head(3)
""")

    nb.faca(
        "Converta `data_publicacao`, que vem no mesmo formato.",
        """
danos["data_publicacao"] = pd.to_datetime(danos["data_publicacao"], format="%d/%m/%Y")

danos[["data_julgamento", "data_publicacao"]].dtypes
""",
        """
danos["data_publicacao"] = pd.to_datetime(danos["data_publicacao"], format="________")

danos[["data_julgamento", "data_publicacao"]].dtypes
""",
    )

    nb.md("""
## Variável, valor observado e estatística

Três palavras que a conversa do dia a dia mistura:

- **variável**: o que se mede, "valor da indenização em reais". Existe antes dos
  dados e é a coluna da tabela;
- **valor observado**: o valor de um caso, "neste acórdão foram R$ 5.000,00". É
  uma célula;
- **estatística**: um resumo de muitos valores observados, "a mediana foi
  R$ 5.000,00". É um número calculado da coluna inteira.

O tipo é propriedade da variável, e é ele que decide qual estatística faz
sentido.
""")

    # ------------------------------------------------ filtros

    nb.md("""
## Filtrar

Recortar a base é decisão de pesquisa, não detalhe técnico. Há três jeitos de
fazer, e eles dão o mesmo resultado.

### 1. Índice lógico

Uma comparação devolve uma série de `True` e `False`, do mesmo tamanho do
DataFrame. Isso é uma máscara:
""")

    nb.code("""
tem_valor = danos["valor_indenizacao"].notna()

tem_valor.head()
""")

    nb.md("""
E o DataFrame indexado pela máscara devolve só as linhas verdadeiras:
""")

    nb.code("""
danos[tem_valor].shape
""")

    nb.faca(
        "Crie a máscara `foi_majorado` a partir de `houve_majoracao`, que já é uma "
        "coluna de `True` e `False`, e veja quantas linhas sobram.",
        """
foi_majorado = danos["houve_majoracao"]

danos[foi_majorado].shape
""",
        """
foi_majorado = danos["________"]

danos[________].shape
""",
    )

    nb.md("""
Para combinar condições: `&` é "e", `|` é "ou", `~` é "não". Os parênteses em
volta de cada condição são obrigatórios.
""")

    nb.code("""
privado_com_valor = danos[(danos["secao"] == "Direito Privado") & tem_valor]

privado_com_valor.shape
""")

    nb.faca(
        "Monte um recorte com os acórdãos que têm valor **e** em que houve majoração.",
        """
com_valor_e_majoracao = danos[tem_valor & foi_majorado]

com_valor_e_majoracao.shape
""",
        """
com_valor_e_majoracao = danos[tem_valor ________ foi_majorado]

com_valor_e_majoracao.shape
""",
    )

    nb.md("""
O índice lógico é o jeito mais explícito de filtrar, e é o único que vamos usar
hoje. Na aula 4 aparecem outros dois, `.loc` e `.query`, que escrevem a mesma
coisa de forma mais curta.

### O recorte da pergunta

Um terço das ementas não trouxe valor. A decisão aqui é analisar só quem tem
valor, e a consequência é que a resposta vale para **os acórdãos que trazem o
valor na ementa**, não para todos.
""")

    nb.code("""
com_valor = danos.dropna(subset=["valor_indenizacao"]).copy()

len(danos), len(com_valor)
""")

    # ------------------------------------------------ posição

    nb.md("""
## Posição: onde fica o centro

`.describe()` já dá vários resumos de uma vez:
""")

    nb.code("""
com_valor["valor_indenizacao"].describe().round(2)
""")

    nb.md("""
As duas medidas de posição mais usadas são a média e a mediana. `.mean()`
devolve a média:
""")

    nb.code("""
com_valor["valor_indenizacao"].mean().round(2)
""")

    nb.faca(
        "Calcule a mediana, com `.median()`.",
        """
com_valor["valor_indenizacao"].median()
""",
        """
com_valor["valor_indenizacao"].________()
""",
    )

    nb.md("""
A média é bem maior que a mediana. Isso é a assinatura de uma distribuição
**assimétrica à direita**: poucos valores muito altos puxam a média, e a mediana
ignora. Em valores monetários no Direito, isso é a regra, não a exceção.

Dá para ver o efeito tirando um único caso, com o mesmo índice lógico de antes:
mantemos só as linhas cujo valor é menor que o máximo.
""")

    nb.code("""
maior = com_valor["valor_indenizacao"].max()
sem_o_maior = com_valor[com_valor["valor_indenizacao"] < maior]

pd.DataFrame({
    "com todos": [
        com_valor["valor_indenizacao"].mean(),
        com_valor["valor_indenizacao"].median(),
    ],
    "sem o maior": [
        sem_o_maior["valor_indenizacao"].mean(),
        sem_o_maior["valor_indenizacao"].median(),
    ],
}, index=["média", "mediana"]).round(2)
""")

    nb.md("""
Uma linha muda a média e não move a mediana. É por isso que "o valor típico da
indenização" quase sempre deve ser reportado com a mediana.
""")

    # ------------------------------------------------ quantis

    nb.md("""
## Quantis: a distribuição inteira

O quantil de ordem $p$ é o valor abaixo do qual está a fração $p$ dos casos. A
mediana é o quantil 0,5. `.quantile()` aceita uma lista:
""")

    nb.code("""
com_valor["valor_indenizacao"].quantile([0.25, 0.50, 0.75]).round(2)
""")

    nb.faca(
        "Peça os quantis 0,10, 0,90 e 0,99, para enxergar as duas pontas.",
        """
com_valor["valor_indenizacao"].quantile([0.10, 0.90, 0.99]).round(2)
""",
        """
com_valor["valor_indenizacao"].quantile([________]).round(2)
""",
    )

    nb.md("""
Compare o quantil 0,90 com o máximo: a distância entre os dois é o tamanho da
cauda.

O intervalo interquartílico (IQR) é a largura da metade central dos dados, ou
seja, a distância entre o quantil 0,25 e o 0,75:
""")

    nb.code("""
q1 = com_valor["valor_indenizacao"].quantile(0.25)
q3 = com_valor["valor_indenizacao"].quantile(0.75)

pd.Series({
    "Q1": q1,
    "Q3": q3,
    "IQR": q3 - q1,
    "amplitude": com_valor["valor_indenizacao"].max() - com_valor["valor_indenizacao"].min(),
})
""")

    nb.md("""
A amplitude é decidida por dois casos extremos. O IQR não, e por isso ele é a
medida de dispersão que acompanha a mediana.
""")

    # ------------------------------------------------ dispersão

    nb.md("""
## Dispersão: variância e desvio padrão

O desvio padrão mede o afastamento típico em relação à média. A conta divide por
$n - 1$, e não por $n$: é o desvio padrão **amostral**, que é o padrão do pandas.
O parâmetro que controla isso é o `ddof`, e ele vale 1 por omissão.
""")

    nb.code("""
com_valor["valor_indenizacao"].std().round(2)
""")

    nb.faca(
        "Calcule o desvio padrão populacional, passando `ddof=0`, e compare com o "
        "de cima.",
        """
com_valor["valor_indenizacao"].std(ddof=0).round(2)
""",
        """
com_valor["valor_indenizacao"].std(ddof=________).round(2)
""",
    )

    nb.md("""
Refazendo a conta na mão, para ver que não tem mágica:
""")

    nb.code("""
x = com_valor["valor_indenizacao"]
n = len(x)

variancia = ((x - x.mean()) ** 2).sum() / (n - 1)

pd.Series({
    "variância na mão": variancia,
    "variância pandas": x.var(),
    "desvio padrão na mão": variancia ** 0.5,
    "desvio padrão pandas": x.std(),
}).round(2)
""")

    nb.md("""
Com $n$ na casa das centenas, a diferença entre dividir por $n$ e por $n-1$ é
pequena. Com $n = 12$, que é o tamanho de muita amostra de pesquisa em Direito,
deixa de ser.

O desvio padrão sozinho é difícil de interpretar, porque ele vem na unidade da
variável. O **coeficiente de variação** põe a dispersão em escala relativa,
dividindo pelo valor médio:
""")

    nb.code("""
com_valor["valor_indenizacao"].std() / com_valor["valor_indenizacao"].mean()
""")

    nb.md("""
Um coeficiente maior que 1 quer dizer que o desvio padrão é maior que a média:
os valores estão espalhadíssimos. Reportar só "a indenização média foi
R$ 7.935" sem dizer isso é enganoso.
""")

    # ------------------------------------------------ binária

    nb.md("""
## A média de uma binária é uma proporção

Este é o truque que mais aparece daqui em diante. Uma variável binária guardada
como `True` e `False` é lida pelo Python como 1 e 0. Somar dá o número de casos
`True`, e dividir pelo total dá a proporção. Ou seja: **a média é a proporção**.

Primeiro criamos a binária, com uma comparação:
""")

    nb.code("""
com_valor["acima_de_10k"] = com_valor["valor_indenizacao"] >= 10000

com_valor["acima_de_10k"].head()
""")

    nb.code("""
pd.Series({
    "quantos True": com_valor["acima_de_10k"].sum(),
    "total": len(com_valor),
    "soma dividida pelo total": com_valor["acima_de_10k"].sum() / len(com_valor),
    "média": com_valor["acima_de_10k"].mean(),
}).round(4)
""")

    nb.faca(
        "Calcule a proporção de acórdãos em que houve majoração, usando `.mean()` "
        "na coluna `houve_majoracao`.",
        """
com_valor["houve_majoracao"].mean().round(4)
""",
        """
com_valor["houve_majoracao"].________().round(4)
""",
    )

    nb.md("""
O desvio padrão de uma binária também não é um número livre: ele depende só da
proporção, e vale $\\sqrt{p(1-p)}$. Confira:
""")

    nb.code("""
p = com_valor["acima_de_10k"].mean()

pd.Series({
    "desvio padrão pelo pandas": com_valor["acima_de_10k"].std(ddof=0),
    "raiz de p(1-p)": (p * (1 - p)) ** 0.5,
}).round(4)
""")

    # ------------------------------------------------ fechamento

    nb.md("""
## Cada tipo, sua estatística

Em variável nominal, média não existe. O que existe é a **moda**, que é a
categoria mais frequente, e a proporção de cada categoria:
""")

    nb.code("""
com_valor["comarca"].mode()
""")

    nb.code("""
com_valor["comarca"].value_counts(normalize=True).head(5).round(3)
""")

    nb.md("""
Resumindo o que cabe em cada tipo:

| tipo | posição | dispersão | o que **não** fazer |
|---|---|---|---|
| numérica contínua | média, mediana | desvio padrão, IQR | reportar só a média em distribuição assimétrica |
| numérica discreta | média, mediana, moda | desvio padrão, IQR | esquecer que a média pode ser fracionária |
| categórica ordinal | mediana, moda | amplitude de postos | média das categorias |
| categórica nominal | moda | nenhuma clássica | média, mediana, desvio padrão |
| categórica binária | proporção (= média) | $\\sqrt{p(1-p)}$ | tratar como contínua |
| identificador | nenhuma | nenhuma | qualquer conta |
""")

    nb.md("""
## Respondendo à pergunta

Juntando filtro e estatística: o valor típico no Direito Privado, comparado com
o geral. Na aula 4 você vai ver o `groupby`, que compara todos os grupos de uma
vez; por enquanto separamos a base em pedaços.
""")

    nb.code("""
privado = com_valor[com_valor["secao"] == "Direito Privado"]

pd.Series({
    "n": len(privado),
    "mediana": privado["valor_indenizacao"].median(),
    "média": privado["valor_indenizacao"].mean(),
    "desvio padrão": privado["valor_indenizacao"].std(),
    "proporção acima de 10 mil": privado["acima_de_10k"].mean(),
}).round(2)
""")

    nb.faca(
        "Monte o mesmo resumo para os acórdãos julgados em 2026. Lembre do "
        "`.dt.year` da aula 2.",
        """
em_2026 = com_valor[com_valor["data_julgamento"].dt.year == 2026]

pd.Series({
    "n": len(em_2026),
    "mediana": em_2026["valor_indenizacao"].median(),
    "média": em_2026["valor_indenizacao"].mean(),
    "desvio padrão": em_2026["valor_indenizacao"].std(),
    "proporção acima de 10 mil": em_2026["acima_de_10k"].mean(),
}).round(2)
""",
        """
em_2026 = com_valor[com_valor["data_julgamento"].dt.________ == 2026]

pd.Series({
    "n": len(em_2026),
    "mediana": em_2026["valor_indenizacao"].________(),
    "média": em_2026["valor_indenizacao"].mean(),
    "desvio padrão": em_2026["valor_indenizacao"].________(),
    "proporção acima de 10 mil": em_2026["acima_de_10k"].mean(),
}).round(2)
""",
    )

    nb.md("""
### Exercício 2

A base tem 460 acórdãos e 303 com valor extraído. Escreva, em duas ou três
linhas, como você reportaria esse número numa seção de metodologia, e que
problema isso pode causar na interpretação da mediana.
""")

    nb.code("# exercício 2 (responda em célula de texto)")

    nb.md("""
## O que ficou

1. **Variável e estatística são coisas diferentes.** A variável é a coluna, o
   valor observado é a célula, a estatística é o resumo da coluna inteira.
2. **Filtrar é decisão de pesquisa.** O recorte precisa estar escrito e
   justificado, porque ele define sobre o que a resposta vale.
3. **A estatística tem que caber no tipo.** Mediana em contínua assimétrica,
   proporção em binária, moda em nominal.
4. **Média de binária é proporção**, e desvio padrão amostral divide por $n-1$.

Na aula 4 vamos escrever tudo isso de forma mais curta, encadeando as operações,
e comparar todos os grupos de uma vez com `groupby`. Para praticar filtros antes
disso, use o notebook `extra_filtros_plano_saude.ipynb`, que está completo.
""")

    return nb


# ====================================================== AULA 4


def montar_aula04() -> Caderno:
    nb = Caderno("aula04")

    nb.md("""
# Aula 4: encadear operações

Até aqui, cada operação foi uma linha separada, guardando o resultado numa
variável nova. Funciona, e fica ilegível rápido.

Nesta aula toda análise vira uma **sequência de operações encadeadas**, escrita
de cima para baixo dentro de um par de parênteses. Cada linha faz uma coisa, e
você lê o que aconteceu na ordem em que aconteceu.

O roteiro:

1. ver o problema que o encadeamento resolve;
2. aprender os verbos, um a um: filtrar, criar coluna, ordenar, escolher
   colunas, agrupar e agregar;
3. montar um pipeline inteiro para responder a uma pergunta.
""")

    nb.code(ABERTURA)

    nb.md("""
## A base

Recursos criminais do TJSP, com o regime inicial e a pena lidos da ementa.

```python
import juscraper as jus

tjsp = jus.scraper("tjsp")
acordaos = tjsp.cjsg('"apelacao criminal" E "regime inicial"', paginas=range(1, 26))
```
""")

    nb.code("""
criminal = pd.read_csv(f"{URL}/tjsp_cjsg_criminal.csv")
criminal.head(3)
""")

    nb.code("""
criminal.info()
""")

    nb.md("""
> `regime_inicial` e `pena_anos` foram lidos do texto da ementa, e nenhum dos
> dois vem completo: o regime aparece em cerca de 70% dos acórdãos e a pena em
> 45%. `pena_anos` ainda traz valores implausíveis, porque a leitura pega o
> primeiro número seguido de "anos" que encontra. Vamos lidar com isso.
""")

    nb.md("""
## A pergunta de pesquisa

> Nas apelações criminais do TJSP, a proporção de acórdãos que mencionam
> reincidência varia conforme o regime inicial fixado?

## O problema: uma variável para cada passo

Resolvendo do jeito que fizemos até agora, com uma variável nova por operação:
""")

    nb.code("""
apelacoes = criminal[criminal["classe"] == "Apelação Criminal"]
com_regime = apelacoes.dropna(subset=["regime_inicial"])
fechado = com_regime[com_regime["regime_inicial"] == "fechado"]
semiaberto = com_regime[com_regime["regime_inicial"] == "semiaberto"]
aberto = com_regime[com_regime["regime_inicial"] == "aberto"]

pd.Series({
    "fechado": fechado["houve_reincidencia"].mean(),
    "semiaberto": semiaberto["houve_reincidencia"].mean(),
    "aberto": aberto["houve_reincidencia"].mean(),
}).round(3)
""")

    nb.md("""
Funciona, e tem três problemas:

1. **seis variáveis** que existem só para chegar num resultado, e que continuam
   ocupando memória e atrapalhando a leitura do resto do notebook;
2. **nomes intermediários** como `com_regime` que não querem dizer nada e que
   você vai reaproveitar por engano daqui a três células;
3. **não escala**: se aparecesse um quarto regime, seria preciso escrever mais
   uma linha e lembrar de incluí-la no resultado.
""")

    nb.md("""
## A mesma coisa, encadeada

Agora o mesmo resultado, escrito como uma sequência:
""")

    nb.code("""
(
    criminal
    .query("classe == 'Apelação Criminal'")
    .dropna(subset=["regime_inicial"])
    .groupby("regime_inicial")
    .agg(proporcao=("houve_reincidencia", "mean"))
    .round(3)
)
""")

    nb.md("""
Leia de cima para baixo: pegue `criminal`, fique só com as apelações, descarte
quem não tem regime, junte por regime, e calcule a proporção. Nenhuma variável
intermediária, e a ordem das operações é a ordem das linhas.

### Por que os parênteses

Em Python, dentro de um par de parênteses você pode quebrar a linha à vontade.
Sem eles, `criminal` seguido de uma quebra de linha e `.query(...)` é erro de
sintaxe. Os parênteses existem só para deixar você pôr uma operação por linha.

O formato que vamos usar sempre é este:

```python
resultado = (
    tabela
    .operacao_1(...)
    .operacao_2(...)
)
```

Abre parêntese, o nome da tabela sozinho na primeira linha, e daí em diante uma
operação por linha, cada uma começando com ponto.
""")

    # ------------------------------------------------ os verbos

    nb.md("""
## Os verbos

São seis operações, e quase toda análise descritiva é uma combinação delas.

### 1. `.query()`: escolher linhas

Recebe a condição escrita como texto. Dentro das aspas, os nomes das colunas
aparecem sem `df[...]`, e o texto que você compara vai entre aspas simples.
""")

    nb.code("""
criminal.query("regime_inicial == 'fechado'").shape
""")

    nb.md("""
Para combinar condições, use `and`, `or` e `not`, por extenso:
""")

    nb.code("""
criminal.query("regime_inicial == 'fechado' and houve_reincidencia").shape
""")

    nb.faca(
        "Fique só com os acórdãos de tráfico em que houve confissão.",
        """
criminal.query("eh_trafico and houve_confissao").shape
""",
        """
criminal.query("eh_trafico ________ houve_confissao").shape
""",
    )

    nb.md("""
Para usar uma variável do Python dentro da condição, ponha `@` na frente dela:
""")

    nb.code("""
regime_alvo = "semiaberto"

criminal.query("regime_inicial == @regime_alvo").shape
""")

    nb.md("""
### 2. `.assign()`: criar colunas

`.assign(nome_da_coluna=...)` devolve uma cópia da tabela com a coluna nova. Ele
não altera a tabela original, e é por isso que serve para encadear.
""")

    nb.code("""
(
    criminal
    .assign(ementa_longa=criminal["n_palavras_ementa"] > 200)
    [["processo", "n_palavras_ementa", "ementa_longa"]]
    .head(3)
)
""")

    nb.md("""
Só que escrever `criminal[...]` lá dentro estraga o encadeamento: se antes do
`.assign` houve um filtro, `criminal` ainda é a tabela inteira, e as duas não
têm mais o mesmo número de linhas.

A solução é `lambda d:`, que quer dizer "a tabela como ela está **neste ponto**
da sequência". O `d` é só um nome, e podia ser qualquer outro.
""")

    nb.code("""
(
    criminal
    .query("regime_inicial == 'fechado'")
    .assign(ementa_longa=lambda d: d["n_palavras_ementa"] > 200)
    [["processo", "regime_inicial", "n_palavras_ementa", "ementa_longa"]]
    .head(3)
)
""")

    nb.faca(
        "Crie a coluna `pena_alta`, verdadeira quando `pena_anos` for maior que 8, "
        "usando `lambda`.",
        """
(
    criminal
    .assign(pena_alta=lambda d: d["pena_anos"] > 8)
    [["processo", "pena_anos", "pena_alta"]]
    .head(3)
)
""",
        """
(
    criminal
    .assign(pena_alta=lambda d: d["________"] > 8)
    [["processo", "pena_anos", "pena_alta"]]
    .head(3)
)
""",
    )

    nb.md("""
Dá para criar várias colunas de uma vez, separando por vírgula. E uma coluna
criada num `.assign` pode ser usada na seguinte, desde que seja com `lambda`:
""")

    nb.code("""
(
    criminal
    .assign(
        pena_meses=lambda d: d["pena_anos"] * 12,
        pena_meses_arredondada=lambda d: d["pena_meses"].round(0),
    )
    [["processo", "pena_anos", "pena_meses", "pena_meses_arredondada"]]
    .head(3)
)
""")

    nb.md("""
### 3. `.sort_values()`: ordenar

`by=` diz por qual coluna, e `ascending=False` inverte para o maior primeiro.
""")

    nb.code("""
(
    criminal
    .sort_values("n_palavras_ementa", ascending=False)
    [["processo", "comarca", "n_palavras_ementa"]]
    .head(5)
)
""")

    nb.faca(
        "Ordene pela pena, da maior para a menor, e olhe as cinco primeiras. Repare "
        "no que aparece: a leitura automática da pena erra em alguns acórdãos.",
        """
(
    criminal
    .sort_values("pena_anos", ascending=False)
    [["processo", "pena_anos", "regime_inicial"]]
    .head(5)
)
""",
        """
(
    criminal
    .sort_values("________", ascending=________)
    [["processo", "pena_anos", "regime_inicial"]]
    .head(5)
)
""",
    )

    nb.md("""
### 4. Escolher colunas

Duas chaves com uma lista de nomes dentro devolvem só aquelas colunas, na ordem
que você pediu. Já apareceu nos exemplos acima:
""")

    nb.code("""
(
    criminal
    [["processo", "comarca", "regime_inicial", "pena_anos"]]
    .head(3)
)
""")

    nb.md("""
### 5. `.groupby()` e `.agg()`: agregar por grupo

Esta é a operação nova de verdade. `.groupby("coluna")` separa a tabela em
pedaços, um por valor da coluna, e `.agg(...)` calcula uma estatística em cada
pedaço, devolvendo uma linha por grupo.

A forma de escrever é `nome_da_saida=("coluna_de_entrada", "estatistica")`:
""")

    nb.code("""
(
    criminal
    .groupby("regime_inicial")
    .agg(
        n=("processo", "size"),
        mediana_palavras=("n_palavras_ementa", "median"),
    )
)
""")

    nb.md("""
`"size"` conta as linhas do grupo. As outras estatísticas são as mesmas da aula
3, escritas como texto: `"mean"`, `"median"`, `"std"`, `"min"`, `"max"`,
`"sum"`, `"nunique"`.

E vale lembrar da aula 3: a média de uma coluna de verdadeiro e falso é a
proporção. Isso funciona igual dentro do `.agg`.
""")

    nb.faca(
        "Acrescente ao resumo acima a proporção de acórdãos com reincidência e a "
        "proporção de tráfico.",
        """
(
    criminal
    .groupby("regime_inicial")
    .agg(
        n=("processo", "size"),
        prop_reincidencia=("houve_reincidencia", "mean"),
        prop_trafico=("eh_trafico", "mean"),
    )
    .round(3)
)
""",
        """
(
    criminal
    .groupby("regime_inicial")
    .agg(
        n=("processo", "size"),
        prop_reincidencia=("houve_reincidencia", "________"),
        prop_trafico=("________", "mean"),
    )
    .round(3)
)
""",
    )

    nb.md("""
Dá para agrupar por mais de uma coluna, passando uma lista. O resultado ganha
uma linha por combinação:
""")

    nb.code("""
(
    criminal
    .groupby(["regime_inicial", "houve_confissao"])
    .agg(n=("processo", "size"))
    .head(6)
)
""")

    nb.md("""
### 6. `.reset_index()`: voltar a ser uma tabela comum

Depois de um `groupby`, a coluna de agrupamento vira o **índice** do resultado,
e não uma coluna normal. Repare que `regime_inicial` está fora da tabela, à
esquerda, em negrito. Isso atrapalha se você quiser continuar encadeando.
`.reset_index()` traz o índice de volta para dentro:
""")

    nb.code("""
(
    criminal
    .groupby("regime_inicial")
    .agg(n=("processo", "size"))
    .reset_index()
)
""")

    nb.md("""
Com o índice de volta, dá para filtrar e ordenar o resultado como qualquer outra
tabela, o que é justamente o que vamos fazer no pipeline completo.
""")

    # ------------------------------------------------ pipeline

    nb.md("""
## Montando o pipeline

Voltando à pergunta: a proporção de menção a reincidência varia conforme o
regime inicial?

Duas coisas ainda faltam. Primeiro, o regime é **ordinal**, e queremos a tabela
na ordem aberto, semiaberto, fechado, e não em ordem alfabética. Isso é a
categórica ordenada da aula 2, criada aqui dentro do `.assign`. Segundo,
`groupby` sobre categórica traz todas as categorias declaradas, e `observed=True`
mantém só as que aparecem.
""")

    nb.code("""
resumo = (
    criminal
    .query("classe == 'Apelação Criminal'")
    .dropna(subset=["regime_inicial"])
    .assign(
        regime=lambda d: pd.Categorical(
            d["regime_inicial"],
            categories=["aberto", "semiaberto", "fechado"],
            ordered=True,
        )
    )
    .groupby("regime", observed=True)
    .agg(
        n=("processo", "size"),
        prop_reincidencia=("houve_reincidencia", "mean"),
        prop_confissao=("houve_confissao", "mean"),
        prop_trafico=("eh_trafico", "mean"),
    )
    .round(3)
)

resumo
""")

    nb.md("""
A leitura é direta: a menção a reincidência sobe conforme o regime fica mais
severo. Isso não é surpresa, é quase a definição legal do regime, e serve para
conferir que a leitura das variáveis está coerente.

E o que **não** dá para concluir: nada sobre causalidade, e nada sobre acórdãos
em que o regime não foi identificado, que são cerca de 30% da base.
""")

    nb.faca(
        "Monte um resumo parecido, agora por `camara`, mantendo só as câmaras com "
        "pelo menos 15 acórdãos e ordenando da maior proporção de reincidência "
        "para a menor. Você vai precisar de `.reset_index()`, `.query()` e "
        "`.sort_values()` depois do `.agg()`.",
        """
(
    criminal
    .query("classe == 'Apelação Criminal'")
    .dropna(subset=["camara"])
    .groupby("camara")
    .agg(
        n=("processo", "size"),
        prop_reincidencia=("houve_reincidencia", "mean"),
    )
    .reset_index()
    .query("n >= 15")
    .sort_values("prop_reincidencia", ascending=False)
    .round(3)
)
""",
        """
(
    criminal
    .query("classe == 'Apelação Criminal'")
    .dropna(subset=["camara"])
    .groupby("________")
    .agg(
        n=("processo", "size"),
        prop_reincidencia=("houve_reincidencia", "________"),
    )
    .________()
    .query("n >= ________")
    .sort_values("________", ascending=False)
    .round(3)
)
""",
    )

    # ------------------------------------------------ erros comuns

    nb.md("""
## Quatro erros que você vai cometer

### 1. Esquecer o parêntese de abertura

Sem os parênteses, a quebra de linha encerra o comando:
""")

    nb.code("""
codigo = '''
criminal
.query("eh_trafico")
'''

try:
    exec(codigo)
except SyntaxError as erro:
    print("SyntaxError:", erro)
""")

    nb.md("""
### 2. Usar a tabela original dentro do encadeamento

Uma coluna criada no meio da sequência não existe na tabela original. Referir a
ela pelo nome da tabela levanta erro:
""")

    nb.code("""
try:
    (
        criminal
        .assign(pena_meses=lambda d: d["pena_anos"] * 12)
        .assign(pena_alta=criminal["pena_meses"] > 96)
    )
except KeyError as erro:
    print("KeyError:", erro)
""")

    nb.md("""
Este erro é o caso fácil, porque ele aparece. O caso difícil é quando **não**
aparece. Abaixo, as duas versões rodam sem reclamar, e dão resultados
diferentes: a da esquerda usa `criminal`, e o pandas casa as linhas pelo número
do índice, que depois do `reset_index` já não é o mesmo.
""")

    nb.code("""
errado = (
    criminal
    .query("regime_inicial == 'fechado'")
    .reset_index(drop=True)
    .assign(longa=criminal["n_palavras_ementa"] > 200)
)

certo = (
    criminal
    .query("regime_inicial == 'fechado'")
    .reset_index(drop=True)
    .assign(longa=lambda d: d["n_palavras_ementa"] > 200)
)

pd.Series({
    "linhas": len(certo),
    "em que as duas versões concordam": (errado["longa"] == certo["longa"]).mean(),
}).round(3)
""")

    nb.md("""
Quase 30% das linhas ficaram com o valor de outro acórdão, sem aviso nenhum.
Por isso a regra é sem exceção: dentro de um encadeamento, olhe para as colunas
com `lambda d:`, nunca pelo nome da tabela.
""")

    nb.md("""
### 3. Achar que `.assign` altera a tabela

`.assign` devolve uma cópia. Se você não guardar o resultado, a coluna não
existe fora do encadeamento:
""")

    nb.code("""
criminal.assign(teste=1)

"teste" in criminal.columns
""")

    nb.md("""
### 4. Encadear demais

Sequência com quinze operações é tão ruim de ler quanto quinze variáveis soltas.
Quando o encadeamento passar de umas oito linhas, ou quando um resultado
intermediário for usado em dois lugares, quebre em duas partes com um nome que
signifique alguma coisa, como fizemos com `resumo`.
""")

    # ------------------------------------------------ exercícios

    nb.md("""
## Exercícios

### Exercício 1

A pena lida da ementa tem valores implausíveis, como penas acima de 40 anos, que
vêm de a leitura pegar um número errado. Monte um encadeamento que descarte as
penas ausentes e as maiores que 30 anos, e devolva mediana, média e desvio
padrão da pena por regime inicial.
""")

    nb.code(
        """
(
    criminal
    .dropna(subset=["pena_anos", "regime_inicial"])
    .query("pena_anos <= 30")
    .groupby("regime_inicial")
    .agg(
        n=("processo", "size"),
        mediana=("pena_anos", "median"),
        media=("pena_anos", "mean"),
        desvio=("pena_anos", "std"),
    )
    .round(2)
)
""",
        """
(
    criminal
    .dropna(subset=["pena_anos", "regime_inicial"])
    .query("pena_anos ________ 30")
    .groupby("________")
    .agg(
        n=("processo", "size"),
        mediana=("pena_anos", "________"),
        media=("pena_anos", "mean"),
        desvio=("pena_anos", "________"),
    )
    .round(2)
)
""",
    )

    nb.md("""
### Exercício 2

Quais são as cinco comarcas com mais apelações criminais nesta base, e qual a
proporção de tráfico em cada uma?
""")

    nb.code(
        """
(
    criminal
    .query("classe == 'Apelação Criminal'")
    .groupby("comarca")
    .agg(n=("processo", "size"), prop_trafico=("eh_trafico", "mean"))
    .reset_index()
    .sort_values("n", ascending=False)
    .head(5)
    .round(3)
)
""",
        """
(
    criminal
    .query("classe == 'Apelação Criminal'")
    .groupby("________")
    .agg(n=("processo", "size"), prop_trafico=("eh_trafico", "________"))
    .reset_index()
    .sort_values("________", ascending=False)
    .head(________)
    .round(3)
)
""",
    )

    nb.md("""
### Exercício 3

Escreva, em duas ou três linhas, uma pergunta descritiva que **não** dá para
responder com esta base, e diga que variável faltaria. Não precisa programar.
""")

    nb.code("# exercício 3 (responda em célula de texto)")

    nb.md("""
## O que ficou

| verbo | para quê |
|---|---|
| `.query("...")` | escolher linhas por uma condição |
| `.dropna(subset=[...])` | descartar linhas sem valor numa coluna |
| `.assign(nova=lambda d: ...)` | criar coluna |
| `[["a", "b"]]` | escolher colunas |
| `.sort_values("a", ascending=False)` | ordenar |
| `.groupby("a").agg(saida=("b", "mean"))` | uma linha por grupo |
| `.reset_index()` | tirar o agrupamento do índice |
| `.head(n)` | cortar as primeiras linhas |

Duas regras que valem sempre: dentro do encadeamento, olhe para as colunas com
`lambda d:`, e não pelo nome da tabela original. E quando a sequência ficar
longa demais para caber na tela, quebre em duas.
""")

    return nb


# ====================================================== EXTRA


def montar_extra() -> Caderno:
    nb = Caderno("extra_filtros_plano_saude", so_completo=True)

    nb.md("""
# Material extra: filtrar e comparar proporções

Este notebook está **completo**, para estudo. Ele repete o roteiro das aulas 2 e
3 numa terceira base, e se aprofunda em duas coisas que ficaram apertadas em
aula: as maneiras de filtrar um DataFrame, e a comparação de proporções entre
grupos.

Rode célula a célula e, em cada bloco, tente prever o resultado antes de
executar.
""")

    nb.code(ABERTURA)

    nb.md("""
## A pergunta de pesquisa

> Nas apelações do TJSP sobre negativa de cobertura de plano de saúde, com que
> frequência o acórdão discute dano moral, e isso varia entre as câmaras de
> Direito Privado?

A pergunta tem três recortes embutidos: só **apelações**, só **câmaras de
Direito Privado**, e o desfecho é **discutir dano moral**.
""")

    nb.md("""
### De onde vieram os dados

```python
import juscraper as jus

tjsp = jus.scraper("tjsp")
acordaos = tjsp.cjsg('"plano de saude" E "negativa de cobertura"', paginas=range(1, 26))
```

Como na base da aula 3, as colunas `camara`, `secao`, `classe`, `assunto`,
`tem_dano_moral` e `n_palavras_ementa` foram lidas do texto antes da publicação.
""")

    nb.code("""
planos = pd.read_csv(f"{URL}/tjsp_cjsg_plano_saude.csv")
planos.head(3)
""")

    nb.code("""
planos.info()
""")

    nb.md("""
## Preparando os tipos

Duas conversões da aula 2: a data e as categóricas.
""")

    nb.code("""
planos["data_julgamento"] = pd.to_datetime(planos["data_julgamento"], format="%d/%m/%Y")
planos["data_publicacao"] = pd.to_datetime(planos["data_publicacao"], format="%d/%m/%Y")

planos["dias_ate_publicacao"] = (
    planos["data_publicacao"] - planos["data_julgamento"]
).dt.days

planos["dias_ate_publicacao"].describe()
""")

    nb.code("""
planos["classe"] = pd.Categorical(planos["classe"])

planos["classe"].value_counts()
""")

    nb.md("""
`camara` não veio preenchida em todas as linhas. Vale entender por quê antes de
filtrar: são os Núcleos de Justiça 4.0, que não são câmaras numeradas.
""")

    nb.code("""
planos["camara"].notna().mean().round(3)
""")

    nb.code("""
planos.loc[planos["camara"].isna(), "orgao_julgador"].value_counts().head()
""")

    nb.md("""
A pergunta fala em câmaras, então esses casos vão sair do recorte **por
decisão**, e não por acidente.
""")

    # ---------------------------------------------- filtros

    nb.md("""
## Filtrar: três jeitos de fazer a mesma coisa

### 1. Índice lógico

Uma comparação devolve uma série de `True` e `False` do mesmo tamanho do
DataFrame. É uma máscara, e não uma lista de posições:
""")

    nb.code("""
eh_apelacao = planos["classe"] == "Apelação Cível"

eh_apelacao.head()
""")

    nb.code("""
len(eh_apelacao), eh_apelacao.sum()
""")

    nb.code("""
planos[eh_apelacao].shape
""")

    nb.md("""
Combinando condições: `&` é "e", `|` é "ou", `~` é "não". Os parênteses são
obrigatórios, porque `&` tem precedência maior que `==`. Sem eles o Python tenta
avaliar a coisa errada e levanta erro, como no terceiro exemplo abaixo.
""")

    nb.code("""
sp_com_dano = planos[(planos["comarca"] == "São Paulo") & planos["tem_dano_moral"]]

len(sp_com_dano)
""")

    nb.code("""
sem_camara = planos[~planos["camara"].notna()]

len(sem_camara)
""")

    nb.code("""
try:
    planos[planos["comarca"] == "São Paulo" & planos["tem_dano_moral"]]
except TypeError as erro:
    print("TypeError:", erro)
""")

    nb.md("""
Três auxiliares que evitam condições longas:
""")

    nb.code("""
pd.Series({
    "isin": len(planos[planos["comarca"].isin(["São Paulo", "Campinas", "Santos"])]),
    "between": len(planos[planos["dias_ate_publicacao"].between(0, 7)]),
    "notna": len(planos[planos["camara"].notna()]),
})
""")

    nb.md("""
### 2. `.loc`

`.loc[linhas, colunas]` filtra e escolhe colunas na mesma expressão:
""")

    nb.code("""
planos.loc[eh_apelacao, ["processo", "camara", "secao", "tem_dano_moral"]].head()
""")

    nb.md("""
E é a forma que você **precisa** usar para atribuir. O `df[cond]["coluna"] = x`
mexe numa cópia temporária, então a alteração se perde:
""")

    nb.code("""
copia = planos.copy()
copia[copia["comarca"] == "Santos"]["comarca"] = "SANTOS"

(copia["comarca"] == "SANTOS").sum()
""")

    nb.code("""
copia.loc[copia["comarca"] == "Santos", "comarca"] = "SANTOS"

(copia["comarca"] == "SANTOS").sum()
""")

    nb.md("""
`.loc` fatia por **rótulo** do índice, e `.iloc` fatia por **posição**. A
diferença aparece no limite superior, que o `.loc` inclui e o `.iloc` não:
""")

    nb.code("""
pd.Series({
    ".loc[0:3]": len(planos.loc[0:3]),
    ".iloc[0:3]": len(planos.iloc[0:3]),
})
""")

    nb.md("""
### 3. `.query`

`.query` recebe a condição escrita como texto, e usa `@` para referir uma
variável do Python:
""")

    nb.code("""
planos.query("classe == 'Apelação Cível' and n_palavras_ementa > 150").shape
""")

    nb.code("""
limite = 150

planos.query("n_palavras_ementa > @limite and secao == 'Direito Privado'").shape
""")

    nb.md("""
Os três jeitos dão o mesmo resultado:
""")

    nb.code("""
a = planos[(planos["classe"] == "Apelação Cível") & (planos["secao"] == "Direito Privado")]
b = planos.loc[(planos["classe"] == "Apelação Cível") & (planos["secao"] == "Direito Privado")]
c = planos.query("classe == 'Apelação Cível' and secao == 'Direito Privado'")

len(a), len(b), len(c)
""")

    nb.md("""
Índice lógico é o mais explícito, `.loc` é o único seguro para atribuir, e
`.query` é o mais legível com muitas condições. Uma limitação do `.query`: nomes
de coluna com espaço ou acento precisam de crase, e nem toda expressão do pandas
funciona lá dentro.
""")

    nb.md("""
### O recorte da pergunta
""")

    nb.code("""
apelacoes = planos.query(
    "classe == 'Apelação Cível' and secao == 'Direito Privado'"
).dropna(subset=["camara"]).copy()

len(planos), len(apelacoes)
""")

    # ---------------------------------------------- proporções

    nb.md("""
## Proporções comparadas entre grupos

`tem_dano_moral` é binária, então a média é a proporção:
""")

    nb.code("""
apelacoes["tem_dano_moral"].mean().round(3)
""")

    nb.code("""
apelacoes["tem_dano_moral"].value_counts(normalize=True).round(3)
""")

    nb.md("""
Para variável nominal, o que existe é contagem e proporção:
""")

    nb.code("""
apelacoes["camara"].value_counts().head(8)
""")

    nb.md("""
`pd.crosstab` faz a tabela de duas entradas. Sem `normalize`, ela traz
contagens:
""")

    nb.code("""
pd.crosstab(apelacoes["camara"], apelacoes["tem_dano_moral"]).head()
""")

    nb.md("""
Com `normalize="index"`, cada linha soma 1, e a tabela passa a mostrar a
proporção dentro de cada câmara:
""")

    nb.code("""
pd.crosstab(
    apelacoes["camara"], apelacoes["tem_dano_moral"], normalize="index"
).round(3).head()
""")

    nb.md("""
`normalize="columns"` divide pela coluna e `normalize=True` divide pelo total
geral. Trocar um pelo outro muda completamente a leitura, e é um erro comum em
relatório. Compare:
""")

    nb.code("""
pd.crosstab(apelacoes["secao"], apelacoes["tem_dano_moral"], normalize="index").round(3)
""")

    nb.code("""
pd.crosstab(apelacoes["secao"], apelacoes["tem_dano_moral"], normalize=True).round(3)
""")

    nb.md("""
Uma câmara com poucos acórdãos tem proporção instável, e mostrar isso ao lado
das outras engana. Vale sempre olhar a contagem junto da proporção:
""")

    nb.code("""
contagem = apelacoes["camara"].value_counts()
proporcao = pd.crosstab(
    apelacoes["camara"], apelacoes["tem_dano_moral"], normalize="index"
)[True]

pd.DataFrame({"n": contagem, "proporcao": proporcao.round(3)}).sort_values(
    "proporcao", ascending=False
).head(10)
""")

    nb.md("""
## Antes de concluir qualquer coisa

A tabela acima mostra proporções que vão de cerca de 0,20 a 0,52. Antes de dizer
que as câmaras decidem diferente, considere:

1. **A medida é grosseira.** `tem_dano_moral` marca a ementa que *menciona* dano
   moral, inclusive para negar. Uma câmara que escreve ementa mais longa tende a
   mencionar mais coisas.
2. **A distribuição de casos não é aleatória.** Cada câmara recebe um perfil
   diferente de recurso, por sorteio, por prevenção e por comarca de origem.
3. **O tamanho do grupo importa.** Com 13 acórdãos, uma proporção de 0,46 muda
   para 0,38 se um único caso for classificado diferente.
4. **A amostra é o que a busca devolveu**, e não todos os acórdãos do tribunal
   sobre o tema.

Nenhum desses pontos invalida o exercício. Todos precisam estar escritos no
relatório.
""")

    nb.md("""
## Para praticar

1. Refaça a tabela por câmara usando apenas acórdãos julgados em 2026.
2. Compare a mediana de `n_palavras_ementa` entre as câmaras com maior e menor
   proporção de menção a dano moral. Elas escrevem ementas de tamanhos
   diferentes?
3. A base tem uma coluna `valor_indenizacao`, preenchida em cerca de um quarto
   das linhas. Monte o recorte com valor e calcule mediana e IQR.
""")

    nb.code("# espaço para praticar")

    return nb


# ====================================================== main


def main() -> None:
    for construir in (montar_aula02, montar_aula03, montar_aula04, montar_extra):
        caderno = construir()
        print(f"{caderno.nome}:")
        caderno.gravar()


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    main()
