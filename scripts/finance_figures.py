# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Finans Matematiği" chapters.

The figures are NOT produced at build time: run this script, then
scripts/center_figures.py "finance-*.md" (which measures each drawing and
centers it in its viewBox), and paste the resulting markup into the .qmd
files — inside the theorem/example/proof box the figure explains, never
inside a definition box. Building the books therefore needs neither Python
nor Jupyter; CI runs Quarto alone.

Nearly every drawing here is a cash-flow timeline, so the module builds one
on top of `tline` (the axis) and `flow` (an arc carrying money from one date
to another). Layout convention, kept the same in every timeline:

    amounts        above the axis      (dy = -11)
    dates/periods  below the axis      (row 1 at +16, row 2 at +29)
    arcs above     gap = 22            (clears the amount row)
    arcs below     gap = 30 / 40       (clears one / two label rows)

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/finance_figures.py && python scripts/center_figures.py "finance-*.md"
Output:  scripts/_figures/finance-<name>.md
"""
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from svg_plot import *  # noqa: E402,F403 — Plot, figure, colors, WIDE, sup, fmt, ...

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}

MINUS_S = "&#8722;"
ARROW_R = "&#8594;"
INFTY_S = "&#8734;"
ELLIP = "&#8230;"
LEQ_S = "&#8804;"
APPROX_S = "&#8776;"
GEQ_S = "&#8805;"


def subs(s, size=9):
    """Subscript inside an SVG <text>: 'a' + subs('n')."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=9):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def tl(v, dec=2):
    """Turkish money formatting: 1234.5 -> '1.234,50'."""
    s = f"{v:,.{dec}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


# ---------------------------------------------------------------------------
# Timeline primitives
# ---------------------------------------------------------------------------
def tline(p, y=0.0, ticks=(), labels=None, sub=None, opacity=0.6, size=10.5,
          sub_size=9.5, arrow=True, tick_h=5.0, lab_dy=16.0, sub_dy=29.0):
    """The time axis: a horizontal line with tick marks, a label row and an
    optional second (date) row underneath."""
    Y = p.Y(y)
    x0, x1 = p.X(p.xmin), p.X(p.xmax)
    p.add(f'<line x1="{x0:.1f}" y1="{Y:.1f}" x2="{x1 - (7 if arrow else 0):.1f}" y2="{Y:.1f}" '
          f'stroke="{TEXT}" stroke-width="1.3" opacity="{opacity}" stroke-linecap="round"/>')
    if arrow:
        p.add(f'<polygon points="{x1:.1f},{Y:.1f} {x1 - 7:.1f},{Y - 3:.1f} {x1 - 7:.1f},{Y + 3:.1f}" '
              f'fill="{TEXT}" opacity="{opacity}"/>')
    for i, t in enumerate(ticks):
        X = p.X(t)
        p.add(f'<line x1="{X:.1f}" y1="{Y - tick_h:.1f}" x2="{X:.1f}" y2="{Y + tick_h:.1f}" '
              f'stroke="{TEXT}" stroke-width="1.2" opacity="{opacity}"/>')
        if labels is not None and i < len(labels) and labels[i]:
            p.text_px(X, Y + lab_dy, labels[i], TEXT, size, "middle")
        if sub is not None and i < len(sub) and sub[i]:
            p.text_px(X, Y + sub_dy, sub[i], TEXT, sub_size, "middle")


def flow(p, xa, xb, label="", color=THEORY, y=0.0, rise=34.0, above=True,
         size=10.0, dash=None, gap=22.0, lab_dy=-6.0, width=1.5, head=7.5,
         lab_dx=0.0, anchor="middle", lab_t=0.5):
    """A quadratic arc that carries an amount from date xa to date xb.

    `rise` is the height of the apex above (or below) the axis in pixels and
    `gap` how far from the axis the arc starts; the label sits at parameter
    `lab_t` along the arc (0.5 = apex). Arcs that converge on a common date
    are separated by giving them different rises and pulling their labels
    back towards their own starting point (lab_t < 0.5).
    """
    sgn = -1.0 if above else 1.0
    x0, y0 = p.X(xa), p.Y(y) + sgn * gap
    x1, y1 = p.X(xb), p.Y(y) + sgn * gap
    apex_y = (y0 + y1) / 2 + sgn * rise
    cx, cy = (x0 + x1) / 2, 2 * apex_y - (y0 + y1) / 2
    da = f' stroke-dasharray="{dash}"' if dash else ""
    tx, ty = x1 - cx, y1 - cy
    tlen = math.hypot(tx, ty) or 1.0
    ux, uy = tx / tlen, ty / tlen
    ex, ey = x1 - ux * head * 0.75, y1 - uy * head * 0.75
    p.add(f'<path d="M{x0:.1f},{y0:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" fill="none" '
          f'stroke="{color}" stroke-width="{width}"{da} stroke-linecap="round"/>')
    px, py = -uy, ux
    hw = head * 0.44
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * head + px * hw:.1f},{y1 - uy * head + py * hw:.1f} '
          f'{x1 - ux * head - px * hw:.1f},{y1 - uy * head - py * hw:.1f}" fill="{color}"/>')
    if label:
        t = lab_t
        bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
        by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
        p.text_px(bx + lab_dx, by + lab_dy, label, color, size, anchor)


def amount(p, x, text, y=0.0, dy=-11.0, color=TEXT, size=10.5, bold=True, anchor="middle", dx=0.0):
    """A cash amount written just above (dy < 0) or below the axis at date x."""
    p.text_px(p.X(x) + dx, p.Y(y) + dy, text, color, size, anchor, bold)


def marker(p, x, text="", y=0.0, color=PRACTICE, r=4.2, dy=-26.0, size=10.0, bold=True):
    """A filled dot on the axis — used for the focal date."""
    p.points([(x, y)], color, r)
    if text:
        p.text_px(p.X(x), p.Y(y) + dy, text, color, size, "middle", bold)


def span(p, xa, xb, text, y=0.0, dy=-46.0, color=TEXT, size=10.0, opacity=0.75, tick=5.0, lab_dy=-6.0):
    """A ⟷ measure line with a caption — 't yıl', 'n dönem', '320 gün' …"""
    Y = p.Y(y) + dy
    x0, x1 = p.X(xa), p.X(xb)
    p.add(f'<line x1="{x0:.1f}" y1="{Y:.1f}" x2="{x1:.1f}" y2="{Y:.1f}" stroke="{color}" '
          f'stroke-width="1" opacity="{opacity}"/>')
    for X, s in ((x0, 1), (x1, -1)):
        p.add(f'<polygon points="{X:.1f},{Y:.1f} {X + s * 6:.1f},{Y - 3:.1f} {X + s * 6:.1f},{Y + 3:.1f}" '
              f'fill="{color}" opacity="{opacity}"/>')
        p.add(f'<line x1="{X:.1f}" y1="{Y - tick:.1f}" x2="{X:.1f}" y2="{Y + tick:.1f}" '
              f'stroke="{color}" stroke-width="0.9" opacity="{opacity}"/>')
    p.text_px((x0 + x1) / 2, Y + lab_dy, text, color, size, "middle")


def drop(p, x, text, y=0.0, depth=30.0, color=PRACTICE, size=10.5, bold=True, dash=None,
         up=False, start=6.0):
    """A short vertical pointer under (or over) the axis: the '↓ S' of the source figures.

    `start` is where the shaft begins, so a downward pointer can start below
    the date rows instead of striking through them.
    """
    sgn = -1.0 if up else 1.0
    X, Y = p.X(x), p.Y(y)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{X:.1f}" y1="{Y + sgn * start:.1f}" x2="{X:.1f}" y2="{Y + sgn * (depth - 7):.1f}" '
          f'stroke="{color}" stroke-width="1.2"{da}/>')
    p.add(f'<polygon points="{X:.1f},{Y + sgn * depth:.1f} {X - 3.2:.1f},{Y + sgn * (depth - 7):.1f} '
          f'{X + 3.2:.1f},{Y + sgn * (depth - 7):.1f}" fill="{color}"/>')
    p.text_px(X, Y + sgn * (depth + 12) if not up else Y - depth - 5, text, color, size, "middle", bold)


def tick_bar(p, x, y=0.0, color=THEORY, h=9.0, width=1.6):
    """A taller, colored tick — marks a payment date on the axis."""
    X, Y = p.X(x), p.Y(y)
    p.add(f'<line x1="{X:.1f}" y1="{Y - h:.1f}" x2="{X:.1f}" y2="{Y + h:.1f}" '
          f'stroke="{color}" stroke-width="{width}"/>')


def bracket(p, xs, xend, text="", y=0.0, dy=30.0, color=THEORY, size=10.0, drop_h=8.0, lab_dy=-6.0):
    """Collect the payments at `xs` on a horizontal bar and carry them to `xend`."""
    Y = p.Y(y) - dy
    x0, x1 = p.X(min(xs + [xend])), p.X(max(xs + [xend]))
    p.add(f'<line x1="{x0:.1f}" y1="{Y:.1f}" x2="{x1:.1f}" y2="{Y:.1f}" stroke="{color}" stroke-width="1.2"/>')
    for x in xs:
        p.add(f'<line x1="{p.X(x):.1f}" y1="{Y:.1f}" x2="{p.X(x):.1f}" y2="{Y + drop_h:.1f}" '
              f'stroke="{color}" stroke-width="1.2"/>')
    p.add(f'<circle cx="{p.X(xend):.1f}" cy="{Y:.1f}" r="3.4" fill="{color}"/>')
    if text:
        p.text_px((x0 + x1) / 2, Y + lab_dy, text, color, size, "middle")


def tl_panel(x0, y0, w, h, xmin, xmax):
    """A panel whose data x is time and whose y is free vertical space (−1 … 1)."""
    return Plot(x0, y0, w, h, (xmin, xmax), (-1.0, 1.0))


def note(p, px, py, text, color=TEXT, size=10.0, anchor="start", bold=False, italic=False):
    p.text_px(px, py, text, color, size, anchor, bold, italic)


def bars(p, items, ymin, color=THEORY, half=0.36, fill=0.18, lab_size=9.5,
         lab_color=None, lab_dy=-7.0, xlab_dy=15.0):
    """Vertical bars: items = [(x, value, top_label, bottom_label), …]."""
    for x, v, top, bot in items:
        X0, X1 = p.X(x - half), p.X(x + half)
        p.add(f'<rect x="{X0:.1f}" y="{p.Y(v):.1f}" width="{X1 - X0:.1f}" height="{p.Y(ymin) - p.Y(v):.1f}" '
              f'fill="{color}" fill-opacity="{fill}" stroke="{color}" stroke-width="1.3" rx="2"/>')
        if top:
            p.text_px(p.X(x), p.Y(v) + lab_dy, top, lab_color or color, lab_size, "middle", True)
        if bot:
            p.text_px(p.X(x), p.Y(ymin) + xlab_dy, bot, TEXT, lab_size, "middle")


# ############################################################################
# PART 1 — Basit faiz (bölüm 1–5)
# ############################################################################

# --- Genel zaman şeması -----------------------------------------------------
p = tl_panel(30, 60, 400, 90, -0.15, 2.15)
tline(p, 0, [0, 1, 2], ["Geçmişteki zaman", "Şimdiki zaman", "Gelecekteki zaman"], size=10.5, lab_dy=-11)
span(p, 0, 1, "t yıl", dy=-52)
span(p, 1, 2, "t yıl", dy=-52)
amount(p, 1, "P", dy=-28, color=PRACTICE, size=13)
flow(p, 1, 0, "P(1 + rt)" + sups(MINUS_S + "1"), THEORY, rise=28, above=False, gap=12, lab_dy=17, size=11)
flow(p, 1, 2, "P(1 + rt)", BASE, rise=28, above=False, gap=12, lab_dy=17, size=11)
OUT["zaman-semasi"] = figure(
    460, 190, [p],
    "Basit faizde paranın zaman değeri: bugünkü <em>P</em> tutarı <em>t</em> yıl ileri taşınırken "
    "birikme çarpanı 1 + <em>rt</em> ile çarpılır, geriye taşınırken iskonto çarpanı "
    "(1 + <em>rt</em>)<sup>&#8722;1</sup> ile çarpılır. Zaman ekseninde sağa gitmek "
    "&#8220;çarp&#8221;, sola gitmek &#8220;böl&#8221; demektir.",
    aria="Basit faizde gecmis, simdi ve gelecek arasinda para tasima semasi")

# --- Örnek 1.4 --------------------------------------------------------------
p = tl_panel(30, 50, 340, 70, -0.15, 1.15)
tline(p, 0, [0, 1], ["bugün", "9 ay sonra"])
amount(p, 0, "P = ?", color=PRACTICE, size=11.5)
amount(p, 1, "S = 1500 TL", color=BASE, size=11.5)
flow(p, 1, 0, "9 ay geri,  r = 0,06", THEORY, rise=28, above=False, gap=30, lab_dy=16)
OUT["ornek-14-simdiki-deger"] = figure(
    400, 160, [p],
    "9 ay sonra eline 1500 TL geçecek bir birikimin bugünkü değeri aranıyor: ok geriye doğru "
    "olduğu için 1500 TL, (1 + 0,06 &#183; 9/12)<sup>&#8722;1</sup> iskonto çarpanıyla çarpılır.",
    aria="9 ay sonraki 1500 TL nin bugunku degeri")


