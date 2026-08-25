"""Gera os notebooks das aulas 2 e 3, e o material extra.

Sai daqui:
    notebooks/aula02_professor.ipynb   tipos de variaveis (DataJud)
    notebooks/aula02_aluno.ipynb
    notebooks/aula03_professor.ipynb   filtro e estatistica descritiva (CJSG)
    notebooks/aula03_aluno.ipynb
    notebooks/aula04_professor.ipynb   encadeamento de operacoes (CJSG criminal)
    notebooks/aula04_aluno.ipynb
    notebooks/aula05_professor.ipynb   gramatica de graficos (plotnine)
    notebooks/aula05_aluno.ipynb
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
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "notebooks"

# A secao da gincana no notebook da aula 5 sai da mesma fonte que os slides e o
# app: `atividades/gincana.py`. Assim o enunciado nao tem como sair de sincronia.
sys.path.insert(0, str(RAIZ / "atividades"))
from gincana import (  # noqa: E402
    TUDO as TUDO_GINCANA, codigo_rodada as CODIGO_RODADA,
    eh_aquecimento as EH_AQUECIMENTO, n_cartas as N_CARTAS, rotulo as ROTULO,
)

URL_FIGURAS = "https://jtrecenti.github.io/cdad2-202662/gincana/figuras"

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
        self.md(f"**✍️ Agora você.** {enunciado.strip()}")
        self.code(professor, aluno)

    # ---------------------------------------------- estilo (padrao cdadeng)

    def cabecalho(self, titulo: str, aula: str, objetivos: list[str],
                  abertura: str = "") -> None:
        """Titulo centralizado, numero da aula e objetivos de aprendizagem."""
        alvos = "\n".join(f" * {o}" for o in objetivos)
        extra = f"\n{abertura.strip()}\n" if abertura else ""
        self.md(f"""
___
# <center>{titulo}</center>
___

## {aula}

**Objetivo da aula:** ao final desta aula, você deve ser capaz de:

{alvos}
{extra}""")

    def indice(self, itens: list) -> None:
        """Indice com ancoras. Cada item e (texto, ancora) ou (texto, ancora, subs)."""
        linhas = ["___", '<div id="indice"></div>', "", "## Índice", ""]
        for item in itens:
            texto, ancora = item[0], item[1]
            linhas.append(f"- [{texto}](#{ancora})")
            for sub_texto, sub_ancora in (item[2] if len(item) > 2 else []):
                linhas.append(f"    - [{sub_texto}](#{sub_ancora})")
            linhas.append("")
        self.md("\n".join(linhas))

    def secao(self, ancora: str, titulo: str, texto: str = "") -> None:
        corpo = f"\n\n{texto.strip()}" if texto else ""
        self.md(f'___\n<div id="{ancora}"></div>\n\n# {titulo}{corpo}')

    def sub(self, ancora: str, titulo: str, texto: str = "") -> None:
        corpo = f"\n\n{texto.strip()}" if texto else ""
        self.md(f'<div id="{ancora}"></div>\n\n### {titulo}{corpo}')

    def operacao(self, nome: str, sintaxe: str, doc: str,
                 texto: str = "") -> None:
        """Bloco ✔️ Uso do metodo: sintaxe geral e link para a documentacao."""
        corpo = f"{texto.strip()}\n\n" if texto else ""
        self.md(f"""
{corpo}✔️ **Uso do `{nome}`**

```python
# Sintaxe geral:
{sintaxe.strip()}
```

Documentação oficial: [{nome}]({doc})
""")

    def exercicio(self, numero: int, ancora: str, enunciado: str) -> None:
        self.md(f'<div id="{ancora}"></div>\n\n### EXERCÍCIO {numero}\n\n{enunciado.strip()}')

    def volta(self) -> None:
        self.md("[Volta ao Índice](#indice)")

    def resumo(self, texto: str) -> None:
        self.md(f'___\n<div id="resumo"></div>\n\n# RESUMO\n\n{texto.strip()}')

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

    nb.cabecalho(
        "Atividade: Tipos de Variáveis",
        "Aula 02",
        [
            "identificar o tipo de cada variável de uma base jurídica;",
            "distinguir o *dtype* do pandas da natureza estatística da variável;",
            "converter uma coluna de um tipo para outro;",
            "declarar variáveis categóricas, com e sem ordem.",
        ],
        abertura="""
**Como este notebook funciona:** cada operação nova aparece primeiro resolvida e
comentada. Logo depois vem um bloco **✍️ Agora você**, com uma célula em que
faltam pedaços, marcados por `________`, para você completar com a mesma
operação em outra coluna.
""",
    )

    nb.indice([
        ("Processos de saúde no TJSP", "problema"),
        ("Tipos de variáveis", "tipos", [
            ("EXERCÍCIO 1: classifique as variáveis", "ex1"),
        ]),
        ("O que o pandas achou de cada coluna", "primeiro-olhar", [
            ("🔎 Olhando o dtype e a contagem de valores distintos", "info"),
            ("⚠️ O dtype não é o tipo da variável", "dtype"),
            ("🚩 Variável que não varia", "constante"),
        ]),
        ("Convertendo o tipo de uma coluna", "converter", [
            ("🔤 De número para texto", "astype"),
            ("📅 De texto para data", "datas"),
            ("➖ Subtraindo duas datas", "subtracao"),
            ("EXERCÍCIO 2: o tempo até a última movimentação", "ex2"),
        ]),
        ("Variáveis categóricas", "categoricas", [
            ("🏷️ Declarando a variável como categórica", "categorical"),
            ("🔢 Declarando a ordem das categorias", "ordinal"),
            ("🕳️ Valor faltante e a categoria Outros", "outros"),
        ]),
        ("✂️ De numérica para categórica com pd.cut", "cut", [
            ("EXERCÍCIO 3: quantos passaram de seis meses", "ex3"),
        ]),
        ("Respondendo à pergunta", "resposta", [
            ("EXERCÍCIO 4: uma variável derivada", "ex4"),
        ]),
        ("RESUMO", "resumo"),
    ])

    # ------------------------------------------------ problema

    nb.secao("problema", "Processos de saúde no TJSP", """
Uma pesquisa empírica em Direito termina numa tabela. Quem decide o que vira
coluna dessa tabela é você, e cada coluna é uma **variável**.

A pergunta que vamos perseguir hoje é esta:

> Entre 2023 e 2025, como se distribuem no TJSP os processos com assunto de
> saúde (medicamento, tratamento médico-hospitalar, plano de saúde): em que grau
> tramitam, de que classe são, e quanto tempo passa entre o ajuizamento e a
> última movimentação registrada?

Repare que a pergunta já obriga a decidir coisas. "Quanto tempo" pede uma
variável numérica que **não existe** na base e vai precisar ser construída.

**As variáveis da base têm os seguintes significados:**

* `numero_processo`: identificador do processo no CNJ.
* `tribunal`: sigla do tribunal.
* `grau`: instância em que o processo tramita (G1, G2 ou JE).
* `classe` e `classe_codigo`: tipo de ação, por extenso e em código.
* `assunto` e `n_assuntos`: matéria discutida e quantos assuntos o processo tem.
* `orgao_julgador`: vara ou câmara responsável.
* `municipio_ibge`: código IBGE do município.
* `sistema`: sistema processual em que o processo corre (SAJ, Projudi, PJe).
* `formato`: eletrônico ou físico.
* `nivel_sigilo`: grau de segredo de justiça.
* `data_ajuizamento`: data em que o processo foi distribuído.
* `data_ultima_atualizacao`: data da última movimentação registrada.

A base saiu da API pública do DataJud (CNJ), pela biblioteca
[juscraper](https://github.com/jtrecenti/juscraper). O código abaixo foi rodado
uma vez e está aqui só para você conhecer a origem da tabela. **Não precisa
rodar.**

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

    nb.code(ABERTURA)

    nb.md("**Carregando os dados a partir do repositório da disciplina:**")

    nb.code("""
saude = pd.read_csv(f"{URL}/tjsp_datajud_saude.csv")
saude.head()
""")

    nb.code("""
saude.shape
""")

    nb.volta()

    # ------------------------------------------------ tipos

    nb.secao("tipos", "Tipos de variáveis", """
Antes de qualquer conta, é preciso **entender a natureza de cada variável**.
Essa classificação não está no arquivo: ela é uma decisão sua, e é ela que
determina que conta faz sentido.

🔹 **IDENTIFICADOR** <br>
> Serve para localizar o caso, não para medir nada. Nunca entra em conta.<br>
> *Exemplos:* `numero_processo`, `municipio_ibge`.

🔹 **CATEGÓRICA NOMINAL** <br>
> Rótulos sem nenhuma ordem natural entre si.<br>
> *Exemplos:* `sistema` (SAJ, Projudi), `classe` (Procedimento Comum, Execução).

🔹 **CATEGÓRICA ORDINAL** <br>
> Rótulos com ordem natural, mas sem distância mensurável entre eles.<br>
> *Exemplo:* `grau` (G1 vem antes de G2).

🔹 **CATEGÓRICA BINÁRIA** <br>
> Só dois valores possíveis. É um caso particular da nominal, e ganha nome
> próprio porque permite contas que as outras não permitem.<br>
> *Exemplo:* `formato` (eletrônico, físico).

🔹 **NUMÉRICA DISCRETA** <br>
> Resultado de **contar**. Assume valores inteiros e isolados.<br>
> *Exemplo:* `n_assuntos`.

🔹 **NUMÉRICA CONTÍNUA** <br>
> Resultado de **medir** numa escala. Entre dois valores sempre cabe outro.<br>
> *Exemplo:* nenhuma ainda nesta base, vamos criar uma.

🔹 **DATA** <br>
> Não é bem um tipo da lista: é matéria-prima. O que entra na análise é o que
> se calcula a partir dela.<br>
> *Exemplos:* `data_ajuizamento`, `data_ultima_atualizacao`.
""")

    nb.exercicio(1, "ex1", """
Classifique cada variável da base preenchendo o dicionário abaixo. As três
primeiras estão preenchidas como modelo.
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

    nb.volta()

    # ------------------------------------------------ primeiro olhar

    nb.secao("primeiro-olhar", "O que o pandas achou de cada coluna", """
Ao ler o arquivo, o pandas atribui a cada coluna um **dtype**, que é o tipo de
armazenamento dele. Cuidado com a palavra "tipo": o dtype é um chute do pandas
a partir do formato do arquivo, e não a natureza da variável.
""")

    nb.sub("info", "🔎 Olhando o dtype e a contagem de valores distintos")

    nb.operacao(
        ".info()",
        "DataFrame.info()",
        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.info.html",
        "Mostra, para cada coluna, quantos valores não são nulos e qual o dtype.",
    )

    nb.code("""
saude.info()
""")

    nb.operacao(
        ".nunique()",
        "DataFrame.nunique()",
        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.nunique.html",
        "Conta quantos valores distintos existem em cada coluna. É a segunda coisa "
        "a olhar, e já adianta muito sobre o tipo de cada variável.",
    )

    nb.code("""
saude.nunique()
""")

    nb.sub("dtype", "⚠️ O dtype não é o tipo da variável", """
Estas quatro colunas vieram todas como número:
""")

    nb.code("""
saude[["classe_codigo", "municipio_ibge", "nivel_sigilo", "n_assuntos"]].dtypes
""")

    nb.md("E o pandas deixa você fazer esta conta sem reclamar:")

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

> 🤔 **Regra prática:** se somar dois valores da variável não produz nada com
> sentido, ela não é numérica, por mais que seja escrita com dígitos.
""")

    nb.sub("constante", "🚩 Variável que não varia", """
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

    nb.volta()

    # ------------------------------------------------ conversões

    nb.secao("converter", "Convertendo o tipo de uma coluna", """
O pandas leu o arquivo do jeito que conseguiu. Agora cabe a você ajustar cada
coluna para que ela represente a variável que você identificou no Exercício 1.
""")

    nb.sub("astype", "🔤 De número para texto")

    nb.operacao(
        ".astype()",
        'DataFrame["coluna"] = DataFrame["coluna"].astype("string")',
        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html",
        "Converte a coluna para outro tipo. O método devolve uma **cópia**, então é "
        "preciso reatribuir o resultado à própria coluna. Fazemos isso com códigos, "
        "para que ninguém calcule média deles por acidente.",
    )

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

    nb.sub("datas", "📅 De texto para data", """
No arquivo, data é texto. Enquanto for texto, `2024-03-15` é só uma sequência de
caracteres: não dá para subtrair, nem ordenar direito, nem pedir o ano.
""")

    nb.operacao(
        "pd.to_datetime()",
        'DataFrame["coluna"] = pd.to_datetime(DataFrame["coluna"])',
        "https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html",
    )

    nb.code("""
saude["data_ajuizamento"].head(3)
""")

    nb.code("""
saude["data_ajuizamento"] = pd.to_datetime(saude["data_ajuizamento"])

saude["data_ajuizamento"].head(3)
""")

    nb.md("Repare no que mudou: o dtype passou de `object` para `datetime64[ns]`.")

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

    nb.operacao(
        ".dt",
        'DataFrame["coluna"].dt.year',
        "https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.year.html",
        "Data é matéria-prima: o que entra na análise é o que se calcula a partir "
        "dela. O acessador `.dt` dá acesso aos pedaços da data, como `.dt.year` "
        "(ano), `.dt.month` (mês) e `.dt.day` (dia).",
    )

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

    nb.sub("subtracao", "➖ Subtraindo duas datas", """
Esta base não traz nenhuma variável de tempo pronta. A duração que a pergunta
pede precisa ser construída, e ela sai da subtração de duas datas.
""")

    nb.operacao(
        ".dt.days",
        '(DataFrame["data_fim"] - DataFrame["data_inicio"]).dt.days',
        "https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.days.html",
        "Subtrair duas datas devolve um `Timedelta`, que é uma duração. Para virar "
        "número é preciso escolher a unidade, e `.dt.days` devolve a duração em dias.",
    )

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
Pronto: a **primeira variável numérica contínua** da base, e ela não existia no
arquivo. Foi você que a criou.
""")

    nb.operacao(
        ".describe()",
        'DataFrame["coluna"].describe()',
        "https://pandas.pydata.org/docs/reference/api/pandas.Series.describe.html",
        "Dá um resumo rápido de uma coluna numérica: contagem, média, desvio "
        "padrão, mínimo, quartis e máximo.",
    )

    nb.code("""
saude["dias_ate_atualizacao"].describe()
""")

    nb.exercicio(2, "ex2", """
Olhando o resultado de `.describe()` acima, responda em uma ou duas frases: o
tempo até a última movimentação parece bem distribuído, ou há sinal de casos
muito fora do padrão? Em que número você se baseou?
""")

    nb.code("# ESCREVA SUA RESPOSTA AQUI (em comentário ou em célula de texto)")

    nb.volta()

    # ------------------------------------------------ categóricas

    nb.secao("categoricas", "Variáveis categóricas", """
Categórica é o tipo mais comum no Direito e o mais chato de representar. Por
padrão o pandas guarda texto (`object`), o que funciona, mas perde duas coisas:
**quais são as categorias possíveis** e **se existe ordem entre elas**.
""")

    nb.sub("categorical", "🏷️ Declarando a variável como categórica")

    nb.operacao(
        "pd.Categorical()",
        'DataFrame["coluna"] = pd.Categorical(DataFrame["coluna"])',
        "https://pandas.pydata.org/docs/reference/api/pandas.Categorical.html",
        "Declara a coluna como categórica e guarda, junto dela, a lista de "
        "categorias possíveis.",
    )

    nb.code("""
saude["assunto"] = pd.Categorical(saude["assunto"])

saude["assunto"].dtype
""")

    nb.operacao(
        ".cat.categories",
        'DataFrame["coluna"].cat.categories',
        "https://pandas.pydata.org/docs/reference/api/pandas.Series.cat.categories.html",
        "Mostra os rótulos que a variável categórica conhece.",
    )

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

    nb.sub("ordinal", "🔢 Declarando a ordem das categorias", """
Quando existe ordem natural, ela precisa ser declarada: o pandas não adivinha.
""")

    nb.operacao(
        "pd.Categorical(categories=, ordered=)",
        'DataFrame["coluna"] = pd.Categorical(\n'
        '    DataFrame["coluna"],\n'
        '    categories=["menor", "meio", "maior"],\n'
        "    ordered=True,\n"
        ")",
        "https://pandas.pydata.org/docs/reference/api/pandas.Categorical.html",
        "`categories=` recebe os rótulos **na ordem certa** e `ordered=True` diz "
        "que essa ordem vale. `grau` tem G1 (primeiro grau) e G2 (segundo grau).",
    )

    nb.code("""
saude["grau_ordenado"] = pd.Categorical(
    saude["grau"], categories=["G1", "G2"], ordered=True
)

saude["grau_ordenado"].dtype
""")

    nb.md("""
Com `ordered=True`, comparação e ordenação passam a funcionar: dá para comparar
a coluna com o nome de uma categoria usando `>`, `>=`, `<` e `<=`.
""")

    nb.code("""
(saude["grau_ordenado"] >= "G2").sum()
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
> ⚠️ **Armadilha 1.** Todo valor fora da lista de categorias vira valor faltante,
> **em silêncio**. Isso é útil (declara o universo esperado) e perigoso (perde
> dado sem avisar). Confira sempre quantos viraram faltante depois de criar a
> categórica.

Aqui a perda é intencional: `JE` não fica nem antes nem depois de G1 e G2, é
outra coisa.
""")

    nb.sub("outros", "🕳️ Valor faltante e a categoria Outros", """
A coluna `assunto` tem processos sem assunto informado. Juntar esses casos numa
categoria explícita costuma ser melhor do que deixá-los faltantes: a categoria
aparece nas contagens e ninguém esquece que ela existe.

A tentação é chamar `.fillna("Outros")` direto, mas isso levanta erro: `Outros`
não está na lista de categorias declaradas. É preciso abrir espaço para a
categoria antes.
""")

    nb.operacao(
        ".cat.add_categories()",
        'DataFrame["coluna"] = (\n'
        '    DataFrame["coluna"].cat.add_categories(["Outros"]).fillna("Outros")\n'
        ")",
        "https://pandas.pydata.org/docs/reference/api/pandas.Series.cat.add_categories.html",
        "Acrescenta rótulos à lista de categorias. Encadeando com `.fillna()`, os "
        "faltantes passam a cair na categoria nova.",
    )

    nb.code("""
saude["assunto"].isna().sum()
""")

    nb.code("""
saude["assunto"] = saude["assunto"].cat.add_categories(["Outros"]).fillna("Outros")

saude["assunto"].isna().sum()
""")

    nb.code("""
saude["assunto"].value_counts()
""")

    nb.md("""
> ⚠️ **Armadilha 2.** `value_counts()` em categórica mostra **todas** as
> categorias declaradas, inclusive as com zero ocorrências. Ótimo para tabela (a
> linha existe mesmo com zero) e péssimo se você não esperava.
""")

    nb.volta()

    # ------------------------------------------------ pd.cut

    nb.secao("cut", "✂️ De numérica para categórica com pd.cut", """
Até aqui convertemos texto em data e número em texto. Falta o caminho de volta:
transformar uma variável **numérica** em **categórica ordinal**, agrupando os
valores em faixas.
""")

    nb.operacao(
        "pd.cut()",
        'DataFrame["faixa"] = pd.cut(\n'
        '    DataFrame["coluna_numerica"],\n'
        "    bins=[limite1, limite2, limite3],\n"
        '    labels=["faixa A", "faixa B"],\n'
        ")",
        "https://pandas.pydata.org/docs/reference/api/pandas.cut.html",
        "`bins` são os pontos de corte e `labels` são os nomes das faixas. O "
        "resultado já sai como categórica **ordenada**.",
    )

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

> 🤔 Cortar em faixas **perde informação**: 31 dias e 179 dias viram a mesma
> coisa. Faça isso quando a faixa for o que interessa para a pergunta, não por
> hábito.
""")

    nb.exercicio(3, "ex3", """
Como `faixa_dias` é ordenada, dá para comparar com o nome de uma faixa, do mesmo
jeito que fizemos com `grau_ordenado >= "G2"`. Conte quantos processos
demoraram mais de seis meses.
""")

    nb.code(
        """
(saude["faixa_dias"] > "1 a 6 meses").sum()
""",
        """
(saude["faixa_dias"] ________ "1 a 6 meses").sum()
""",
    )

    nb.volta()

    # ------------------------------------------------ fechamento

    nb.secao("resposta", "Respondendo à pergunta", """
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
        "Faça o mesmo para o segundo grau, criando `segundo_grau` do mesmo jeito.",
        """
segundo_grau = saude[saude["grau"] == "G2"]

segundo_grau["dias_ate_atualizacao"].median()
""",
        """
segundo_grau = saude[saude["grau"] == "________"]

segundo_grau["dias_ate_atualizacao"].________()
""",
    )

    nb.exercicio(4, "ex4", """
A coluna `orgao_julgador` tem mais de mil valores distintos. Ela é categórica
nominal, mas com tantas categorias não serve para comparar grupos. Escreva, em
duas ou três linhas, que variável derivada dela você criaria para que ela
virasse útil, e por quê. Não precisa programar.
""")

    nb.code("# ESCREVA SUA RESPOSTA AQUI (em comentário ou em célula de texto)")

    nb.volta()

    # ------------------------------------------------ resumo

    nb.resumo("""
O **dtype** é o chute do pandas a partir do formato do arquivo. O **tipo da
variável** é decisão sua, e é ele que determina que conta faz sentido. Ajustar
um ao outro é o trabalho desta aula.

Abaixo, todas as operações da aula em sequência, para consulta rápida.
""")

    nb.code("""
#=> LER A BASE
saude = pd.read_csv(f"{URL}/tjsp_datajud_saude.csv")

#=> OLHAR: dtype de cada coluna e quantos valores distintos
saude.info()
saude.nunique()

#=> NÚMERO -> TEXTO: para códigos, que não devem entrar em conta
saude["classe_codigo"] = saude["classe_codigo"].astype("string")

#=> NÚMERO COM FALTANTE -> TEXTO: passa por "Int64" para não carregar o ".0"
saude["municipio_ibge"] = saude["municipio_ibge"].astype("Int64").astype("string")

#=> TEXTO -> DATA
saude["data_ajuizamento"] = pd.to_datetime(saude["data_ajuizamento"])
saude["data_ultima_atualizacao"] = pd.to_datetime(saude["data_ultima_atualizacao"])

#=> DATA -> NÚMERO: pedaços da data com .dt
saude["ano_ajuizamento"] = saude["data_ajuizamento"].dt.year

#=> DUAS DATAS -> DURAÇÃO EM DIAS
saude["dias_ate_atualizacao"] = (
    saude["data_ultima_atualizacao"] - saude["data_ajuizamento"]
).dt.days

#=> TEXTO -> CATEGÓRICA NOMINAL
saude["assunto"] = pd.Categorical(saude["assunto"])

#=> TEXTO -> CATEGÓRICA ORDINAL: categories na ordem certa e ordered=True
saude["grau_ordenado"] = pd.Categorical(
    saude["grau"], categories=["G1", "G2"], ordered=True
)

#=> FALTANTE -> CATEGORIA "Outros": abre espaço antes de preencher
saude["assunto"] = saude["assunto"].cat.add_categories(["Outros"]).fillna("Outros")

#=> NUMÉRICA -> CATEGÓRICA ORDINAL: faixas com pd.cut
saude["faixa_dias"] = pd.cut(
    saude["dias_ate_atualizacao"],
    bins=[-float("inf"), 30, 180, 365, float("inf")],
    labels=["até 1 mês", "1 a 6 meses", "6 a 12 meses", "mais de 1 ano"],
)
""")

    nb.md("""
**Duas armadilhas para levar daqui:**

1. Valor fora da lista de `categories` vira faltante **em silêncio**. Confira com
   `.isna().sum()` depois de criar uma categórica.
2. `value_counts()` em categórica mostra também as categorias com zero casos.

Na aula 3 vamos usar esses tipos para escolher a estatística certa.
""")

    nb.volta()

    return nb


