"""
Exporta um .pptx para PDF pelo PowerPoint, preservando os links.

Por que existe, em vez de um `SaveCopyAs(caminho, 32)` de uma linha: o
SaveCopyAs usa o exportador simples e descarta as anotacoes de link, entao o
"Baixar a tabela inteira em Excel" do slide 4 chegava no PDF como texto
vermelho sublinhado e nada mais. O ExportAsFixedFormat e o caminho que aceita
opcoes e escreve as anotacoes /Link.

Uso:
    python exportar_pdf.py                 # todos os decks da pasta
    python exportar_pdf.py aula03.pptx     # so um
"""

from __future__ import annotations

import glob
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))

# constantes do PowerPoint (msoTrue = -1)
PP_PDF = 2                 # ppFixedFormatTypePDF
PP_INTENT_TELA = 2         # ppFixedFormatIntentScreen
PP_HANDOUT_VERTICAL = 1    # ppPrintHandoutVerticalFirst
PP_SAIDA_SLIDES = 1        # ppPrintOutputSlides
PP_TUDO = 1                # ppPrintAll
MSO_TRUE = -1
MSO_FALSE = 0


def exportar(app, pptx: str) -> str:
    pdf = pptx[:-5] + ".pdf"
    apresentacao = app.Presentations.Open(pptx, WithWindow=False)
    try:
        # posicional: com late binding o COM do PowerPoint nao aceita os
        # argumentos por nome. A ordem e Path, FixedFormatType, Intent,
        # FrameSlides, HandoutOrder, OutputType, PrintHiddenSlides, PrintRange,
        # RangeType, SlideShowName, IncludeDocProperties, KeepIRMSettings,
        # DocStructureTags, BitmapMissingFonts.
        apresentacao.ExportAsFixedFormat(
            pdf, PP_PDF, PP_INTENT_TELA, MSO_FALSE,
            PP_HANDOUT_VERTICAL, PP_SAIDA_SLIDES, MSO_FALSE, None,
            PP_TUDO, "", MSO_TRUE, MSO_TRUE,
            # o que faltava: sem as marcas de estrutura o exportador nao
            # escreve as anotacoes de link
            MSO_TRUE, MSO_TRUE,
        )
    finally:
        apresentacao.Close()
    return pdf


def conferir_links(pdf: str) -> list[str]:
    """Lista os URLs que sobreviveram, para o export nao falhar em silencio."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return []
    achados = []
    for pagina in PdfReader(pdf).pages:
        for anotacao in pagina.get("/Annots") or []:
            acao = anotacao.get_object().get("/A")
            if acao and acao.get("/URI"):
                achados.append(str(acao["/URI"]))
    return achados


def main() -> None:
    import win32com.client as win32

    alvos = sys.argv[1:] or sorted(glob.glob(os.path.join(AQUI, "*.pptx")))
    alvos = [a if os.path.isabs(a) else os.path.join(AQUI, a) for a in alvos]

    app = win32.Dispatch("PowerPoint.Application")
    try:
        for pptx in alvos:
            pdf = exportar(app, pptx)
            urls = {u for u in conferir_links(pdf)
                    if "insper.edu.br" not in u}
            extra = f" · {len(urls)} link(s) externo(s)" if urls else ""
            print(f"{os.path.basename(pdf)}{extra}")
            for u in sorted(urls):
                print(f"    {u}")
    finally:
        app.Quit()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
