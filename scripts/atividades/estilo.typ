// ---------------------------------------------------------------------------
// Estilo comum dos materiais impressos das dinamicas
// Ciencia de Dados Aplicada ao Direito II | Insper
//
// Identidade visual conforme o Guia de Marca Insper (abril/2024):
//   - GT Ultra Fine Bold em titulos, nunca em caixa alta
//   - Inter em textos corridos e rotulos
//   - rotulos em caixa alta usam Inter com tracking
//   - grafismos solidos, sem sombra e sem contorno
//
// Compilar com:  quarto typst compile arquivo.typ --font-path ../listas/fontes
// ---------------------------------------------------------------------------

#let brand      = rgb("#E50505")
#let ink        = rgb("#000000")
#let ink-soft   = rgb("#333333")
#let muted      = rgb("#767676")
#let rule-col   = rgb("#C8C8C8")
#let tint       = rgb("#F2F2F2")
#let tint-deep  = rgb("#E4E4E4")

#let turquesa   = rgb("#3ACC9F")
#let amarelo    = rgb("#FFCC00")
#let rosa       = rgb("#F47DCD")

#let title-font = ("GT Ultra Fine", "Georgia", "Times New Roman")
#let body-font  = ("Inter 18pt", "Inter", "Segoe UI", "Verdana")
#let mono-font  = ("Cascadia Mono", "Consolas", "DejaVu Sans Mono")

// Rotulo pequeno em caixa alta
#let eyebrow(corpo, cor: brand, tamanho: 7.5pt) = text(
  font: body-font, size: tamanho, weight: "bold", fill: cor,
  tracking: 1.3pt, upper(corpo),
)

// Cabecalho de folha: rotulo, titulo e regua vermelha
#let folha-titulo(rotulo, titulo, subtitulo: none) = block(width: 100%, below: 10pt, {
  block(above: 0pt, below: 3pt, eyebrow(rotulo))
  block(above: 0pt, below: 4pt,
    text(font: title-font, size: 20pt, weight: "bold", fill: ink, titulo))
  line(length: 100%, stroke: (paint: brand, thickness: 2.2pt))
  if subtitulo != none {
    block(above: 7pt, below: 0pt,
      text(font: body-font, size: 9pt, fill: ink-soft, subtitulo))
  }
})

// Linha "rotulo | valor" de dentro da carta
#let campo(rotulo, valor, destaque: false) = grid(
  columns: (33%, 1fr),
  column-gutter: 3pt,
  align: (left + horizon, left + horizon),
  text(font: body-font, size: 6pt, fill: muted, weight: "medium",
    tracking: 0.5pt, upper(rotulo)),
  text(font: body-font, size: 8.5pt, fill: ink,
    weight: if destaque { "bold" } else { "regular" }, valor),
)

// Uma carta do baralho de acordaos
#let carta-acordao(id, comarca, regime, pena, reincidencia, trafico) = block(
  width: 100%, height: 100%, breakable: false,
  stroke: (paint: rule-col, thickness: 0.6pt, dash: "dashed"),
  inset: 7pt,
  {
    grid(
      columns: (1fr, auto),
      align: (left + bottom, right + bottom),
      text(font: title-font, size: 15pt, weight: "bold", fill: ink, id),
      text(font: body-font, size: 5.5pt, fill: muted, tracking: 1pt, upper("acórdão")),
    )
    v(2pt)
    line(length: 100%, stroke: (paint: brand, thickness: 1.6pt))
    v(6pt)
    campo("comarca", comarca)
    v(3.5pt)
    campo("regime", regime, destaque: true)
    v(3.5pt)
    campo("pena", pena, destaque: true)
    v(3.5pt)
    campo("reincid.", reincidencia)
    v(3.5pt)
    campo("tráfico", trafico)
    v(1fr)
    line(length: 100%, stroke: (paint: rule-col, thickness: 0.5pt, dash: "dotted"))
    v(4pt)
    {
      text(font: body-font, size: 5.5pt, fill: muted, tracking: 0.5pt,
        upper("coluna nova")) + h(4pt)
      box(width: 1fr, line(length: 100%,
        stroke: (paint: rule-col, thickness: 0.5pt)))
    }
  },
)

// Pagina de cartas: grade 3 x 4 ocupando a folha inteira
#let pagina-de-cartas(cartas) = block(width: 100%, height: 100%, {
  grid(
    columns: (1fr, 1fr, 1fr),
    rows: (1fr, 1fr, 1fr, 1fr),
    column-gutter: 4mm,
    row-gutter: 4mm,
    ..cartas,
  )
})

