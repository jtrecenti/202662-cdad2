// ---------------------------------------------------------------------------
// Template Typst | APS Pesquisa de Campo
// Ciencia de Dados Aplicada ao Direito II | Insper
// Identidade visual conforme o Guia de Marca Insper (abril/2024)
//
// Como editar:
//   - cores e fontes: bloco "Paleta"
//   - componentes visuais: bloco "Componentes"
//   - o conteudo em si fica no arquivo .qmd
//
// Regras de marca respeitadas aqui:
//   - GT Ultra Fine Bold em titulos, nunca em caixa alta
//   - Inter para textos corridos e informacoes menores
//   - rotulos em caixa alta usam Inter Bold com tracking (substituto da
//     Acumin ExtraCondensed Bold, que nao acompanha o kit de marca)
//   - grafismos: retangulos solidos sobrepostos, sem sombra, sem contorno,
//     sem alteracao de opacidade e sem tamanhos muito discrepantes
// ---------------------------------------------------------------------------

// ----------------------------- Paleta --------------------------------------
// Cores principais
#let brand      = rgb("#E50505")   // vermelho Insper
#let ink        = rgb("#000000")   // preto Insper
#let paper-col  = rgb("#FFFFFF")   // branco Insper

// Cores secundarias
#let turquesa   = rgb("#3ACC9F")
#let verde      = rgb("#92D053")
#let amarelo    = rgb("#FFCC00")
#let laranja    = rgb("#F89D49")
#let rosa       = rgb("#F47DCD")
#let roxo       = rgb("#730D9F")

// Neutros de apoio
#let ink-soft   = rgb("#333333")
#let muted      = rgb("#767676")
#let rule-col   = rgb("#DCDCDC")
#let tint       = rgb("#F4F4F4")
#let tint-deep  = rgb("#EAEAEA")

#let title-font = ("GT Ultra Fine", "Georgia", "Times New Roman")
#let body-font  = ("Inter 18pt", "Inter", "Segoe UI", "Verdana")

// ------------------------------ Componentes ---------------------------------

// Grafismo: "janelas" sobrepostas, inspiradas na sobreposicao de papeis
#let janelas(w: 11cm, h: 8cm, a: brand, b: amarelo, c: rosa) = box(
  width: w, height: h, clip: false,
  {
    place(top + left, dx: w * 0.02, dy: h * 0.10,
      rotate(-5deg, rect(width: w * 0.68, height: h * 0.74, fill: c, stroke: none)))
    place(top + left, dx: w * 0.26, dy: h * 0.02,
      rotate(4deg, rect(width: w * 0.66, height: h * 0.76, fill: b, stroke: none)))
    place(top + left, dx: w * 0.14, dy: h * 0.16,
      rotate(-1.5deg, rect(width: w * 0.72, height: h * 0.76, fill: a, stroke: none)))
  },
)

// Rotulo pequeno em caixa alta. `top` controla o espaco antes do rotulo.
#let eyebrow(body, cor: brand, top: 0pt) = block(
  above: top, below: 0.5em,
  text(font: body-font, size: 8pt, weight: "bold", fill: cor, tracking: 1.4pt, upper(body)),
)

// Etiqueta solida (bloco de cor com texto dentro)
#let tag(body, fundo: brand, cor-texto: white) = box(
  fill: fundo,
  inset: (x: 7pt, y: 4pt),
  baseline: 0.28em,
  text(font: body-font, size: 8pt, weight: "bold", fill: cor-texto, tracking: 1.2pt, upper(body)),
)

// Nota discreta
#let note(body) = block(
  above: 0.7em,
  text(font: body-font, size: 8.5pt, fill: muted, body),
)