# --- Örnek 1.5: iki odak noktası --------------------------------------------
def odak_panel(focus):
    q = tl_panel(34, 96, 420, 96, -0.4, 10.6)
    tline(q, 0, [0, 3, 5, 6, 10], ["0", "3", "5", "6", "10"])
    q.text_px(q.X(10.5), q.Y(0) + 16, "ay", TEXT, 10, "start")
    amount(q, 5, "2000", color=THEORY)
    amount(q, 10, "3000", color=THEORY)
    amount(q, 3, "X", color=BASE, size=12, dx=-15, anchor="end")
    amount(q, 6, "2X", color=BASE, size=12, dx=15, anchor="start")
    if focus == 3:
        flow(q, 5, 3, "2 ay geri", THEORY, rise=32, lab_t=0.6)
        flow(q, 10, 3, "7 ay geri", THEORY, rise=62)
        flow(q, 6, 3, "3 ay geri", BASE, rise=30, above=False, gap=30, lab_dy=16)
        marker(q, 3, "ODAK", dy=-88, color=PRACTICE)
    else:
        flow(q, 5, 6, "1 ay ileri", THEORY, rise=30)
        flow(q, 10, 6, "4 ay geri", THEORY, rise=58)
        flow(q, 3, 6, "3 ay ileri", BASE, rise=30, above=False, gap=30, lab_dy=16)
        marker(q, 6, "ODAK", dy=-84, color=PRACTICE)
    return q


OUT["ornek-15-odak3"] = figure(
    490, 210, [odak_panel(3)],
    "Birinci seçenek (2000 ve 3000 TL) ile ikinci seçenek (<em>X</em> ve 2<em>X</em>) 3. aya taşınıp "
    "eşitlenirse <em>X</em> = 1619,62 TL bulunur. Basit faizde her ödeme, odak noktasına olan "
    "<strong>kendi</strong> süresiyle taşınır.",
    aria="Ornek 1.5: odak noktasi 3. ay alinarak denk odemeler")
OUT["ornek-15-odak6"] = figure(
    490, 210, [odak_panel(6)],
    "Aynı iki seçenek bu kez 6. aya taşınıyor: 5. aydaki 2000 TL bir ay ileri, 10. aydaki 3000 TL "
    "dört ay geri gidiyor. Sonuç <em>X</em> = 1618,69 TL &#8212; basit faizde odak noktası "
    "değişince cevap da değişir.",
    aria="Ornek 1.5: odak noktasi 6. ay alinarak denk odemeler")

# --- Örnek 1.6a: Tüccar Kuralı ----------------------------------------------
XS = [0, 1.55, 3.05, 3.75, 4.6]
DATES = ["15.1.2011", "12.4.2011", "10.8.2011", "3.10.2011", "1.12.2011"]
p = tl_panel(34, 128, 450, 100, -0.55, 5.3)
tline(p, 0, XS, DATES, size=9.5)
amount(p, 0, "1000", color=THEORY)
amount(p, 1.55, "350", color=BASE)
amount(p, 3.05, "20", color=BASE)
amount(p, 3.75, "400", color=BASE)
amount(p, 4.6, "X = ?", color=PRACTICE)
flow(p, 0, 4.6, "320 gün", THEORY, rise=104, lab_t=0.42)
flow(p, 1.55, 4.6, "233 gün", BASE, rise=76, lab_t=0.36)
flow(p, 3.05, 4.6, "113 gün", BASE, rise=50, lab_t=0.30)
flow(p, 3.75, 4.6, "59 gün", BASE, rise=26, lab_t=0.28)
marker(p, 4.6, "", color=PRACTICE)
OUT["ornek-16-tuccar"] = figure(
    530, 250, [p],
    "Tüccar Kuralı: <strong>bütün</strong> tutarlar &#8212; ana borç da taksitler de &#8212; borcun "
    "bitiş tarihine taşınır ve orada eşitlenir. Ödeme yapılmayan aralarda faiz işlemeye devam eder.",
    aria="Ornek 1.6 Tuccar Kurali: tum odemeler bitis tarihine tasiniyor")

# --- Örnek 1.6b: Amerikan Kuralı --------------------------------------------
p = tl_panel(34, 96, 450, 104, -0.55, 5.3)
tline(p, 0, XS, DATES, size=9.5)
amount(p, 0, "1000", color=THEORY)
amount(p, 1.55, "350", color=BASE)
amount(p, 3.05, "20", color=REMARK)
amount(p, 3.75, "400", color=BASE)
amount(p, 4.6, "X = ?", color=PRACTICE)
flow(p, 0, 1.55, "87 gün", THEORY, rise=30, above=False, gap=30, lab_dy=16)
flow(p, 1.55, 3.75, "174 gün", THEORY, rise=52, above=False, gap=30, lab_dy=16)
flow(p, 3.75, 4.6, "59 gün", THEORY, rise=26, above=False, gap=30, lab_dy=16)
p.add(f'<circle cx="{p.X(3.05):.1f}" cy="{p.Y(0) - 15:.1f}" r="13" fill="none" stroke="{REMARK}" '
      f'stroke-width="1.3" stroke-dasharray="3 3"/>')
note(p, p.X(3.05), p.Y(0) - 52, "faiz 36,73 &gt; taksit 20", REMARK, 9.5, "middle")
note(p, p.X(3.05), p.Y(0) - 40, "&#8594; bu taksit ödenmez", REMARK, 9.5, "middle")
OUT["ornek-16-amerikan"] = figure(
    530, 230, [p],
    "Amerikan Kuralı: borç taksitten taksite taşınır. 10.8.2011 taksidi (20 TL), o güne kadar "
    "işlemiş 36,73 TL faizi karşılamadığı için ödenmez; 3.10.2011&#8217;de 400 + 20 = 420 TL "
    "birlikte ödenir.",
    aria="Ornek 1.6 Amerikan Kurali: borc taksitten taksite tasiniyor")

# --- Faiz mi iskonto mu (Örnek 1.7) -----------------------------------------
p = Plot(64, 44, 320, 150, (0, 2.2), (0, 1180))
p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(0):.1f}" x2="{p.X(2.2):.1f}" y2="{p.Y(0):.1f}" '
      f'stroke="{TEXT}" stroke-width="1.1" opacity="0.45"/>')
p.add(f'<line x1="{p.X(0.05):.1f}" y1="{p.Y(1000):.1f}" x2="{p.X(2.15):.1f}" y2="{p.Y(1000):.1f}" '
      f'stroke="{REMARK}" stroke-width="1.3" stroke-dasharray="5 4"/>')
p.text_px(p.X(1.1), p.Y(1000) - 8, "1 yıl sonra ödenecek S = 1000 TL", REMARK, 10.5, "middle")
for cx, val, col, lab in ((0.6, 888.89, THEORY, "r = %12,5 faiz ile"), (1.6, 875.00, PRACTICE, "d = %12,5 iskonto ile")):
    X0, X1 = p.X(cx - 0.32), p.X(cx + 0.32)
    p.add(f'<rect x="{X0:.1f}" y="{p.Y(val):.1f}" width="{X1 - X0:.1f}" height="{p.Y(0) - p.Y(val):.1f}" '
          f'fill="{col}" fill-opacity="0.18" stroke="{col}" stroke-width="1.4" rx="2"/>')
    p.text_px(p.X(cx), p.Y(val) + 18, tl(val) + " TL", col, 11.5, "middle", True)
    p.text_px(p.X(cx), p.Y(0) + 16, lab, col, 10.5, "middle")
p.text_px(p.X(1.1), p.Y(0) + 34, "Bugün eline geçen para (P)", TEXT, 10.5, "middle")
OUT["faiz-vs-iskonto"] = figure(
    450, 230, [p],
    "Aynı yüzde, iki farklı sonuç: faiz oranı bugünkü değer <em>P</em> üzerinden, iskonto oranı ise "
    "gelecekteki değer <em>S</em> üzerinden işler. Bu yüzden %12,5 iskonto, %12,5 faizden daha "
    "pahalıdır &#8212; borçlunun eline daha az para geçer.",
    aria="Ayni yuzdeden faiz ve iskonto ile bulunan simdiki degerlerin karsilastirmasi")

# --- Örnek 1.10: senet kırdırma ---------------------------------------------
p = tl_panel(34, 100, 420, 100, -0.45, 4.3)
tline(p, 0, [0, 2.2, 3.9], ["11.5.2012", "2.7.2012", "9.8.2012"],
      sub=["senet imzalandı", "bankaya satıldı", "vade"], size=10)
amount(p, 0, "1500", color=THEORY)
amount(p, 2.2, "P&#8322; = ?", color=PRACTICE)
amount(p, 3.9, "1530", color=BASE)
flow(p, 0, 3.9, "90 gün,  r = 0,08  (faiz)", THEORY, rise=66)
flow(p, 3.9, 2.2, "38 gün,  d = 0,09  (iskonto)", BASE, rise=30)
flow(p, 0, 2.2, "52 gün: Orhan Bey'in parasının bağlı kaldığı süre", REMARK,
     rise=30, above=False, gap=42, lab_dy=16, dash="4 3")
OUT["ornek-110-senet"] = figure(
    510, 250, [p],
    "Senedin vade değeri <strong>faiz</strong> ile ileri taşınarak (1530 TL), bankanın ödediği tutar "
    "ise vade değerinden <strong>iskonto</strong> ile geri gelinerek (1515,47 TL) bulunur. Alttaki "
    "52 gün, Orhan Bey&#8217;in getirisinin hangi süreye bölüneceğini gösterir.",
    aria="Senedin vade degeri ve iskonto edilerek bankaya satilmasi")

# ############################################################################
# PART 2 — Bileşik faiz (bölüm 6–8)
# ############################################################################

# --- Basit faiz - bileşik faiz karşılaştırması ------------------------------
p = Plot(60, 34, 330, 150, (0, 20), (0, 6000))
p.axes(range(0, 21, 4), range(0, 6001, 1000), "yıl", "TL")
p.grid(range(0, 21, 4), range(0, 6001, 1000))
p.line([(t, 1000 * (1 + 0.09 * t)) for t in range(0, 21)], BASE, 2.0)
p.line([(t, 1000 * 1.09 ** t) for t in range(0, 21)], THEORY, 2.2)
p.points([(20, 1000 * 1.09 ** 20)], THEORY, 4.0)
p.points([(20, 1000 * (1 + 0.09 * 20))], BASE, 4.0)
p.label(20, 1000 * 1.09 ** 20, "bileşik faiz: 5604,41", -8, -8, THEORY, 10.5, "end", True)
p.label(20, 1000 * (1 + 0.09 * 20), "basit faiz: 2800,00", -8, 15, BASE, 10.5, "end", True)
p.label(0.6, 5500, "P = 1000 TL,  yıllık oran %9", 0, 0, TEXT, 10.5, "start")
OUT["basit-vs-bilesik"] = figure(
    440, 220, [p],
    "Basit faizde yalnızca anapara faiz getirdiği için birikim bir <strong>doğru</strong> boyunca "
    "artar; bileşik faizde her dönemin faizi anaparaya eklendiğinden artış "
    "<strong>üstel</strong>dir. Fark kısa vadede küçük, uzun vadede belirleyicidir.",
    aria="Basit faiz dogrusu ile bilesik faiz ussel egrisinin karsilastirmasi")

# --- Bileşik faizde değer taşıma --------------------------------------------
p = tl_panel(30, 60, 400, 90, -0.15, 2.15)
tline(p, 0, [0, 1, 2], ["Geçmişteki zaman", "Şimdiki zaman", "Gelecekteki zaman"], lab_dy=-11)
span(p, 0, 1, "n dönem", dy=-52)
span(p, 1, 2, "n dönem", dy=-52)
amount(p, 1, "X", dy=-28, color=PRACTICE, size=13)
flow(p, 1, 0, "X(1 + i)" + sups(MINUS_S + "n"), THEORY, rise=28, above=False, gap=12, lab_dy=17, size=11)
flow(p, 1, 2, "X(1 + i)" + sups("n"), BASE, rise=28, above=False, gap=12, lab_dy=17, size=11)
OUT["bilesik-deger-semasi"] = figure(
    460, 190, [p],
    "Bileşik faizde de kural aynıdır, yalnızca çarpan değişir: <em>n</em> dönem ileri gitmek "
    "(1 + <em>i</em>)<sup><em>n</em></sup> ile çarpmak, <em>n</em> dönem geri gitmek "
    "(1 + <em>i</em>)<sup>&#8722;<em>n</em></sup> ile çarpmaktır.",
    aria="Bilesik faizde gecmis, simdi ve gelecek arasinda deger tasima")