# ====================================================== AULA 3


def montar_aula03() -> Caderno:
    nb = Caderno("aula03")

    nb.cabecalho(
        "Atividade: Filtrar e Resumir",
        "Aula 03",
        [
            "distinguir variável, valor observado e estatística;",
            "recortar uma base com índice lógico, justificando o recorte;",
            "escolher a medida de posição e de dispersão adequadas ao tipo da variável;",
            "reconhecer que a média de uma variável binária é uma proporção.",
        ],
        abertura="""
Na aula 2 arrumamos os tipos de uma base. Agora vamos usar esses tipos para duas
coisas: **recortar** o que entra na análise e **resumir** a coluna em um número.

O notebook segue o mesmo formato: cada operação aparece primeiro resolvida, e
depois vem um bloco **✍️ Agora você** com a mesma operação em outra coluna.
""",
    )

    nb.indice([
        ("Indenização por dano moral no TJSP", "problema", [
            ("As colunas que vieram do texto", "colunas-texto"),
            ("EXERCÍCIO 1: uma variável que falta", "ex1"),
        ]),
        ("Preparando a base", "preparo", [
            ("🏷️ Retomando: que tipo é cada coluna", "tipos"),
            ("📅 Convertendo as datas", "datas"),
        ]),
        ("Variável, valor observado e estatística", "conceitos"),
        ("Filtrar", "filtrar", [
            ("🎭 Índice lógico", "mascara"),
            ("🔗 Combinando condições", "combinar"),
            ("📍 E o .loc, qual a diferença?", "loc"),
            ("✂️ O recorte da pergunta", "recorte"),
        ]),
        ("Medidas de posição", "posicao", [
            ("📊 Média e mediana", "media"),
            ("📐 Quantis e o intervalo interquartílico", "quantis"),
        ]),
        ("Medidas de dispersão", "dispersao", [
            ("〽️ Desvio padrão e coeficiente de variação", "desvio"),
        ]),
        ("A média de uma binária é uma proporção", "binaria"),
        ("Cada tipo, sua estatística", "tabela-tipos"),
        ("Respondendo à pergunta", "resposta", [
            ("EXERCÍCIO 2: o que dizer na metodologia", "ex2"),
        ]),
        ("RESUMO", "resumo"),
    ])

    # ------------------------------------------------ problema

    nb.secao("problema", "Indenização por dano moral no TJSP", """
A pergunta de hoje:

> Nos acórdãos do TJSP que arbitram indenização por dano moral, qual é o valor
> típico, e quanto ele varia?

"Valor típico" e "quanto varia" são as duas perguntas que a estatística
descritiva responde: uma medida de **posição** e uma medida de **dispersão**.
Escolher qual é o conteúdo da aula.

**As variáveis da base:**

* `processo`, `cd_acordao`: identificadores do acórdão.
* `classe`, `assunto`, `relator`, `comarca`, `orgao_julgador`: dados do julgamento.
* `camara`, `secao`: número da câmara e seção, lidos do órgão julgador.
* `data_julgamento`, `data_publicacao`: datas, no formato brasileiro.
* `valor_indenizacao`: valor em reais arbitrado, lido da ementa.
* `tem_dano_moral`, `houve_majoracao`: indicadores lidos da ementa.
* `n_palavras_ementa`: tamanho da ementa.
* `ementa`: o texto do resumo do acórdão.

A base foi coletada com a biblioteca
[juscraper](https://github.com/jtrecenti/juscraper). **Não precisa rodar:**

```python
import juscraper as jus

tjsp = jus.scraper("tjsp")
acordaos = tjsp.cjsg('"dano moral" E "arbitro a indenizacao"', paginas=range(1, 26))
```
""")

    nb.code(ABERTURA)

    nb.code("""
danos = pd.read_csv(f"{URL}/tjsp_cjsg_dano_moral.csv")
danos.head(3)
""")

    nb.code("""
danos.info()
""")

    nb.sub("colunas-texto", "As colunas que vieram do texto", """
Quatro colunas desta base não vieram prontas do tribunal: foram **lidas do texto
da ementa** antes de o arquivo ser publicado. A ferramenta que faz isso é a
expressão regular, assunto da aula 12. Aqui interessa o que essas definições
custam:

- `valor_indenizacao` pega o **primeiro** valor em reais da ementa. Nem sempre é
  o valor arbitrado: pode ser o pedido, o da sentença reformada, ou custas;
- `tem_dano_moral` marca a ementa que **menciona** dano moral, inclusive para
  dizer que não é caso de indenizar.

Nenhuma das duas invalida o exercício. As duas mudam o que se pode concluir, e
por isso precisam estar escritas no relatório.
""")

    nb.code("""
danos.loc[[0], ["processo", "valor_indenizacao", "tem_dano_moral", "houve_majoracao"]]
""")

    nb.exercicio(1, "ex1", """
Escolha uma variável que você gostaria de ter nesta tabela e que não está lá.
Escreva o nome dela, o tipo, e a instrução que faria duas pessoas lerem a mesma
ementa e registrarem o mesmo valor. Não precisa programar. Este é exatamente o
trabalho que o Projeto 1 vai pedir hoje.
""")

    nb.code("# ESCREVA SUA RESPOSTA AQUI (em comentário ou em célula de texto)")

    nb.volta()

    # ------------------------------------------------ preparo

    nb.secao("preparo", "Preparando a base", """
Mesma rotina da aula 2: identificar o tipo de cada variável e ajustar as colunas
que precisam de conversão.
""")

    nb.sub("tipos", "🏷️ Retomando: que tipo é cada coluna", """
Duas já estão preenchidas como modelo.
""")

    nb.code(
        """
tipos = {
    "processo": "identificador",
    "ementa": "texto",
    "comarca": "categorica_nominal",
    "orgao_julgador": "categorica_nominal",
    "camara": "identificador",
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
    "orgao_julgador": "________",
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
> 🤔 `camara` é o caso interessante desta tabela, e a resposta mais óbvia não é a
> melhor. Ela é escrita com dígitos e não é número de medir: a 13ª câmara não é
> maior nem vem depois da 2ª. Até aí, categórica nominal daria conta.
>
> O que muda a resposta é `orgao_julgador` estar na tabela ao lado. `camara` e
> `secao` foram **lidas dele**, e não medem atributo nenhum do acórdão: repetem,
> em pedaços, o nome do órgão que julgou. E `camara` sozinha nem chega a nomear um
> órgão, porque existem a 6ª Câmara de Direito Criminal, a 6ª de Direito Privado e
> a 6ª de Direito Público. Nesta base, oito dos 37 números aparecem em mais de uma
> seção. São `camara` e `secao` **juntas** que apontam para um órgão, o que faz de
> `camara` a metade de um código, ou seja, um **identificador**.
>
> A sobreposição entre os dois tipos é real, e decidir faz parte do ofício. O
> critério que costuma resolver: categórica nominal **agrupa** casos para
> comparar, e é o que `secao` faz com seus quatro valores; identificador **nomeia**
> uma entidade, e em geral veio de outro campo ou de um cadastro. Quando o rótulo
> inteiro estiver disponível, como aqui, compare por ele.
""")

    nb.sub("datas", "📅 Convertendo as datas", """
Mesma operação da aula 2, com uma diferença: aqui a data vem no formato
brasileiro, `07/08/2026`, e o pandas precisa que você diga isso com `format=`.
""")

    nb.operacao(
        "pd.to_datetime(format=)",
        'DataFrame["coluna"] = pd.to_datetime(DataFrame["coluna"], format="%d/%m/%Y")',
        "https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html",
        "`%d` é o dia, `%m` o mês e `%Y` o ano com quatro dígitos.",
    )

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

    nb.volta()

    # ------------------------------------------------ conceitos

    nb.secao("conceitos", "Variável, valor observado e estatística", """
Três palavras que a conversa do dia a dia mistura:

🔹 **VARIÁVEL** <br>
> O que se mede: "valor da indenização em reais". Existe antes dos dados e é a
> **coluna** da tabela.

🔹 **VALOR OBSERVADO** <br>
> O valor de um caso: "neste acórdão foram R$ 5.000,00". É uma **célula**.

🔹 **ESTATÍSTICA** <br>
> Um resumo de muitos valores observados: "a mediana foi R$ 5.000,00". É um
> **número calculado da coluna inteira**.

O tipo é propriedade da variável, e é ele que decide qual estatística faz
sentido.
""")

    nb.volta()

    # ------------------------------------------------ filtrar

    nb.secao("filtrar", "Filtrar", """
Recortar a base é decisão de pesquisa, não detalhe técnico. O recorte define
sobre o que a sua resposta vale.
""")

    nb.sub("mascara", "🎭 Índice lógico", """
Uma comparação devolve uma série de `True` e `False`, do mesmo tamanho do
DataFrame. Isso é uma **máscara**. O DataFrame indexado pela máscara devolve só
as linhas verdadeiras.
""")

    nb.operacao(
        "índice lógico",
        'mascara = DataFrame["coluna"] > valor\nDataFrame[mascara]',
        "https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing",
        "É o jeito mais explícito de filtrar: primeiro você constrói a condição, "
        "depois aplica.",
    )

    nb.code("""
tem_valor = danos["valor_indenizacao"].notna()

tem_valor.head()
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

    nb.sub("combinar", "🔗 Combinando condições", """
`&` é "e", `|` é "ou", `~` é "não". Os parênteses em volta de cada condição são
**obrigatórios**, porque `&` tem precedência maior que `==` em Python.
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

    nb.sub("loc", "📍 E o .loc, qual a diferença?", """
Para **filtrar linhas**, `df[mascara]` e `df.loc[mascara]` fazem exatamente a
mesma coisa. A diferença aparece em dois casos:

1. `.loc` escolhe linhas **e** colunas na mesma expressão;
2. `.loc` é o jeito correto de **atribuir** valor a um recorte. Sem ele, o
   pandas às vezes altera uma cópia e o seu comando não tem efeito nenhum.
""")

    nb.operacao(
        ".loc[]",
        'DataFrame.loc[mascara, ["coluna_a", "coluna_b"]]',
        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html",
        "Recebe o recorte de linhas e, opcionalmente, a lista de colunas.",
    )

    nb.code("""
danos.loc[tem_valor, ["processo", "valor_indenizacao"]].head(3)
""")

    nb.md("""
Na aula 4 aparece um terceiro jeito, o `.query()`, que escreve a condição como
texto e encaixa melhor em operações encadeadas.
""")

    nb.sub("recorte", "✂️ O recorte da pergunta", """
Um terço das ementas não trouxe valor. A decisão aqui é analisar só quem tem
valor, e a consequência é que a resposta vale para **os acórdãos que trazem o
valor na ementa**, não para todos.
""")

    nb.code("""
com_valor = danos.dropna(subset=["valor_indenizacao"]).copy()

len(danos), len(com_valor)
""")

    nb.volta()

    # ------------------------------------------------ posição

    nb.secao("posicao", "Medidas de posição", """
Uma medida de posição responde "onde fica o centro dos dados".
""")

    nb.sub("media", "📊 Média e mediana")

    nb.operacao(
        ".mean() e .median()",
        'DataFrame["coluna"].mean()\nDataFrame["coluna"].median()',
        "https://pandas.pydata.org/docs/reference/api/pandas.Series.median.html",
        "A média soma tudo e divide pelo número de casos. A mediana é o valor do "
        "meio, quando os casos são postos em ordem.",
    )

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
> 🤔 Uma linha muda a média e não move a mediana. É por isso que "o valor típico
> da indenização" quase sempre deve ser reportado com a **mediana**.
""")

    nb.sub("quantis", "📐 Quantis e o intervalo interquartílico", """
O quantil de ordem $p$ é o valor abaixo do qual está a fração $p$ dos casos. A
mediana é o quantil 0,5.
""")

    nb.operacao(
        ".quantile()",
        'DataFrame["coluna"].quantile([0.25, 0.50, 0.75])',
        "https://pandas.pydata.org/docs/reference/api/pandas.Series.quantile.html",
        "Aceita um valor ou uma lista de valores entre 0 e 1.",
    )

    nb.code("""
com_valor["valor_indenizacao"].quantile([0.25, 0.50, 0.75]).round(2)
""")

    nb.md("""
O **intervalo interquartílico** (IQR) é a largura da metade central dos dados,
ou seja, a distância entre o quantil 0,25 e o 0,75:
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

    nb.volta()

    # ------------------------------------------------ dispersão

    nb.secao("dispersao", "Medidas de dispersão", """
Uma medida de dispersão responde "quanto os valores se espalham em torno do
centro".
""")

    nb.sub("desvio", "〽️ Desvio padrão e coeficiente de variação")

    nb.operacao(
        ".std()",
        'DataFrame["coluna"].std()',
        "https://pandas.pydata.org/docs/reference/api/pandas.Series.std.html",
        "Mede o afastamento típico em relação à média. A conta divide por $n - 1$, "
        "e não por $n$: é o desvio padrão **amostral**, que é o padrão do pandas. "
        "O parâmetro que controla isso é o `ddof`, e ele vale 1 por omissão.",
    )

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
> ⚠️ Um coeficiente maior que 1 quer dizer que o desvio padrão é maior que a
> média: os valores estão espalhadíssimos. Reportar só "a indenização média foi
> R$ 7.935" sem dizer isso é enganoso.
""")

    nb.volta()

    # ------------------------------------------------ binária

    nb.secao("binaria", "A média de uma binária é uma proporção", """
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

    nb.volta()

    # ------------------------------------------------ tabela de tipos

    nb.secao("tabela-tipos", "Cada tipo, sua estatística", """
Em variável nominal, média não existe. O que existe é a **moda**, que é a
categoria mais frequente, e a proporção de cada categoria:
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

    nb.volta()

    # ------------------------------------------------ fechamento

    nb.secao("resposta", "Respondendo à pergunta", """
Juntando filtro e estatística: o valor típico no Direito Privado. Na aula 4 você
vai ver o `groupby`, que compara todos os grupos de uma vez; por enquanto
separamos a base em pedaços.
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

    nb.exercicio(2, "ex2", """
A base tem 460 acórdãos e 303 com valor extraído. Escreva, em duas ou três
linhas, como você reportaria esse número numa seção de metodologia, e que
problema isso pode causar na interpretação da mediana.
""")

    nb.code("# ESCREVA SUA RESPOSTA AQUI (em comentário ou em célula de texto)")

    nb.volta()

    # ------------------------------------------------ resumo

    nb.resumo("""
A **variável** é a coluna, o **valor observado** é a célula, a **estatística** é
o resumo da coluna inteira. Filtrar é decisão de pesquisa, e a estatística tem
que caber no tipo da variável.

Abaixo, todas as operações da aula em sequência, para consulta rápida.
""")

    nb.code("""
#=> LER E CONVERTER
danos = pd.read_csv(f"{URL}/tjsp_cjsg_dano_moral.csv")
danos["data_julgamento"] = pd.to_datetime(danos["data_julgamento"], format="%d/%m/%Y")

#=> FILTRAR COM ÍNDICE LÓGICO: monta a máscara, depois aplica
tem_valor = danos["valor_indenizacao"].notna()
danos[tem_valor]

#=> COMBINAR CONDIÇÕES: & é "e", | é "ou", ~ é "não". Parênteses obrigatórios
danos[(danos["secao"] == "Direito Privado") & tem_valor]

#=> .loc: mesma filtragem, mas escolhe linhas E colunas, e serve para atribuir
danos.loc[tem_valor, ["processo", "valor_indenizacao"]]

#=> DESCARTAR FALTANTES DE UMA COLUNA
com_valor = danos.dropna(subset=["valor_indenizacao"]).copy()

#=> POSIÇÃO: média é puxada por extremos, mediana não
com_valor["valor_indenizacao"].mean()
com_valor["valor_indenizacao"].median()

#=> QUANTIS E IQR: largura da metade central
com_valor["valor_indenizacao"].quantile([0.25, 0.50, 0.75])

#=> DISPERSÃO: desvio padrão amostral (ddof=1, o padrão)
com_valor["valor_indenizacao"].std()

#=> COEFICIENTE DE VARIAÇÃO: dispersão em escala relativa
com_valor["valor_indenizacao"].std() / com_valor["valor_indenizacao"].mean()

#=> BINÁRIA: a média É a proporção
com_valor["acima_de_10k"] = com_valor["valor_indenizacao"] >= 10000
com_valor["acima_de_10k"].mean()

#=> NOMINAL: proporção de cada categoria
com_valor["comarca"].value_counts(normalize=True)
""")

    nb.md("""
Na aula 4 vamos escrever tudo isso de forma mais curta, encadeando as operações,
e comparar todos os grupos de uma vez com `groupby`. Para praticar filtros antes
disso, use o notebook `extra_filtros.ipynb`, que está completo.
""")

    nb.volta()

    return nb


# ====================================================== AULA 4


def montar_aula04() -> Caderno:
    nb = Caderno("aula04")

    nb.cabecalho(
        "Atividade: Encadear Operações",
        "Aula 04",
        [
            "escrever uma análise como uma sequência de operações encadeadas;",
            "usar os quatro verbos: escolher linhas, escolher colunas, ordenar e agregar por grupo;",
            "explicar por que trocar a ordem de duas operações muda o resultado;",
            "criar uma coluna nova antes de encadear.",
        ],
        abertura="""
Na **Gincana do Pipeline** você montou estes encadeamentos com tiras de papel,
sem digitar uma linha. Este notebook é o mesmo conteúdo escrito em python, um
verbo de cada vez, e serve para estudar por conta: em sala nós rodamos só as
rodadas da gincana, no notebook da aula 5.

A tradução das peças é direta:

| a carta no tabuleiro | no código |
|---|---|
| separar as linhas que passam | `.query("...")` |
| ler só algumas colunas | `[["a", "b"]]` |
| enfileirar em ordem | `.sort_values("a")` |
| fazer as pilhas e resumir cada uma | `.groupby("a").agg(...)` |
| criar uma coluna nova | `.assign(nova=...)` |

> 📌 Este notebook é a referência do **Projeto 02**, na quinta-feira. Se você só
> for rodar uma coisa em casa, rode a seção *A ordem importa*.
""",
    )

    nb.indice([
        ("Reincidência e regime inicial", "problema"),
        ("Por que encadear", "problema-encadeamento", [
            ("🔗 A mesma coisa, encadeada", "encadeada"),
            ("( ) Por que os parênteses", "parenteses"),
        ]),
        ("Os quatro verbos", "verbos", [
            ("1️⃣ .query(): escolher linhas", "query"),
            ("2️⃣ [[...]]: escolher colunas", "colunas"),
            ("3️⃣ .sort_values(): ordenar", "sort"),
            ("4️⃣ .groupby() e .agg(): agregar por grupo", "groupby"),
        ]),
        ("Mais duas operações de apoio", "apoio"),
        ("A ordem importa", "ordem"),
        ("Criar uma coluna nova", "coluna"),
        ("Montando o pipeline", "pipeline", [
            ("EXERCÍCIO 1: resumo por câmara", "ex1"),
        ]),
        ("Exercícios", "exercicios", [
            ("EXERCÍCIO 2: pena por regime", "ex2"),
            ("EXERCÍCIO 3: as cinco maiores comarcas", "ex3"),
        ]),
        ("RESUMO", "resumo"),
    ])

    # ------------------------------------------------ problema

    nb.secao("problema", "Reincidência e regime inicial", """
A pergunta de hoje é a mesma da mesa, agora na base inteira:

> Nas apelações criminais do TJSP, a proporção de acórdãos que mencionam
> reincidência varia conforme o regime inicial fixado?

**As variáveis da base:**

* `processo`, `cd_acordao`: identificadores.
* `classe`, `assunto`, `relator`, `comarca`, `orgao_julgador`, `camara`: dados do julgamento.
* `data_julgamento`, `data_publicacao`: datas.
* `regime_inicial`: aberto, semiaberto ou fechado, lido da ementa.
* `pena_anos`: pena em anos, lida da ementa.
* `houve_reincidencia`, `houve_confissao`, `eh_trafico`: indicadores lidos da ementa.
* `n_palavras_ementa`: tamanho da ementa.

Coletada com a biblioteca
[juscraper](https://github.com/jtrecenti/juscraper). **Não precisa rodar:**

```python
import juscraper as jus

tjsp = jus.scraper("tjsp")
acordaos = tjsp.cjsg('"apelacao criminal" E "regime inicial"', paginas=range(1, 26))
```
""")

    nb.code(ABERTURA)

    nb.code("""
criminal = pd.read_csv(f"{URL}/tjsp_cjsg_criminal.csv")
criminal.head(3)
""")

    nb.code("""
criminal.info()
""")

    nb.md("""
> ⚠️ `regime_inicial` e `pena_anos` foram lidos do texto da ementa, e nenhum dos
> dois vem completo: o regime aparece em cerca de 70% dos acórdãos e a pena em
> 45%. `pena_anos` ainda traz valores implausíveis, porque a leitura pega o
> primeiro número seguido de "anos" que encontra. É a carta A10, agora com 475
> linhas em volta.
""")

    nb.volta()

    # ------------------------------------------------ por que encadear

    nb.secao("problema-encadeamento", "Por que encadear", """
Do jeito que fizemos até a aula 3, com uma variável nova a cada operação, a
resposta sai assim:
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
2. **nomes intermediários** como `com_regime`, que não querem dizer nada e que
   você vai reaproveitar por engano daqui a três células;
3. **não escala**: se aparecesse um quarto regime, seria preciso escrever mais
   uma linha e lembrar de incluí-la no resultado.
""")

    nb.sub("encadeada", "🔗 A mesma coisa, encadeada")

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
Leia de cima para baixo, como você leu o tabuleiro: pegue `criminal`, fique só
com as apelações, descarte quem não tem regime, faça as pilhas por regime, e
calcule a proporção de cada pilha. Nenhuma variável intermediária, e a ordem das
operações é a ordem das linhas.
""")

    nb.sub("parenteses", "( ) Por que os parênteses", """
Em python, dentro de um par de parênteses você pode quebrar a linha à vontade.
Sem eles, `criminal` seguido de uma quebra de linha e `.query(...)` é erro de
sintaxe. Os parênteses existem só para deixar você pôr uma operação por linha,
e são o equivalente do tabuleiro que você usou na dinâmica.

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

    nb.volta()

    # ------------------------------------------------ os verbos

    nb.secao("verbos", "Os quatro verbos", """
São os quatro que você já executou com as cartas. Um de cada vez.
""")

    nb.sub("query", "1️⃣ .query(): escolher linhas")

    nb.operacao(
        ".query()",
        'DataFrame.query("coluna == \'valor\'")',
        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html",
        texto="""
Separar as cartas que passam na condição. A condição vai escrita como **texto**:
dentro das aspas, os nomes das colunas aparecem sem `df[...]`, e o valor
comparado vai entre aspas simples.
""",
    )

    nb.code("""
criminal.query("regime_inicial == 'fechado'").shape
""")

    nb.md("""
`.shape` devolve o par (linhas, colunas). É a forma rápida de conferir quantas
cartas sobraram na mesa.

Para combinar condições, use `and`, `or` e `not`, por extenso:
""")

    nb.code("""
criminal.query("regime_inicial == 'fechado' and houve_reincidencia").shape
""")

    nb.faca(
        "Fique só com os acórdãos de tráfico em que houve confissão.",
        'criminal.query("eh_trafico and houve_confissao").shape',
        'criminal.query("eh_trafico ________ houve_confissao").shape',
    )

    nb.sub("colunas", "2️⃣ [[...]]: escolher colunas", """
Ler só algumas colunas de cada carta. Duas chaves com uma lista de nomes dentro
devolvem as colunas pedidas, na ordem em que você pediu.
""")

    nb.code("""
(
    criminal
    [["processo", "comarca", "regime_inicial", "pena_anos"]]
    .head(3)
)
""")

    nb.md("""
> ⚠️ São **dois** pares de colchetes. Um só, como em `criminal["comarca"]`,
> devolve uma coluna solta, e não uma tabela. Com uma coluna solta o
> encadeamento acaba ali.
""")

    nb.faca(
        "Devolva só `processo`, `camara` e `houve_reincidencia`.",
        '(\n    criminal\n    [["processo", "camara", "houve_reincidencia"]]\n    .head(3)\n)',
        '(\n    criminal\n    [["processo", "________", "houve_reincidencia"]]\n    .head(3)\n)',
    )

    nb.sub("sort", "3️⃣ .sort_values(): ordenar")

    nb.operacao(
        ".sort_values()",
        'DataFrame.sort_values("coluna", ascending=False)',
        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html",
        texto="""
Enfileirar as cartas. O primeiro argumento diz por qual coluna ordenar, e
`ascending=False` inverte para o maior primeiro.
""",
    )

    nb.code("""
(
    criminal
    .sort_values("n_palavras_ementa", ascending=False)
    [["processo", "comarca", "n_palavras_ementa"]]
    .head(5)
)
""")

    nb.faca(
        "Ordene pela pena, da maior para a menor, e olhe as cinco primeiras. "
        "É a carta A10 de novo: a leitura automática da pena erra em alguns acórdãos.",
        '(\n    criminal\n    .sort_values("pena_anos", ascending=False)\n'
        '    [["processo", "pena_anos", "regime_inicial"]]\n    .head(5)\n)',
        '(\n    criminal\n    .sort_values("________", ascending=________)\n'
        '    [["processo", "pena_anos", "regime_inicial"]]\n    .head(5)\n)',
    )

    nb.sub("groupby", "4️⃣ .groupby() e .agg(): agregar por grupo", """
Fazer as pilhas e virar fichas. `.groupby("coluna")` separa a tabela em pedaços,
um por valor da coluna, e `.agg(...)` calcula uma estatística em cada pedaço,
devolvendo **uma linha por grupo**.
""")

    nb.operacao(
        ".groupby().agg()",
        'DataFrame.groupby("coluna_de_grupo").agg(nome_da_saida=("coluna_de_entrada", "estatistica"))',
        "https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.agg.html",
        texto="""
As estatísticas são as mesmas da aula 3, agora escritas como texto: `"mean"`,
`"median"`, `"std"`, `"min"`, `"max"`, `"sum"`, `"nunique"`, além de `"size"`,
que conta as linhas do grupo.
""",
    )

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
Repare que `regime_inicial` saiu **fora** da tabela, à esquerda, em negrito:
depois de um `groupby`, a coluna de agrupamento vira o **índice** do resultado, e
não uma coluna normal. Isso atrapalha se você quiser continuar encadeando.

O `.reset_index()` traz o índice de volta para dentro da tabela. Por isso ele
aparece no fim de quase todo `groupby`: com o índice de volta, dá para filtrar e
ordenar o resultado como qualquer outra tabela.
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
E vale lembrar da aula 3: a média de uma coluna de verdadeiro e falso é a
proporção. Foi assim que você preencheu a ficha-resumo, contando quantas cartas
tinham "sim" e dividindo pelo tamanho da pilha.
""")

    nb.faca(
        "Acrescente ao resumo a proporção de acórdãos com reincidência e a proporção de tráfico.",
        '(\n    criminal\n    .groupby("regime_inicial")\n    .agg(\n'
        '        n=("processo", "size"),\n'
        '        prop_reincidencia=("houve_reincidencia", "mean"),\n'
        '        prop_trafico=("eh_trafico", "mean"),\n    )\n'
        '    .reset_index()\n    .round(3)\n)',
        '(\n    criminal\n    .groupby("regime_inicial")\n    .agg(\n'
        '        n=("processo", "size"),\n'
        '        prop_reincidencia=("houve_reincidencia", "________"),\n'
        '        prop_trafico=("________", "mean"),\n    )\n'
        '    .reset_index()\n    .round(3)\n)',
    )

    nb.volta()

    # ------------------------------------------------ apoio

    nb.secao("apoio", "Mais duas operações de apoio", """
Não são verbos novos, são utilidades que aparecem o tempo todo:

* `.dropna(subset=["coluna"])` descarta as linhas em que aquela coluna está
  vazia. Serve para tirar da mesa os acórdãos em que a leitura da ementa não
  achou o regime ou a pena.
* `.head(n)` fica com as `n` primeiras linhas **da tabela como ela está naquele
  ponto**. Guarde esta frase, porque a próxima seção é sobre ela.
""")

    nb.code("""
(
    criminal
    .dropna(subset=["pena_anos"])
    .shape
)
""")

    nb.volta()

    # ------------------------------------------------ ordem

    nb.secao("ordem", "A ordem importa", """
Esta é a parte que você já descobriu com as cartas. As duas células abaixo têm
exatamente as mesmas operações, e só trocam duas linhas de lugar.

Primeiro do jeito certo: ordenar e **depois** cortar.
""")

    nb.code("""
(
    criminal
    .dropna(subset=["pena_anos"])
    .query("not eh_trafico")
    .sort_values("pena_anos", ascending=False)
    .head(3)
    [["processo", "comarca", "pena_anos"]]
)
""")

    nb.md("""
Agora cortando **antes** de ordenar:
""")

    nb.code("""
(
    criminal
    .dropna(subset=["pena_anos"])
    .query("not eh_trafico")
    .head(3)
    .sort_values("pena_anos", ascending=False)
    [["processo", "comarca", "pena_anos"]]
)
""")

    nb.md("""
O segundo resultado não é "as três maiores penas". É "as três primeiras linhas
da base, ordenadas entre si", que é uma pergunta que ninguém fez.

O motivo é o mesmo do tabuleiro: cada operação enxerga a tabela que a operação
anterior deixou. `.head(3)` não sabe nada sobre ordenar, ele só corta o que está
na sua frente.

> 🤔 Repare também no que apareceu no primeiro resultado: uma pena de 75,3 anos.
> O código está certo e o dado está errado. Olhar os extremos antes de acreditar
> no resultado é parte do trabalho.
""")

    nb.volta()

    # ------------------------------------------------ coluna nova

    nb.secao("coluna", "Criar uma coluna nova", """
Na carta havia um espaço em branco embaixo, para escrever uma coluna nova. Aqui
é a mesma coisa, e por enquanto vamos fazer isso **antes** do encadeamento, numa
linha só:
""")

    nb.code("""
criminal["pena_meses"] = criminal["pena_anos"] * 12

criminal[["processo", "pena_anos", "pena_meses"]].head(3)
""")

    nb.md("""
A conta vale para a tabela inteira, linha por linha, sem `for` nenhum. É a mesma
ideia de escrever a coluna nova em todas as 24 cartas de uma vez.

Isso também serve para declarar a ordem de uma categórica, como na aula 2. O
regime é **ordinal**, e queremos a tabela na ordem aberto, semiaberto, fechado, e
não em ordem alfabética:
""")

    nb.code("""
criminal["regime"] = pd.Categorical(
    criminal["regime_inicial"],
    categories=["aberto", "semiaberto", "fechado"],
    ordered=True,
)

criminal["regime"].dtype
""")

    nb.faca(
        "Crie a coluna `ementa_longa`, verdadeira quando a ementa tiver mais de 200 palavras.",
        'criminal["ementa_longa"] = criminal["n_palavras_ementa"] > 200\n\n'
        'criminal[["processo", "n_palavras_ementa", "ementa_longa"]].head(3)',
        'criminal["ementa_longa"] = criminal["________"] > 200\n\n'
        'criminal[["processo", "n_palavras_ementa", "ementa_longa"]].head(3)',
    )

    nb.md("""
> 🤔 Existe um jeito de criar a coluna **dentro** do encadeamento, com
> `.assign()`. Ele é útil quando a coluna nova depende de um filtro que veio
> antes, e vamos deixar para quando essa necessidade aparecer. Por enquanto,
> coluna nova é uma linha antes do parêntese.
""")

    nb.volta()

    # ------------------------------------------------ pipeline

    nb.secao("pipeline", "Montando o pipeline", """
Com a coluna `regime` já criada, a resposta da pergunta de hoje cabe em seis
linhas. O `observed=True` no `groupby` existe porque a coluna é categórica: sem
ele, o pandas devolveria também as categorias que não aparecem em nenhuma linha.
""")

    nb.code("""
resumo = (
    criminal
    .query("classe == 'Apelação Criminal'")
    .dropna(subset=["regime"])
    .groupby("regime", observed=True)
    .agg(
        n=("processo", "size"),
        prop_reincidencia=("houve_reincidencia", "mean"),
        prop_confissao=("houve_confissao", "mean"),
        prop_trafico=("eh_trafico", "mean"),
    )
    .reset_index()
    .round(3)
)

resumo
""")

    nb.md("""
A leitura é direta, e é a mesma conclusão a que a mesa chegou: a menção a
reincidência sobe conforme o regime fica mais severo. Não é surpresa, é quase a
definição legal do regime, e serve para conferir que a leitura das variáveis está
coerente.

> 🤔 E o que **não** dá para concluir: nada sobre causalidade, e nada sobre os
> acórdãos em que o regime não foi identificado, que são cerca de 30% da base.

Guarde a tabela `resumo`. Ela volta na aula 5, virando gráfico.
""")

    nb.exercicio(1, "ex1", """
Monte um resumo parecido, agora por `camara`, mantendo só as câmaras com pelo
menos 15 acórdãos e ordenando da maior proporção de reincidência para a menor.
Você vai precisar de `.reset_index()`, `.query()` e `.sort_values()` **depois**
do `.agg()`.

> 🤔 Na aula 3 vimos que `camara` é a metade de um código, e que sozinha não
> nomeia um órgão. Aqui ela serve: esta base só tem câmaras criminais, então não
> existem duas 6ª câmaras para confundir. O tipo de uma variável depende da
> tabela em que ela está, e não só do nome dela.
""")

    nb.code(
        '(\n    criminal\n    .query("classe == \'Apelação Criminal\'")\n'
        '    .dropna(subset=["camara"])\n    .groupby("camara")\n    .agg(\n'
        '        n=("processo", "size"),\n'
        '        prop_reincidencia=("houve_reincidencia", "mean"),\n    )\n'
        '    .reset_index()\n    .query("n >= 15")\n'
        '    .sort_values("prop_reincidencia", ascending=False)\n    .round(3)\n)',
        '(\n    criminal\n    .query("classe == \'Apelação Criminal\'")\n'
        '    .dropna(subset=["camara"])\n    .groupby("________")\n    .agg(\n'
        '        n=("processo", "size"),\n'
        '        prop_reincidencia=("houve_reincidencia", "________"),\n    )\n'
        '    .________()\n    .query("n >= ________")\n'
        '    .sort_values("________", ascending=False)\n    .round(3)\n)',
    )

    nb.volta()

    # ------------------------------------------------ exercicios

    nb.secao("exercicios", "Exercícios")

    nb.exercicio(2, "ex2", """
A pena lida da ementa tem valores implausíveis, como penas acima de 40 anos, que
vêm de a leitura pegar um número errado. Monte um encadeamento que descarte as
penas ausentes e as maiores que 30 anos, e devolva mediana, média e desvio padrão
da pena por regime inicial.
""")

    nb.code(
        '(\n    criminal\n    .dropna(subset=["pena_anos", "regime"])\n'
        '    .query("pena_anos <= 30")\n    .groupby("regime", observed=True)\n    .agg(\n'
        '        n=("processo", "size"),\n        mediana=("pena_anos", "median"),\n'
        '        media=("pena_anos", "mean"),\n        desvio=("pena_anos", "std"),\n    )\n'
        '    .reset_index()\n    .round(2)\n)',
        '(\n    criminal\n    .dropna(subset=["pena_anos", "regime"])\n'
        '    .query("pena_anos ________ 30")\n    .groupby("________", observed=True)\n    .agg(\n'
        '        n=("processo", "size"),\n        mediana=("pena_anos", "________"),\n'
        '        media=("pena_anos", "mean"),\n        desvio=("pena_anos", "________"),\n    )\n'
        '    .reset_index()\n    .round(2)\n)',
    )

    nb.md("""
Compare a mediana com a média em cada regime. Em todos eles a média fica acima da
mediana, e a diferença é maior justamente onde as penas são mais curtas. Isso é
assimetria à direita: uns poucos valores altos puxam a média e não mexem na
mediana, que foi exatamente o que a carta A10 fez na sua pilha.
""")

    nb.exercicio(3, "ex3", """
Quais são as cinco comarcas com mais apelações criminais nesta base, e qual a
proporção de tráfico em cada uma?
""")

    nb.code(
        '(\n    criminal\n    .query("classe == \'Apelação Criminal\'")\n'
        '    .groupby("comarca")\n'
        '    .agg(n=("processo", "size"), prop_trafico=("eh_trafico", "mean"))\n'
        '    .reset_index()\n    .sort_values("n", ascending=False)\n'
        '    .head(5)\n    .round(3)\n)',
        '(\n    criminal\n    .query("classe == \'Apelação Criminal\'")\n'
        '    .groupby("________")\n'
        '    .agg(n=("processo", "size"), prop_trafico=("eh_trafico", "________"))\n'
        '    .reset_index()\n    .sort_values("________", ascending=False)\n'
        '    .head(________)\n    .round(3)\n)',
    )

    nb.volta()

    # ------------------------------------------------ resumo

    nb.resumo("""
Uma análise descritiva é uma sequência de operações, escrita de cima para baixo
dentro de um par de parênteses, com uma operação por linha.

| verbo | na mesa | para quê |
|---|---|---|
| `.query("...")` | separar cartas | escolher linhas por uma condição |
| `[["a", "b"]]` | ler só algumas colunas | escolher colunas |
| `.sort_values("a", ascending=False)` | enfileirar | ordenar |
| `.groupby("a").agg(saida=("b", "mean"))` | pilhas viram fichas | uma linha por grupo |
| `.dropna(subset=[...])` | tirar cartas incompletas | descartar linhas sem valor |
| `.head(n)` | pegar as n primeiras da fila | cortar |
| `.reset_index()` | | tirar o agrupamento do índice |
""")

    nb.code("""
#=> COLUNA NOVA: uma linha antes do parêntese, vale para a tabela inteira
criminal["regime"] = pd.Categorical(
    criminal["regime_inicial"],
    categories=["aberto", "semiaberto", "fechado"],
    ordered=True,
)

#=> O FORMATO: abre parêntese, tabela sozinha, uma operação por linha
resumo = (
    criminal

    #=> ESCOLHER LINHAS: condição como texto, colunas sem aspas
    .query("classe == 'Apelação Criminal'")

    #=> DESCARTAR FALTANTES de uma coluna
    .dropna(subset=["regime"])

    #=> AGRUPAR: observed=True descarta categorias sem nenhuma linha
    .groupby("regime", observed=True)

    #=> AGREGAR: saida=("coluna_de_entrada", "estatistica")
    .agg(
        n=("processo", "size"),
        prop_reincidencia=("houve_reincidencia", "mean"),
    )

    #=> TIRAR O AGRUPAMENTO DO ÍNDICE, para poder continuar encadeando
    .reset_index()

    #=> ORDENAR e ARREDONDAR
    .sort_values("prop_reincidencia", ascending=False)
    .round(3)
)

resumo
""")

    nb.md("""
**Duas regras que valem sempre:**

1. Cada operação enxerga a tabela que a anterior deixou. Antes de escrever a
   próxima linha, pergunte o que está na mesa naquele ponto.
2. Quando a sequência passar de umas oito linhas, quebre em duas partes, com um
   nome que signifique alguma coisa, como fizemos com `resumo`.
""")

    nb.volta()

    return nb


# ====================================================== AULA 5


def montar_aula05() -> Caderno:
    """Espelho dos slides da aula 5, na mesma ordem, com o mesmo código.

    Nada aqui vai além do que está projetado: quem acompanha a aula com este
    notebook aberto vê na tela exatamente o que vê no telão. O material que
    passa disso está em `aula05_extra_graficos`.
    """
    nb = Caderno("aula05")

    nb.cabecalho(
        "Aula 5: o pipeline e a gramática de gráficos",
        "Aula 05",
        [
            "escrever uma análise como uma sequência de operações encadeadas;",
            "usar os cinco verbos do pandas, e dizer por que a ordem importa;",
            "definir um gráfico como um mapeamento de variáveis em aspectos estéticos;",
            "montar um gráfico camada por camada, no plotnine;",
            "explicar a diferença entre pintar de uma cor e mapear uma variável em cor.",
        ],
        abertura="""
Este notebook é o **espelho dos slides**: as seções seguem a ordem do que está
projetado, e o código é o mesmo. Ele serve para você acompanhar rodando, e
depois para reler em casa.

A última seção é a **Gincana do Pipeline**, com o enunciado de cada rodada e uma
célula em branco para você escrever a resposta. Os gabaritos não estão aqui:
eles aparecem no telão depois que a rodada fecha.

> O que vai além do slide (histograma, densidade, boxplot, facetas, rótulos e
> exercícios) está no notebook **aula05_extra_graficos**, para estudar por conta.
""",
    )

    nb.indice([
        ("A tabela de hoje", "dados"),
        ("A pergunta de hoje", "pergunta"),
        ("Encadear operações", "encadear", [
            ("Do jeito da aula 3", "antigo"),
            ("🔗 A mesma coisa, encadeada", "encadeado"),
            ("Os cinco verbos", "verbos"),
            ("A ordem importa", "ordem"),
        ]),
        ("O que é um gráfico", "definicao"),
        ("A gramática de gráficos", "gramatica"),
        ("Uma camada de cada vez", "camadas"),
        ("🎨 Pintar não é mapear", "pintar"),
        ("A regra vale para toda estética", "regra-aes"),
        ("Geometrias e tipos de variáveis", "geometrias"),
        ("A Gincana do Pipeline", "gincana"),
        ("Quinta-feira", "depois"),
    ])

    # ------------------------------------------------ dados

    nb.secao("dados", "A tabela de hoje", """
A base de apelações criminais do TJSP, a mesma da aula 4.
""")

    nb.md("""
O plotnine não vem instalado no Google Colab. Tire o `#` da segunda linha, rode
uma vez, e ponha o `#` de volta:
""")

    nb.code("""
# no Colab, rode uma vez:
# %pip install -q plotnine
""")

    nb.code("""
import pandas as pd
from plotnine import *

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)

URL = "https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/dados"
""")

    nb.code("""
criminal = pd.read_csv(f"{URL}/tjsp_cjsg_criminal.csv")

criminal["regime"] = pd.Categorical(
    criminal["regime_inicial"],
    categories=["aberto", "semiaberto", "fechado"],
    ordered=True,
)

penas = (
    criminal
    .dropna(subset=["regime", "pena_anos"])
    .query("pena_anos <= 30")
)

criminal.shape, penas.shape
""")

    nb.md("""
São duas tabelas, e as duas aparecem nas cartas da gincana:

* **`criminal`** é a base inteira, com 475 acórdãos;
* **`penas`** é a mesma base com duas decisões já tomadas: fora quem não tem
  regime ou pena, e fora as penas acima de 30 anos. Ela tem uma coluna a mais,
  `regime`, que é a versão **ordenada** de `regime_inicial`.

`.head()` mostra as primeiras linhas. É a primeira coisa a fazer depois de ler
um arquivo: se a tabela veio torta, você descobre agora e não daqui a vinte
células.
""")

    nb.code("""
criminal.head()
""")

    nb.code("""
penas.head()
""")

    nb.volta()

    # ------------------------------------------------ a pergunta

    nb.secao("pergunta", "A pergunta de hoje", """
> Nas apelações criminais do TJSP, a proporção de acórdãos que mencionam
> reincidência varia conforme o regime inicial fixado?

Três colunas resolvem a pergunta:

| coluna | o que é | o estado dela |
|---|---|---|
| `regime_inicial` | aberto, semiaberto ou fechado, lido da ementa | vazio em 142 acórdãos |
| `houve_reincidencia` | verdadeiro ou falso, lido da ementa | completo |
| `pena_anos` | a pena em anos, lida da ementa | vazio em 55%, e com valores implausíveis |

Guarde a terceira linha. A pena foi lida pegando o primeiro número seguido de
"anos", e às vezes o número está errado. Isso aparece já no aquecimento da
gincana.
""")

    nb.volta()

    # ------------------------------------------------ encadear

    nb.secao("encadear", "Encadear operações")

    nb.sub("antigo", "Do jeito da aula 3", """
Uma variável nova a cada operação. Funciona, e responde a pergunta:
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
Três problemas: **seis variáveis** que existem só para chegar num resultado,
**nomes que não dizem nada** (`com_regime` vai ser reaproveitado por engano daqui
a três células) e **não escala** (um quarto regime obriga a escrever mais uma
linha e a lembrar de incluí-la).
""")

    nb.sub("encadeado", "🔗 A mesma coisa, encadeada", """
Nenhuma variável intermediária, e a ordem das operações é a ordem das linhas.
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
Leia de cima para baixo, como uma frase: pegue `criminal`, fique só com as
apelações, descarte quem não tem regime, faça as pilhas por regime, e calcule a
proporção de cada pilha.

**Por que os parênteses.** Dentro de um par de parênteses o python deixa você
quebrar a linha à vontade. Sem eles, `criminal` seguido de quebra de linha e
`.query(...)` é erro de sintaxe. Eles existem só para você pôr uma operação por
linha:

```python
resultado = (
    tabela
    .operacao_1(...)
    .operacao_2(...)
)
```
""")

    nb.sub("verbos", "Os cinco verbos", """
Cinco operações resolvem quase toda análise descritiva. São as mesmas que estão
nas cartas da gincana, mais duas de apoio.
""")

    nb.md("""
**1. `.query()` escolhe linhas.** A condição vai escrita como texto. Colunas de
verdadeiro e falso dispensam a comparação: basta o nome.
""")

    nb.code("""
criminal.query("eh_trafico").shape
""")

    nb.md("""
**2. `[[...]]` escolhe colunas.** São **dois** pares de colchetes. Um só devolve
a coluna solta, e o encadeamento acaba ali.
""")

    nb.code("""
(
    criminal
    [["processo", "comarca", "regime_inicial", "pena_anos"]]
    .head(3)
)
""")

    nb.md("""
**3. `.sort_values()` ordena.** `ascending=False` põe o maior primeiro.
""")

    nb.code("""
(
    criminal
    .sort_values("pena_anos", ascending=False)
    [["processo", "assunto", "pena_anos"]]
    .head(5)
)
""")

    nb.md("""
> ⚠️ Olhe o resultado acima com atenção. As maiores penas da base estão num
> furto, num estelionato e numa apropriação indébita, e chegam a 75 anos. É por
> isso que a tabela `penas` corta em 30.

**4. `.groupby()` e `.agg()` agregam por grupo.** O `groupby` faz as pilhas e o
`agg` calcula uma estatística em cada uma, devolvendo **uma linha por grupo**.
Depois dele a coluna de agrupamento vira índice, e o `.reset_index()` traz ela de
volta para dentro da tabela.
""")

    nb.code("""
(
    criminal
    .groupby("regime_inicial")
    .agg(
        n=("processo", "size"),
        pena_mediana=("pena_anos", "median"),
        prop_reincidencia=("houve_reincidencia", "mean"),
    )
    .reset_index()
    .round(3)
)
""")

    nb.md("""
A média de uma coluna de verdadeiro e falso é a **proporção** de verdadeiros.

**5. `.assign()` cria uma coluna nova**, dentro do encadeamento. A coluna criada
só existe da linha seguinte em diante, então o `.assign()` vem **antes** de
qualquer operação que use ela.
""")

    nb.code("""
(
    criminal
    .assign(eh_capital=criminal["comarca"] == "São Paulo")
    .groupby("eh_capital")
    .agg(n=("processo", "size"))
    .reset_index()
)
""")

    nb.md("""
E duas operações de apoio, que não são verbos novos:

* `.dropna(subset=["coluna"])` descarta as linhas em que **aquela** coluna está
  vazia. Sem o `subset`, descarta toda linha que tenha qualquer campo vazio.
* `.head(n)` fica com as `n` primeiras linhas **da tabela como ela está naquele
  ponto**. Guarde esta frase: a próxima seção é sobre ela.
""")

    nb.sub("ordem", "A ordem importa", """
As duas células abaixo têm exatamente as mesmas operações. Só trocam duas linhas
de lugar. Primeiro do jeito certo: ordenar e **depois** cortar.
""")

    nb.code("""
(
    criminal
    .sort_values("pena_anos", ascending=False)
    .head(5)
    [["processo", "pena_anos"]]
)
""")

    nb.md("""
Agora ao contrário: cortar e **depois** ordenar.
""")

    nb.code("""
(
    criminal
    .head(5)
    .sort_values("pena_anos", ascending=False)
    [["processo", "pena_anos"]]
)
""")

    nb.md("""
São cinco acórdãos quaisquer, os cinco primeiros da tabela, ordenados entre si.
Nada a ver com as maiores penas.

O `.head(5)` não sabe o que você queria. Ele pega as cinco primeiras linhas da
tabela **como ela está naquele ponto**, e é por isso que quase sempre vem por
último.
""")

    nb.volta()

    # ------------------------------------------------ definicao

    nb.secao("definicao", "O que é um gráfico", """
> Um gráfico estatístico é um **mapeamento de variáveis (colunas)** em
> **aspectos estéticos** de **formas geométricas**.

Quatro expressões fazem o trabalho:

| a expressão | o que quer dizer |
|---|---|
| mapeamento | uma ligação: cada valor da coluna vira um valor visual |
| variáveis (colunas) | o que sai da tabela, e nada mais |
| aspectos estéticos | posição, altura, cor, tamanho, forma |
| formas geométricas | barra, ponto, linha, caixa |

Repare no que a definição **não** diz: nada sobre que biblioteca usar, que cor
fica bonita ou que tipo de gráfico escolher. Ela diz o que precisa ser
**decidido**.
""")

    nb.volta()

    # ------------------------------------------------ gramatica

    nb.secao("gramatica", "A gramática de gráficos", """
A definição vira código quase palavra por palavra. São três camadas, somadas
com `+`, e todas as três são obrigatórias:

```python
(
    ggplot(tabela)      # dados: de que tabela saem as variáveis
    + aes(x="coluna")   # estética: que variável vira que aspecto visual
    + geom_bar()        # geometria: que forma aparece na tela
)
```

É a mesma ideia dos cinco verbos: lá, operações somadas com ponto. Aqui, camadas
somadas com mais.
""")

    nb.volta()

    # ------------------------------------------------ camadas

    nb.secao("camadas", "Uma camada de cada vez", """
**1. Os dados.** Um retângulo vazio. Já é um gráfico válido: só não dissemos que
variável vira o quê.
""")

    nb.code("""
ggplot(penas)
""")

    nb.md("""
**2. A estética.** O mapeamento aconteceu: `regime` virou posição no eixo. Ainda
não há forma nenhuma.
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="regime")
)
""")

    nb.md("""
