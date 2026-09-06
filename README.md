# Ciência de Dados Aplicada ao Direito II

Materiais da disciplina no Insper, graduação em Direito, turma 4A, semestre
2026/2. Aqui ficam os slides, os notebooks das aulas, as bases usadas em sala e
o documento da pesquisa de campo.

Os notebooks abrem direto no Google Colab, sem instalar nada.

## Aulas

| aula | tema | slides | notebook |
|---|---|---|---|
| 1 | Sobre a disciplina | [PDF](slides/aula01-sobre-a-disciplina.pdf) | |
| 2 | Tipos de variáveis | [PDF](slides/aula02-tipos-de-variaveis.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula02_tipos_de_variaveis.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula02_tipos_de_variaveis.ipynb) |
| 3 | Filtrar e resumir | [PDF](slides/aula03-filtrar-e-resumir.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula03_filtrar_e_resumir.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula03_filtrar_e_resumir.ipynb) |
| 4 | Encadear operações | [PDF](slides/aula04-encadear-operacoes.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula04_encadear_operacoes.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula04_encadear_operacoes.ipynb) |
| 5 | Gramática de gráficos | [PDF](slides/aula05-gramatica-de-graficos.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula05_gramatica_de_graficos.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula05_gramatica_de_graficos.ipynb) |
| 6 | Gráficos de duas variáveis | [PDF](slides/aula06-duas-variaveis.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula06_duas_variaveis.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula06_duas_variaveis.ipynb) |
| 7 | Probabilidade e incerteza | [web](https://jtrecenti.github.io/cdad2-202662/slides/aula07.html) · [PDF](https://jtrecenti.github.io/cdad2-202662/slides/aula07.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula07_probabilidade.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula07_probabilidade.ipynb) |
| 8 | Condicional, Bayes e distribuições | [web](https://jtrecenti.github.io/cdad2-202662/slides/aula08.html) · [PDF](https://jtrecenti.github.io/cdad2-202662/slides/aula08.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula08_condicional_bayes.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula08_condicional_bayes.ipynb) |
| 9 | Variáveis aleatórias | [web](https://jtrecenti.github.io/cdad2-202662/slides/aula09.html) · [PDF](https://jtrecenti.github.io/cdad2-202662/slides/aula09.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula09_variaveis_aleatorias.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula09_variaveis_aleatorias.ipynb) |
| 10 | Um catálogo de distribuições | [web](https://jtrecenti.github.io/cdad2-202662/slides/aula10.html) · [PDF](https://jtrecenti.github.io/cdad2-202662/slides/aula10.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula10_distribuicoes.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula10_distribuicoes.ipynb) |
| 11 | Inferência estatística | [web](https://jtrecenti.github.io/cdad2-202662/slides/aula11.html) · [PDF](https://jtrecenti.github.io/cdad2-202662/slides/aula11.pdf) | [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/aula11_inferencia.ipynb) · [baixar](https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/notebooks/aula11_inferencia.ipynb) |

Material extra, completo, para estudar filtros e comparação de proporções com
mais calma: [Colab](https://colab.research.google.com/github/jtrecenti/202662-cdad2/blob/main/notebooks/extra_filtros.ipynb).

Das aulas 7 em diante os slides são páginas web, com quiz, gráficos
interativos e tema claro ou escuro na tecla `d`. O PDF é a mesma coisa
congelada, para imprimir ou anotar.

Os notebooks das aulas vêm com lacunas (`________`), que são preenchidas em
sala. As versões resolvidas são distribuídas pelo BlackBoard depois de cada
aula.

## Pesquisa de campo

O enunciado completo da atividade em grupo, com os sete temas, os métodos, as
regras e as rubricas de avaliação:
[pesquisa-campo.pdf](pesquisa-de-campo/pesquisa-campo.pdf).

A pasta traz também o fonte em Quarto e o template Typst usados para gerar o
documento.

## Bases de dados

Quatro bases de decisões do TJSP, coletadas com o
[juscraper](https://github.com/jtrecenti/juscraper) a partir de fontes públicas.
As colunas vêm em texto, do jeito que o tribunal devolve: converter data,
dinheiro e categoria faz parte do exercício.

| arquivo | o que é | linhas |
|---|---|---|
| [`tjsp_datajud_saude.csv`](dados/tjsp_datajud_saude.csv) | processos com assunto de saúde ajuizados no TJSP entre 2023 e 2025, pela API pública do DataJud (CNJ) | 4000 |
| [`tjsp_cjsg_plano_saude.csv`](dados/tjsp_cjsg_plano_saude.csv) | acórdãos sobre negativa de cobertura de plano de saúde | 488 |
| [`tjsp_cjsg_dano_moral.csv`](dados/tjsp_cjsg_dano_moral.csv) | acórdãos que arbitram indenização por dano moral | 460 |
| [`tjsp_cjsg_criminal.csv`](dados/tjsp_cjsg_criminal.csv) | apelações criminais com regime inicial fixado | 475 |

Nas três bases do segundo grau, algumas colunas foram lidas do texto da ementa
antes da publicação (`valor_indenizacao`, `regime_inicial`, `pena_anos`,
`camara`, `secao` e os indicadores `tem_dano_moral`, `houve_majoracao`,
`houve_reincidencia`, `houve_confissao`, `eh_trafico`). São medidas grosseiras,
feitas por expressão regular, e cada notebook discute o que elas conseguem e o
que não conseguem sustentar.

Para ler direto no pandas:

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/jtrecenti/202662-cdad2/main/dados"
saude = pd.read_csv(f"{URL}/tjsp_datajud_saude.csv")
```

## Como os materiais são gerados

A pasta `scripts/` traz o código que produz tudo o que está aqui:

- `scripts/baixar_bases.py` coleta as bases com o juscraper;
- `scripts/gerar_notebooks.py` gera, de uma fonte só, a versão do aluno e a do
  professor de cada notebook;
- `scripts/slides/` monta os slides em cima do template institucional do Insper.

Os scripts de slides dependem do template e das fontes da marca, que são
licenciados e por isso não estão neste repositório. As bases e os notebooks se
reproduzem sem nada disso.

## Licença e uso

Os dados vêm de decisões públicas do TJSP e são redistribuídos aqui apenas para
uso didático. O material da disciplina pode ser usado e adaptado citando a
fonte.