# --- X, Y, Z zinciri --------------------------------------------------------
p = tl_panel(34, 80, 400, 92, -0.45, 4.3)
tline(p, 0, [0, 1.3, 2.1, 3.9], ["0", "n&#8321;", "n&#8322;", "n&#8323;"])
amount(p, 1.3, "X", color=THEORY, size=12.5)
amount(p, 2.1, "Y", color=BASE, size=12.5)
amount(p, 3.9, "Z", color=PRACTICE, size=12.5)
flow(p, 1.3, 2.1, "(1 + i)" + sups("n&#8322;" + MINUS_S + "n&#8321;"), THEORY, rise=26)
flow(p, 2.1, 3.9, "(1 + i)" + sups("n&#8323;" + MINUS_S + "n&#8322;"), BASE, rise=26)
flow(p, 1.3, 3.9, "(1 + i)" + sups("n&#8323;" + MINUS_S + "n&#8321;"), PRACTICE,
     rise=34, above=False, gap=30, lab_dy=17)
OUT["deger-denklik-xyz"] = figure(
    480, 210, [p],
    "İki adımda taşımak ile tek adımda taşımak aynı sonucu verir: çarpanlar üst üste binerken "
    "üsler toplanır. Bu yüzden bileşik faizde <strong>odak noktası önemsizdir</strong> &#8212; "
    "bir odakta denk olan iki ödeme kümesi her tarihte denktir.",
    aria="X, Y ve Z degerlerinin ardisik tasinmasi ve tek adimda tasinmasi")

# --- Örnek 1.15: m arttıkça S -----------------------------------------------
p = Plot(70, 46, 320, 140, (0, 6.6), (30500, 33900))
p.axes((), range(31000, 33501, 500), "", "TL")
vals = [(0.6, 31058.48, "31.058", "m = 1"), (1.75, 32071.35, "32.071", "m = 2"),
        (2.9, 32620.38, "32.620", "m = 4"), (4.05, 33003.87, "33.004", "m = 12"),
        (5.2, 33155.30, "33.155", "m = 52"), (6.05, 33194.62, "33.195", "m = 365")]
bars(p, [(x, v, "", b) for x, v, t, b in vals], 30500, THEORY, half=0.42)
for x, v, t, b in vals:
    p.text_px(p.X(x), p.Y(v) + 16, t, THEORY, 9.5, "middle", True)
p.add(f'<line x1="{p.X(0.1):.1f}" y1="{p.Y(33201.17):.1f}" x2="{p.X(6.55):.1f}" y2="{p.Y(33201.17):.1f}" '
      f'stroke="{PRACTICE}" stroke-width="1.3" stroke-dasharray="5 4"/>')
p.text_px(p.X(0.15), p.Y(33201.17) - 8, "sürekli bileşik faiz sınırı: 33.201,17 TL", PRACTICE, 10, "start")
OUT["esdeger-oranlar-m"] = figure(
    450, 230, [p],
    "10000 TL, <em>j<sub>m</sub></em> = %12&#8217;den 10 yıl bekletiliyor. Faiz dönemi sıklaştıkça "
    "(<em>m</em> büyüdükçe) birikmiş değer artar, ama artış giderek yavaşlar: kesikli çizgi, "
    "10000<em>e</em><sup>1,2</sup> = 33.201,17 TL olan sürekli bileşik faiz sınırıdır.",
    aria="m buyudukce birikmis degerin artisi ve surekli bilesik faiz siniri")

# --- Örnek 1.17b: pratik metod ileri ----------------------------------------
p = tl_panel(34, 76, 410, 92, -0.35, 4.4)
tline(p, 0, [0, 3.4, 4.1], ["0", "11. dönem", "5 yıl 7 ay"], sub=["", "(5 yıl 6 ay)", ""], size=10)
amount(p, 0, "1000", color=THEORY)
amount(p, 4.1, "2074,46", color=PRACTICE)
flow(p, 0, 3.4, "11 dönem bileşik faiz  (j&#8322; = 0,1350)", THEORY, rise=40)
flow(p, 3.4, 4.1, "1 ay basit", BASE, rise=26, lab_dx=6)
OUT["ornek-117-pratik"] = figure(
    490, 200, [p],
    "Pratik metod: tarihi <strong>geçmeyen</strong> en büyük tam dönem sayısı kadar bileşik faiz "
    "uygulanır (11 dönem = 5 yıl 6 ay), artan 1 aylık parça için ileriye doğru basit faiz eklenir.",
    aria="Kesirli donemde pratik metod: 11 donem bilesik, 1 ay basit faiz")

# --- Örnek 1.18b: pratik metod geri -----------------------------------------
p = tl_panel(34, 92, 410, 96, -0.45, 4.5)
tline(p, 0, [0, 0.85, 4.1], ["&#8722;5 ay", "0 (bugün)", "3 yıl 7 ay"], size=10)
amount(p, 4.1, "2800", color=BASE)
amount(p, 0.85, "P = 1992,12", color=PRACTICE, dx=18)
flow(p, 4.1, 0, "4 dönem (yıl) geriye bileşik faiz", THEORY, rise=48, above=False, gap=30, lab_dy=16)
flow(p, 0, 0.85, "5 ay ileri basit faiz", BASE, rise=32)
OUT["ornek-118-pratik"] = figure(
    490, 220, [p],
    "Geçmişteki değeri bulurken pratik metod ters çalışır: tarihi <strong>içeren</strong> en küçük "
    "tam dönem kadar geriye bileşik faizle gidilir (4 yıl), sonra aranan tarihe kadar ileriye doğru "
    "basit faiz uygulanır (5 ay).",
    aria="Kesirli donemde geriye dogru pratik metod")

# --- Örnek 1.23 -------------------------------------------------------------
p = tl_panel(34, 84, 410, 96, -0.35, 4.4)
tline(p, 0, [0, 1.2, 2.8, 4.1], ["0", "36. dönem", "84. dönem", "120. dönem"],
      sub=["", "3 yıl", "7 yıl", "10 yıl"], size=10)
amount(p, 2.8, "2500", color=THEORY, size=11.5)
amount(p, 1.2, "X = ?", color=PRACTICE, size=11.5)
amount(p, 4.1, "Y = ?", color=BASE, size=11.5)
flow(p, 2.8, 1.2, "48 dönem geri", THEORY, rise=34)
flow(p, 2.8, 4.1, "36 dönem ileri", BASE, rise=34)
OUT["ornek-123-denklik"] = figure(
    490, 210, [p],
    "<em>j</em><sub>12</sub> = %10 olduğu için dönem = 1 ay: 3. yıl 36., 7. yıl 84., 10. yıl 120. "
    "dönemdir. 7. yıldaki 2500 TL, 3. yıla 48 dönem geri, 10. yıla 36 dönem ileri taşınır.",
    aria="Ornek 1.23: 7. yildaki borcun 3. ve 10. yildaki denkleri")

# --- Örnek 1.24 -------------------------------------------------------------
p = tl_panel(34, 108, 410, 100, -0.45, 4.4)
tline(p, 0, [0, 1.4, 2.1, 4.0], ["0", "6. dönem", "8. dönem", "16. dönem"],
      sub=["bugün", "18 ay", "2 yıl", "4 yıl"], size=10)
amount(p, 1.4, "1000", color=THEORY)
amount(p, 4.0, "1500", color=THEORY)
amount(p, 0, "X = ?", color=PRACTICE, size=11)
amount(p, 2.1, "Y = ?", color=BASE, size=11)
flow(p, 1.4, 0, "6 dönem", PRACTICE, rise=34)
flow(p, 4.0, 0, "16 dönem", PRACTICE, rise=76)
flow(p, 1.4, 2.1, "2 dönem", BASE, rise=30, above=False, gap=42, lab_dy=16)
flow(p, 4.0, 2.1, "8 dönem", BASE, rise=56, above=False, gap=42, lab_dy=16)
OUT["ornek-124-denklik"] = figure(
    490, 260, [p],
    "<em>j</em><sub>4</sub> = %6&#8217;da dönem 3 aydır: 18 ay 6 dönem, 2 yıl 8 dönem, 4 yıl 16 dönem "
    "eder. İki borç önce bugüne (<em>X</em>, üstteki oklar), sonra 2. yıla (<em>Y</em>, alttaki "
    "oklar) taşınıyor.",
    aria="Ornek 1.24: iki borcun bugune ve 2 yil sonraya tasinmasi")


# ############################################################################
# PART 3 — Anüiteler (bölüm 9–13)
# ############################################################################

def dots(p, x, y=0.0, dy=-11.0, color=TEXT, size=13):
    p.text_px(p.X(x), p.Y(y) + dy, "&#183;  &#183;  &#183;", color, size, "middle")


def stream(p, xs, target, color=THEORY, rise0=26.0, drise=15.0, above=True,
           gap=22.0, width=1.3, head=6.5, reverse=False):
    """Arcs carrying every payment of an annuity to the same date."""
    order = list(range(len(xs)))
    if reverse:
        order = order[::-1]
    k = 0
    for idx in order:
        if abs(xs[idx] - target) < 1e-9:      # the payment already sits on the target date
            continue
        flow(p, xs[idx], target, "", color, rise=rise0 + k * drise, above=above,
             gap=gap, width=width, head=head)
        k += 1


# --- Normal (dönem sonu) basit anüite ---------------------------------------
p = tl_panel(40, 118, 420, 104, -0.6, 7.4)
XS = [0, 1, 2, 3, 5, 6, 6.9]
tline(p, 0, XS, ["0", "1", "2", "3", "n &#8722; 2", "n &#8722; 1", "n"])
dots(p, 4, dy=6, size=12)
for x in XS[1:]:
    amount(p, x, "R", color=THEORY, size=11.5)
stream(p, XS[1:], 6.9, THEORY, rise0=22, drise=14)
drop(p, 6.9, "S = R &#183; s" + subs("n|i"), up=True, depth=112, color=PRACTICE, dash="4 3", size=11.5)
drop(p, 0, "A = R &#183; a" + subs("n|i"), up=True, depth=112, color=BASE, dash="4 3", size=11.5)
flow(p, 6.9, 0, "n dönem geri", BASE, rise=30, above=False, gap=30, lab_dy=16)
OUT["normal-anuite"] = figure(
    510, 260, [p],
    "Normal basit anüite: <em>n</em> tane <em>R</em> ödemesi her dönemin <strong>sonunda</strong> "
    "yapılır. Bütün ödemeler son tarihe taşınırsa toplam değer <em>S</em> = <em>R</em> &#183; "
    "<em>s</em><sub><em>n</em>|<em>i</em></sub>, başlangıca taşınırsa iskontolu değer "
    "<em>A</em> = <em>R</em> &#183; <em>a</em><sub><em>n</em>|<em>i</em></sub> elde edilir; ikisi "
    "arasında <em>S</em> = <em>A</em>(1 + <em>i</em>)<sup><em>n</em></sup> bağıntısı vardır.",
    aria="Normal basit anuitede odemelerin toplam degere ve iskontolu degere tasinmasi")

# --- Örnek 2.1 --------------------------------------------------------------
p = tl_panel(40, 96, 380, 92, -0.5, 5.5)
tline(p, 0, [0, 1, 2, 3, 4, 5], ["0", "1", "2", "3", "4", "5"])
for x in range(1, 6):
    amount(p, x, "2000", color=THEORY, size=10)
stream(p, [1, 2, 3, 4, 5], 5, THEORY, rise0=20, drise=15)
drop(p, 5, "S = 11.969,42 TL", depth=48, start=26, color=PRACTICE)
OUT["ornek-21-anuite"] = figure(
    470, 210, [p],
    "Yıl sonlarında ödenen 5 taksitin her biri 5. yıla taşınıyor: son ödeme hiç faiz görmez, "
    "sondan bir önceki bir yıl faiz görür &#8230; ilk ödeme dört yıl faiz görür. Toplamları "
    "<em>s</em><sub>5|0,09</sub> çarpanını verir.",
    aria="Ornek 2.1: bes yillik anuitenin toplam degeri")

# --- Örnek 2.2 --------------------------------------------------------------
p = tl_panel(40, 100, 420, 96, -0.6, 5.5)
XS = [0, 1, 2, 3, 4, 5]
tline(p, 0, XS, ["Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım"], size=9.5)
for x in range(1, 6):
    amount(p, x, "250", color=THEORY, size=10)
stream(p, [1, 2, 3, 4, 5], 5, THEORY, rise0=20, drise=14)
note(p, p.X(2.5), p.Y(0) + 34, "ödenmeyen taksitler", REMARK, 9.5, "middle")
drop(p, 5, "S = 1280,36 TL", depth=48, start=26, color=PRACTICE)
OUT["ornek-22-anuite"] = figure(
    500, 220, [p],
    "Temmuz&#8211;Ekim taksitleri ödenmemiş, Kasım taksidiyle birlikte kapatılacaktır. Beş taksit "
    "de Kasım ayına taşındığında ödenmesi gereken tutar, beş dönemlik bir anüitenin toplam "
    "değeridir.",
    aria="Ornek 2.2: odenmeyen taksitlerin Kasim ayina tasinmasi")

# --- Örnek 2.3 --------------------------------------------------------------
p = tl_panel(40, 108, 430, 100, -0.7, 7.4)
XS = [0, 1, 2, 3, 5.6, 6.9]
tline(p, 0, XS, ["0", "1", "2", "3", "16", "17"],
      sub=["1.12.1992", "1.3.1993", "1.6.1993", "1.9.1993", "1.12.1996", "1.3.1997"], size=10, sub_size=8.8)