**3. A geometria.** A forma apareceu. `geom_bar()` conta as linhas de cada
categoria sozinho: não existe `groupby` antes.
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="regime")
    + geom_bar()
)
""")

    nb.md("""
As barras saem na ordem aberto, semiaberto, fechado porque `regime` é uma
categórica **ordenada**, declarada lá em cima. Se fosse texto comum, o plotnine
usaria a ordem alfabética.
""")

    nb.volta()

    # ------------------------------------------------ pintar

    nb.secao("pintar", "🎨 Pintar não é mapear", """
A distinção mais importante da aula, e a que mais gera erro. Depende só de o
argumento estar dentro ou fora do `aes()`.

`fill` **fora** do `aes()` é uma escolha de tinta. Vale para todas as barras,
não representa nada, e não gera legenda:
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="regime")
    + geom_bar(fill="#E50505")
    + labs(x="Regime inicial", y="Acórdãos")
)
""")

    nb.md("""
`fill` **dentro** do `aes()` é um mapeamento. A cor passa a representar uma
variável, cada regime vira duas barras, e aparece uma legenda:
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="regime", fill="houve_reincidencia")
    + geom_bar(position="dodge")
    + labs(x="Regime inicial", y="Acórdãos")
)
""")

    nb.md("""
> 🤔 O `position="dodge"` põe as barras **lado a lado**. Sem ele, o padrão é
> empilhar, e aí a fatia de cima de cada regime começa numa altura diferente:
> comparar de olho fica quase impossível. Rode a mesma célula sem o
> `position="dodge"` e veja a diferença.
""")

    nb.volta()

    # ------------------------------------------------ a regra

    nb.secao("regra-aes", "A regra vale para toda estética", """