// Cartao de conteudo. `tone`: "light" (cinza), "dark" (preto), "accent" (barra de cor)
#let card(title: none, tone: "light", accent: brand, height: auto, body) = {
  let fill-col   = if tone == "dark" { ink } else { tint }
  let title-col  = if tone == "dark" { white } else { ink }
  let text-col   = if tone == "dark" { rgb("#D6D6D6") } else { ink-soft }
  block(
    width: 100%,
    breakable: false,
    {
      if tone == "accent" {
        block(above: 0pt, below: 0pt, rect(width: 100%, height: 3pt, fill: accent, stroke: none))
      }
      block(
        width: 100%,
        height: height,
        fill: fill-col,
        inset: (x: 10pt, y: 9pt),
        {
          if title != none {
            block(above: 0pt, below: 5pt,
              text(font: title-font, size: 12pt, weight: "bold", fill: title-col, title))
          }
          set text(font: body-font, size: 9pt, fill: text-col)
          set par(leading: 0.58em, spacing: 0.6em)
          body
        },
      )
    },
  )
}

// Grade de cartoes
#let cards(cols: 3, gutter: 11pt, ..items) = block(
  width: 100%,
  breakable: false,
  grid(
    columns: (1fr,) * cols,
    column-gutter: gutter,
    row-gutter: gutter,
    ..items.pos(),
  ),
)

// Bloco de duas colunas
#let two-cols(left-w: 1fr, right-w: 1fr, gutter: 22pt, left-body, right-body) = block(
  width: 100%,
  breakable: false,
  grid(columns: (left-w, right-w), column-gutter: gutter, left-body, right-body),
)

// Bloco de tres colunas
#let three-cols(gutter: 20pt, a, b, c) = block(
  width: 100%,
  breakable: false,
  grid(columns: (1fr, 1fr, 1fr), column-gutter: gutter, a, b, c),
)

// Faixa de contexto, usada no topo das paginas de tema
#let contexto(titulo: "O problema", body) = block(
  width: 100%,
  breakable: false,
  above: 0pt,
  below: 11pt,
  fill: tint,
  inset: (x: 11pt, y: 8pt),
  {
    block(above: 0pt, below: 3pt,
      text(font: body-font, size: 7.5pt, weight: "bold", fill: brand, tracking: 1.4pt, upper(titulo)))
    set text(font: body-font, size: 8.7pt, fill: ink-soft)
    set par(leading: 0.55em, spacing: 0.6em)
    body
  },
)

// Linha "topico: descricao"
#let topic(name, desc, cor: brand) = block(above: 0pt, below: 6pt, {
  set par(leading: 0.58em)
  text(font: body-font, size: 9.5pt, weight: "bold", fill: ink, name)
  text(font: body-font, size: 9.5pt, fill: cor, [ · ])
  text(font: body-font, size: 9.5pt, fill: ink-soft, desc)
})

// Numero de destaque com legenda
#let stat(value, label, cor: brand) = block({
  block(above: 0pt, below: 1pt,
    text(font: title-font, size: 27pt, weight: "bold", fill: cor, value))
  text(font: body-font, size: 8.5pt, fill: ink-soft, label)
})

// Titulo de pagina padrao
#let page-title(body, size: 24pt) = block(above: 0pt, below: 12pt, width: 100%, {
  block(above: 0pt, below: 6pt,
    text(font: title-font, size: size, weight: "bold", fill: ink, body))
  line(length: 100%, stroke: (paint: brand, thickness: 2.5pt))
})

// Cabecalho de pagina de tema
#let tema-title(
  numero: "",
  titulo: "",
  metodo: "",
  pergunta: "",
  accent: brand,
  accent-text: white,
) = block(above: 0pt, below: 11pt, width: 100%, {
  block(above: 0pt, below: 6pt, {
    tag("Tema " + numero, fundo: accent, cor-texto: accent-text)
    h(9pt)
    text(font: body-font, size: 7.5pt, weight: "bold", fill: muted, tracking: 1.2pt,
      upper("Método: " + metodo))
  })
  block(above: 0pt, below: 8pt,
    text(font: title-font, size: 21pt, weight: "bold", fill: ink, titulo))
  line(length: 100%, stroke: (paint: accent, thickness: 2.5pt))
  v(6pt)
  block(above: 0pt, below: 0pt, {
    text(font: body-font, size: 9.5pt, weight: "bold", fill: ink, "Pergunta. ")
    text(font: body-font, size: 9.5pt, fill: ink-soft, pergunta)
  })
})

