// Açık Matematik — Typst book template call for the exported PDFs.
//
// Quarto renders books to Typst with the "orange-book" template. This partial
// replaces the template's own typst-show.typ so that the book is configured
// in Turkish (chapter/part supplements), in the site's accent colour, and
// with the licence on the cover page. Everything else is left to the
// template. The dollar-sign placeholders are filled in by Quarto/Pandoc
// (this file is a Pandoc template partial, so a bare dollar sign is not
// allowed anywhere in it, comments included).
#import "@preview/orange-book:0.7.1": book, part, chapter, appendices

#show: book.with(
$if(title)$
  title: [$title$],
$endif$
$if(subtitle)$
  subtitle: [$subtitle$],
$endif$
$if(by-author)$
  author: "$for(by-author)$$it.name.literal$$sep$, $endfor$",
$endif$
$if(date)$
  date: "$date$",
$endif$
$if(lang)$
  lang: "$lang$",
$endif$
  main-color: rgb("#0D6E6A"),
  supplement-chapter: "Bölüm",
  supplement-part: "Kısım",
  first-line-indent: false,
  copyright: [
    #set text(size: 9pt, fill: luma(90))
    #set par(justify: false)
    Açık Matematik — açık kaynaklı, reklamsız Türkçe matematik notları \
    #link("https://acik-matematik.com")[acik-matematik.com] \
    Bu çalışma #link("https://creativecommons.org/licenses/by-nc-sa/4.0/deed.tr")[Creative Commons BY-NC-SA 4.0]
    lisansıyla paylaşılmıştır: kaynak göstererek ve aynı lisansla, ticari olmayan amaçlarla
    kopyalayabilir, dağıtabilir ve uyarlayabilirsiniz. \
    $if(date)$Bu sürüm: $date$$endif$
  ],
$if(toc-depth)$
  outline-depth: $toc-depth$,
$endif$
$if(lof)$
  list-of-figure-title: "$if(crossref.lof-title)$$crossref.lof-title$$else$$crossref-lof-title$$endif$",
$endif$
$if(lot)$
  list-of-table-title: "$if(crossref.lot-title)$$crossref.lot-title$$else$$crossref-lot-title$$endif$",
$endif$
$if(margin-geometry)$
  padded-heading-number: false,
$endif$
)

$if(margin-geometry)$
#import "@preview/marginalia:0.3.1" as marginalia

#show: marginalia.setup.with(
  inner: (
    far: $margin-geometry.inner.far$,
    width: $margin-geometry.inner.width$,
    sep: $margin-geometry.inner.separation$,
  ),
  outer: (
    far: $margin-geometry.outer.far$,
    width: $margin-geometry.outer.width$,
    sep: $margin-geometry.outer.separation$,
  ),
  top: $if(margin.top)$$margin.top$$else$1.25in$endif$,
  bottom: $if(margin.bottom)$$margin.bottom$$else$1.25in$endif$,
  book: true,
  clearance: $margin-geometry.clearance$,
)
$endif$