> Dentro do `aes()`, o argumento recebe o **nome de uma coluna**.
> Fora do `aes()`, o argumento recebe um **valor fixo**.

Trocar os dois de lugar é o erro mais comum de quem começa, e o sintoma é sempre
um destes dois:

1. **Apareceu uma legenda que você não queria.** Você pôs `fill="azul"` dentro
   do `aes()`, e o plotnine criou uma variável com um valor só, chamada "azul".
2. **Sumiu a legenda que você queria.** Você pôs `fill="regime"` fora do
   `aes()`, e o plotnine tentou pintar tudo de uma cor chamada "regime", que não
   existe.

Os aspectos estéticos mais usados: `x`, `y`, `fill` (preenchimento), `color`
(traço), `size` (tamanho), `alpha` (transparência).
""")

    nb.volta()

    # ------------------------------------------------ geometrias

    nb.secao("geometrias", "Geometrias e tipos de variáveis", """
Hoje só variáveis sozinhas. Quinta-feira, duas de cada vez.

| a variável | a pergunta | a geometria | o detalhe |
|---|---|---|---|
| uma categórica | quantos casos em cada categoria | `geom_bar()` | conta sozinho: a altura sai da contagem |
| uma categórica, altura já calculada | mostrar um valor por categoria | `geom_col()` | usa a coluna que você mapeou em `y` |
| uma numérica | como os valores se distribuem | `geom_histogram(bins=)` | o número de caixas muda a leitura |
| uma numérica | a mesma distribuição, alisada | `geom_density()` | sem o degrau das caixas |
| uma numérica | mediana, quartis e pontos fora | `geom_boxplot()` | resume, e por isso esconde a forma |

