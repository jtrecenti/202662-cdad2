"""Baixa, com o juscraper, as tres bases usadas no notebook das aulas 2 e 3.

As bases sao gravadas em `202662/dados/` e depois publicadas como assets de uma
release publica do GitHub, para o notebook conseguir le-las por URL sem que o
aluno precise raspar nada (e sem depender do site do tribunal estar de pe).

Decisao importante: as colunas saem em TEXTO, do jeito que o tribunal devolve.
Converter data, dinheiro e categoria e justamente o exercicio da aula 2. Se o
CSV ja viesse tipado, o notebook perderia o assunto.

Uso (com o venv do repo do curso, que tem o juscraper instalado):

    ...\\202662-cdad2\\.venv\\Scripts\\python.exe scripts/baixar_bases_aula02.py
"""

from __future__ import annotations

import argparse
import re
import time
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"

# --- exemplo 1: DataJud ---------------------------------------------------
# codigos TPU de assuntos de saude, colhidos de uma pagina generica do TJSP
ASSUNTOS_SAUDE = [6064, 6233, 7775, 10064, 10356, 12484, 12487, 12489, 14760]
ANOS = (2023, 2024, 2025)
N_DATAJUD = 4000

# --- exemplos 2 e 3: CJSG -------------------------------------------------
CJSG_PLANO = '"plano de saude" E "negativa de cobertura"'
CJSG_DANO = '"dano moral" E "arbitro a indenizacao"'
# base da aula 4: recursos criminais, escolhida porque o regime inicial da uma
# categorica ordinal de verdade e a pena da uma numerica continua
CJSG_CRIMINAL = '"apelacao criminal" E "regime inicial"'
PAGINAS_CJSG = 25  # 20 acordaos por pagina


def limpar(texto) -> str:
    if texto is None or (isinstance(texto, float) and pd.isna(texto)):
        return ""
    texto = unicodedata.normalize("NFC", str(texto))
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def tirar_repeticao(texto: str) -> str:
    """Remove o resumo truncado que o e-SAJ repete antes da ementa completa.

    A pagina do TJSP mostra um trecho cortado e, logo depois, a ementa inteira.
    O scraper pega os dois, entao o comeco do texto reaparece mais adiante.
    """
    if len(texto) < 120:
        return texto
    inicio = texto[:60]
    posicao = texto.find(inicio, 40)
    if posicao > 0 and len(texto) - posicao > 200:
        return texto[posicao:].strip()
    return texto


def com_tentativas(funcao, tentativas: int = 4, espera: int = 8):
    """O e-SAJ derruba conexao com alguma frequencia; insistir resolve."""
    ultimo = None
    for i in range(tentativas):
        try:
            return funcao()
        except Exception as erro:  # noqa: BLE001
            ultimo = erro
            print(f"   tentativa {i + 1} falhou ({type(erro).__name__}), esperando {espera}s")
            time.sleep(espera)
    raise ultimo


# ---------------------------------------------------------------- datajud