for x in [1, 2, 3, 5.6, 6.9]:
    amount(p, x, "300", color=THEORY, size=10)
dots(p, 4.4, dy=-11, size=12)
stream(p, [1, 2, 3, 5.6, 6.9], 6.9, THEORY, rise0=20, drise=15)
drop(p, 6.9, "S = 6003,62 TL", depth=60, start=38, color=PRACTICE)
OUT["ornek-23-anuite"] = figure(
    510, 250, [p],
    "İlk ödeme 1.3.1993, son ödeme 1.3.1997: aradaki 4 yıl 16 çeyrek dönemdir, ödeme sayısı ise "
    "bir fazla, <em>n</em> = 17&#8217;dir. Normal anüitede ilk ödeme birinci dönemin sonunda "
    "yapıldığı için &#8220;0. dönem&#8221; 1.12.1992&#8217;ye düşer.",
    aria="Ornek 2.3: uc ayda bir yapilan 17 odemenin toplam degeri")

# --- Örnek 2.4: değişen faiz oranları ---------------------------------------
p = tl_panel(40, 128, 440, 104, -0.6, 10.6)
tline(p, 0, list(range(11)), [str(k) for k in range(11)])
for x in range(1, 11):
    amount(p, x, "1000", color=TEXT, size=9)
for xa, xb, lab in ((0, 3, "j&#8321; = %8"), (3, 7, "j&#8321; = %10,25"), (7, 10, "j&#8321; = %9")):
    span(p, xa, xb, lab, dy=70, lab_dy=13)
bracket(p, [1, 2, 3], 3, "1000 &#183; s" + subs("3|0,08") + " = 3246,40", dy=30, color=THEORY)
bracket(p, [4, 5, 6, 7], 7, "1000 &#183; s" + subs("4|0,1025") + " = 4658,79", dy=30, color=BASE)
bracket(p, [8, 9, 10], 10, "1000 &#183; s" + subs("3|0,09") + " = 3278,10", dy=30, color=PRACTICE)
flow(p, 3, 10, "&#215; (1,1025)" + sups("4") + "(1,09)" + sups("3") + " = 6211,49", THEORY, rise=44, gap=44)
flow(p, 7, 10, "&#215; (1,09)" + sups("3") + " = 6032,38", BASE, rise=22, gap=44, lab_t=0.42)
drop(p, 10, "S = 15.521,97 TL", depth=48, start=26, color=TEXT)
OUT["ornek-24-degisen-oran"] = figure(
    520, 280, [p],
    "Faiz oranı üç kez değişiyor. Her blok kendi oranıyla <strong>blok sonuna</strong> toplanır "
    "(yatay çubuklar), sonra biriken tutar sonraki blokların çarpanlarıyla topluca 10. yıla "
    "taşınır. Üç bloğun 10. yıldaki değerleri toplanınca 15.521,97 TL bulunur.",
    aria="Ornek 2.4: uc farkli faiz orani altinda on yillik anuite")

# --- Örnek 2.5 --------------------------------------------------------------
p = tl_panel(40, 100, 420, 96, -0.6, 10.6)
tline(p, 0, list(range(11)), [str(k) for k in range(11)])
for x in range(1, 11):
    amount(p, x, "R", color=THEORY, size=10.5)
stream(p, list(range(1, 11)), 10, THEORY, rise0=18, drise=7)
drop(p, 10, "S = 80.000 TL", depth=48, start=26, color=PRACTICE)
OUT["ornek-25-anuite"] = figure(
    500, 220, [p],
    "Hedef belli, taksit aranıyor: 10 yıl sonunda 80.000 TL biriktirmek için her yıl sonunda "
    "yatırılması gereken <em>R</em>, toplam değer formülünden çekilir &#8212; "
    "<em>R</em> = <em>S</em> / <em>s</em><sub>10|0,08</sub>.",
    aria="Ornek 2.5: hedeflenen birikim icin yillik taksitin bulunmasi")

# --- Örnek 2.7: peşinatlı taksitli satış ------------------------------------
p = tl_panel(40, 104, 430, 100, -0.6, 7.4)
XS = [0, 1, 2, 3, 5.6, 6.9]
tline(p, 0, XS, ["0", "1", "2", "3", "35", "36"])
amount(p, 0, "1500", color=BASE, size=10.5)
for x in [1, 2, 3, 5.6, 6.9]:
    amount(p, x, "182,5", color=THEORY, size=9.5)
dots(p, 4.4, dy=-11, size=12)
stream(p, [1, 2, 3, 5.6, 6.9], 0, THEORY, rise0=22, drise=15)
drop(p, 0, "X = nakit değer", depth=48, start=26, color=PRACTICE)
OUT["ornek-27-pesinat"] = figure(
    510, 240, [p],
    "Telefonun nakit değeri, bugün ödenen 1500 TL peşinat ile 36 taksidin <strong>bugüne "
    "taşınmış</strong> toplamıdır. Taksitlerin toplamı 6570 TL olsa da bugünkü değerleri "
    "5048,07 TL&#8217;dir; aradaki fark ödenen faizdir.",
    aria="Ornek 2.7: pesinat ve 36 taksidin bugunku degeri")

# --- Peşin anüite -----------------------------------------------------------
p = tl_panel(40, 122, 420, 104, -1.2, 7.4)
XS = [-0.9, 0, 1, 2, 5, 6, 6.9]
tline(p, 0, XS, ["&#8722;1", "0", "1", "2", "n &#8722; 2", "n &#8722; 1", "n"])
dots(p, 3.6, dy=6, size=12)
for x in [0, 1, 2, 5, 6]:
    amount(p, x, "R", color=THEORY, size=11.5)
stream(p, [0, 1, 2, 5, 6], 6.9, THEORY, rise0=22, drise=14)
drop(p, 6.9, "S", up=True, depth=110, color=PRACTICE, dash="4 3")
drop(p, 6, "S&#8242;", up=True, depth=94, color=REMARK, dash="4 3")
drop(p, 0, "A", up=True, depth=110, color=BASE, dash="4 3")
drop(p, -0.9, "A&#8242;", up=True, depth=94, color=REMARK, dash="4 3")
OUT["pesin-anuite"] = figure(
    510, 260, [p],
    "Peşin anüitede ödemeler dönem <strong>başında</strong> yapılır. Ödemeler bir dönem erken "
    "olduğu için, normal anüite formülleriyle bulunan <em>A</em>&#8242; ve <em>S</em>&#8242; "
    "değerlerinin bir dönem ileri taşınması yeterlidir: <em>A</em> = <em>A</em>&#8242;(1 + <em>i</em>), "
    "<em>S</em> = <em>S</em>&#8242;(1 + <em>i</em>).",
    aria="Pesin anuitede odemelerin donem basinda yapilmasi")

# --- Örnek 2.8 --------------------------------------------------------------
p = tl_panel(40, 100, 420, 96, -0.7, 7.4)
XS = [0, 1, 2, 3, 5.7, 6.9]
tline(p, 0, XS, ["0", "1", "2", "3", "59", "60"])
for x in [0, 1, 2, 3, 5.7]:
    amount(p, x, "200", color=THEORY, size=10)
dots(p, 4.4, dy=-11, size=12)
stream(p, [0, 1, 2, 3, 5.7], 6.9, THEORY, rise0=20, drise=14)
drop(p, 6.9, "S = 15.831,10 TL", depth=48, start=26, color=PRACTICE)
OUT["ornek-28-pesin"] = figure(
    500, 220, [p],
    "Her ayın <strong>başında</strong> 200 TL yatırılıyor: 60 ödemenin ilki 0. anda, sonuncusu "
    "59. ayın başında yapılır ve hesap 60. ayın sonunda kapatılır. Bu yüzden normal anüite "
    "toplamı bir dönem daha faizlendirilir.",
    aria="Ornek 2.8: ay baslarinda yatirilan 60 odemenin bes yil sonundaki degeri")

# --- Ertelenmiş anüite ------------------------------------------------------
p = tl_panel(40, 116, 430, 104, -0.6, 8.4)
XS = [0, 1, 2, 3.4, 4.4, 5.4, 7.9]
tline(p, 0, XS, ["0", "1", "2", "k", "k+1", "k+2", "k+n"])
dots(p, 2.7, dy=6, size=12)
dots(p, 6.6, dy=6, size=12)
for x in [4.4, 5.4, 7.9]:
    amount(p, x, "R", color=THEORY, size=11.5)
span(p, 0, 3.4, "k dönem ödeme yok", dy=-96, lab_dy=-6)
drop(p, 0, "A", up=True, depth=78, color=BASE, dash="4 3")
drop(p, 3.4, "A&#8242;", up=True, depth=78, color=REMARK, dash="4 3")
drop(p, 7.9, "S", up=True, depth=78, color=PRACTICE, dash="4 3")
flow(p, 3.4, 0, "k dönem geri", BASE, rise=28, above=False, gap=30, lab_dy=16)
OUT["ertelenmis-anuite"] = figure(
    520, 260, [p],
    "Ertelenmiş anüitede ilk ödeme <em>k</em> dönem sonra, yani (<em>k</em>+1). dönemde yapılır. "
    "Ödemeler <em>k</em>. döneme göre normal bir anüitedir: önce <em>A</em>&#8242; = "
    "<em>R</em> &#183; <em>a</em><sub><em>n</em>|<em>i</em></sub> bulunur, sonra <em>k</em> dönem "
    "geri taşınır. Toplam değer ise ertelemeden etkilenmez: <em>S</em> = <em>R</em> &#183; "
    "<em>s</em><sub><em>n</em>|<em>i</em></sub>.",
    aria="Ertelenmis anuitede ilk odemenin k donem sonra baslamasi")

# --- Örnek 2.9 --------------------------------------------------------------
p = tl_panel(40, 106, 430, 100, -0.6, 8.4)
XS = [0, 1, 3.4, 4.4, 5.4, 7.9]
tline(p, 0, XS, ["0", "1", "37", "38", "39", "45"],
      sub=["doğum", "", "19. yaş", "", "", ""], size=10, sub_size=9)
dots(p, 2.3, dy=6, size=12)
dots(p, 6.6, dy=6, size=12)
for x in [4.4, 5.4, 7.9]:
    amount(p, x, "1500", color=THEORY, size=10)
span(p, 0, 3.4, "37 dönem (18,5 yıl) ödeme yok", dy=-88, lab_dy=-6)
drop(p, 0, "A = 1941,16 TL", up=True, depth=70, color=BASE, dash="4 3")
flow(p, 3.4, 0, "37 dönem geri", BASE, rise=28, above=False, gap=42, lab_dy=16)
OUT["ornek-29-ertelenmis"] = figure(
    520, 250, [p],
    "Dönem altı ay olduğundan 19. yaş 37. döneme düşer; ilk geri ödeme 38. dönemdedir. Sekiz "
    "ödemelik anüitenin 37. dönemdeki değeri bulunup 37 dönem geriye taşınırsa bugün yatırılması "
    "gereken anapara elde edilir.",
    aria="Ornek 2.9: 19 yas sonrasi baslayan sekiz odemeli ertelenmis anuite")

# --- Örnek 2.10: iki yöntem -------------------------------------------------
q1 = tl_panel(30, 84, 400, 92, -0.6, 7.4)
tline(q1, 0, [0, 1, 2, 5.4, 6.5], ["0", "1", "2", "20", "21"])
dots(q1, 3.7, dy=-11, size=12)
for x in [1, 2, 5.4]:
    amount(q1, x, "200", color=THEORY, size=10)
amount(q1, 6.5, "200 + X", color=PRACTICE, size=10.5)
stream(q1, [1, 2, 5.4, 6.5], 6.5, THEORY, rise0=20, drise=14)
drop(q1, 6.5, "S = 8000", depth=48, start=26, color=BASE)
note(q1, q1.X(3.4), q1.Y(0) - 84, "1. yöntem: son ödemeye X = 1,45 TL eklenir", TEXT, 10.5, "middle", True)

q2 = tl_panel(30, 248, 400, 92, -0.6, 7.4)
tline(q2, 0, [0, 1, 2, 5.4, 6.5, 7.1], ["0", "1", "2", "20", "21", "22"])
dots(q2, 3.7, dy=-11, size=12)
for x in [1, 2, 5.4, 6.5]:
    amount(q2, x, "200", color=THEORY, size=10)
amount(q2, 7.1, "Y", color=PRACTICE, size=11)
stream(q2, [1, 2, 5.4, 6.5], 7.1, THEORY, rise0=20, drise=14)
drop(q2, 7.1, "S = 8000", depth=48, start=26, color=BASE)
note(q2, q2.X(3.4), q2.Y(0) - 84, "2. yöntem: 22. döneme küçük bir Y ödemesi konur", TEXT, 10.5, "middle", True)
note(q2, q2.X(6.0), q2.Y(0) + 78, "Y = &#8722;478,46 &lt; 0  &#8594;  22. dönemde ödemeye gerek yok", PRACTICE, 10, "middle", True)
OUT["ornek-210-yontemler"] = figure(
    460, 400, [q1, q2],
    "Dönem sayısı 21,002 çıktığında iki yol vardır: <strong>1. yöntem</strong>de fark son ödemeye "
    "eklenir (21. ödeme 201,45 TL olur); <strong>2. yöntem</strong>de bir dönem sonraya küçük bir "
    "ödeme konur. Burada bu ödeme eksi çıkıyor, yani 21 tam ödeme hedefi zaten aşmıştır.",
    aria="Ornek 2.10: son odemenin iki farkli yontemle duzenlenmesi", css_class=WIDE)

