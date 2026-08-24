// Açık Matematik — settings applied to the body of every exported PDF,
// after the book template's own rules (Quarto's include-before-body).

// The book template numbers every display equation "(1.1)"; the notes number
// equations by hand with \tag{…} instead (see scripts/export_math.lua), so
// automatic numbering is switched off here.
#set math.equation(numbering: none)

// Quarto renders the crossref environments Tanım, Teorem, Lemma, Sonuç,
// Önerme, Sanı, Örnek, Alıştırma (and Algoritma) as theorion frames, i.e.
// Typst figures whose kind is the environment name. Proofs, solutions and
// remarks are plain blocks (see collapsible.lua) and need nothing here.
//
// The book template centres every figure, which also centres these text
// blocks, and it adds space after a frame but none before it. Put them
// back on the left margin with a little room above.
#let theorem-kinds = (
  "theorem", "lemma", "corollary", "proposition", "conjecture",
  "definition", "example", "exercise", "algorithm",
)
#show figure: it => {
  if theorem-kinds.contains(it.kind) {
    v(0.9em, weak: true)
    set align(left)
    it
  } else {
    it
  }
}

// Quarto sets the whole body of every environment in italics (the classic
// "plain" theorem style). That is right for theorems, lemmas and
// corollaries, but definitions, examples and exercises read better upright
// — as in LaTeX's "definition" style. The italics come from an emph()
// wrapper around the body; only that outer wrapper is removed, emphasis the
// authors wrote inside the body is kept italic.
#let upright-kinds = ("definition", "example", "exercise", "algorithm")
#show figure: it => {
  if upright-kinds.contains(it.kind) {
    show emph: e => {
      show emph: inner => text(style: "italic", inner.body)
      e.body
    }
    it
  } else {
    it
  }
}