**`geom_bar()` conta. `geom_col()` usa a altura que você deu.** Confundir os dois
é a pegadinha da última rodada da gincana.

> As três geometrias de variável numérica estão trabalhadas no notebook
> **aula05_extra_graficos**.
""")

    nb.volta()

    return _gincana_e_fim(nb)


def _gincana_e_fim(nb: Caderno) -> Caderno:
    """A seção da gincana, gerada a partir de `atividades/gincana.py`.

    O enunciado de cada rodada é o mesmo que vai para o slide e para o app: são
    lidos da mesma fonte, então não há como um sair de sincronia com o outro.

    Na versão do aluno, as rodadas que valem ponto vêm com a célula em branco.
    Os aquecimentos vêm resolvidos, como no slide.
    """
    nb.secao("gincana", "A Gincana do Pipeline", """
Cada mesa tem um baralho de 40 cartas e um tabuleiro. A cada rodada, o problema
aparece na tela, o cronômetro começa para a sala inteira, e o grupo monta o
encadeamento com as cartas.

Como funciona uma rodada:

1. O problema aparece, com o número de cartas da resposta.
2. A mesa monta no tabuleiro, uma carta por linha.
3. Um integrante digita os códigos no app, na ordem, e **pode rodar até 5 vezes**
   para ver o que sai.
4. O grupo envia antes do alarme e escreve, no papel, uma carta que descartou e
   por quê.

Abaixo, o enunciado de cada rodada e uma célula para você escrever a resposta.
**Os gabaritos não estão aqui**: eles aparecem no telão depois que a rodada fecha.
""")

    for r in TUDO_GINCANA:
        enunciado = r["pergunta"]
        if r.get("figura"):
            enunciado += (
                f"\n\n![o gráfico que a rodada pede]"
                f"({URL_FIGURAS}/{r['figura']}.png)")
        marca = ("não pontua" if EH_AQUECIMENTO(r)
                 else f"{N_CARTAS(r)} cartas · {r['minutos']} min")
        nb.sub(f"rod{r['n']}", f"{ROTULO(r)}: {r['titulo']}",
               f"*{marca}*\n\n{enunciado}")
        if EH_AQUECIMENTO(r):
            nb.code(CODIGO_RODADA(r))
        else:
            nb.code(CODIGO_RODADA(r),
                    f"# a sua resposta da {ROTULO(r).lower()}\n")

    nb.volta()

    nb.secao("depois", "Quinta-feira", """
**Aula 6, das 16h30 às 18h30.**

* **Primeira hora:** gráficos de duas variáveis. Duas numéricas, uma numérica e
  uma categórica, duas categóricas. É a mesma gramática de hoje, com mais uma
  variável mapeada.
* **Segunda hora:** **Projeto 02**, individual, valendo nota. Você recebe blocos
  de pandas e de plotnine fora de ordem e organiza na ordem em que devem rodar.
  É exatamente a gincana de hoje, sozinho e no computador. Entrega no mesmo dia.

Para chegar pronto: rode este notebook inteiro, e depois o
**aula05_extra_graficos**.
""")

    nb.volta()

    return nb


# ====================================================== AULA 5, COMPLETA


def montar_aula05_completo() -> Caderno:
    """A aula 5 inteira em texto, para estudar por conta.

    Convive com `montar_aula05`, que e o espelho dos slides. Esta versao vai
    alem do que foi projetado: histograma, densidade, boxplot, rotulos, facetas
    e os exercicios.
    """
    nb = Caderno("aula05_completo")

    nb.cabecalho(
        "Aula 5, completa: Gramática de Gráficos",
        "Aula 05",
        [
            "descrever qualquer gráfico como dados, estética e geometria;",
            "escolher a geometria a partir do tipo da variável;",
            "fazer gráficos de uma variável só, categórica ou numérica, no plotnine;",
            "explicar a diferença entre pintar de uma cor e mapear uma variável em cor;",
            "repartir um gráfico em facetas.",
        ],
        abertura="""
Esta é a **versão completa** da aula 5: a gramática de gráficos do começo ao
fim, com o que foi projetado e também o que não coube no telão (histograma,
densidade, boxplot, rótulos, facetas e três exercícios).

> Um gráfico estatístico é um **mapeamento de variáveis (colunas) em aspectos
> estéticos de formas geométricas**.

A ideia é a mesma do encadeamento. Lá, uma análise era uma sequência de operações
somadas com `.`. Aqui, um gráfico é uma sequência de camadas somadas com `+`.

> 📌 Se você quer **acompanhar a aula** rodando o mesmo código que está no
> telão, use o notebook **aula05**, que segue os slides na ordem e traz a
> gincana. Este aqui é para depois: é a referência do **Projeto 02**, na
> quinta-feira.
""",
    )

    nb.indice([
        ("A tabela de hoje", "dados"),
        ("Encadear operações", "encadear", [
            ("Do jeito da aula 3", "antigo"),
            ("🔗 A mesma coisa, encadeada", "encadeado"),
            ("Os cinco verbos", "verbos"),
            ("A ordem importa", "ordem"),
        ]),
        ("O que é um gráfico", "definicao"),
        ("Os três elementos obrigatórios", "gramatica", [
            ("1️⃣ Os dados", "elem-dados"),
            ("2️⃣ A estética: aes()", "elem-aes"),
            ("3️⃣ A geometria: geom_", "elem-geom"),
        ]),
        ("Uma variável categórica: barras", "categorica", [
            ("Barras deitadas", "flip"),
            ("🎨 Pintar não é mapear", "fill"),
        ]),
        ("Uma variável numérica: histograma", "numerica", [
            ("O número de caixas muda a leitura", "bins"),
            ("Densidade e boxplot", "outras-geoms"),
        ]),
        ("Rótulos: labs()", "labs"),
        ("Facetas: facet_wrap()", "facetas"),
        ("Que gráfico usar para cada variável", "escolha"),
        ("Exercícios", "exercicios", [
            ("EXERCÍCIO 1: barras de comarca", "ex1"),
            ("EXERCÍCIO 2: histograma da ementa", "ex2"),
            ("EXERCÍCIO 3: o gráfico da sua pergunta", "ex3"),
        ]),
        ("RESUMO", "resumo"),
    ])

    # ------------------------------------------------ dados

    nb.secao("dados", "A tabela de hoje", """
A mesma base de apelações criminais da aula 4, e a mesma tabela `penas` que
estava impressa na folha da dinâmica.
""")

    nb.md("""
O plotnine não vem instalado no Google Colab. Tire o `#` da segunda linha, rode
uma vez, e ponha o `#` de volta:
""")

    nb.code("""
# no Colab, rode uma vez:
# %pip install -q plotnine
""")

    nb.code("""
import pandas as pd
from plotnine import *

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)

URL = "https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/dados"
""")

    nb.md("""
> 🤔 `from plotnine import *` traz todos os nomes da biblioteca de uma vez:
> `ggplot`, `aes`, `geom_bar` e companhia. Fora do plotnine essa forma é
> desaconselhada, porque você não sabe mais de onde cada nome veio. Aqui ela é a
> convenção, porque um gráfico junta cinco ou seis desses nomes numa expressão só.
""")

    nb.code("""
criminal = pd.read_csv(f"{URL}/tjsp_cjsg_criminal.csv")

criminal["regime"] = pd.Categorical(
    criminal["regime_inicial"],
    categories=["aberto", "semiaberto", "fechado"],
    ordered=True,
)

penas = (
    criminal
    .dropna(subset=["regime", "pena_anos"])
    .query("pena_anos <= 30")
)

criminal.shape, penas.shape
""")

    nb.md("""
O corte em 30 anos tira as penas implausíveis, aquelas em que a leitura da ementa
pegou o número errado. É uma decisão de análise: está escrita no código, e
qualquer pessoa que leia o notebook sabe que ela existe.

Antes de qualquer coisa, olhe as duas tabelas. `.head()` mostra as primeiras
linhas, e é a primeira coisa a fazer depois de ler um arquivo: se a tabela veio
torta, você descobre agora e não daqui a vinte células.
""")

    nb.code("""
criminal.head()
""")

    nb.md("""
`penas` é a mesma tabela com duas decisões já tomadas: fora quem não tem regime
ou pena, e fora as penas acima de 30 anos. Repare que ela tem uma coluna a mais,
`regime`, que é a versão **ordenada** de `regime_inicial`.
""")

    nb.code("""
penas.head()
""")

    nb.volta()

    # ------------------------------------------------ espelho dos slides

    nb.secao("encadear", "Encadear operações", """
Esta seção é o espelho dos slides, para você acompanhar rodando. Nada aqui é
novo em relação ao que está sendo projetado.

A pergunta é a mesma da aula 4:

> Nas apelações criminais do TJSP, a proporção de acórdãos que mencionam
> reincidência varia conforme o regime inicial fixado?
""")

    nb.sub("antigo", "Do jeito da aula 3", """
Uma variável nova a cada operação. Funciona, e responde a pergunta:
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
Três problemas: **seis variáveis** que existem só para chegar num resultado,
**nomes que não dizem nada** (`com_regime` vai ser reaproveitado por engano daqui
a três células) e **não escala** (um quarto regime obriga a escrever mais uma
linha e a lembrar de incluí-la).
""")

    nb.sub("encadeado", "🔗 A mesma coisa, encadeada", """
Nenhuma variável intermediária, e a ordem das operações é a ordem das linhas.
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
Leia de cima para baixo, como uma frase: pegue `criminal`, fique só com as
apelações, descarte quem não tem regime, faça as pilhas por regime, e calcule a
proporção de cada pilha.