def baixar_datajud() -> pd.DataFrame:
    import juscraper as jus

    d = jus.scraper("datajud")
    d.set_verbose(0)

    partes = []
    for ano in ANOS:
        print(f"-- DataJud TJSP, assuntos de saude, ajuizados em {ano}")
        df = com_tentativas(
            lambda ano=ano: d.listar_processos(
                tribunal="TJSP", assuntos=ASSUNTOS_SAUDE, ano_ajuizamento=ano, paginas=1
            )
        )
        print(f"   {len(df)} processos")
        partes.append(df)

    bruto = pd.concat(partes, ignore_index=True)

    def nome(campo):
        return bruto[campo].map(lambda v: (v or {}).get("nome") if isinstance(v, dict) else None)

    def codigo(campo):
        return bruto[campo].map(lambda v: (v or {}).get("codigo") if isinstance(v, dict) else None)

    saude = set(ASSUNTOS_SAUDE) | {str(c) for c in ASSUNTOS_SAUDE}

    def achatar(valor):
        """A API as vezes devolve os assuntos aninhados em outra lista."""
        if isinstance(valor, dict):
            return [valor]
        if isinstance(valor, list):
            return [item for sub in valor for item in achatar(sub)]
        return []

    def data_iso(serie: pd.Series) -> pd.Series:
        """Normaliza a data para AAAA-MM-DD, em texto.

        O DataJud devolve `dataAjuizamento` em dois formatos no mesmo campo:
        ISO ("2023-01-05") e compacto ("20230102161234"). Deixar os dois
        conviverem quebraria o `pd.to_datetime` logo na primeira aula, por um
        motivo que não é o assunto da aula.
        """
        digitos = serie.astype(str).str.replace(r"\D", "", regex=True).str.slice(0, 8)
        return pd.to_datetime(digitos, format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")

    def assunto_de_saude(lista):
        """O processo pode ter varios assuntos; guardamos o que motivou a busca."""
        itens = achatar(lista)
        for a in itens:
            if a.get("codigo") in saude and a.get("nome"):
                return a["nome"]
        return next((a.get("nome") for a in itens if a.get("nome")), None)

    df = pd.DataFrame(
        {
            "numero_processo": bruto["numeroProcesso"],
            "tribunal": bruto["tribunal"],
            "grau": bruto["grau"],
            "classe": nome("classe"),
            "classe_codigo": codigo("classe"),
            "assunto": bruto["assuntos"].map(assunto_de_saude),
            "n_assuntos": bruto["assuntos"].map(lambda x: len(achatar(x))),
            "orgao_julgador": nome("orgaoJulgador"),
            "municipio_ibge": bruto["orgaoJulgador"].map(
                lambda v: (v or {}).get("codigoMunicipioIBGE") if isinstance(v, dict) else None
            ),
            "sistema": nome("sistema"),
            "formato": nome("formato"),
            "nivel_sigilo": bruto["nivelSigilo"],
            # fica em texto de proposito: converter para data e exercicio da aula
            "data_ajuizamento": data_iso(bruto["dataAjuizamento"]),
            "data_ultima_atualizacao": data_iso(bruto["dataHoraUltimaAtualizacao"]),
        }
    )
    df = df.dropna(subset=["numero_processo", "data_ajuizamento"])
    df = df.drop_duplicates(subset=["numero_processo"])
    if len(df) > N_DATAJUD:
        df = df.sample(N_DATAJUD, random_state=20262).reset_index(drop=True)
    return df.sort_values("data_ajuizamento").reset_index(drop=True)


# ------------------------------------------------------------------- cjsg


def baixar_cjsg(pesquisa: str, paginas: int, enriquecer=None) -> pd.DataFrame:
    import juscraper as jus

    s = jus.scraper("tjsp")
    s.set_verbose(0)

    partes = []
    for inicio in range(1, paginas + 1, 5):
        faixa = range(inicio, min(inicio + 5, paginas + 1))
        print(f"-- CJSG {pesquisa!r}, paginas {faixa.start} a {faixa.stop - 1}")
        try:
            partes.append(com_tentativas(lambda f=faixa: s.cjsg(pesquisa, paginas=f)))
        except Exception as erro:  # noqa: BLE001
            print(f"   desistindo dessa faixa: {erro}")
    if not partes:
        raise SystemExit(f"nada baixado para {pesquisa!r}")

    bruto = pd.concat(partes, ignore_index=True)
    df = pd.DataFrame(
        {
            "processo": bruto["processo"].map(limpar),
            "cd_acordao": bruto["cd_acordao"].map(limpar),
            "classe_assunto": bruto["classe_assunto"].map(limpar),
            "relator": bruto["relatora"].map(limpar),
            "comarca": bruto["comarca"].map(limpar),
            "orgao_julgador": bruto["orgao_julgador"].map(limpar),
            "data_julgamento": bruto["data_julgamento"].map(limpar),
            "data_publicacao": bruto["data_publicacao"].map(limpar),
            "ementa": bruto["ementa"].map(lambda t: tirar_repeticao(limpar(t))),
        }
    )
    df = df[df["ementa"].str.len() >= 300]
    df = df.drop_duplicates(subset=["processo"]).reset_index(drop=True)
    return (enriquecer or enriquecer_cjsg)(df)


def enriquecer_cjsg(df: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta as variaveis que sairiam do texto do acordao.

    Extrair isso e trabalho de expressao regular, que so entra na aula 12. Nas
    aulas 2 e 3 o aluno precisa das colunas prontas para poder falar de tipo e
    de estatistica; a decisao de o que extrair, e as limitacoes de cada medida,
    ficam para a discussao em sala.
    """
    df = df.copy()

    bruto = df["ementa"].str.extract(r"R\$\s?([\d\.]+,\d{2})")[0]
    df["valor_indenizacao"] = (
        bruto.str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    df["camara"] = df["orgao_julgador"].str.extract(r"^(\d+)ª Câmara")[0]
    df["secao"] = df["orgao_julgador"].str.extract(r"C[âa]mara.* de (Direito \w+)")[0]
    df[["classe", "assunto"]] = df["classe_assunto"].str.split(" / ", n=1, expand=True)
    df["tem_dano_moral"] = df["ementa"].str.contains("dano moral", case=False, na=False)
    df["houve_majoracao"] = df["ementa"].str.contains("majora", case=False, na=False)
    df["n_palavras_ementa"] = df["ementa"].str.split().str.len()

    ordem = [
        "processo", "cd_acordao", "classe", "assunto", "relator", "comarca",
        "orgao_julgador", "camara", "secao", "data_julgamento", "data_publicacao",
        "valor_indenizacao", "tem_dano_moral", "houve_majoracao",
        "n_palavras_ementa", "ementa",
    ]
    return df[ordem]


def enriquecer_criminal(df: pd.DataFrame) -> pd.DataFrame:
    """Colunas da base de recursos criminais, usada na aula 4."""
    df = df.copy()
    e = df["ementa"]

    regime = e.str.extract(
        r"regime\s+(?:inicial\s+)?(fechado|semiaberto|semi-aberto|aberto)",
        flags=re.IGNORECASE,
    )[0]
    df["regime_inicial"] = regime.str.lower().str.replace("semi-aberto", "semiaberto")

    anos = e.str.extract(r"(\d{1,2})\s+anos?", flags=re.IGNORECASE)[0]
    meses = e.str.extract(r"(\d{1,2})\s+(?:meses|m[eê]s)", flags=re.IGNORECASE)[0]
    df["pena_anos"] = (
        pd.to_numeric(anos, errors="coerce").fillna(0)
        + pd.to_numeric(meses, errors="coerce").fillna(0) / 12
    ).where(anos.notna() | meses.notna())

    df["houve_reincidencia"] = e.str.contains("reincid", case=False, na=False)
    df["houve_confissao"] = e.str.contains("confiss", case=False, na=False)
    df["eh_trafico"] = e.str.contains("tr[áa]fico", case=False, na=False, regex=True)
    df["camara"] = df["orgao_julgador"].str.extract(r"^(\d+)ª Câmara")[0]
    df[["classe", "assunto"]] = df["classe_assunto"].str.split(" / ", n=1, expand=True)
    df["n_palavras_ementa"] = e.str.split().str.len()

    ordem = [
        "processo", "cd_acordao", "classe", "assunto", "relator", "comarca",
        "orgao_julgador", "camara", "data_julgamento", "data_publicacao",
        "regime_inicial", "pena_anos", "houve_reincidencia", "houve_confissao",
        "eh_trafico", "n_palavras_ementa", "ementa",
    ]
    return df[ordem]


def reprocessar() -> None:
    """Reaplica o enriquecimento nos CSVs que ja estao em dados/."""
    for nome in ("tjsp_cjsg_plano_saude.csv", "tjsp_cjsg_dano_moral.csv"):
        caminho = DADOS / nome
        df = pd.read_csv(caminho)
        if "classe_assunto" not in df.columns:
            print(f"** {nome} ja está enriquecido, pulando")
            continue
        gravar(enriquecer_cjsg(df), nome)


def gravar(df: pd.DataFrame, nome: str) -> None:
    DADOS.mkdir(parents=True, exist_ok=True)
    caminho = DADOS / nome
    df.to_csv(caminho, index=False, encoding="utf-8")
    kb = caminho.stat().st_size / 1024
    print(f"** {nome}: {len(df)} linhas, {len(df.columns)} colunas, {kb:.0f} KB")
    print(f"   colunas: {list(df.columns)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--so", choices=["datajud", "plano", "dano", "criminal"],
                    help="baixa uma base so")
    ap.add_argument("--reprocessar", action="store_true",
                    help="so refaz as colunas derivadas dos CSVs que ja estao em dados/")
    args = ap.parse_args()

    if args.reprocessar:
        reprocessar()
        return

    if args.so in (None, "datajud"):
        gravar(baixar_datajud(), "tjsp_datajud_saude.csv")
    if args.so in (None, "plano"):
        gravar(baixar_cjsg(CJSG_PLANO, PAGINAS_CJSG), "tjsp_cjsg_plano_saude.csv")
    if args.so in (None, "dano"):
        gravar(baixar_cjsg(CJSG_DANO, PAGINAS_CJSG), "tjsp_cjsg_dano_moral.csv")
    if args.so in (None, "criminal"):
        gravar(
            baixar_cjsg(CJSG_CRIMINAL, PAGINAS_CJSG, enriquecer=enriquecer_criminal),
            "tjsp_cjsg_criminal.csv",
        )


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    main()