# --- Örnek 2.11 -------------------------------------------------------------
p = tl_panel(40, 100, 420, 96, -0.6, 7.4)
tline(p, 0, [0, 1, 2, 5.4, 6.5], ["0", "1", "2", "15", "16"])
dots(p, 3.7, dy=-11, size=12)
for x in [1, 2, 5.4]:
    amount(p, x, "400", color=THEORY, size=10)
amount(p, 6.5, "X = 292,39", color=PRACTICE, size=10)
stream(p, [1, 2, 5.4, 6.5], 0, THEORY, rise0=20, drise=15)
drop(p, 0, "A = 4000 TL", depth=48, start=26, color=BASE)
OUT["ornek-211-son-odeme"] = figure(
    500, 220, [p],
    "4000 TL&#8217;lik borç 15,73 dönemde bitiyor: 15 tam ödemeden sonra borcun bugünkü değerinden "
    "geriye kalan küçük parça, 16. dönemde yapılacak tek bir ödemeye dönüştürülür.",
    aria="Ornek 2.11: 15 tam odeme ve 16. donemde kucuk son odeme")

# --- Doğrusal interpolasyon -------------------------------------------------
p = Plot(70, 40, 320, 140, (6.85, 8.15), (11.65, 12.08))
p.axes([7, 7.5, 8], [11.7, 11.8, 11.9, 12.0], "j&#8322; (%)", "s")
p.grid([7, 7.5, 8], [11.7, 11.8, 11.9, 12.0])
p.line([(7, 11.7314), (8, 12.0061)], THEORY, 2.0)
p.points([(7, 11.7314), (8, 12.0061)], THEORY, 4.2)
p.vline(7.98, 11.65, 12.0061, TEXT, "4 3", 0.45)
p.add(f'<line x1="{p.X(6.85):.1f}" y1="{p.Y(12):.1f}" x2="{p.X(7.98):.1f}" y2="{p.Y(12):.1f}" '
      f'stroke="{PRACTICE}" stroke-width="1.2" stroke-dasharray="4 3"/>')
p.points([(7.98, 12)], PRACTICE, 4.6)
p.label(7, 11.7314, "(7 ; 11,7314)", 6, 14, THEORY, 10, "start")
p.label(8, 12.0061, "(8 ; 12,0061)", -8, 16, THEORY, 10, "end")
p.label(7.6, 12, "aranan oran: %7,98", 0, -10, PRACTICE, 10.5, "middle", True)
OUT["dogrusal-interpolasyon"] = figure(
    450, 210, [p],
    "İnterpolasyon, aradaki eğriyi bir <strong>doğru</strong> gibi kabul eder: aralarında %1 fark "
    "olan iki oran için hesaplanan iki nokta birleştirilir ve aranan değere karşılık gelen oran "
    "bu doğru üzerinden okunur. Aralık dar tutulduğu için hata küçüktür.",
    aria="Iki nokta arasinda dogrusal interpolasyon ile faiz oraninin bulunmasi")

# --- Örnek 2.13: genel anüite -----------------------------------------------
p = tl_panel(40, 108, 430, 100, -0.6, 7.4)
tline(p, 0, [0, 1, 2, 3, 5.6, 6.9], ["0", "1", "2", "3", "59", "60"], sub=["", "", "", "", "", "(ay)"], size=10)
dots(p, 4.4, dy=-11, size=12)
for x in [1, 2, 3, 5.6, 6.9]:
    amount(p, x, "300", color=THEORY, size=10)
for k in range(0, 5):
    xa = 1.38 * k
    p.add(f'<rect x="{p.X(max(xa, 0)):.1f}" y="{p.Y(0) + 34:.1f}" width="{p.X(min(xa + 1.38, 6.9)) - p.X(max(xa, 0)):.1f}" '
          f'height="12" fill="{BASE}" fill-opacity="0.13" stroke="{BASE}" stroke-width="0.9"/>')
note(p, p.X(3.45), p.Y(0) + 60, "faiz dönemi 3 ay (j&#8324;) &#8212; ödeme aralığı 1 ay", BASE, 10, "middle")
stream(p, [1, 2, 3, 5.6, 6.9], 6.9, THEORY, rise0=20, drise=14)
drop(p, 6.9, "S = 20.915,01 TL", up=True, depth=98, color=PRACTICE, dash="4 3")
OUT["ornek-213-genel-anuite"] = figure(
    510, 250, [p],
    "Genel anüitede ödeme aralığı ile faiz dönemi çakışmaz (altta gri bloklar üç aylık faiz "
    "dönemleri). Çözüm, verilen <em>j</em><sub>4</sub> oranına <strong>denk</strong> olan "
    "<em>j</em><sub>12</sub> oranını bulup problemi basit anüiteye çevirmektir.",
    aria="Ornek 2.13: aylik odemeler ve uc aylik faiz donemi olan genel anuite")

# --- Daimi gelir ------------------------------------------------------------
p = tl_panel(40, 92, 420, 96, -0.6, 7.6)
tline(p, 0, [0, 1, 2, 3, 4, 5, 6], ["0", "1", "2", "3", "4", "5", "6"])
for x in range(1, 7):
    amount(p, x, "R", color=THEORY, size=11.5)
dots(p, 7.1, dy=-11, size=13)
stream(p, [1, 2, 3, 4, 5, 6], 0, THEORY, rise0=18, drise=11)
drop(p, 0, "A" + subs(INFTY_S) + " = R / i", depth=48, start=26, color=PRACTICE, size=11.5)
OUT["daimi-gelir"] = figure(
    500, 220, [p],
    "Daimi gelirde ödemeler hiç bitmez, bu yüzden bir toplam değerden söz edilemez; ama iskontolu "
    "değer sonludur. Uzaktaki ödemelerin bugünkü değeri hızla küçüldüğü için sonsuz toplam "
    "<em>R</em>/<em>i</em> sayısına yakınsar &#8212; yani &#8220;yalnızca faizini harcamak&#8221;.",
    aria="Daimi gelirde sonsuz odeme dizisinin iskontolu degeri")

# --- Değişik (artan) ödemeli anüite -----------------------------------------
p = tl_panel(40, 108, 420, 104, -0.6, 7.4)
XS = [0, 1, 2, 3, 5.6, 6.9]
tline(p, 0, XS, ["0", "1", "2", "3", "n &#8722; 1", "n"])
dots(p, 4.4, dy=6, size=12)
for x, lab in ((1, "R"), (2, "2R"), (3, "3R"), (5.6, "(n&#8722;1)R"), (6.9, "nR")):
    amount(p, x, lab, color=THEORY, size=10.5)
for k, x in enumerate([1, 2, 3, 5.6, 6.9]):
    h = 14 + 9 * k
    X0, X1 = p.X(x - 0.22), p.X(x + 0.22)
    p.add(f'<rect x="{X0:.1f}" y="{p.Y(0) - 24 - h:.1f}" width="{X1 - X0:.1f}" height="{h:.1f}" '
          f'fill="{THEORY}" fill-opacity="0.20" stroke="{THEORY}" stroke-width="1"/>')
drop(p, 0, "A", depth=48, start=26, color=BASE)
drop(p, 6.9, "S", depth=48, start=26, color=PRACTICE)
OUT["artan-anuite"] = figure(
    500, 240, [p],
    "Ödemeler her dönem <em>R</em> kadar artıyor. Böyle bir dizinin iskontolu değeri, sabit "
    "ödemeli anüite formülüyle doğrudan bulunamaz; toplamı (1 + <em>i</em>) ile çarpıp kendisinden "
    "çıkarma hilesiyle kapalı biçime getirilir.",
    aria="R, 2R, 3R diye artan odemeli anuite")


# ############################################################################
# PART 4 — Amortisman (bölüm 14–15)
# ############################################################################

# --- Örnek 3.1: borcun taksitlerle amortismanı ------------------------------
p = tl_panel(40, 100, 400, 96, -0.6, 6.5)
tline(p, 0, list(range(7)), [str(k) for k in range(7)])
for x in range(1, 6):
    amount(p, x, "R", color=THEORY, size=11.5)
amount(p, 6, "X", color=PRACTICE, size=11.5)
stream(p, [1, 2, 3, 4, 5, 6], 0, THEORY, rise0=20, drise=14)
drop(p, 0, "A = 6000 TL", depth=48, start=26, color=BASE)
OUT["ornek-31-amortisman"] = figure(
    480, 220, [p],
    "Amortismanda mantık terstir: taksitler bilinmez, <strong>borç</strong> bilinir. Altı taksidin "
    "bugüne taşınmış toplamı 6000 TL&#8217;ye eşitlenir ve <em>R</em> buradan çekilir. Son ödeme "
    "<em>X</em>, yuvarlamadan doğan farkı kapatmak için ayrıca hesaplanır.",
    aria="Ornek 3.1: alti taksidin bugunku degerinin borca esitlenmesi")

# --- Taksitin faiz / anapara ayrışması --------------------------------------
p = Plot(64, 40, 330, 150, (0.3, 6.7), (0, 1750))
p.axes(range(1, 7), range(0, 1401, 400), "ödeme", "TL")
rows = [(480.00, 817.89), (414.57, 883.32), (343.90, 953.99),
        (267.58, 1030.31), (185.16, 1112.73), (96.14, 1201.76)]
for k, (fa, an) in enumerate(rows):
    x = k + 1
    X0, X1 = p.X(x - 0.3), p.X(x + 0.3)
    p.add(f'<rect x="{X0:.1f}" y="{p.Y(fa):.1f}" width="{X1 - X0:.1f}" height="{p.Y(0) - p.Y(fa):.1f}" '
          f'fill="{PRACTICE}" fill-opacity="0.28" stroke="{PRACTICE}" stroke-width="1.1"/>')
    p.add(f'<rect x="{X0:.1f}" y="{p.Y(fa + an):.1f}" width="{X1 - X0:.1f}" height="{p.Y(fa) - p.Y(fa + an):.1f}" '
          f'fill="{THEORY}" fill-opacity="0.28" stroke="{THEORY}" stroke-width="1.1"/>')
for k, (lab, col, yy) in enumerate((("anapara (borç kısmı)", THEORY, 1690), ("faiz kısmı", PRACTICE, 1560))):
    p.add(f'<rect x="{p.X(0.95):.1f}" y="{p.Y(yy) - 8:.1f}" width="11" height="11" fill="{col}" '
          f'fill-opacity="0.28" stroke="{col}" stroke-width="1.1"/>')
    p.text_px(p.X(0.95) + 17, p.Y(yy) + 2, lab, col, 10.5, "start", True)
OUT["amortisman-bilesenleri"] = figure(
    450, 230, [p],
    "Taksit hep aynı (1297,89 TL) ama içeriği değişir: kalan borç azaldıkça faiz kısmı küçülür, "
    "anaparadan düşen kısım büyür. Amortisman tablosunun anlattığı şey tam olarak bu kaymadır.",
    aria="Sabit taksitin faiz ve anapara bilesenlerinin donemden doneme degisimi")

# --- Örnek 3.2: genel anüite biçiminde amortisman ---------------------------
p = tl_panel(40, 106, 420, 100, -0.6, 8.5)
tline(p, 0, list(range(9)), ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
      sub=["", "3 ay", "6 ay", "9 ay", "1 yıl", "", "", "", "2 yıl"], size=10, sub_size=8.8)
for x in range(1, 8):
    amount(p, x, "R", color=THEORY, size=11)
amount(p, 8, "X", color=PRACTICE, size=11)
stream(p, list(range(1, 9)), 0, THEORY, rise0=20, drise=11)
drop(p, 0, "A = 2000 TL", depth=60, start=38, color=BASE)
note(p, p.X(4.2), p.Y(0) + 82, "ödeme aralığı 3 ay, faiz aylık (j&#8321;&#8322;) &#8594; önce denk üç aylık oran bulunur",
     BASE, 10, "middle")
OUT["ornek-32-amortisman"] = figure(
    500, 250, [p],
    "Ödemeler üç ayda bir, faiz ise aylık işliyor: bu bir genel anüitedir. Önce "
    "<em>j</em><sub>12</sub> = %24&#8217;e denk gelen üç aylık <em>i</em> oranı bulunur "
    "((1+<em>i</em>)<sup>4</sup> = (1,02)<sup>12</sup>), sonra her şey basit anüite gibi yürür.",
    aria="Ornek 3.2: uc aylik odemeler ve aylik faizle amortisman")

# --- Kalan borç: iki yöntem -------------------------------------------------
p = tl_panel(40, 128, 430, 104, -0.7, 8.5)
XS = [0, 1, 2, 3.2, 4.2, 5.2, 7.9]
tline(p, 0, XS, ["0", "1", "2", "k", "k+1", "k+2", "n"])
dots(p, 2.6, dy=6, size=12)
dots(p, 6.6, dy=6, size=12)
for x in [1, 2, 3.2, 4.2, 5.2, 7.9]:
    amount(p, x, "R", color=TEXT, size=10.5)