**Por que os parênteses.** Dentro de um par de parênteses o python deixa você
quebrar a linha à vontade. Sem eles, `criminal` seguido de quebra de linha e
`.query(...)` é erro de sintaxe. Eles existem só para você pôr uma operação por
linha:

```python
resultado = (
    tabela
    .operacao_1(...)
    .operacao_2(...)
)
```
""")

    nb.sub("verbos", "Os cinco verbos", """
Cinco operações resolvem quase toda análise descritiva. São as mesmas que estão
nas cartas da gincana.
""")

    nb.md("""
**1. `.query()` escolhe linhas.** A condição vai escrita como texto, e o valor
comparado vai entre aspas simples. Colunas de verdadeiro e falso dispensam a
comparação: basta o nome.
""")

    nb.code("""
criminal.query("eh_trafico").shape
""")

    nb.md("""
**2. `[[...]]` escolhe colunas.** São **dois** pares de colchetes. Um só devolve
a coluna solta, e o encadeamento acaba ali.
""")

    nb.code("""
(
    criminal
    [["processo", "comarca", "regime_inicial", "pena_anos"]]
    .head(3)
)
""")

    nb.md("""
**3. `.sort_values()` ordena.** `ascending=False` põe o maior primeiro.
""")

    nb.code("""
(
    criminal
    .sort_values("pena_anos", ascending=False)
    [["processo", "assunto", "pena_anos"]]
    .head(5)
)
""")

    nb.md("""
> ⚠️ Olhe o resultado acima com atenção. As maiores penas da base estão num
> furto, num estelionato e numa apropriação indébita, e chegam a 75 anos. A pena
> foi lida pegando o primeiro número seguido de "anos" na ementa, e às vezes o
> número está errado. É por isso que a tabela `penas` corta em 30.

**4. `.groupby()` e `.agg()` agregam por grupo.** O `groupby` faz as pilhas e o
`agg` calcula uma estatística em cada uma, devolvendo **uma linha por grupo**.
Depois dele, a coluna de agrupamento vira índice, e o `.reset_index()` traz ela
de volta para dentro da tabela.
""")

    nb.code("""
(
    criminal
    .groupby("regime_inicial")
    .agg(
        n=("processo", "size"),
        pena_mediana=("pena_anos", "median"),
        prop_reincidencia=("houve_reincidencia", "mean"),
    )
    .reset_index()
    .round(3)
)
""")

    nb.md("""
A média de uma coluna de verdadeiro e falso é a **proporção** de verdadeiros. Foi
assim que saiu `prop_reincidencia`.

**5. `.assign()` cria uma coluna nova**, dentro do encadeamento. O nome novo vai
à esquerda do `=`. A coluna criada só existe da linha seguinte em diante, então
o `.assign()` precisa vir **antes** de qualquer operação que use ela.
""")

    nb.code("""
(
    criminal
    .assign(eh_capital=criminal["comarca"] == "São Paulo")
    .groupby("eh_capital")
    .agg(n=("processo", "size"))
    .reset_index()
)
""")

    nb.md("""
E duas operações de apoio, que não são verbos novos:

* `.dropna(subset=["coluna"])` descarta as linhas em que **aquela** coluna está
  vazia. Sem o `subset`, descarta toda linha que tenha qualquer campo vazio, o
  que quase sempre é mais do que você queria.
* `.head(n)` fica com as `n` primeiras linhas **da tabela como ela está naquele
  ponto**. Guarde esta frase: a próxima seção é sobre ela.
""")

    nb.sub("ordem", "A ordem importa", """
As duas células abaixo têm exatamente as mesmas operações. Só trocam duas linhas
de lugar.
""")

    nb.md("""
Primeiro do jeito certo: ordenar e **depois** cortar.
""")

    nb.code("""
(
    criminal
    .sort_values("pena_anos", ascending=False)
    .head(5)
    [["processo", "pena_anos"]]
)
""")

    nb.md("""
Agora ao contrário: cortar e **depois** ordenar.
""")

    nb.code("""
(
    criminal
    .head(5)
    .sort_values("pena_anos", ascending=False)
    [["processo", "pena_anos"]]
)
""")

    nb.md("""
São cinco acórdãos quaisquer, os cinco primeiros da tabela, ordenados entre si.
Nada a ver com as maiores penas.

O `.head(5)` não sabe o que você queria. Ele pega as cinco primeiras linhas da
tabela **como ela está naquele ponto**, e é por isso que quase sempre vem por
último.
""")

    nb.volta()

    # ------------------------------------------------ definicao

    nb.secao("definicao", "O que é um gráfico", """
Antes de desenhar qualquer coisa, uma definição:

> Um gráfico estatístico é um **mapeamento de variáveis (colunas)** em
> **aspectos estéticos** de **formas geométricas**.

Quatro expressões fazem o trabalho:

| a expressão | o que quer dizer |
|---|---|
| mapeamento | uma ligação: cada valor da coluna vira um valor visual |
| variáveis (colunas) | o que sai da tabela, e nada mais |
| aspectos estéticos | posição, altura, cor, tamanho, forma |
| formas geométricas | barra, ponto, linha, caixa |

Repare no que a definição **não** diz: nada sobre que biblioteca usar, que cor
fica bonita ou que tipo de gráfico escolher. Ela diz o que precisa ser
**decidido**, e é essa lista de decisões que a próxima seção transforma em
código.
""")

    nb.volta()

    # ------------------------------------------------ gramatica

    nb.secao("gramatica", "Os três elementos obrigatórios", """
Todo gráfico do plotnine é uma soma de camadas, escrita dentro de parênteses,
uma por linha. As três primeiras são obrigatórias:

```python
(
    ggplot(tabela)          # 1. os dados
    + aes(x="coluna")       # 2. a estética: que variável vai em que lugar
    + geom_barra()          # 3. a geometria: que desenho aparece na tela
)
```

Repare no formato: é o mesmo da aula 4, com `+` no lugar de `.`. Abre parêntese,
uma camada por linha, e o parêntese permite quebrar a linha.
""")

    nb.sub("elem-dados", "1️⃣ Os dados", """
`ggplot(penas)` diz de qual tabela o gráfico sai. Só isso já é um gráfico
válido, e é um retângulo vazio: ainda não dissemos o que desenhar.
""")

    nb.code("""
ggplot(penas)
""")

    nb.sub("elem-aes", "2️⃣ A estética: aes()", """
**Estética** é a ligação entre uma coluna da tabela e uma propriedade visual do
gráfico. As mais usadas são `x`, `y`, `fill` (preenchimento), `color` (traço) e
`size`.

`aes(x="regime")` diz: a coluna `regime` vai no eixo horizontal. O plotnine
agora sabe do que se trata o eixo, e já desenha a escala.
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="regime")
)
""")

    nb.sub("elem-geom", "3️⃣ A geometria: geom_", """
**Geometria** é o desenho: barra, coluna, ponto, linha, caixa. É a camada que
finalmente põe tinta no papel.
""")

    nb.operacao(
        "geom_bar()",
        '(\n    ggplot(tabela)\n    + aes(x="coluna_categorica")\n    + geom_bar()\n)',
        "https://plotnine.org/reference/geom_bar.html",
        texto="""
`geom_bar()` conta quantas linhas existem em cada categoria e desenha uma barra
com a altura dessa contagem. Você não precisa contar antes: a contagem é parte
da geometria.
""",
    )

    nb.code("""
(
    ggplot(penas)
    + aes(x="regime")
    + geom_bar()
)
""")

    nb.md("""
As barras saem na ordem aberto, semiaberto, fechado porque `regime` é uma
categórica **ordenada**, declarada lá em cima. Se fosse texto comum, o plotnine
usaria a ordem alfabética, e o gráfico diria que semiaberto vem depois de
fechado, o que não é verdade em nada.

É a aula 2 cobrando a fatura: declarar o tipo certo não é preciosismo, é o que
faz o gráfico sair certo.
""")

    nb.volta()

    # ------------------------------------------------ categorica

    nb.secao("categorica", "Uma variável categórica: barras", """
Com uma variável categórica, a pergunta quase sempre é *quantos casos em cada
categoria*, e a resposta quase sempre é uma barra.
""")

    nb.faca(
        "Troque a variável do eixo x e faça as barras da classe processual.",
        '(\n    ggplot(penas)\n    + aes(x="classe")\n    + geom_bar()\n)',
        '(\n    ggplot(penas)\n    + aes(x="________")\n    + geom_bar()\n)',
    )

    nb.md("""
Os rótulos ficaram um por cima do outro. Isso acontece sempre que a categórica
tem nomes longos, e a solução é deitar as barras.
""")

    nb.sub("flip", "Barras deitadas", """
`coord_flip()` troca os eixos depois que o gráfico já está montado. Nada muda nos
dados nem na geometria: é só o sistema de coordenadas.
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="classe")
    + geom_bar()
    + coord_flip()
)
""")

    nb.sub("fill", "🎨 Pintar não é mapear", """
Esta é a distinção que o desafio da folha pedia, e é a ideia mais importante da
aula.

`fill` **fora** do `aes()` é uma escolha de tinta. Vale para tudo, não representa
nada, e não gera legenda:
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="regime")
    + geom_bar(fill="#E50505")
)
""")

    nb.md("""
`fill` **dentro** do `aes()` é um mapeamento. A cor passa a representar uma
variável, cada barra se reparte, e aparece uma legenda, porque agora a cor
significa alguma coisa:
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="regime", fill="houve_reincidencia")
    + geom_bar()
)
""")

    nb.md("""
> ⚠️ A regra vale para todas as estéticas, não só para `fill`. Dentro do `aes()`
> o argumento recebe o **nome de uma coluna**. Fora do `aes()` ele recebe um
> **valor fixo**. Trocar os dois de lugar é o erro mais comum de quem está
> começando, e o sintoma é sempre o mesmo: apareceu uma legenda que você não
> queria, ou sumiu a legenda que você queria.

Este gráfico já responde à pergunta da aula 4, agora sem tabela: a fatia colorida
cresce conforme o regime fica mais severo. Guarde a pergunta que ele **não**
responde: as três barras têm tamanhos diferentes, então comparar as fatias de
olho é comparar proporções em bases diferentes. Voltamos a isso na aula 6.
""")

    nb.faca(
        "Faça as barras de `regime` repartidas por `eh_trafico`.",
        '(\n    ggplot(penas)\n    + aes(x="regime", fill="eh_trafico")\n    + geom_bar()\n)',
        '(\n    ggplot(penas)\n    + aes(x="regime", ________="eh_trafico")\n    + geom_bar()\n)',
    )

    nb.volta()

    # ------------------------------------------------ numerica

    nb.secao("numerica", "Uma variável numérica: histograma", """
Com uma variável numérica contínua não dá para contar por valor: quase toda pena
aparece uma ou duas vezes. O histograma resolve isso cortando o eixo em faixas de
mesma largura, as **caixas**, e contando quantos casos caem em cada uma.
""")

    nb.operacao(
        "geom_histogram()",
        '(\n    ggplot(tabela)\n    + aes(x="coluna_numerica")\n    + geom_histogram(bins=10)\n)',
        "https://plotnine.org/reference/geom_histogram.html",
        texto="""
`bins` é o número de caixas. Sem ele, o plotnine escolhe um número e avisa que
escolheu.
""",
    )

    nb.code("""
(
    ggplot(penas)
    + aes(x="pena_anos")
    + geom_histogram(bins=10)
)
""")

    nb.md("""
A leitura: a maior parte das penas está abaixo de cinco anos, e a distribuição
tem uma cauda longa à direita. É a mesma assimetria que separava a média da
mediana na aula 3, agora visível de uma vez.
""")

    nb.sub("bins", "O número de caixas muda a leitura", """
São as cartas 5 e 6 da dinâmica. Mesmos dados, mesma geometria, duas histórias:
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="pena_anos")
    + geom_histogram(bins=40)
)
""")

    nb.md("""
Com 40 caixas aparecem picos e buracos que são, em boa parte, o tamanho da
amostra, e não um padrão das penas. Com 5 caixas aconteceria o contrário: a
cauda sumiria dentro de uma barra só.

Qual está certo? Nenhum. **O número de caixas é decisão de quem analisa**, e é
por isso que ele fica escrito no código, à vista. Um bom hábito é olhar dois ou
três valores antes de escolher.
""")

    nb.faca(
        "Rode o mesmo histograma com 5 caixas e compare com os dois de cima.",
        '(\n    ggplot(penas)\n    + aes(x="pena_anos")\n    + geom_histogram(bins=5)\n)',
        '(\n    ggplot(penas)\n    + aes(x="pena_anos")\n    + geom_histogram(bins=________)\n)',
    )

    nb.sub("outras-geoms", "Densidade e boxplot", """
Trocar a geometria é trocar uma linha. `geom_density()` desenha uma curva lisa no
lugar das colunas, e é útil quando o interesse é o formato da distribuição, e não
a contagem:
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x="pena_anos")
    + geom_density()
)
""")

    nb.md("""
O boxplot é o resumo da aula 3 virado desenho: a caixa vai do primeiro ao
terceiro quartil, a linha do meio é a mediana, e os pontos soltos são os valores
distantes do resto.

Ele precisa de duas estéticas, uma para o eixo do grupo e outra para o valor.
Como aqui não há grupo nenhum, o `x` recebe um texto fixo, entre aspas duplas e
simples, só para o plotnine ter o que pôr no eixo:
""")

    nb.code("""
(
    ggplot(penas)
    + aes(x='"todos os acórdãos"', y="pena_anos")
    + geom_boxplot()
)
""")

    nb.md("""
> 🤔 Um boxplot de uma variável só serve para pouca coisa. O boxplot fica útil
> quando há um grupo no eixo `x`, e aí ele compara várias distribuições lado a
> lado. Isso é a aula 6.
""")

    nb.volta()

    # ------------------------------------------------ labs

    nb.secao("labs", "Rótulos: labs()", """
Por padrão, os eixos recebem o nome da coluna. `pena_anos` e `count` servem para
você, e não servem para ninguém mais. `labs()` troca os rótulos, e é a diferença
entre um gráfico de rascunho e um gráfico que pode ir para o relatório.
""")

    nb.operacao(
        "labs()",
        'labs(title="Título", x="Eixo x", y="Eixo y", fill="Legenda")',
        "https://plotnine.org/reference/labs.html",
    )

    nb.code("""
(
    ggplot(penas)
    + aes(x="pena_anos")
    + geom_histogram(bins=10, fill="#E50505")
    + labs(
        title="Penas fixadas em apelações criminais do TJSP",
        subtitle="Acórdãos com pena identificada na ementa, até 30 anos",
        x="Pena (anos)",
        y="Acórdãos",
    )
    + theme_minimal()
)
""")

    nb.md("""
`theme_minimal()` é uma decisão só de aparência: tira o fundo cinza e deixa o
gráfico mais limpo para impressão. Existem outros temas prontos, e nenhum deles
muda os dados.
""")

    nb.faca(
        "Ponha título e rótulos no gráfico de barras do regime.",
        '(\n    ggplot(penas)\n    + aes(x="regime")\n    + geom_bar(fill="#E50505")\n'
        '    + labs(\n        title="Regime inicial fixado",\n'
        '        x="Regime inicial",\n        y="Acórdãos",\n    )\n'
        '    + theme_minimal()\n)',
        '(\n    ggplot(penas)\n    + aes(x="regime")\n    + geom_bar(fill="#E50505")\n'
        '    + ________(\n        title="Regime inicial fixado",\n'
        '        x="________",\n        y="Acórdãos",\n    )\n'
        '    + theme_minimal()\n)',
    )

    nb.volta()

    # ------------------------------------------------ facetas

    nb.secao("facetas", "Facetas: facet_wrap()", """
A faceta não faz um gráfico novo. Ela **repete** o mesmo gráfico, uma vez para
cada valor de uma variável, com os mesmos eixos, para que os painéis sejam
comparáveis.
""")

    nb.operacao(
        "facet_wrap()",
        'facet_wrap("coluna_categorica")',
        "https://plotnine.org/reference/facet_wrap.html",
    )

    nb.code("""
(
    ggplot(penas)
    + aes(x="pena_anos")
    + geom_histogram(bins=10)
    + facet_wrap("regime")
    + labs(x="Pena (anos)", y="Acórdãos")
    + theme_minimal()
)
""")

    nb.md("""
Agora dá para ver o que a tabela da aula 4 dizia com números: a distribuição das
penas se desloca para a direita conforme o regime fica mais severo.

Faceta ou cor? As duas mostram a mesma informação. A cor põe tudo junto e facilita
comparar o total; a faceta separa e facilita comparar o formato de cada grupo.
Com três categorias, qualquer uma serve. Com dez, faceta.
""")

    nb.faca(
        "Reparta o histograma por `eh_trafico` em vez de por regime.",
        '(\n    ggplot(penas)\n    + aes(x="pena_anos")\n    + geom_histogram(bins=10)\n'
        '    + facet_wrap("eh_trafico")\n    + theme_minimal()\n)',
        '(\n    ggplot(penas)\n    + aes(x="pena_anos")\n    + geom_histogram(bins=10)\n'
        '    + ________("eh_trafico")\n    + theme_minimal()\n)',
    )

    nb.volta()

    # ------------------------------------------------ escolha

    nb.secao("escolha", "Que gráfico usar para cada variável", """
O tipo da variável, que é a aula 2, decide a geometria. Para uma variável de cada
vez:

