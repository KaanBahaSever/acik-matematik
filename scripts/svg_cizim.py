# -*- coding: utf-8 -*-
"""Tema uyumlu, bagimliliksiz SVG cizim yardimcisi."""

TXT  = "var(--academic-text)"
THE  = "var(--color-theory)"
PRA  = "var(--color-practice)"
BAS  = "var(--color-base)"
REM  = "var(--color-remark)"

def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"

class Plot:
    """Tek bir kartezyen panel."""
    def __init__(self, x0, y0, w, h, xr, yr):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xmin, self.xmax = xr
        self.ymin, self.ymax = yr
        self.parts = []

    def X(self, x): return self.x0 + (x - self.xmin) / (self.xmax - self.xmin) * self.w
    def Y(self, y): return self.y0 + self.h - (y - self.ymin) / (self.ymax - self.ymin) * self.h

    def add(self, s): self.parts.append(s)

    def eksen(self, xticks, yticks, xlab="", ylab="", xfmt=fmt, yfmt=fmt):
        a = [f'<g stroke="{TXT}" stroke-width="1.1" opacity="0.45">',
             f'<line x1="{self.x0:.1f}" y1="{self.y0+self.h:.1f}" x2="{self.x0+self.w+8:.1f}" y2="{self.y0+self.h:.1f}"/>',
             f'<line x1="{self.x0:.1f}" y1="{self.y0-8:.1f}" x2="{self.x0:.1f}" y2="{self.y0+self.h:.1f}"/>',
             '</g>']
        a.append(f'<g fill="{TXT}" font-size="11" opacity="0.7">')
        for t in xticks:
            a.append(f'<text x="{self.X(t):.1f}" y="{self.y0+self.h+16:.1f}" text-anchor="middle">{xfmt(t)}</text>')
        for t in yticks:
            a.append(f'<text x="{self.x0-7:.1f}" y="{self.Y(t)+4:.1f}" text-anchor="end">{yfmt(t)}</text>')
        if xlab:
            a.append(f'<text x="{self.x0+self.w+14:.1f}" y="{self.y0+self.h+4:.1f}" font-style="italic">{xlab}</text>')
        if ylab:
            a.append(f'<text x="{self.x0-4:.1f}" y="{self.y0-14:.1f}" text-anchor="middle" font-style="italic">{ylab}</text>')
        a.append('</g>')
        self.add("\n  ".join(a))

    def izgara(self, xs=(), ys=()):
        a = [f'<g stroke="{TXT}" stroke-width="0.7" opacity="0.13">']
        for x in xs:
            a.append(f'<line x1="{self.X(x):.1f}" y1="{self.y0:.1f}" x2="{self.X(x):.1f}" y2="{self.y0+self.h:.1f}"/>')
        for y in ys:
            a.append(f'<line x1="{self.x0:.1f}" y1="{self.Y(y):.1f}" x2="{self.x0+self.w:.1f}" y2="{self.Y(y):.1f}"/>')
        a.append('</g>')
        self.add("".join(a))

    def cizgi(self, pts, renk=THE, gen=1.9, kesik=None, opak=1.0):
        d = " ".join(("M" if i == 0 else "L") + f"{self.X(x):.1f},{self.Y(y):.1f}" for i, (x, y) in enumerate(pts))
        da = f' stroke-dasharray="{kesik}"' if kesik else ""
        self.add(f'<path d="{d}" fill="none" stroke="{renk}" stroke-width="{gen}"{da} opacity="{opak}" stroke-linejoin="round" stroke-linecap="round"/>')

    def nokta(self, pts, renk=PRA, r=4.0):
        for x, y in pts:
            self.add(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{renk}"/>')

    def bosnokta(self, pts, renk=PRA, r=4.0):
        for x, y in pts:
            self.add(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="none" stroke="{renk}" stroke-width="1.8"/>')

    def cubuk(self, pts, renk=THE, gen=7, opak=0.85):
        for x, y in pts:
            X, Y0, Y1 = self.X(x), self.Y(0), self.Y(y)
            self.add(f'<rect x="{X-gen/2:.1f}" y="{Y1:.1f}" width="{gen}" height="{Y0-Y1:.1f}" fill="{renk}" opacity="{opak}" rx="1.5"/>')

    def dikey(self, x, y1, y2, renk=TXT, kesik="4 3", opak=0.5):
        self.add(f'<line x1="{self.X(x):.1f}" y1="{self.Y(y1):.1f}" x2="{self.X(x):.1f}" y2="{self.Y(y2):.1f}" stroke="{renk}" stroke-width="1" stroke-dasharray="{kesik}" opacity="{opak}"/>')

    def yazi(self, x, y, s, renk=TXT, boyut=11.5, hiza="start", kalin=False, egik=False):
        st = f' font-weight="600"' if kalin else ""
        it = f' font-style="italic"' if egik else ""
        self.add(f'<text x="{self.X(x):.1f}" y="{self.Y(y):.1f}" fill="{renk}" font-size="{boyut}" text-anchor="{hiza}"{st}{it}>{s}</text>')

    def yazi_px(self, px, py, s, renk=TXT, boyut=11.5, hiza="start", kalin=False, egik=False):
        st = f' font-weight="600"' if kalin else ""
        it = f' font-style="italic"' if egik else ""
        self.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{renk}" font-size="{boyut}" text-anchor="{hiza}"{st}{it}>{s}</text>')

    def svg(self): return "\n  ".join(self.parts)


def figur(W, H, paneller, baslik_alt, sinif="ders-grafik", aria=""):
    icerik = "\n  ".join(p.svg() for p in paneller)
    return (f'```{{=html}}\n'
            f'<figure class="{sinif}">\n'
            f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{aria}">\n  '
            f'{icerik}\n</svg>\n'
            f'<figcaption>{baslik_alt}</figcaption>\n</figure>\n```\n')