// Lista de referencias bibliograficas
#let refs(..items) = block(width: 100%, {
  set par(leading: 0.55em, spacing: 0.5em, hanging-indent: 9pt)
  set text(font: body-font, size: 8pt, fill: ink-soft)
  for it in items.pos() { block(above: 0pt, below: 5pt, it) }
})

// Lista de links de estudo
#let links(..items) = block(width: 100%, {
  set par(leading: 0.55em, spacing: 0.5em, hanging-indent: 9pt)
  set text(font: body-font, size: 8.5pt, fill: ink-soft)
  for it in items.pos() {
    block(above: 0pt, below: 5pt, {
      text(fill: brand, weight: "bold", "→ ")
      it
    })
  }
})

// Capa
#let cover-page(
  kicker: none,
  title: none,
  subtitle: none,
  meta: none,
) = page(
  footer: none,
  margin: (left: 2.4cm, right: 2.4cm, top: 2.0cm, bottom: 1.8cm),
)[
  #place(top + right, dx: 1.4cm, dy: 0.4cm, janelas(w: 13cm, h: 10cm))
  #if kicker != none {
    text(font: body-font, size: 9pt, weight: "bold", fill: ink, tracking: 1.8pt, upper(kicker))
  }
  #v(1fr)
  #block(width: 60%, {
    text(font: title-font, size: 46pt, weight: "bold", fill: ink, title)
    if subtitle != none {
      v(14pt)
      block(width: 88%, text(font: body-font, size: 13pt, weight: "medium", fill: ink-soft, subtitle))
    }
  })
  #v(20pt)
  #block(width: 46%, line(length: 100%, stroke: (paint: brand, thickness: 3pt)))
  #v(1fr)
  #if meta != none {
    text(font: body-font, size: 9.5pt, weight: "medium", fill: ink-soft, meta)
  }
]

// ------------------------------ Documento -----------------------------------
#let article(
  title: none,
  subtitle: none,
  margin: (left: 2.2cm, right: 2.2cm, top: 1.7cm, bottom: 1.4cm),
  paper: "presentation-16-9",
  font: body-font,
  fontsize: 11pt,
  doc,
) = {
  set page(
    paper: paper,
    margin: margin,
    fill: paper-col,
    footer: context {
      set text(font: body-font, size: 7.5pt, fill: muted)
      grid(
        columns: (1fr, auto),
        align(left, text(tracking: 1.1pt,
          upper("Ciência de Dados Aplicada ao Direito II  ·  4A  ·  2026/62"))),
        align(right, str(counter(page).get().first())),
      )
    },
    footer-descent: 0.6cm,
  )

  set text(font: font, size: fontsize, fill: ink, lang: "pt", region: "BR")
  set par(justify: false, leading: 0.64em, spacing: 0.85em)

  // Nova pagina a cada titulo de nivel 1
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    page-title(it.body)
  }

  // Rotulo vermelho dentro da pagina
  show heading.where(level: 2): it => block(above: 14pt, below: 6pt,
    text(font: body-font, size: 8.5pt, weight: "bold", fill: brand, tracking: 1.5pt, upper(it.body)))

  show heading.where(level: 3): it => block(above: 10pt, below: 4pt,
    text(font: title-font, size: 12pt, weight: "bold", fill: ink, it.body))

  // Listas
  set list(
    marker: (text(fill: brand, "\u{25AA}"), text(fill: muted, "\u{2013}")),
    indent: 2pt, body-indent: 7pt, spacing: 0.55em,
  )
  set enum(indent: 2pt, body-indent: 7pt, spacing: 0.55em)

  // Tabelas
  set table(
    stroke: none,
    inset: (x: 9pt, y: 6.5pt),
    fill: (x, y) => if y == 0 { ink } else if calc.odd(y) { tint } else { white },
  )
  show table.cell.where(y: 0): set text(fill: white, weight: "bold", size: 9pt)
  show table: set text(font: body-font, size: 8.5pt, fill: ink-soft)
  show table: set par(leading: 0.52em)

  show figure: it => block(width: 100%, breakable: false, it.body)

  show link: it => text(fill: brand, it)

  doc
}