amount(p, 0, "A", color=BASE, size=11.5)
flow(p, 0, 3.2, "", BASE, rise=68, gap=22)
stream(p, [1, 2, 3.2], 3.2, THEORY, rise0=24, drise=13)
stream(p, [4.2, 5.2, 7.9], 3.2, PRACTICE, rise0=24, drise=13, above=False, gap=44)
marker(p, 3.2, "", color=TEXT, r=4.0)
p.text_px(p.X(3.2), p.Y(0) + 32, "P" + subs("k"), TEXT, 11, "middle", True)
note(p, p.X(-0.6), p.Y(0) - 112, "1. yöntem (geçmişe bakarak):", BASE, 10.5, "start", True)
note(p, p.X(-0.6), p.Y(0) - 98, "P" + subs("k") + " = A(1 + i)" + sups("k") + " &#8722; R &#183; s" + subs("k|i"),
     BASE, 11, "start")
note(p, p.X(8.4), p.Y(0) + 74, "2. yöntem (geleceğe bakarak):", PRACTICE, 10.5, "end", True)
note(p, p.X(8.4), p.Y(0) + 88, "P" + subs("k") + " = R &#183; a" + subs("n" + MINUS_S + "k|i"),
     PRACTICE, 11, "end")
OUT["kalan-borc-yontemler"] = figure(
    510, 290, [p],
    "<em>k</em>. ödemeden sonraki kalan borcu iki yönden görebiliriz: <strong>geçmişe bakarak</strong> "
    "(ana borcun o güne taşınmış değerinden, yapılan ödemelerin biriktirdiği tutarı çıkararak) ya da "
    "<strong>geleceğe bakarak</strong> (henüz yapılmamış <em>n</em> &#8722; <em>k</em> ödemenin o "
    "güne taşınmış değerini alarak). İkisi aynı sayıyı verir.",
    aria="Kalan borcun gecmise ve gelecege bakarak hesaplanmasi")

# --- Örnek 3.3: ev kredisi --------------------------------------------------
p = tl_panel(40, 106, 430, 100, -0.7, 8.4)
XS = [0, 1, 2, 3.6, 6.2, 7.1, 8.0]
tline(p, 0, XS, ["0", "1", "2", "7", "346", "347", "348"],
      sub=["1.5.1994", "1.6.1994", "1.7.1994", "1.12.1994", "", "", "1.5.2023"], size=10, sub_size=8.8)
dots(p, 2.8, dy=6, size=12)
dots(p, 4.9, dy=6, size=12)
for x in [1, 2, 3.6, 6.2, 7.1]:
    amount(p, x, "458,9", color=THEORY, size=9.5)
amount(p, 8.0, "434,65", color=PRACTICE, size=9.5, dy=-26)
amount(p, 0, "52.000", color=BASE, size=10)
marker(p, 3.6, "P&#8327; = 51.816,50", dy=-46, color=PRACTICE, size=10)
flow(p, 0, 3.6, "7 ay", BASE, rise=30, gap=22)
OUT["ornek-33-ev-kredisi"] = figure(
    510, 250, [p],
    "29 yıllık kredi 348 aylık taksite bölünüyor. 1994 yılı içinde yalnızca 7 taksit ödenmiştir; "
    "o tarihteki kalan borç 51.816,50 TL&#8217;dir, yani yedi ayda anaparadan düşen tutar sadece "
    "183,50 TL&#8217;dir &#8212; ödenen 3212,30 TL&#8217;nin geri kalanı faizdir.",
    aria="Ornek 3.3: 348 aylik ev kredisinin ilk yedi ayi")

# --- Ev kredisinde kalan borç eğrisi ----------------------------------------
i33 = 5 / 600
R33 = 458.9
bal = [52000 * (1 + i33) ** k - R33 * (((1 + i33) ** k - 1) / i33) for k in range(0, 349)]
p = Plot(64, 36, 340, 148, (0, 348), (0, 55000))
p.axes(range(0, 349, 58), range(0, 50001, 10000), "ay", "TL")
p.grid(range(0, 349, 58), range(0, 50001, 10000))
p.line([(k, bal[k]) for k in range(0, 349)], THEORY, 2.2)
p.line([(0, 52000), (348, 0)], REMARK, 1.3, dash="5 4")
p.points([(84, bal[84]), (174, bal[174])], PRACTICE, 4.0)
p.label(84, bal[84], "7 yıl sonra hâlâ 47.735 TL", 6, -8, PRACTICE, 10, "start", True)
p.label(174, bal[174], "yarı yolda 39.049 TL", 6, -8, PRACTICE, 10, "start", True)
p.label(232, 17000, "borç eşit hızda azalsaydı", 0, 0, REMARK, 10, "middle", True)
OUT["ev-kredisi-borc-egrisi"] = figure(
    450, 230, [p],
    "Uzun vadeli kredide kalan borç <strong>doğrusal azalmaz</strong>: ilk yıllarda taksitin neredeyse "
    "tamamı faize gittiği için borç çok yavaş erir, sona doğru hızlanır. Kesikli çizgi, borç eşit "
    "hızda azalsaydı izleyeceği yoldur.",
    aria="348 aylik kredide kalan borcun zamana gore azalisi")

# ############################################################################
# PART 5 — Tahviller (bölüm 16–17)
# ############################################################################

# --- Tahvilin nakit akışı ---------------------------------------------------
p = tl_panel(40, 108, 420, 100, -0.6, 7.4)
XS = [0, 1, 2, 5, 6, 6.9]
tline(p, 0, XS, ["0", "1", "2", "n &#8722; 2", "n &#8722; 1", "n"])
dots(p, 3.5, dy=-11, size=12)
for x in [1, 2, 5, 6]:
    amount(p, x, "Fr", color=THEORY, size=11)
amount(p, 6.9, "Fr + C", color=PRACTICE, size=11)
stream(p, [1, 2, 5, 6, 6.9], 0, THEORY, rise0=20, drise=15)
drop(p, 0, "P = ihraç fiyatı", depth=48, start=26, color=BASE)
OUT["tahvil-nakit-akisi"] = figure(
    500, 240, [p],
    "Tahvil iki parçadan oluşur: her dönem ödenen <em>Fr</em> kupon anüitesi ve vadede ödenen "
    "<em>C</em> vade değeri. İhraç fiyatı, bu iki parçanın istenen <em>i</em> getiri oranından "
    "bugüne taşınmış toplamıdır.",
    aria="Tahvilin kupon odemeleri ve vade degerinden olusan nakit akisi")

# --- Örnek 4.2 --------------------------------------------------------------
p = tl_panel(40, 106, 430, 100, -0.7, 7.4)
XS = [0, 1, 2, 5.3, 6.2, 6.9]
tline(p, 0, XS, ["0", "1", "2", "13", "14", "15"],
      sub=["1.4.1995", "1.10.1995", "1.4.1996", "1.10.2001", "1.4.2002", "1.10.2002"], size=10, sub_size=8.5)
dots(p, 3.7, dy=-11, size=12)
for x in [1, 2, 5.3, 6.2]:
    amount(p, x, "262,50", color=THEORY, size=9.5)
amount(p, 6.9, "262,50 + 5150", color=PRACTICE, size=9.5)
stream(p, [1, 2, 5.3, 6.2, 6.9], 0, THEORY, rise0=20, drise=15)
drop(p, 0, "P = 5338,71 TL", depth=60, start=38, color=BASE)
OUT["ornek-42-tahvil"] = figure(
    510, 250, [p],
    "1.4.1995 ile 1.10.2002 arası 7,5 yıl, yani altı ayda bir ödemeyle 15 dönemdir. Kupon "
    "5000 &#183; 0,0525 = 262,50 TL, vade değeri ise nominalin 1,03 katı olan 5150 TL&#8217;dir.",
    aria="Ornek 4.2: 15 donemlik kuponlu tahvilin alis fiyati")

# --- Tahvil fiyatı - getiri eğrisi ve interpolasyon -------------------------
def bond_price(j):
    i = j / 2
    return 62.5 * (1 - (1 + i) ** -16) / i + 1060 * (1 + i) ** -16


p = Plot(70, 38, 330, 146, (0.115, 0.155), (900, 1100))
p.axes([0.12, 0.13, 0.14, 0.15], range(920, 1081, 40), "j&#8322;", "P (TL)",
       xfmt=lambda v: "%" + f"{v * 100:.0f}")
p.grid([0.12, 0.13, 0.14, 0.15], range(920, 1081, 40))
p.line([(0.115 + 0.04 * k / 60, bond_price(0.115 + 0.04 * k / 60)) for k in range(61)], THEORY, 2.0)
p.line([(0.13, bond_price(0.13)), (0.14, bond_price(0.14))], PRACTICE, 1.8, dash="5 3")
p.points([(0.13, bond_price(0.13)), (0.14, bond_price(0.14))], THEORY, 4.2)
p.points([(0.13781, 960)], PRACTICE, 4.6)
p.vline(0.13781, 900, 960, PRACTICE, "4 3", 0.6)
p.add(f'<line x1="{p.X(0.115):.1f}" y1="{p.Y(960):.1f}" x2="{p.X(0.13781):.1f}" y2="{p.Y(960):.1f}" '
      f'stroke="{PRACTICE}" stroke-width="1.1" stroke-dasharray="4 3"/>')
p.label(0.13, bond_price(0.13), "997,49", -6, -8, THEORY, 10, "end", True)
p.label(0.14, bond_price(0.14), "949,47", 7, -9, THEORY, 10, "start", True)
p.label(0.13781, 960, "j&#8322; = %13,78", -7, 20, PRACTICE, 10.5, "end", True)
p.label(0.116, 960, "P = 960", 0, -6, PRACTICE, 10, "start", True)
OUT["tahvil-fiyat-getiri"] = figure(
    450, 230, [p],
    "Tahvilin fiyatı ile getirisi ters yönlü hareket eder: oran büyüdükçe fiyat düşer. Eğri hafifçe "
    "bükümlü olduğu için, %1 aralıktaki iki nokta bir <strong>doğru</strong> ile birleştirilip "
    "aranan fiyata karşılık gelen oran okunur.",
    aria="Tahvil fiyati ile getiri orani arasindaki iliski ve interpolasyon")

# --- Örnek 4.4 --------------------------------------------------------------
p = tl_panel(40, 102, 430, 100, -0.7, 7.4)
XS = [0, 1, 2, 4, 5, 6.9]
tline(p, 0, XS, ["0", "1", "2", "16", "17", "32"],
      sub=["1.9.1987", "", "", "1.9.1995", "", "1.9.2003"], size=10, sub_size=8.8)
dots(p, 3.1, dy=-11, size=12)
dots(p, 6.0, dy=-11, size=12)
for x in [1, 2, 4]:
    amount(p, x, "62,5", color=THEORY, size=9.5)
amount(p, 0, "P = 960", color=BASE, size=10)
amount(p, 4, "C = 1060", color=PRACTICE, size=10, dx=0, dy=-44)
stream(p, [1, 2, 4], 0, THEORY, rise0=22, drise=15)
flow(p, 4, 0, "", PRACTICE, rise=68, gap=22)
note(p, p.X(5.5), p.Y(0) + 46, "yatırımcı 16. dönemde satıyor: kalan kuponlar onu ilgilendirmez",
     REMARK, 9.5, "middle")
OUT["ornek-44-tahvil"] = figure(
    510, 240, [p],
    "Yatırımcı tahvili 1.9.1987&#8217;de 960 TL&#8217;ye alıp 1.9.1995&#8217;te 1060 TL&#8217;ye "
    "satıyor. Onun için nakit akışı 16 kupon ile satış tutarından ibarettir; bu akışı 960 TL&#8217;ye "
    "eşitleyen oran, elde ettiği getiridir.",
    aria="Ornek 4.4: tahvilin alinip vadeden once satilmasi")

# ############################################################################
# PART 6 — Hayat anüiteleri ve sigortalar (bölüm 18–20)
# ############################################################################

# --- Hayat tablosunun kavramları --------------------------------------------
p = Plot(56, 44, 360, 140, (0, 4.4), (0, 1.15))
boxes = ((0.1, 1.45, "&#8467;" + subs("x") + " kişi", "x yaşına erişenler", THEORY, 0.62, 1.0),
         (2.6, 1.45, "&#8467;" + subs("x+1") + " kişi", "x+1 yaşına erişenler", BASE, 0.62, 1.0),
         (2.6, 1.45, "d" + subs("x") + " kişi", "x yaşında ölenler", PRACTICE, 0.02, 0.40))
for x0, w, lab, sub2, col, ylo, yhi in boxes:
    dash = ' stroke-dasharray="4 3"' if col == PRACTICE else ""
    p.add(f'<rect x="{p.X(x0):.1f}" y="{p.Y(yhi):.1f}" width="{p.X(x0 + w) - p.X(x0):.1f}" '
          f'height="{p.Y(ylo) - p.Y(yhi):.1f}" rx="6" fill="{col}" fill-opacity="0.14" '
          f'stroke="{col}" stroke-width="1.4"{dash}/>')
    p.text_px(p.X(x0 + w / 2), p.Y((ylo + yhi) / 2) - 2, lab, col, 12.5, "middle", True)
    p.text_px(p.X(x0 + w / 2), p.Y((ylo + yhi) / 2) + 13, sub2, col, 9.5, "middle")