// Tira de operacao, para recortar e posicionar no tabuleiro
#let tira(codigo, cor: ink) = block(
  width: 100%, height: 100%, breakable: false,
  fill: tint,
  stroke: (paint: rule-col, thickness: 0.6pt, dash: "dashed"),
  inset: (x: 9pt, y: 0pt),
  align(horizon, text(font: mono-font, size: 11pt, fill: cor, codigo)),
)

// Espaco em branco onde o grupo encaixa uma tira
#let vaga(numero) = block(
  width: 100%, height: 100%,
  fill: white,
  stroke: (paint: rule-col, thickness: 0.8pt, dash: "dashed"),
  inset: (x: 9pt, y: 0pt),
  align(horizon + left, text(font: body-font, size: 8pt, fill: rule-col,
    "operação " + str(numero))),
)

// Ficha em branco onde o grupo escreve o resumo de uma pilha
#let ficha-resumo(campos) = block(
  width: 100%, height: 100%, breakable: false,
  stroke: (paint: brand, thickness: 1pt),
  inset: 9pt,
  {
    block(above: 0pt, below: 7pt, eyebrow("ficha-resumo", tamanho: 6.5pt))
    grid(
      columns: (1fr,),
      rows: (1fr,) * campos.len(),
      ..campos.map(c => align(horizon, {
        text(font: body-font, size: 8pt, fill: ink-soft, c) + h(5pt)
        box(width: 1fr, line(length: 100%,
          stroke: (paint: rule-col, thickness: 0.5pt)))
      })),
    )
  },
)

// Carta de codigo da dinamica de match
#let carta-codigo(numero, codigo) = block(
  width: 100%, height: 100%, breakable: false,
  stroke: (paint: rule-col, thickness: 0.6pt, dash: "dashed"),
  inset: 9pt,
  {
    block(above: 0pt, below: 0pt, {
      box(fill: ink, inset: (x: 6pt, y: 3pt),
        text(font: body-font, size: 8pt, weight: "bold", fill: white,
          "código " + str(numero)))
    })
    set par(leading: 0.85em)
    align(horizon + left, text(font: mono-font, size: 10pt, fill: ink, codigo))
  },
)

// Carta de grafico da dinamica de match
#let carta-grafico(letra, caminho) = block(
  width: 100%, height: 100%, breakable: false,
  stroke: (paint: rule-col, thickness: 0.6pt, dash: "dashed"),
  inset: 8pt,
  {
    block(above: 0pt, below: 5pt, {
      box(fill: brand, inset: (x: 7pt, y: 3pt),
        text(font: body-font, size: 8pt, weight: "bold", fill: white,
          "gráfico " + letra))
    })
    align(center + horizon, image(caminho, width: 100%))
  },
)

// Bloco de codigo com fundo cinza
#let codigo(corpo, tamanho: 9pt) = block(
  width: 100%, fill: tint, inset: (x: 9pt, y: 8pt), breakable: false,
  text(font: mono-font, size: tamanho, fill: ink-soft, corpo),
)

// Caixa de instrucao numerada
#let passo(numero, titulo, corpo) = block(width: 100%, below: 9pt, breakable: false, {
  grid(
    columns: (16pt, 1fr),
    column-gutter: 8pt,
    text(font: title-font, size: 13pt, weight: "bold", fill: brand, str(numero)),
    {
      block(above: 0pt, below: 2pt,
        text(font: body-font, size: 9.5pt, weight: "bold", fill: ink, titulo))
      text(font: body-font, size: 9pt, fill: ink-soft, corpo)
    },
  )
})

// Pergunta seguida de uma ou mais linhas em branco
#let resposta(pergunta, linhas: 1) = block(width: 100%, below: 15pt, breakable: false, {
  block(above: 0pt, below: 11pt,
    text(font: body-font, size: 9pt, fill: ink, pergunta))
  stack(
    spacing: 11pt,
    ..range(linhas).map(i =>
      line(length: 100%, stroke: (paint: rule-col, thickness: 0.6pt))),
  )
})

// Espaco em branco com moldura, para o grupo escrever livremente
#let quadro(altura) = block(
  width: 100%, height: altura, below: 13pt,
  stroke: (paint: rule-col, thickness: 0.6pt, dash: "dashed"),
)

// Rodape padrao das folhas
#let rodape = context {
  set text(font: body-font, size: 7pt, fill: muted)
  grid(
    columns: (1fr, auto),
    align(left, text(tracking: 1pt,
      upper("Ciência de Dados Aplicada ao Direito II  ·  4A  ·  Aula 5"))),
    align(right, str(counter(page).get().first())),
  )
}