| tipo da variável | exemplo na base | geometria | o que você lê |
|---|---|---|---|
| categórica nominal | `comarca`, `classe` | `geom_bar()` + `coord_flip()` | quantos casos em cada categoria |
| categórica ordinal | `regime` | `geom_bar()` | o mesmo, na ordem que importa |
| binária | `houve_reincidencia` | `geom_bar()` | quantos sim e quantos não |
| numérica discreta | `n_palavras_ementa` | `geom_histogram()` | onde os valores se concentram |
| numérica contínua | `pena_anos` | `geom_histogram()`, `geom_density()`, `geom_boxplot()` | formato, centro e dispersão |

Duas armadilhas frequentes:

* **Histograma de categórica** não existe. Se a variável é texto, é barra.
* **Barras de uma variável contínua** também não: cada valor viraria uma barra de
  altura 1, e o gráfico não diria nada. Se for contínua, é histograma.
""")

    nb.volta()

    # ------------------------------------------------ exercicios

    nb.secao("exercicios", "Exercícios")

    nb.exercicio(1, "ex1", """
Faça um gráfico de barras das dez comarcas com mais acórdãos, deitado, com título
e rótulos.

A parte de pandas é a da aula 4: agrupe, conte, ordene e corte. Depois use
`geom_col()`, que desenha barras com a altura que **você** informou em `y`, em
vez de contar as linhas como o `geom_bar()`.
""")

    nb.code(
        'top_comarcas = (\n    criminal\n    .groupby("comarca")\n'
        '    .agg(n=("processo", "size"))\n    .reset_index()\n'
        '    .sort_values("n", ascending=False)\n    .head(10)\n)\n\n'
        '(\n    ggplot(top_comarcas)\n    + aes(x="comarca", y="n")\n'
        '    + geom_col(fill="#E50505")\n    + coord_flip()\n'
        '    + labs(title="Comarcas com mais acórdãos", x="Comarca", y="Acórdãos")\n'
        '    + theme_minimal()\n)',
        'top_comarcas = (\n    criminal\n    .groupby("________")\n'
        '    .agg(n=("processo", "size"))\n    .reset_index()\n'
        '    .sort_values("n", ascending=________)\n    .head(________)\n)\n\n'
        '(\n    ggplot(top_comarcas)\n    + aes(x="comarca", y="________")\n'
        '    + geom_col(fill="#E50505")\n    + ________()\n'
        '    + labs(title="Comarcas com mais acórdãos", x="Comarca", y="Acórdãos")\n'
        '    + theme_minimal()\n)',
    )

    nb.exercicio(2, "ex2", """
Faça um histograma do tamanho da ementa, `n_palavras_ementa`, com 20 caixas,
repartido por regime, com título e rótulos.
""")

    nb.code(
        '(\n    ggplot(penas)\n    + aes(x="n_palavras_ementa")\n'
        '    + geom_histogram(bins=20)\n    + facet_wrap("regime")\n'
        '    + labs(\n        title="Tamanho da ementa por regime inicial",\n'
        '        x="Palavras na ementa",\n        y="Acórdãos",\n    )\n'
        '    + theme_minimal()\n)',
        '(\n    ggplot(penas)\n    + aes(x="________")\n'
        '    + geom_histogram(bins=________)\n    + ________("regime")\n'
        '    + labs(\n        title="Tamanho da ementa por regime inicial",\n'
        '        x="Palavras na ementa",\n        y="Acórdãos",\n    )\n'
        '    + theme_minimal()\n)',
    )

    nb.exercicio(3, "ex3", """
Escreva, em uma frase, uma pergunta descritiva sobre esta base que possa ser
respondida com **uma variável só**. Depois faça o gráfico que a responde, com
título e rótulos, e escreva embaixo, em duas linhas, o que ele mostra e o que ele
não permite concluir.

É o mesmo exercício que vocês vão repetir na pesquisa de campo, com os dados de
vocês.
""")

    nb.code(
        '# pergunta: em que faixa se concentram as penas dos acórdãos de tráfico?\n\n'
        '(\n    ggplot(penas.query("eh_trafico"))\n    + aes(x="pena_anos")\n'
        '    + geom_histogram(bins=12, fill="#E50505")\n'
        '    + labs(\n        title="Penas em acórdãos de tráfico",\n'
        '        x="Pena (anos)",\n        y="Acórdãos",\n    )\n'
        '    + theme_minimal()\n)\n\n'
        '# mostra: concentração entre 1 e 6 anos, com cauda à direita.\n'
        '# não permite concluir: nada sobre acórdãos sem pena identificada na\n'
        '# ementa, que são mais da metade da base.',
        '# pergunta:\n\n(\n    ggplot(________)\n    + aes(x="________")\n'
        '    + ________\n    + labs(\n        title="________",\n'
        '        x="________",\n        y="________",\n    )\n'
        '    + theme_minimal()\n)\n\n# mostra:\n# não permite concluir:',
    )

    nb.volta()

    # ------------------------------------------------ resumo

    nb.resumo("""
Um gráfico é uma soma de camadas, escrita dentro de parênteses, uma por linha.
Três são obrigatórias, o resto é ajuste.

| camada | para quê |
|---|---|
| `ggplot(tabela)` | de qual tabela o gráfico sai |
| `+ aes(x=..., fill=...)` | que coluna vai em que propriedade visual |
| `+ geom_bar()` | contar categorias e desenhar barras |
| `+ geom_histogram(bins=n)` | cortar uma variável numérica em caixas e contar |
| `+ geom_density()` | o formato da distribuição, em curva |
| `+ geom_boxplot()` | mediana, quartis e valores distantes |
| `+ geom_col()` | barras com a altura que você informou em `y` |
| `+ coord_flip()` | deitar as barras |
| `+ facet_wrap("coluna")` | repetir o mesmo gráfico por categoria |
| `+ labs(title=..., x=..., y=...)` | rótulos que outra pessoa entende |
| `+ theme_minimal()` | aparência |
""")

    nb.code("""
#=> DADOS: a tabela, já filtrada e com os tipos declarados
(
    ggplot(penas)

    #=> ESTÉTICA: nome de coluna dentro do aes() é mapeamento
    + aes(x="pena_anos")

    #=> GEOMETRIA: valor fixo fora do aes() é só tinta
    + geom_histogram(bins=10, fill="#E50505")

    #=> FACETA: o mesmo gráfico, repetido por categoria
    + facet_wrap("regime")

    #=> RÓTULOS: sem isso o eixo diz "count"
    + labs(
        title="Penas por regime inicial",
        x="Pena (anos)",
        y="Acórdãos",
    )

    #=> TEMA: só aparência
    + theme_minimal()
)
""")

    nb.md("""
**Três regras que valem sempre:**

1. Dentro do `aes()` vai **nome de coluna**; fora do `aes()` vai **valor fixo**.
   Legenda que apareceu sem ser chamada é quase sempre isso.
2. O tipo da variável escolhe a geometria: categórica pede barra, numérica pede
   histograma.
3. Todo número que você escolheu, como `bins`, é uma decisão de análise. Ele fica
   no código para que a decisão seja discutível.
""")

    nb.volta()

    return nb

# ====================================================== AULA EXTRA


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


# ====================================================== AULA 6


def montar_aula06() -> Caderno:
    nb = Caderno("aula06")

    nb.cabecalho(
        "Atividade: Duas Variáveis",
        "Aula 06",
        [
            "escolher a geometria a partir do par de tipos das duas variáveis;",
            "ler uma nuvem de pontos e uma linha de tendência sem exagerar na conclusão;",
            "comparar uma numérica entre categorias com boxplot;",
            "comparar duas categóricas em contagem e em proporção;",
            "preparar a tabela com `.assign()` antes de fazer o gráfico;",
            "saber quando a altura da barra é contagem (`geom_bar`) e quando "
            "já é uma conta pronta (`geom_col`).",
        ],
        abertura="""
Na aula 5 todo gráfico tinha **uma** variável: quantos acórdãos em cada regime,
como as penas se distribuem. A pergunta era sempre sobre uma coluna sozinha.

Hoje entram duas. A gramática é a mesma, e a única mudança é que o `aes()` passa
a receber dois nomes de coluna em vez de um. Toda a novidade da aula cabe nesta
frase:

> **O par de tipos escolhe a geometria.** Duas numéricas pedem pontos, uma
> numérica com uma categórica pede caixas, duas categóricas pedem barras
> repartidas.

Na segunda hora de hoje é o **Projeto 02**, individual e valendo nota. Ele é a
Gincana do Pipeline no computador: blocos de pandas e de plotnine fora de ordem,
e você organiza. Este notebook tem, de propósito, tudo o que o projeto vai
cobrar e que ainda não apareceu.
""",
    )

    nb.indice([
        ("A tabela de hoje", "dados"),
        ("De onde a gincana parou", "retomada", [
            ("Uma variável numérica sozinha", "histograma"),
            ("A coluna que não existe na base", "assign"),
            ("Contar não é medir: geom_bar e geom_col", "contarmedir"),
        ]),
        ("Uma forma mais curta de escrever", "curta"),
        ("Duas numéricas: pontos", "numnum", [
            ("A linha de tendência", "smooth"),
            ("Uma terceira variável na cor", "cor"),
        ]),
        ("Numérica e categórica: caixas", "numcat"),
        ("Duas categóricas: barras repartidas", "catcat", [
            ("Contagem ou proporção: position", "position"),
        ]),
        ("Preparar a tabela antes do gráfico", "preparar", [
            ("Sair do groupby já com a coluna", "asindex"),
            ("Ordenar as barras com reorder()", "reorder"),
        ]),
        ("Que gráfico para que par de variáveis", "escolha"),
        ("Exercícios", "exercicios", [
            ("EXERCÍCIO 1: pena e tamanho da ementa", "ex1"),
            ("EXERCÍCIO 2: tráfico e regime", "ex2"),
            ("EXERCÍCIO 3: a sua pergunta, com duas variáveis", "ex3"),
        ]),
        ("RESUMO", "resumo"),
    ])

    # ------------------------------------------------ dados

    nb.secao("dados", "A tabela de hoje", """
A mesma base de apelações criminais da aula 5, e a mesma tabela `penas`.
""")

    nb.code("""
# no Colab, rode uma vez:
# %pip install -q plotnine
""")

    nb.code("""
import pandas as pd
from plotnine import *

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)

URL = "https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/dados"
""")

    nb.code("""
criminal = pd.read_csv(f"{URL}/tjsp_cjsg_criminal.csv")

criminal["regime"] = pd.Categorical(
    criminal["regime_inicial"],
    categories=["aberto", "semiaberto", "fechado"],
    ordered=True,
)

penas = (
    criminal
    .dropna(subset=["regime", "pena_anos"])
    .query("pena_anos <= 30")
)

penas.shape
""")

    nb.volta()

    # ------------------------------------------------ retomada da gincana

    nb.secao("retomada", "De onde a gincana parou", """
A gincana da aula 5 não chegou até o fim: ficaram duas rodadas na mesa, e as
duas voltam aqui. Não é revisão: são três ideias que o **Projeto 02** cobra e
que ainda não apareceram escritas.
""")

    nb.sub("histograma", "Uma variável numérica sozinha", """
Antes de comparar duas variáveis, vale olhar uma. Uma coluna **categórica** vira
barras, e você já fez isso. Uma coluna **numérica** não tem categorias para
contar: o que se faz é cortar a variável em faixas e contar quantos casos caem
em cada uma. Isso é o histograma.
""")

    nb.operacao(
        "geom_histogram()",
        "geom_histogram(bins=20)",
        "https://plotnine.org/reference/geom_histogram.html",
    )

    nb.code("""
(
    ggplot(penas)
    + aes(x="pena_anos")
    + geom_histogram(bins=20)
    + labs(x="Pena (anos)", y="Acórdãos")
)
""")

    nb.md("""
> 🤔 Troque `bins=20` por `bins=5` e depois por `bins=60`. O número de faixas
> muda o que o gráfico deixa ver, e não existe número certo: existe número que
> responde à sua pergunta.

Guarde esta leitura, porque o **boxplot** de hoje é um resumo dela. Onde o
histograma mostra a forma inteira, o boxplot mostra mediana, quartis e pontos
fora, e é isso que permite pôr vários lado a lado.
""")

    nb.sub("assign", "A coluna que não existe na base", """
Às vezes a coluna que responde à pergunta simplesmente não está na tabela.
"A capital julga diferente do interior?" precisa de uma coluna que diga capital
ou interior, e a base só tem `comarca`.

`.assign()` cria essa coluna **dentro** do encadeamento, sem quebrar o pipeline
em duas partes. O nome novo vai à esquerda do `=`.
""")

    nb.operacao(
        ".assign()",
        "DataFrame.assign(nome_novo=expressao)",
        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.assign.html",
    )

    nb.code("""
(
    criminal
    .assign(eh_capital=criminal["comarca"] == "São Paulo")
    .dropna(subset=["pena_anos"])
    .groupby("eh_capital")
    .agg(
        n=("processo", "size"),
        pena_mediana=("pena_anos", "median"),
    )
    .reset_index()
)
""")

    nb.md("""
> 📌 O `.assign()` precisa vir **antes** do `.groupby()` que usa a coluna nova.
> É a única ordem do pipeline que não pode trocar: a coluna tem que existir para
> poder ser agrupada. Todas as outras operações acima comutam entre si.
""")

    nb.sub("contarmedir", "Contar não é medir: geom_bar e geom_col", """
Duas perguntas parecidas, e dois gráficos diferentes:

* *quantos acórdãos em cada regime?* A altura da barra é uma **contagem**, e
  quem conta é a geometria.
* *que proporção dos acórdãos de cada regime é de reincidentes?* A altura é uma
  **conta que você fez**, e a geometria só desenha o número que já está lá.
""")

    nb.code("""
# contar: geom_bar() conta as linhas sozinho, e não existe coluna y
(
    ggplot(penas)
    + aes(x="regime")
    + geom_bar()
    + labs(x="Regime inicial", y="Acórdãos")
)
""")

    nb.code("""
# medir: primeiro o pandas faz a conta...
resumo_regime = (
    penas
    .groupby("regime", as_index=False, observed=True)
    .agg(prop_reincidencia=("houve_reincidencia", "mean"))
)

resumo_regime
""")

    nb.md("""
Repare no `"mean"` aplicado a `houve_reincidencia`, que é uma coluna de
verdadeiro e falso. A média de uma coluna assim **é** a proporção de
verdadeiros: verdadeiro conta como 1, falso como 0, e a média de 1 e 0 é a
fração de 1. É o jeito mais curto de calcular proporção em pandas, e o Projeto
02 usa isso nos dois desafios de barras e de linhas.
""")

    nb.code("""
# ...e aí o plotnine só desenha a altura que já está na coluna y
(
    ggplot(resumo_regime)
    + aes(x="regime", y="prop_reincidencia")
    + geom_col()
    + labs(x="Regime inicial", y="Proporção com reincidência")
)
""")

    nb.md("""
> ⚠️ Trocar `geom_col()` por `geom_bar()` aqui não dá erro: dá três barras de
> altura 1, porque cada regime tem uma linha na tabela `resumo_regime` e o
> `geom_bar()` conta linhas. Vale rodar para ver.

**A regra:** a altura já está na tabela? `geom_col()`. A altura é o número de
linhas? `geom_bar()`.
""")

    nb.volta()

    # ------------------------------------------------ forma curta

    nb.secao("curta", "Uma forma mais curta de escrever", """
Na aula 5 escrevemos os dados e a estética em camadas separadas, uma por linha.
Existe uma forma mais curta, em que o `aes()` vai **dentro** do `ggplot()`, como
segundo argumento:
""")

    nb.code("""
# as duas células abaixo produzem exatamente o mesmo gráfico

(
    ggplot(penas)
    + aes(x="regime")
    + geom_bar()
)
""")

    nb.code("""
(
    ggplot(penas, aes(x="regime"))
    + geom_bar()
)
""")

    nb.md("""
> 📌 As duas formas convivem, e você vai encontrar as duas em qualquer código
> que buscar na internet. A forma longa é melhor para aprender, porque separa
> as camadas. A curta é a mais comum na prática, e é a que o **Projeto 02**
> usa. Reconhecer as duas é obrigatório; escolher entre elas é gosto.

A regra de sempre continua valendo, e é a mesma da aula 5: **nome de coluna
dentro do `aes()`, valor fixo fora dele**. O que mudou foi só onde o `aes()`
está escrito, não o que ele faz.
""")

    nb.volta()

    # ------------------------------------------------ duas numericas

    nb.secao("numnum", "Duas numéricas: pontos", """
Quando as duas variáveis são numéricas, a pergunta é *quando uma cresce, o que
acontece com a outra*, e a geometria é o ponto: um ponto por linha da tabela,
com a posição dada pelas duas colunas.
""")

    nb.operacao(
        "geom_point()",
        '(\n'
        '    ggplot(tabela, aes(x="coluna_numerica", y="outra_numerica"))\n'
        '    + geom_point()\n'
        ')',
        "https://plotnine.org/reference/geom_point.html",
        "Agora o `aes()` recebe dois nomes: um para cada eixo.",
    )

    nb.code("""
(
    ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos"))
    + geom_point()
    + labs(x="Palavras na ementa", y="Pena (anos)")
)
""")

    nb.md("""
Os pontos estão empilhados uns sobre os outros na parte de baixo. Quando isso
acontece, `alpha` deixa cada ponto transparente, e a mancha escura passa a
mostrar onde há muitos casos sobrepostos.

`alpha` vai **fora** do `aes()`, porque é um valor fixo: 0 é invisível e 1 é
opaco.
""")

    nb.faca(
        "Deixe os pontos com 40% de opacidade e um pouco maiores.",
        """
(
    ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos"))
    + geom_point(alpha=0.4, size=2)
    + labs(x="Palavras na ementa", y="Pena (anos)")
)
""",
        """