p.arrow((1.6, 0.78), (2.55, 0.78), BASE, 1.5, head=8)
p.arrow((1.62, 0.66), (2.55, 0.28), PRACTICE, 1.5, head=8)
p.text_px(p.X(2.07), p.Y(0.99), "1 yıl sonra", TEXT, 9.5, "middle")
p.text_px(p.X(2.07), p.Y(0.88), "p" + subs("x") + " = &#8467;" + subs("x+1") + " / &#8467;" + subs("x"),
          BASE, 10.5, "middle", True)
p.text_px(p.X(2.52), p.Y(0.22), "q" + subs("x") + " = d" + subs("x") + " / &#8467;" + subs("x"),
          PRACTICE, 10.5, "end", True)
p.text_px(p.X(0.82), p.Y(0.20), "p" + subs("x") + " + q" + subs("x") + " = 1", TEXT, 10.5, "middle")
OUT["hayat-tablosu-kavramlari"] = figure(
    470, 210, [p],
    "Hayat tablosu bir <strong>kuşağı</strong> izler: <em>x</em> yaşına erişen "
    "&#8467;<sub><em>x</em></sub> kişiden <em>d<sub>x</sub></em> tanesi o yıl içinde ölür, "
    "kalan &#8467;<sub><em>x</em>+1</sub> kişi bir sonraki yaşa geçer. Bütün olasılıklar bu iki "
    "sayının &#8467;<sub><em>x</em></sub>&#8217;e oranıdır.",
    aria="Hayat tablosunda l_x, d_x, p_x ve q_x kavramlari")

# --- nEx şeması -------------------------------------------------------------
p = tl_panel(40, 92, 400, 92, -0.5, 5.4)
tline(p, 0, [0, 1, 4, 5], ["x", "x+1", "x+n&#8722;1", "x+n"], sub=["(bugün)", "", "", ""], size=10.5)
dots(p, 2.5, dy=-11, size=12)
amount(p, 5, "1 TL", color=THEORY, size=11)
flow(p, 5, 0, "(1 + i)" + sups(MINUS_S + "n") + " &#183; " + subs("n") + "p" + subs("x"), THEORY, rise=40)
drop(p, 0, subs("n") + "E" + subs("x") + " = iskonto &#215; yaşama olasılığı", depth=60, start=38,
     color=PRACTICE, size=11)
OUT["nex-semasi"] = figure(
    480, 230, [p],
    "<em>x</em> yaşındaki birine, <em>n</em> yıl sonra <strong>hayatta ise</strong> ödenecek 1 "
    "TL&#8217;nin bugünkü beklenen değeri iki çarpandan oluşur: parayı geri taşıyan "
    "(1+<em>i</em>)<sup>&#8722;<em>n</em></sup> ve ödemenin gerçekleşme olasılığı olan "
    "<sub><em>n</em></sub><em>p<sub>x</sub></em>.",
    aria="Hayatta olma halinde odenecek 1 TL nin iskontolu beklenen degeri")

# --- Ömür boyu hayat anüitesi: dönem sonu / dönem başı ----------------------
q1 = tl_panel(30, 92, 400, 88, -0.5, 6.6)
tline(q1, 0, [0, 1, 3, 4, 5.6, 6.2], ["x", "x+1", "x+k", "x+k+1", "99", "100"], size=10)
dots(q1, 2.0, dy=-11, size=12)
dots(q1, 4.9, dy=-11, size=12)
for x in [4, 5.6]:
    amount(q1, x, "1", color=THEORY, size=11.5)
stream(q1, [4, 5.6], 0, THEORY, rise0=22, drise=16)
note(q1, q1.X(3.1), q1.Y(0) - 100, "ilk ödeme (k+1). yılın sonunda:   " + subs("k") + "|a" + subs("x"),
     THEORY, 11, "middle", True)

q2 = tl_panel(30, 248, 400, 88, -0.5, 6.6)
tline(q2, 0, [0, 1, 3, 4, 5.6, 6.2], ["x", "x+1", "x+k", "x+k+1", "99", "100"], size=10)
dots(q2, 2.0, dy=-11, size=12)
dots(q2, 4.9, dy=-11, size=12)
for x in [3, 4, 5.6]:
    amount(q2, x, "1", color=BASE, size=11.5)
stream(q2, [3, 4, 5.6], 0, BASE, rise0=22, drise=16)
note(q2, q2.X(3.1), q2.Y(0) - 100, "ilk ödeme k. yılın başında:   " + subs("k") + "|ä" + subs("x"),
     BASE, 11, "middle", True)
OUT["omur-boyu-anuite"] = figure(
    460, 380, [q1, q2],
    "Ömür boyu ertelenmiş hayat anüitesinin iki biçimi. Aradaki tek fark <em>k</em>. yılda bir "
    "ödeme olup olmadığıdır: <em>ä</em> biçiminde toplam <em>t</em> = 0&#8217;dan, <em>a</em> "
    "biçiminde <em>t</em> = 1&#8217;den başlar. Ödemeler 100 yaşından önce biter, çünkü kimsenin "
    "100 yaşına erişmediği kabul edilmektedir.",
    aria="Omur boyu hayat anuitesinin donem sonu ve donem basi bicimleri", css_class=WIDE)

# --- Geçici hayat anüitesi --------------------------------------------------
q1 = tl_panel(30, 92, 400, 88, -0.5, 6.4)
tline(q1, 0, [0, 1, 2, 4.6, 5.6], ["x", "x+1", "x+2", "x+n&#8722;1", "x+n"], size=10)
dots(q1, 3.3, dy=-11, size=12)
for x in [1, 2, 4.6, 5.6]:
    amount(q1, x, "1", color=THEORY, size=11.5)
stream(q1, [1, 2, 4.6, 5.6], 0, THEORY, rise0=20, drise=15)
note(q1, q1.X(2.9), q1.Y(0) - 100, "yıl sonlarında n ödeme:   a" + subs("x:n"), THEORY, 11, "middle", True)

q2 = tl_panel(30, 244, 400, 88, -0.5, 6.4)
tline(q2, 0, [0, 1, 2, 4.6, 5.6], ["x", "x+1", "x+2", "x+n&#8722;1", "x+n"], size=10)
dots(q2, 3.3, dy=-11, size=12)
for x in [0, 1, 2, 4.6]:
    amount(q2, x, "1", color=BASE, size=11.5)
stream(q2, [0, 1, 2, 4.6], 0, BASE, rise0=20, drise=15)
note(q2, q2.X(2.9), q2.Y(0) - 100, "yıl başlarında n ödeme:   ä" + subs("x:n"), BASE, 11, "middle", True)
OUT["gecici-anuite"] = figure(
    460, 375, [q1, q2],
    "Geçici hayat anüitesinde ödemeler <em>n</em> yılla sınırlıdır. Yıl sonu biçiminde ilk ödeme "
    "<em>x</em>+1 yaşında, yıl başı biçiminde ise hemen <em>x</em> yaşında yapılır; ikincisinde ilk "
    "ödeme kesin olduğu için ne iskonto edilir ne de olasılıkla çarpılır.",
    aria="Gecici hayat anuitesinin yil sonu ve yil basi bicimleri", css_class=WIDE)

# --- Örnek 5.5: beş terimin ayrıştırılması ----------------------------------
p = Plot(64, 44, 340, 140, (94.4, 100.9), (0, 172000))
p.axes(range(95, 100), range(0, 150001, 50000), "yaş", "kişi",
       yfmt=lambda v: f"{v/1000:.0f}".replace(".", ",") + " bin")
vals = [(95, 146721), (96, 98309), (97, 60504), (98, 31450), (99, 10757)]
disc = [(95, 20421.6), (96, 12668.1), (97, 7220.2), (98, 3475.0), (99, 1100.5)]
for (x, v), (_, d) in zip(vals, disc):
    X0, X1 = p.X(x - 0.3), p.X(x + 0.3)
    p.add(f'<rect x="{X0:.1f}" y="{p.Y(v):.1f}" width="{X1 - X0:.1f}" height="{p.Y(0) - p.Y(v):.1f}" '
          f'fill="{THEORY}" fill-opacity="0.16" stroke="{THEORY}" stroke-width="1.2" rx="2"/>')
    p.add(f'<rect x="{X0:.1f}" y="{p.Y(d):.1f}" width="{X1 - X0:.1f}" height="{p.Y(0) - p.Y(d):.1f}" '
          f'fill="{PRACTICE}" fill-opacity="0.45" stroke="{PRACTICE}" stroke-width="1.2" rx="2"/>')
    p.text_px(p.X(x), p.Y(v) - 7, f"{v:,}".replace(",", "."), THEORY, 9, "middle", True)
for lab, col, yy in (("&#8467; : hayatta olan kişi sayısı", THEORY, 165000),
                     ("koyu: (1,08)" + sups(MINUS_S + "t") + " ile iskonto edilmişi", PRACTICE, 143000)):
    p.add(f'<rect x="{p.X(97.15):.1f}" y="{p.Y(yy) - 8:.1f}" width="11" height="11" fill="{col}" '
          f'fill-opacity="{0.16 if col == THEORY else 0.45}" stroke="{col}" stroke-width="1.1"/>')
    p.text_px(p.X(97.15) + 17, p.Y(yy) + 2, lab, col, 10, "start", True)
OUT["ornek-55-hayat"] = figure(
    450, 230, [p],
    "Ömür boyu anüitenin sonsuz toplamı aslında beş terimden ibarettir: 95, 96, 97, 98 ve 99 "
    "yaşlarında hayatta olan kişi sayıları. Koyu kısımlar aynı sayıların 25&#8211;29 yıl geri "
    "iskonto edilmiş hâlidir &#8212; uzaktaki ödemelerin katkısı bu yüzden çok küçüktür.",
    aria="Ornek 5.5: omur boyu anuitedeki bes terimin buyuklugu")

# --- Hayat sigortası şeması -------------------------------------------------
p = tl_panel(40, 116, 420, 96, -0.5, 6.4)
tline(p, 0, [0, 1, 2, 3, 5.6], ["x", "x+1", "x+2", "x+3", "x+n"], size=10.5)
dots(p, 4.4, dy=-11, size=12)
for x, lab in ((1, "d" + subs("x")), (2, "d" + subs("x+1")), (3, "d" + subs("x+2"))):
    amount(p, x, lab, color=PRACTICE, size=10.5)
amount(p, 5.6, "d" + subs("x+n" + MINUS_S + "1"), color=PRACTICE, size=10.5)
stream(p, [1, 2, 3, 5.6], 0, PRACTICE, rise0=20, drise=15)
drop(p, 0, "A" + sups("1") + subs("x:n") + "  (net tek prim)", depth=48, start=26, color=BASE, size=11)
note(p, p.X(3.0), p.Y(0) - 104, "ödeme, ölümün gerçekleştiği yılın SONUNDA yapılır", REMARK, 10, "middle")
OUT["hayat-sigortasi-semasi"] = figure(
    500, 260, [p],
    "Hayat sigortasında ödeme, <strong>ölüm hâlinde</strong> ve ölümün gerçekleştiği yılın sonunda "
    "yapılır. Bu yüzden her yılın katkısı, o yıl ölenlerin oranı "
    "<em>d</em><sub><em>x</em>+<em>t</em></sub>/&#8467;<sub><em>x</em></sub> ile "
    "(1+<em>i</em>)<sup>&#8722;(<em>t</em>+1)</sup> çarpanının çarpımıdır.",
    aria="n yillik hayat sigortasinin net tek priminin olusumu")

# --- Örnek 6.1: beş terim ---------------------------------------------------
p = Plot(64, 44, 340, 140, (94.4, 100.9), (0, 62000))
p.axes(range(95, 100), range(0, 50001, 10000), "yaş", "kişi",
       yfmt=lambda v: f"{v/1000:.0f}" + " bin")
dvals = [(95, 48412, 44825.93), (96, 37805, 32410.15), (97, 29054, 23063.30),
         (98, 20693, 15211.93), (99, 10757, 7321.90)]
for x, d, pv in dvals:
    X0, X1 = p.X(x - 0.3), p.X(x + 0.3)
    p.add(f'<rect x="{X0:.1f}" y="{p.Y(d):.1f}" width="{X1 - X0:.1f}" height="{p.Y(0) - p.Y(d):.1f}" '
          f'fill="{PRACTICE}" fill-opacity="0.16" stroke="{PRACTICE}" stroke-width="1.2" rx="2"/>')
    p.add(f'<rect x="{X0:.1f}" y="{p.Y(pv):.1f}" width="{X1 - X0:.1f}" height="{p.Y(0) - p.Y(pv):.1f}" '
          f'fill="{PRACTICE}" fill-opacity="0.45" stroke="{PRACTICE}" stroke-width="1.2" rx="2"/>')
    p.text_px(p.X(x), p.Y(d) - 7, f"{d:,}".replace(",", "."), PRACTICE, 9, "middle", True)
