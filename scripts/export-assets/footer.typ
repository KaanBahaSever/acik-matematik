// Açık Matematik — page footer for exported PDFs (license + site address).
#set page(footer: context {
  if here().page() > 1 {
    set text(size: 8.5pt, fill: luma(110))
    grid(
      columns: (1fr, auto, 1fr),
      align: (left, center, right),
      [Açık Matematik · #link("https://acik-matematik.com")[acik-matematik.com]],
      [#counter(page).display("1")],
      [#link("https://creativecommons.org/licenses/by-nc-sa/4.0/deed.tr")[CC BY-NC-SA 4.0]],
    )
  }
})