(
    ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos"))
    + geom_point(alpha=________, size=2)
    + labs(x="Palavras na ementa", y="Pena (anos)")
)
""",
    )

    nb.sub("smooth", "A linha de tendência", """
`geom_smooth(method="lm")` desenha a reta que melhor resume a nuvem, com uma
faixa de incerteza em volta. É uma camada a mais, somada com `+` como qualquer
outra.
""")

    nb.code("""
(
    ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm", color="#E50505")
    + labs(x="Palavras na ementa", y="Pena (anos)")
)
""")

    nb.md("""
**A reta é quase plana, e a faixa em volta dela é larga.** Isso é uma resposta,
e uma resposta útil: o tamanho da ementa não diz quase nada sobre a pena.

Duas leituras que o gráfico **não** autoriza:

1. **Reta plana não prova que não há relação.** Prova que não há relação *linear*
   nestes 197 acórdãos, que são os que tinham regime e pena legíveis na ementa.
2. **Reta inclinada não provaria causa.** Se ementas longas viessem com penas
   altas, o mais provável seria que caso grave gera ementa longa *e* pena alta.
   A reta mede associação, e associação não é causa.

> ⚠️ A ordem das camadas importa para o que fica **por cima**: `geom_point()`
> antes de `geom_smooth()` deixa a linha visível sobre os pontos. Trocar a ordem
> não muda os dados, só quem tapa quem.
""")

    nb.sub("cor", "Uma terceira variável na cor", """
A mesma nuvem, com `color` dentro do `aes()`: cada regime ganha uma cor, e a
partir daí o `geom_smooth()` desenha **uma reta por grupo**.
""")

    nb.code("""
(
    ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos", color="regime"))
    + geom_point(alpha=0.6)
    + geom_smooth(method="lm", se=False)
    + labs(x="Palavras na ementa", y="Pena (anos)", color="Regime inicial")
)
""")

    nb.md("""
É a mesma ideia do `fill` da aula 5: dentro do `aes()`, a cor virou variável.
E repare no `labs(color=...)`: o `labs()` dá nome a qualquer estética, não só
aos eixos. Sem ele, a legenda sairia escrita `regime`.

> 🤔 Quando o eixo x é tempo, a geometria que liga os pontos é `geom_line()`, e
> `color` dentro do `aes()` desenha uma linha por categoria. É exatamente o que
> você acabou de fazer, trocando `geom_point` por `geom_line`.
""")

    nb.volta()

    # ------------------------------------------------ numerica x categorica

    nb.secao("numcat", "Numérica e categórica: caixas", """
Quando uma variável é numérica e a outra é categórica, a pergunta é *a
distribuição da numérica muda entre as categorias*, e a geometria é o boxplot:
uma caixa por categoria.
""")

    nb.operacao(
        "geom_boxplot()",
        '(\n'
        '    ggplot(tabela, aes(x="categorica", y="numerica"))\n'
        '    + geom_boxplot()\n'
        ')',
        "https://plotnine.org/reference/geom_boxplot.html",
    )

    nb.code("""
(
    ggplot(penas, aes(x="regime", y="pena_anos"))
    + geom_boxplot(fill="#DCDCDC")
    + labs(x="Regime inicial", y="Pena (anos)")
)
""")

    nb.md("""
Cada caixa é o resumo da aula 3, desenhado: a linha do meio é a **mediana**, a
caixa vai do primeiro ao terceiro **quartil**, os fios vão até os valores ainda
considerados típicos, e os pontos soltos são os distantes.

A leitura sai direta: a mediana sobe de cerca de 1,4 ano no regime aberto para
3,1 no semiaberto e 5,8 no fechado, e as caixas quase não se sobrepõem. É a
mesma conclusão da tabela da rodada 3 da gincana, agora em uma imagem.

> ⚠️ O boxplot resume, e resumir é esconder. Duas distribuições muito diferentes
> podem ter a mesma caixa. Quando a forma importar, o histograma com facetas da
> aula 5 mostra o que a caixa apagou.
""")

    nb.md("""
Com muitas categorias, ou com nomes longos, vale deitar: `coord_flip()` de novo,
igual à aula 5.
""")

    nb.faca(
        "Deite as caixas de `pena_anos` por `classe`.",
        """
(
    ggplot(penas, aes(x="classe", y="pena_anos"))
    + geom_boxplot(fill="#DCDCDC")
    + coord_flip()
    + labs(x="Classe processual", y="Pena (anos)")
)
""",
        """
(
    ggplot(penas, aes(x="classe", y="pena_anos"))
    + geom_boxplot(fill="#DCDCDC")
    + ________
    + labs(x="Classe processual", y="Pena (anos)")
)
""",
    )

    nb.volta()

    # ------------------------------------------------ duas categoricas

    nb.secao("catcat", "Duas categóricas: barras repartidas", """
Quando as duas são categóricas, a pergunta é *a distribuição de uma muda
conforme a outra*, e a geometria é a barra, com a segunda variável no `fill`.

Você já fez isso na rodada 5 da gincana:
""")

    nb.code("""
(
    ggplot(penas, aes(x="regime", fill="houve_reincidencia"))
    + geom_bar()
    + labs(x="Regime inicial", y="Acórdãos", fill="Reincidência")
)
""")

    nb.md("""
E já ouviu o problema dele: **as três barras têm alturas diferentes**, porque há
mais acórdãos em regime fechado. Comparar as fatias de olho engana, porque você
está comparando pedaços de bolos de tamanhos diferentes.
""")

    nb.sub("position", "Contagem ou proporção: position", """
O argumento `position` decide como as fatias se arrumam dentro da barra. São
três valores, e cada um responde a uma pergunta diferente.
""")

    nb.operacao(
        "geom_bar(position=)",
        'geom_bar(position="stack")  # empilhado: o padrão, mostra a contagem\n'
        'geom_bar(position="fill")   # todas as barras com altura 1: proporção\n'
        'geom_bar(position="dodge")  # lado a lado: contagem, sem empilhar',
        "https://plotnine.org/reference/geom_bar.html",
    )

    nb.code("""
(
    ggplot(penas, aes(x="regime", fill="houve_reincidencia"))
    + geom_bar(position="fill")
    + labs(x="Regime inicial", y="Proporção", fill="Reincidência")
)
""")

    nb.md("""
Agora sim as três barras têm a mesma altura, e a comparação é honesta: a
proporção de acórdãos com reincidência vai de 0,07 no regime aberto para 0,42 no
semiaberto e 0,51 no fechado.

**É a resposta da pergunta que abriu a aula 4**, e é o mesmo número que a rodada
6 da gincana calculou no pandas. A diferença é que aqui o plotnine calculou a
proporção sozinho, dentro da geometria.

> ⚠️ `position="fill"` esconde quanta gente tem em cada barra. Uma barra com 4
> acórdãos e outra com 400 ficam do mesmo tamanho. Quando o tamanho do grupo
> importa, mostre os dois gráficos, ou escreva o `n` no rótulo.
""")

    nb.faca(
        "Faça as barras lado a lado, em vez de empilhadas.",
        """
(
    ggplot(penas, aes(x="regime", fill="eh_trafico"))
    + geom_bar(position="dodge")
    + labs(x="Regime inicial", y="Acórdãos", fill="Tráfico")
)
""",
        """
(
    ggplot(penas, aes(x="regime", fill="eh_trafico"))
    + geom_bar(position="________")
    + labs(x="Regime inicial", y="Acórdãos", fill="Tráfico")
)
""",
    )

    nb.volta()

    # ------------------------------------------------ preparar a tabela

    nb.secao("preparar", "Preparar a tabela antes do gráfico", """
Você já viu a primeira operação desta lista lá em cima, no `.assign()`. Faltam
duas, e as duas caem no **Projeto 02**: um atalho para sair do `groupby` já com
a coluna, e o jeito de ordenar barras.
""")

    nb.sub("asindex", "Sair do groupby já com a coluna", """
Na aula 5 você usou `.reset_index()` depois de todo `groupby`, para trazer a
coluna de agrupamento de volta para dentro da tabela. Existe um atalho:
`as_index=False` dentro do próprio `groupby()` faz a mesma coisa, e poupa uma
peça.
""")

    nb.code("""
# as duas células abaixo devolvem exatamente a mesma tabela

(
    criminal
    .groupby("regime_inicial")
    .agg(n=("processo", "size"))
    .reset_index()
)
""")

    nb.code("""
(
    criminal
    .groupby("regime_inicial", as_index=False)
    .agg(n=("processo", "size"))
)
""")

    nb.md("""
> 📌 O `Projeto 02` usa a forma com `as_index=False`. As duas estão certas, e
> reconhecer que fazem a mesma coisa evita que você procure um `.reset_index()`
> que não existe.

Para agrupar por **duas** colunas, passe uma lista. O resultado tem uma linha por
combinação, e é a tabela típica de um gráfico com `color` ou `fill`.
""")

    nb.code("""
(
    penas
    .groupby(["regime", "eh_trafico"], as_index=False, observed=True)
    .agg(n=("processo", "size"), pena_mediana=("pena_anos", "median"))
)
""")

    nb.sub("reorder", "Ordenar as barras com reorder()", """
Ordenar a **tabela** com `.sort_values()` não reordena as **barras**: o plotnine
usa a ordem das categorias, não a ordem das linhas. Quem ordena barra é o
`reorder()`, escrito dentro do `aes()`.

`reorder("categoria", "valor")` põe as categorias em ordem crescente do valor.
""")

    nb.code("""
resumo_comarca = (
    penas
    .groupby("comarca", as_index=False)
    .agg(pena_mediana=("pena_anos", "median"), n=("processo", "size"))
    .query("n >= 5")
)

resumo_comarca
""")

    nb.faca(
        "Ordene as barras da menor para a maior pena mediana, usando "
        "`reorder()` no eixo x. Depois `coord_flip()` deita, e a maior fica em "
        "cima.",
        """
(
    ggplot(resumo_comarca, aes(x="reorder(comarca, pena_mediana)", y="pena_mediana"))
    + geom_col(fill="#E50505")
    + coord_flip()
    + labs(x="Comarca", y="Pena mediana (anos)")
)
""",
        """
(
    ggplot(resumo_comarca, aes(x="reorder(comarca, ________)", y="pena_mediana"))
    + geom_col(fill="#E50505")
    + coord_flip()
    + labs(x="Comarca", y="Pena mediana (anos)")
)
""",
    )

    nb.md("""
Repare que a altura já estava calculada na coluna `pena_mediana`, então a
geometria é `geom_col()`, e não `geom_bar()`. É a pegadinha da rodada 6 da
gincana, e ela vai reaparecer no projeto.
""")

    nb.volta()

    # ------------------------------------------------ escolha

    nb.secao("escolha", "Que gráfico para que par de variáveis", """
| as duas variáveis | a pergunta | a geometria |
|---|---|---|
| numérica × numérica | quando uma cresce, o que a outra faz | `geom_point()`, com `geom_smooth()` por cima |
| numérica × numérica, x é tempo | como evolui | `geom_line()` |
| numérica × categórica | a distribuição muda entre as categorias | `geom_boxplot()` |
| numérica × categórica, já resumida | comparar um valor por categoria | `geom_col()` |
| categórica × categórica | a composição muda entre as categorias | `geom_bar(position="fill")` |
| categórica × categórica, contagem | quantos casos em cada combinação | `geom_bar(position="dodge")` |

A terceira variável, quando existe, entra em `color` ou `fill` dentro do
`aes()`, ou em `facet_wrap()` quando o gráfico ficar carregado demais.
""")

    nb.volta()

    # ------------------------------------------------ exercicios

    nb.secao("exercicios", "Exercícios")

    nb.exercicio(1, "ex1", """
A pena e o tamanho da ementa, separando por tráfico.

Faça a nuvem de pontos de `pena_anos` contra `n_palavras_ementa`, com a cor
mapeada em `eh_trafico`, e uma reta de tendência por grupo. Depois escreva, em
uma linha, o que o gráfico mostra e o que ele **não** permite concluir.
""")

    nb.code(
        '(\n'
        '    ggplot(penas, aes(x="n_palavras_ementa", y="pena_anos", color="eh_trafico"))\n'
        '    + geom_point(alpha=0.6)\n'
        '    + geom_smooth(method="lm", se=False)\n'
        '    + labs(x="Palavras na ementa", y="Pena (anos)", color="Tráfico")\n'
        ')\n\n'
        '# mostra: as duas retas são quase planas, e os acórdãos de tráfico\n'
        '# aparecem com penas um pouco maiores em quase toda a faixa.\n'
        '# não permite concluir: nada sobre causa, e nada sobre os acórdãos\n'
        '# em que a pena não foi lida da ementa, que são mais da metade.',
        '(\n'
        '    ggplot(penas, aes(x="________", y="pena_anos", color="________"))\n'
        '    + geom_point(alpha=0.6)\n'
        '    + geom_smooth(method="lm", se=False)\n'
        '    + labs(x="Palavras na ementa", y="Pena (anos)", color="Tráfico")\n'
        ')\n\n'
        '# mostra:\n'
        '# não permite concluir:',
    )

    nb.exercicio(2, "ex2", """
Tráfico e regime, em proporção.

A proporção de acórdãos de tráfico muda conforme o regime inicial? Faça o
gráfico que responde isso **em proporção**, e não em contagem.
""")

    nb.code(
        '(\n'
        '    ggplot(penas, aes(x="regime", fill="eh_trafico"))\n'
        '    + geom_bar(position="fill")\n'
        '    + labs(x="Regime inicial", y="Proporção", fill="Tráfico")\n'
        ')',
        '(\n'
        '    ggplot(penas, aes(x="________", fill="________"))\n'
        '    + geom_bar(position="________")\n'
        '    + labs(x="Regime inicial", y="Proporção", fill="Tráfico")\n'
        ')',
    )

    nb.exercicio(3, "ex3", """
A sua pergunta, com duas variáveis.

Escolha **duas** colunas da base e escreva uma pergunta que só se responde
olhando as duas juntas. Depois:

1. diga o tipo de cada uma;
2. escolha a geometria pela tabela da seção anterior;
3. faça o gráfico, com `labs()` preenchido;
4. escreva o que ele mostra e o que ele não permite concluir.

O passo 1 é o que decide os outros três. Se você não souber dizer o tipo das
duas, o gráfico vai sair errado.
""")

    nb.code(
        '# pergunta: a proporção de reincidência muda conforme a comarca é a\n'
        '# capital ou não?\n'
        '# tipos: eh_capital é categórica, houve_reincidencia é categórica\n\n'
        '(\n'
        '    ggplot(\n'
        '        penas.assign(eh_capital=penas["comarca"] == "São Paulo"),\n'
        '        aes(x="eh_capital", fill="houve_reincidencia"),\n'
        '    )\n'
        '    + geom_bar(position="fill")\n'
        '    + labs(x="É da capital", y="Proporção", fill="Reincidência")\n'
        ')\n\n'
        '# mostra: as duas barras ficam parecidas, então a comarca ser a capital\n'
        '# não separa os acórdãos quanto a reincidência.\n'
        '# não permite concluir: nada sobre o resto do estado agrupado, que\n'
        '# junta comarcas muito diferentes entre si.',
        '# pergunta: ________\n'
        '# tipos: ________\n\n'
        '(\n'
        '    ggplot(________, aes(x="________", ________="________"))\n'
        '    + ________\n'
        '    + labs(x="________", y="________")\n'
        ')\n\n'
        '# mostra:\n'
        '# não permite concluir:',
    )

    nb.volta()

    # ------------------------------------------------ resumo

    nb.resumo("""
Com duas variáveis, a gramática não muda: o que muda é que o `aes()` recebe dois
nomes de coluna, e o par de tipos escolhe a geometria.

| camada | para quê |
|---|---|
| `ggplot(tabela, aes(x=..., y=...))` | a forma curta: dados e estética juntos |
| `+ geom_point(alpha=, size=)` | duas numéricas, um ponto por linha |
| `+ geom_smooth(method="lm", se=False)` | a reta que resume a nuvem |
| `+ geom_line()` | duas numéricas quando o x é tempo |
| `+ geom_boxplot()` | uma numérica comparada entre categorias |
| `+ geom_col()` | a altura já calculada numa coluna |
| `+ geom_bar(position="fill")` | duas categóricas, em proporção |
| `+ geom_bar(position="dodge")` | duas categóricas, em contagem, lado a lado |
| `+ labs(x=, y=, color=, fill=)` | rótulos, inclusive o da legenda |

E três operações de pandas que quase todo gráfico calculado precisa:

| operação | para quê |
|---|---|
| `.assign(nova=expressao)` | criar uma coluna sem quebrar o encadeamento |
| `.groupby(col, as_index=False)` | agrupar já saindo com a coluna na tabela |
| `reorder("cat", "valor")` | ordenar as barras, dentro do `aes()` |
""")

    nb.md("""
**Três regras que valem sempre:**

1. **O par de tipos escolhe a geometria.** Antes de escrever qualquer coisa,
   diga em voz alta o tipo das duas variáveis.
2. **Ordenar a tabela não ordena as barras.** Quem ordena categoria no gráfico é
   o `reorder()`, dentro do `aes()`.
3. **`position="fill"` responde sobre proporção e esconde o tamanho do grupo.**
   Toda escolha de gráfico decide, junto, o que fica visível e o que some.
""")

    nb.volta()

    return nb


# ====================================================== main


def main() -> None:
    for construir in (montar_aula02, montar_aula03, montar_aula04,
                      montar_aula05, montar_aula05_completo, montar_aula06,
                      montar_extra):
        caderno = construir()
        print(f"{caderno.nome}:")
        caderno.gravar()


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    main()