for lab, op, yy in (("d" + subs("95+t") + " : o yıl ölenler", 0.16, 59000),
                    ("koyu: (1,08)" + sups(MINUS_S + "(t+1)") + " ile iskonto edilmişi", 0.45, 51500)):
    p.add(f'<rect x="{p.X(97.15):.1f}" y="{p.Y(yy) - 8:.1f}" width="11" height="11" fill="{PRACTICE}" '
          f'fill-opacity="{op}" stroke="{PRACTICE}" stroke-width="1.1"/>')
    p.text_px(p.X(97.15) + 17, p.Y(yy) + 2, lab, PRACTICE, 10, "start", True)
OUT["ornek-61-sigorta"] = figure(
    450, 230, [p],
    "95 yaşındaki bir erkeğin ömür boyu sigortasında toplam beş terim vardır, çünkü 100 yaşına "
    "kimse erişmez. Ölüm sayıları önce iskonto edilir (koyu sütunlar), sonra &#8467;<sub>95</sub> "
    "= 146.721&#8217;e bölünür: sonuç, 1 TL&#8217;lik teminatın net tek primidir.",
    aria="Ornek 6.1: omur boyu hayat sigortasinin bes terimi")

# ############################################################################
# PART 7 — Hisse senetleri ve portföy (bölüm 21–24)
# ############################################################################

def ss_panel(y0, mean, sd, k, inner, outer, title):
    """A number line showing the mean ± k·SS band and the tail probabilities."""
    lo, hi = mean - 3.6 * sd, mean + 3.6 * sd
    q = Plot(40, y0, 400, 40, (lo, hi), (-1, 1))
    def num(v):
        return f"{v:,.2f}".replace(".", ",").replace("-", MINUS_S)
    tline(q, 0, [mean - k * sd, mean, mean + k * sd],
          [num(mean - k * sd), str(mean), num(mean + k * sd)], arrow=False, size=10)
    q.polygon([(mean - k * sd, -0.32), (mean + k * sd, -0.32), (mean + k * sd, 0.32), (mean - k * sd, 0.32)],
              THEORY, 0.13)
    q.text_px(q.X(mean), q.Y(0) - 12, inner, THEORY, 11, "middle", True)
    q.text_px(q.X(lo + 0.55 * sd), q.Y(0) - 12, outer, PRACTICE, 11, "middle", True)
    q.text_px(q.X(hi - 0.55 * sd), q.Y(0) - 12, outer, PRACTICE, 11, "middle", True)
    q.text_px(q.X(lo), q.Y(0) - 34, title, TEXT, 10.5, "start", True)
    return q


OUT["standart-sapma-bantlari"] = figure(
    460, 230,
    [ss_panel(46, 10, 15.35, 1, "2/3", "1/6", "1 standart sapma: getirinin bu aralıkta kalma şansı 2/3"),
     ss_panel(126, 10, 15.35, 2, "21/22", "1/44", "2 standart sapma: bu aralıkta kalma şansı 21/22"),
     ss_panel(206, 10, 15.35, 3, "738/740", "1/740", "3 standart sapma: bu aralıkta kalma şansı 738/740")],
    "Ortalaması 10, standart sapması 15,35 olan bir hisse. Bant genişledikçe içine düşme şansı "
    "artar, dışına taşma şansı hızla küçülür: sol taraftaki kuyruk, &#8220;bu kadardan fazla "
    "kaybetme&#8221; olasılığıdır &#8212; sırasıyla 1/6, 1/44 ve 1/740.",
    aria="Ortalama etrafinda bir, iki ve uc standart sapmalik bantlar", css_class=WIDE)

# --- Örnek 7.8: Arçelik ------------------------------------------------------
p2 = Plot(40, 50, 400, 44, (183 - 3.6 * 240.93, 183 + 3.6 * 240.93), (-1, 1))
tline(p2, 0, [183 - 3 * 240.93, 183 - 2 * 240.93, 183 - 240.93, 183, 183 + 240.93, 183 + 2 * 240.93, 183 + 3 * 240.93],
      ["&#8722;539,79", "&#8722;298,86", "&#8722;57,93", "183", "423,93", "664,86", "905,79"], arrow=False, size=9.5)
for k, col in ((1, THEORY), (2, BASE), (3, PRACTICE)):
    p2.add(f'<line x1="{p2.X(183 - k * 240.93):.1f}" y1="{p2.Y(0) - 12 - 13 * k:.1f}" '
           f'x2="{p2.X(183 + k * 240.93):.1f}" y2="{p2.Y(0) - 12 - 13 * k:.1f}" stroke="{col}" stroke-width="1.4"/>')
    p2.text_px(p2.X(183), p2.Y(0) - 16 - 13 * k, f"{k} SS", col, 9.5, "middle", True)
p2.points([(183, 0)], TEXT, 4.0)
OUT["ornek-78-arcelik"] = figure(
    460, 160, [p2],
    "Arçelik hissesinin ortalama yıllık getirisi %183, riski (standart sapması) %240,93. Bantlar "
    "çok geniştir: gelecek yıl %57,93&#8217;ten fazla kaybetme şansı 1/6, %298,86&#8217;dan fazla "
    "kaybetme şansı 1/44&#8217;tür.",
    aria="Arcelik hissesinin ortalama getirisi etrafindaki standart sapma bantlari")

# --- Risk - getiri grafikleri ------------------------------------------------
def risk_return(y0, pts, xrange, yrange, xt, yt, labels=None, w=330, h=140, x0=70):
    q = Plot(x0, y0, w, h, xrange, yrange)
    q.axes(xt, yt, "RİSK (SS)", "GETİRİ")
    q.grid(xt, yt)
    q.line(pts, THEORY, 1.8)
    q.points(pts, PRACTICE, 4.0)
    if labels:
        for (x, y), lab, dx, dy, anc in labels:
            q.label(x, y, lab, dx, dy, TEXT, 9.5, anc)
    return q


pts79 = [(5.77, 5), (7.22, 6), (11.92, 8), (17.38, 9), (23.09, 10)]
OUT["risk-getiri-79"] = figure(
    450, 220,
    [risk_return(38, pts79, (4, 25), (4, 11), range(5, 26, 5), range(4, 12, 2),
                 [(pts79[0], "%100 B", 6, 12, "start"), (pts79[4], "%100 A", -6, -8, "end"),
                  (pts79[2], "%50 A + %50 B", 4, -8, "start")])],
    "Örnek 7.9&#8217;un beş portföyü. A hissesinin payı arttıkça hem getiri hem risk büyüyor: bu "
    "iki hisse arasında &#8220;bedava öğle yemeği&#8221; yok, daha yüksek getiri ancak daha çok "
    "risk alarak elde ediliyor.",
    aria="Ornek 7.9 portfoylerinin risk getiri grafigi")

pts710 = [(68.74, 60), (60.96, 59), (57.00, 59), (57.63, 58), (62.72, 57), (71.33, 57),
          (82.35, 56), (94.95, 56), (108.59, 55), (122.91, 54), (137.70, 54)]
OUT["risk-getiri-710"] = figure(
    450, 220,
    [risk_return(38, pts710, (50, 145), (53, 61), range(60, 141, 20), range(54, 61, 2),
                 [(pts710[0], "%100 A", -6, -8, "end"), (pts710[2], "%80 A + %20 B  (en az riskli)", 8, 24, "start"),
                  (pts710[10], "%100 B", -6, -8, "end")])],
    "Örnek 7.10&#8217;un portföyleri geriye kıvrılan bir eğri çiziyor. Sol uçtaki %80A + %20B "
    "portföyü, tek başına A&#8217;dan da B&#8217;den de <strong>daha az risklidir</strong> &#8212; "
    "çeşitlendirmenin sağladığı kazanç budur. Eğrinin alt kolundaki portföyler ise hem daha riskli "
    "hem daha az getirilidir; kimse onları seçmez.",
    aria="Ornek 7.10 portfoylerinin risk getiri grafigi ve en az riskli portfoy")

# --- Örnek 7.11: on beş portföyün dağılımı ----------------------------------
pts711 = [(3.09, 20, "%100A"), (9.45, 24, ""), (13.41, 21, ""), (18.13, 28, ""), (18.94, 25, ""),
          (24.89, 22, ""), (26.98, 32, "%25A+%75B"), (26.40, 29, ""), (29.95, 26, ""),
          (36.45, 23, ""), (35.87, 36, "%100B"), (34.57, 33, ""), (36.53, 30, ""),
          (41.29, 27, ""), (48.03, 24, "%100C")]
p = Plot(70, 40, 330, 146, (0, 52), (17, 39))
p.axes(range(0, 51, 10), range(18, 39, 4), "RİSK (SS)", "GETİRİ")
p.grid(range(0, 51, 10), range(18, 39, 4))
p.add(f'<rect x="{p.X(0):.1f}" y="{p.Y(39):.1f}" width="{p.X(30) - p.X(0):.1f}" '
      f'height="{p.Y(17) - p.Y(39):.1f}" fill="{BASE}" fill-opacity="0.07" stroke="{BASE}" '
      f'stroke-width="1" stroke-dasharray="4 3"/>')
p.text_px(p.X(29), p.Y(18.4), "risk &#8804; %30", BASE, 10, "end")
for x, y, lab in pts711:
    p.points([(x, y)], PRACTICE, 4.0)
    if lab:
        p.label(x, y, lab, 7, -7, TEXT, 9.5, "start", True)
OUT["risk-getiri-711"] = figure(
    450, 220, [p],
    "Örnek 7.11&#8217;in on beş portföyü artık bir eğri değil bir <strong>bulut</strong> oluşturuyor. "
    "Yatırımcı bu bulutun sol-üst sınırındaki noktalarla ilgilenir: aynı riske karşılık en yüksek "
    "getiriyi verenler. Taralı bölge, %30&#8217;u aşmayan risk sınırını gösterir.",
    aria="Ornek 7.11 portfoylerinin risk getiri dagilimi")

# --- Çeşitlendirme -----------------------------------------------------------
p = Plot(64, 38, 340, 140, (0, 50), (0, 105))
p.axes(range(0, 51, 10), range(0, 101, 20), "portföydeki hisse sayısı", "risk (%)")
p.grid(range(0, 51, 10), range(0, 101, 20))
p.line([(n, 15 + 85 / n) for n in range(1, 51)], THEORY, 2.2)
p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(15):.1f}" x2="{p.X(50):.1f}" y2="{p.Y(15):.1f}" '
      f'stroke="{PRACTICE}" stroke-width="1.3" stroke-dasharray="5 4"/>')
p.text_px(p.X(26), p.Y(15) + 16, "piyasa riski: çeşitlendirme ile yok edilemez", PRACTICE, 10, "middle")
p.vline(15, 0, 15 + 85 / 15, BASE, "4 3", 0.7)
p.points([(15, 15 + 85 / 15)], BASE, 4.2)
p.label(15, 15 + 85 / 15, "15 hisseden sonra kazanç çok azalır", 8, -8, BASE, 10, "start", True)
OUT["cesitlendirme"] = figure(
    450, 220, [p],
    "Portföye yeni hisse eklendikçe risk düşer, ama düşüş hızla yavaşlar ve bir tabana dayanır: "
    "hisselere özgü riskler birbirini götürebilir, piyasanın tamamını etkileyen risk götüremez. "
    "Bu yüzden 15&#8211;20 hisseden sonra yeni hisse eklemenin faydası küçüktür.",
    aria="Hisse sayisi arttikca portfoy riskinin azalisi ve piyasa riski tabani")

# --- Alıştırma 7.6 grafikleri -----------------------------------------------
pa = [(6.48, -3), (2.79, 0), (1.26, 3), (4.83, 6), (8.54, 9)]
OUT["alistirma-761-risk-getiri"] = figure(
    450, 220,
    [risk_return(38, pa, (0, 10), (-4, 10), range(0, 11, 2), range(-4, 11, 2),
                 [(pa[0], "%100 B", 6, 12, "start"), (pa[4], "%100 A", -6, -8, "end"),
                  (pa[2], "%50 A + %50 B  (en az riskli)", 6, 12, "start")])],
    "Alıştırma 1&#8217;in portföyleri. En az riskli karışım uçlarda değil <strong>ortada</strong>: "
    "%50A + %50B portföyünün riski 1,26, oysa tek başına A&#8217;nın riski 8,54, B&#8217;nin 6,48.",
    aria="Alistirma 7.6-1 portfoylerinin risk getiri grafigi")

pb = [(11.09, 1), (8.00, 5), (7.18, 8), (9.28, 12), (12.91, 15)]
OUT["alistirma-762-risk-getiri"] = figure(
    450, 220,
    [risk_return(38, pb, (5, 14), (0, 16), range(6, 15, 2), range(0, 16, 5),
                 [(pb[0], "%100 B", 6, 12, "start"), (pb[4], "%100 A", -6, -8, "end"),
                  (pb[2], "%50 A + %50 B", 6, 12, "start")])],
    "Alıştırma 2&#8217;nin portföyleri. Burada da eğri geriye kıvrılıyor: %50A + %50B karışımı hem "
    "B&#8217;den daha az riskli hem de ondan çok daha yüksek getirili.",
    aria="Alistirma 7.6-2 portfoylerinin risk getiri grafigi")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "finance-%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated:", len(OUT), "figures:", ", ".join(OUT))
