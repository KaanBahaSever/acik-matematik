#!/usr/bin/env python3
"""
Açık Matematik — tüm siteyi derler.

Yapı:
  * Kök proje (type: website)  -> ana sayfa + ders kataloğu  ->  _site/
  * dersler/<ders>/            -> her biri bağımsız Quarto "book" projesi
                                  -> dersler/<ders>/_book/  -> _site/dersler/<ders>/

Her kitap önce kendi _book/ dizinine derlenir, sonra _site altına kopyalanır.
Kitapları doğrudan _site içine yazdırmak Quarto'nun proje dışı dizinleri
temizlemeyi reddetmesine ve eski dosyaların birikmesine yol açıyordu.

Sıralama önemlidir: kök proje derlenirken _site temizlendiği için,
ders kitapları kök projeden SONRA derlenip kopyalanır.

Kullanım:
    python scripts/build.py             # her şeyi derle
    python scripts/build.py kriptografi # yalnızca bir dersi derle
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DERSLER = ROOT / "dersler"
SITE = ROOT / "_site"

# Windows konsolu varsayılan olarak cp1252 kullanıyor; ders adlarındaki
# Türkçe karakterler bu kod sayfasında yazdırılamıyor.
for akis in (sys.stdout, sys.stderr):
    try:
        akis.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def quarto() -> str:
    exe = shutil.which("quarto")
    if not exe:
        sys.exit("HATA: 'quarto' PATH üzerinde bulunamadı. https://quarto.org/docs/get-started/")
    return exe


def render(target: Path, label: str) -> float:
    """Verilen dizindeki Quarto projesini derler, geçen süreyi döndürür."""
    print(f"\n\033[1m>> {label}\033[0m")
    started = time.time()
    result = subprocess.run(
        [quarto(), "render"],
        cwd=target,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = time.time() - started

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(f"HATA: '{label}' derlenemedi (çıkış kodu {result.returncode}).")

    # Quarto uyarıları gözden kaçmasın
    for line in (result.stdout + result.stderr).splitlines():
        if "WARN" in line or "ERROR" in line:
            print(f"   ! {line.strip()}")

    print(f"   tamam ({elapsed:.1f} sn)")
    return elapsed


def books() -> list[Path]:
    """dersler/ altındaki tüm kitap projelerini alfabetik olarak listeler."""
    return sorted(p.parent for p in DERSLER.glob("*/_quarto.yml"))


def paylasilan_varliklar() -> None:
    """styles/ ve assets/ dizinlerini _site altına tazeler.

    Ders kitapları bu dosyalara _site kökünden (../../../styles/global.css
    gibi) bağlanıyor; dosyalar proje dizinlerinin dışında kaldığı için
    Quarto bunları kitap çıktısına kopyalamıyor. Normalde portal derlemesi
    hallediyor; ancak tek ders derlerken portal çalışmadığından stiller
    eski kalıyordu.
    """
    for ad in ("styles", "assets"):
        kaynak = ROOT / ad
        if not kaynak.is_dir():
            continue
        hedef = SITE / ad
        if hedef.exists():
            shutil.rmtree(hedef)
        hedef.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(kaynak, hedef)


def publish(book: Path) -> None:
    """Derlenmiş kitabı dersler/<ders>/_book/ dizininden _site altına taşır."""
    built = book / "_book"
    if not built.is_dir():
        sys.exit(f"HATA: '{book.name}' için _book dizini oluşmadı.")

    hedef = SITE / "dersler" / book.name
    if hedef.exists():
        shutil.rmtree(hedef)
    hedef.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(built, hedef)


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    started = time.time()

    if only:
        target = DERSLER / only
        if not (target / "_quarto.yml").exists():
            sys.exit(f"HATA: '{only}' diye bir ders projesi yok.")
        render(target, f"ders: {only}")
        publish(target)
        paylasilan_varliklar()
    else:
        # 1) Portal sayfaları — bu adım _site dizinini temizler
        render(ROOT, "portal (ana sayfa + ders kataloğu)")

        # 2) Ders kitapları — çıktıları _site/dersler/<ders>/ altına yazılır
        found = books()
        if not found:
            print("   ! dersler/ altında hiç kitap projesi bulunamadı")
        for book in found:
            render(book, f"ders: {book.name}")
            publish(book)

    pages = len(list(SITE.rglob("*.html"))) if SITE.exists() else 0
    print(f"\n\033[1mBitti.\033[0m {pages} HTML sayfa, {time.time() - started:.1f} sn -> {SITE}")


if __name__ == "__main__":
    main()
