// Interactive scene helpers for the "İntegral Calculus" book.
//
// The chapters embed Observable JS cells that import these helpers. The code
// runs in the reader's browser only: nothing is executed when the book is
// built, and every scene is wrapped in `content-visible when-format="html:js"`
// so the PDF and EPUB exports keep the static SVG figures instead.
//
// The module starts from the diferansiyel-geometri helpers (same theme,
// layout, curve, arrow, surface and render API) and adds what multiple
// integrals and vector calculus need: graphs over rectangles and over type I,
// type II and polar regions, Riemann columns, slicing planes, curtains,
// vector fields in space and in the plane, direction marks on curves,
// iso-parameter curves on parametric surfaces and a small set of 2D helpers.
//
// Plotly is loaded once per page with OJS `require(PLOTLY)` and passed in, so
// this module makes no network request of its own. Colors come from the
// site's CSS custom properties and are re-read whenever the reader toggles
// the light/dark theme (Quarto flips the `quarto-dark` class on <body>).
//
// Conventions: points and vectors are arrays ([x, y, z] in space, [x, y] in
// the plane); a bound such as g1, g2, r1, r2 or a curtain height may be a
// number or a function; builders that need more than one Plotly trace return
// an array, so spread them into the trace list (`...columns(...)`).

export const PLOTLY = "plotly.js-dist-min@2.35.2";

const CONFIG_3D = {
  responsive: true,
  displaylogo: false,
  scrollZoom: false, // the page must keep scrolling when the wheel passes over a scene
  modeBarButtonsToRemove: ["toImage", "resetCameraLastSave3d", "hoverClosest3d"],
};

// 2D panels are pictures driven by the controls: no zoom, pan or mode bar, so
// a finger on a phone scrolls the page instead of panning the plot.
const CONFIG_2D = { responsive: true, staticPlot: true };

// ---------------------------------------------------------------------------
// theme and formatting
// ---------------------------------------------------------------------------
export function readTheme() {
  const style = getComputedStyle(document.body);
  const dark = document.body.classList.contains("quarto-dark");
  const read = (name, fallback) => (style.getPropertyValue(name) || "").trim() || fallback;
  return {
    dark,
    text: read("--academic-text", dark ? "#E6E1DA" : "#2C2A27"),
    background: read("--academic-bg", dark ? "#1E1D1B" : "#FAF6EE"),
    theory: read("--color-theory", dark ? "#8AB4F8" : "#2B4C7E"),
    practice: read("--color-practice", dark ? "#E8A088" : "#9C3F1E"),
    base: read("--color-base", dark ? "#4DB6AC" : "#0D6E6A"),
    remark: read("--color-remark", dark ? "#A89F91" : "#5C5346"),
    grid: dark ? "rgba(230, 225, 218, 0.14)" : "rgba(44, 42, 39, 0.12)",
    axis: dark ? "rgba(230, 225, 218, 0.45)" : "rgba(44, 42, 39, 0.45)",
    surface: dark ? "rgba(230, 225, 218, 0.55)" : "rgba(44, 42, 39, 0.55)",
  };
}

// Use as `theme = Generators.observe(watchTheme)`: the value is re-emitted on
// every theme switch, so each scene redraws itself in the new palette.
export function watchTheme(notify) {
  notify(readTheme());
  const observer = new MutationObserver(() => notify(readTheme()));
  observer.observe(document.body, { attributes: true, attributeFilter: ["class"] });
  return () => observer.disconnect();
}

// A theme color with transparency: withAlpha(theme.text, 0.5). Accepts #rgb,
// #rrggbb, rgb() and rgba(); anything else is returned unchanged.
export function withAlpha(color, alpha) {
  const value = (color || "").trim();
  const hex = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(value);
  if (hex) {
    const digits = hex[1].length === 3 ? [...hex[1]].map((c) => c + c).join("") : hex[1];
    const n = parseInt(digits, 16);
    return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
  }
  const rgb = /^rgba?\(([^)]+)\)$/i.exec(value);
  if (rgb) {
    const [r, g, b] = rgb[1].split(",").map((part) => part.trim());
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }
  return color;
}

function turkish(x, minDigits, maxDigits) {
  const value = Math.abs(x) < 0.5 * 10 ** -maxDigits ? 0 : x;
  return value
    .toLocaleString("tr-TR", { minimumFractionDigits: minDigits, maximumFractionDigits: maxDigits, useGrouping: false })
    .replace("-", "−");
}

// Turkish number formatting for the read-outs, fixed digits: 0.5 -> "0,50", -2 -> "−2,00".
export function fmt(x, digits = 2) {
  return turkish(x, digits, digits);
}

// Up to `digits` decimals with trailing zeros dropped, for values the text
// prints exactly: 34 -> "34", 41.5 -> "41,5", 48.015625 -> "48,015625".
export function fmtTrim(x, digits = 6) {
  return turkish(x, 0, digits);
}

// ---------------------------------------------------------------------------
// small vector tools
// ---------------------------------------------------------------------------
export const dot = (a, b) => a.reduce((sum, c, i) => sum + c * b[i], 0);
export const norm = (a) => Math.hypot(...a);
export const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];

// Numerical partial derivatives [r_u, r_v] of a parametric surface (u, v) -> [x, y, z]
// (central differences): tangent vectors, and cross(r_u, r_v) is a normal vector.
export function partials(f, u, v, h = 1e-5) {
  const a = f(u + h, v);
  const b = f(u - h, v);
  const c = f(u, v + h);
  const d = f(u, v - h);
  return [a.map((x, i) => (x - b[i]) / (2 * h)), c.map((x, i) => (x - d[i]) / (2 * h))];
}

const asFn = (value) => (typeof value === "function" ? value : () => value);
const spread = (a, b, count) =>
  count <= 1 ? [(a + b) / 2] : Array.from({ length: count }, (_, i) => a + ((b - a) * i) / (count - 1));

// ---------------------------------------------------------------------------
// layouts
// ---------------------------------------------------------------------------
const legendStyle = (theme) => ({
  orientation: "h",
  x: 0,
  y: 1,
  yanchor: "bottom",
  font: { size: 11, color: theme.text },
  bgcolor: "rgba(0,0,0,0)",
});

// A 3D scene. Options: x, y, z (axis ranges), eye (camera), legend (default
// true), aspectratio (e.g. { x: 1, y: 1, z: 0.8 } to squash a tall graph),
// aspectmode, revision, titles ({ x, y, z } axis titles).
export function sceneLayout(theme, options = {}) {
  const titles = options.titles ?? {};
  const axis = (title, range) => ({
    title: { text: title, font: { color: theme.text, size: 13 } },
    ...(range ? { range } : {}),
    color: theme.text,
    tickfont: { color: theme.text, size: 10 },
    gridcolor: theme.grid,
    zerolinecolor: theme.axis,
    showbackground: false,
    showspikes: false,
  });
  const legend = options.legend ?? true;
  // Plotly's "data" aspect mode sizes the box from the traces, not from the axis ranges, so a scene
  // with fixed ranges would be drawn distorted and change shape whenever a slider moves the data.
  // When all three ranges are fixed, keep the box proportional to them instead; an explicit
  // aspectratio (a squashed vertical axis, say) switches to manual mode.
  const spans = [options.x, options.y, options.z].map((range) => (range ? range[1] - range[0] : 0));
  const fixedBox = !options.aspectmode && !options.aspectratio && spans.every((span) => span > 0);
  const meanSpan = Math.cbrt(spans[0] * spans[1] * spans[2]);
  let aspect;
  if (fixedBox) {
    aspect = { aspectmode: "manual", aspectratio: { x: spans[0] / meanSpan, y: spans[1] / meanSpan, z: spans[2] / meanSpan } };
  } else if (options.aspectratio) {
    aspect = { aspectmode: options.aspectmode ?? "manual", aspectratio: options.aspectratio };
  } else {
    aspect = { aspectmode: options.aspectmode ?? "data" };
  }
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    font: { color: theme.text },
    separators: ",.", // decimal comma on the tick labels
    margin: { l: 0, r: 0, t: legend ? 30 : 0, b: 0 },
    showlegend: legend,
    legend: legendStyle(theme),
    // A constant uirevision keeps the reader's camera when a slider redraws the scene.
    uirevision: options.revision ?? "scene",
    scene: {
      ...aspect,
      xaxis: axis(titles.x ?? "x", options.x),
      yaxis: axis(titles.y ?? "y", options.y),
      zaxis: axis(titles.z ?? "z", options.z),
      camera: { eye: options.eye ?? { x: 1.55, y: 1.35, z: 0.85 } },
      dragmode: "turntable",
    },
  };
}

// A 2D panel. Options: x, y (axis ranges, give both), equal (default true:
// one unit is the same length on both axes, needed for arrows and circles),
// legend (default true), titles ({ x, y }), revision.
export function planeLayout(theme, options = {}) {
  const titles = options.titles ?? {};
  const equal = options.equal ?? true;
  const axis = (title, range) => ({
    title: { text: title, font: { color: theme.text, size: 13 }, standoff: 4 },
    ...(range ? { range, autorange: false } : {}),
    color: theme.text,
    tickfont: { color: theme.text, size: 10 },
    gridcolor: theme.grid,
    zerolinecolor: theme.axis,
    zerolinewidth: 1.2,
    showline: false,
    fixedrange: true,
    // With equal scales the plot area shrinks to fit instead of widening the requested ranges.
    ...(equal ? { constrain: "domain" } : {}),
  });
  const legend = options.legend ?? true;
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { color: theme.text },
    separators: ",.", // decimal comma on the tick labels
    margin: { l: 40, r: 10, t: legend ? 30 : 10, b: 36 },
    showlegend: legend,
    legend: legendStyle(theme),
    uirevision: options.revision ?? "plane",
    hovermode: false,
    dragmode: false,
    xaxis: axis(titles.x ?? "x", options.x),
    yaxis: { ...axis(titles.y ?? "y", options.y), ...(equal ? { scaleanchor: "x", scaleratio: 1 } : {}) },
  };
}

// ---------------------------------------------------------------------------
// 3D: points, curves, arrows
// ---------------------------------------------------------------------------
export function curve(f, t0, t1, samples = 240) {
  const x = [];
  const y = [];
  const z = [];
  for (let k = 0; k <= samples; k++) {
    const [a, b, c] = f(t0 + ((t1 - t0) * k) / samples);
    x.push(a);
    y.push(b);
    z.push(c);
  }
  return { x, y, z };
}

// A parametric space curve t -> f(t) drawn as a line.
export function path(f, t0, t1, color, name, options = {}) {
  return {
    type: "scatter3d",
    mode: "lines",
    ...curve(f, t0, t1, options.samples),
    line: { color, width: options.width ?? 6, dash: options.dash ?? "solid" },
    name,
    showlegend: options.legend ?? Boolean(name),
    hoverinfo: "skip",
  };
}

export function point(p, color, name, options = {}) {
  return {
    type: "scatter3d",
    mode: options.text ? "markers+text" : "markers",
    x: [p[0]],
    y: [p[1]],
    z: [p[2]],
    marker: { color, size: options.size ?? 5 },
    ...(options.text ? { text: [options.text], textposition: options.position ?? "top center" } : {}),
    textfont: { color, size: 12 },
    name,
    showlegend: options.legend ?? Boolean(name),
    hoverinfo: "skip",
  };
}

// Many points as one trace: sample points of a Riemann sum, grid nodes.
export function points(list, color, name, options = {}) {
  return {
    type: "scatter3d",
    mode: "markers",
    x: list.map((p) => p[0]),
    y: list.map((p) => p[1]),
    z: list.map((p) => p[2]),
    marker: { color, size: options.size ?? 3 },
    name,
    showlegend: options.legend ?? Boolean(name),
    hoverinfo: "skip",
  };
}

// Text in space. Keep the text constant while sliders move: WebGL text whose
// content changes on an update can be redrawn at half size, so changing values
// belong in the read-out line under the scene.
export function label(p, text, color, options = {}) {
  return {
    type: "scatter3d",
    mode: "text",
    x: [p[0]],
    y: [p[1]],
    z: [p[2]],
    text: [text],
    textposition: options.position ?? "top center",
    textfont: { color, size: options.size ?? 13 },
    showlegend: false,
    hoverinfo: "skip",
  };
}

// A straight segment from a to b, dashed by default: coordinate guides, secants.
export function segment(a, b, color, options = {}) {
  return {
    type: "scatter3d",
    mode: "lines",
    x: [a[0], b[0]],
    y: [a[1], b[1]],
    z: [a[2], b[2]],
    line: { color, width: options.width ?? 3, dash: options.dash ?? "dash" },
    name: options.name ?? "",
    showlegend: Boolean(options.name),
    hoverinfo: "skip",
  };
}

// A legend entry for a trace that has none of its own (surfaces, meshes): an
// invisible line of the given color that only shows up in the legend.
export function legendItem(name, color, options = {}) {
  return {
    type: "scatter3d",
    mode: "lines",
    x: [null],
    y: [null],
    z: [null],
    line: { color, width: options.width ?? 8 },
    name,
    showlegend: true,
    hoverinfo: "skip",
  };
}

// The vector v applied at p: a shaft from p plus a cone whose tip is exactly
// at p + v. Returns an array of traces; spread it into the trace list.
export function arrow(p, v, color, name, options = {}) {
  const length = Math.hypot(v[0], v[1], v[2]);
  if (length < 1e-9) return [point(p, color, name, { size: 4 })];
  const unit = v.map((c) => c / length);
  const head = Math.min(options.head ?? 0.3, 0.45 * length);
  const tip = [p[0] + v[0], p[1] + v[1], p[2] + v[2]];
  const base = tip.map((c, i) => c - unit[i] * head);
  return [
    {
      type: "scatter3d",
      mode: "lines",
      x: [p[0], base[0]],
      y: [p[1], base[1]],
      z: [p[2], base[2]],
      line: { color, width: options.width ?? 7 },
      name,
      showlegend: options.legend ?? Boolean(name),
      hoverinfo: "skip",
    },
    cones([base], [unit.map((c) => c * head)], color),
  ];
}

// Cone trace for arrow heads: each cone starts at bases[k] and is exactly as
// long as vectors[k] ("raw" size mode: no rescaling by Plotly). The scene
// should use true scale (equal units on the axes) or the heads are skewed.
function cones(bases, vectors, color) {
  return {
    type: "cone",
    x: bases.map((p) => p[0]),
    y: bases.map((p) => p[1]),
    z: bases.map((p) => p[2]),
    u: vectors.map((v) => v[0]),
    v: vectors.map((v) => v[1]),
    w: vectors.map((v) => v[2]),
    anchor: "tail",
    sizemode: "raw",
    sizeref: 1,
    colorscale: [
      [0, color],
      [1, color],
    ],
    showscale: false,
    showlegend: false,
    hoverinfo: "skip",
  };
}

// Direction marks on a space curve t -> f(t): `count` cones centered on the
// curve at evenly spaced parameters, pointing the way t increases. Options:
// size (cone length; default 6% of the curve's bounding-box diagonal).
export function arrowHeads3d(f, t0, t1, count, color, options = {}) {
  const sample = curve(f, t0, t1, 120);
  const diagonal = Math.hypot(
    ...["x", "y", "z"].map((key) => Math.max(...sample[key]) - Math.min(...sample[key])),
  );
  const size = options.size ?? 0.06 * (diagonal || 1);
  const h = (t1 - t0) * 1e-4;
  const bases = [];
  const vectors = [];
  for (let k = 0; k < count; k++) {
    const t = t0 + ((t1 - t0) * (k + 0.5)) / count;
    const p = f(t);
    const d = f(t + h).map((c, i) => c - f(t - h)[i]);
    const length = norm(d);
    if (length < 1e-12) continue;
    const step = d.map((c) => (c / length) * size);
    bases.push(p.map((c, i) => c - step[i] / 2));
    vectors.push(step);
  }
  return cones(bases, vectors, color);
}

// ---------------------------------------------------------------------------
// 3D: surfaces
// ---------------------------------------------------------------------------
// Options shared by every surface builder: opacity (default 0.18); colors:
// [low, high] shades the surface by height instead of one flat color (cmin,
// cmax fix the scale); trace: extra Plotly attributes merged in last.
function surfaceTrace(x, y, z, color, options) {
  let surfacecolor = z.map((row) => row.map(() => 0));
  let colorscale = [
    [0, color],
    [1, color],
  ];
  let cmin = 0;
  let cmax = 1;
  if (options.colors) {
    surfacecolor = z;
    colorscale = [
      [0, options.colors[0]],
      [1, options.colors[1]],
    ];
    const heights = z.flat().filter(Number.isFinite);
    cmin = options.cmin ?? Math.min(...heights);
    cmax = options.cmax ?? Math.max(...heights);
    if (cmax - cmin < 1e-12) cmax = cmin + 1;
  }
  return {
    type: "surface",
    x,
    y,
    z,
    surfacecolor,
    colorscale,
    cmin,
    cmax,
    showscale: false,
    opacity: options.opacity ?? 0.18,
    lighting: { ambient: 0.9, diffuse: 0.35, specular: 0.05 },
    hoverinfo: "skip",
    showlegend: false,
    ...(options.trace ?? {}),
  };
}

// A parametric surface (u, v) -> f(u, v) on [u0, u1] x [v0, v1]; nu, nv set
// the mesh (default 40 x 40).
export function surface(f, u0, u1, v0, v1, color, options = {}) {
  const nu = options.nu ?? 40;
  const nv = options.nv ?? 40;
  const x = [];
  const y = [];
  const z = [];
  for (let i = 0; i <= nu; i++) {
    const u = u0 + ((u1 - u0) * i) / nu;
    const rowX = [];
    const rowY = [];
    const rowZ = [];
    for (let j = 0; j <= nv; j++) {
      const [a, b, c] = f(u, v0 + ((v1 - v0) * j) / nv);
      rowX.push(a);
      rowY.push(b);
      rowZ.push(c);
    }
    x.push(rowX);
    y.push(rowY);
    z.push(rowZ);
  }
  return surfaceTrace(x, y, z, color, options);
}

// The graph z = f(x, y) over the rectangle [x0, x1] x [y0, y1] (mesh nx x ny, default 32 x 32).
export function graph(f, x0, x1, y0, y1, color, options = {}) {
  return surface((x, y) => [x, y, f(x, y)], x0, x1, y0, y1, color, {
    nu: options.nx ?? 32,
    nv: options.ny ?? 32,
    ...options,
  });
}

// The graph z = f(x, y) over the type I region a <= x <= b, g1(x) <= y <= g2(x).
// With f = () => 0 (or any constant) it draws the region itself as a flat patch.
export function graphTypeI(f, a, b, g1, g2, color, options = {}) {
  const lower = asFn(g1);
  const upper = asFn(g2);
  return surface(
    (x, s) => {
      const y = lower(x) + s * (upper(x) - lower(x));
      return [x, y, f(x, y)];
    },
    a,
    b,
    0,
    1,
    color,
    { nu: options.nx ?? 40, nv: options.ny ?? 24, ...options },
  );
}

// The graph z = f(x, y) over the type II region c <= y <= d, h1(y) <= x <= h2(y).
export function graphTypeII(f, c, d, h1, h2, color, options = {}) {
  const left = asFn(h1);
  const right = asFn(h2);
  return surface(
    (y, s) => {
      const x = left(y) + s * (right(y) - left(y));
      return [x, y, f(x, y)];
    },
    c,
    d,
    0,
    1,
    color,
    { nu: options.ny ?? 40, nv: options.nx ?? 24, ...options },
  );
}

// The graph z = f(x, y) over the polar region t0 <= theta <= t1, r1(theta) <= r <= r2(theta).
// f still takes Cartesian (x, y).
export function graphPolar(f, t0, t1, r1, r2, color, options = {}) {
  const inner = asFn(r1);
  const outer = asFn(r2);
  return surface(
    (theta, s) => {
      const r = inner(theta) + s * (outer(theta) - inner(theta));
      const x = r * Math.cos(theta);
      const y = r * Math.sin(theta);
      return [x, y, f(x, y)];
    },
    t0,
    t1,
    0,
    1,
    color,
    { nu: options.nt ?? 48, nv: options.nr ?? 20, ...options },
  );
}

// The cylinder (x - cx)^2 + (y - cy)^2 = r^2 between heights z0 and z1.
export function cylinder(radius, z0, z1, color, options = {}) {
  const cx = options.cx ?? 0;
  const cy = options.cy ?? 0;
  return surface(
    (theta, height) => [cx + radius * Math.cos(theta), cy + radius * Math.sin(theta), height],
    0,
    2 * Math.PI,
    z0,
    z1,
    color,
    { nu: 48, nv: 2, ...options },
  );
}

// The vertical "curtain" over the plane curve t -> [x(t), y(t)], t0 <= t <= t1,
// between the heights low(x, y) and high(x, y) (functions or numbers): the
// cross-section under a graph along a line, the wall of a solid, or the
// sheet between a curve in the xy-plane and the surface above it (a line
// integral with respect to arc length). Options: samples (default 80).
export function curtain(planeCurve, t0, t1, low, high, color, options = {}) {
  const bottom = asFn(low);
  const top = asFn(high);
  return surface(
    (t, s) => {
      const [x, y] = planeCurve(t);
      const z0 = bottom(x, y);
      return [x, y, z0 + s * (top(x, y) - z0)];
    },
    t0,
    t1,
    0,
    1,
    color,
    { nu: options.samples ?? 80, nv: 1, ...options },
  );
}

// Iso-parameter curves of a parametric surface f(u, v) as one line trace:
// ku + 1 curves u = const and kv + 1 curves v = const (0 skips a family).
// Highlight a single curve with path(u => f(u, v*), ...) on top.
export function gridCurves(f, u0, u1, v0, v1, ku, kv, color, options = {}) {
  const samples = options.samples ?? 48;
  const x = [];
  const y = [];
  const z = [];
  const add = (g) => {
    for (let k = 0; k <= samples; k++) {
      const p = g(k / samples);
      x.push(p[0]);
      y.push(p[1]);
      z.push(p[2]);
    }
    x.push(null);
    y.push(null);
    z.push(null);
  };
  for (let i = 0; ku > 0 && i <= ku; i++) {
    const u = u0 + ((u1 - u0) * i) / ku;
    add((s) => f(u, v0 + (v1 - v0) * s));
  }
  for (let j = 0; kv > 0 && j <= kv; j++) {
    const v = v0 + ((v1 - v0) * j) / kv;
    add((s) => f(u0 + (u1 - u0) * s, v));
  }
  return {
    type: "scatter3d",
    mode: "lines",
    x,
    y,
    z,
    line: { color, width: options.width ?? 2 },
    name: options.name,
    showlegend: Boolean(options.name),
    hoverinfo: "skip",
  };
}

// A flat quadrilateral p0 p1 p2 p3 (in order around the edge) as a mesh.
export function quad(p0, p1, p2, p3, color, options = {}) {
  const corners = [p0, p1, p2, p3];
  return {
    type: "mesh3d",
    x: corners.map((p) => p[0]),
    y: corners.map((p) => p[1]),
    z: corners.map((p) => p[2]),
    i: [0, 0],
    j: [1, 2],
    k: [2, 3],
    color,
    opacity: options.opacity ?? 0.25,
    flatshading: true,
    lighting: { ambient: 1, diffuse: 0, specular: 0 },
    hoverinfo: "skip",
    showlegend: false,
    showscale: false,
  };
}

// A slicing plane: axis "x" draws x = value over y in u and z in v; "y" draws
// y = value over x in u and z in v; "z" draws z = value over x in u and y in v.
// Returns [fill, outline]. Options: opacity (fill, default 0.25), width, name.
export function slicePlane(axis, value, u, v, color, options = {}) {
  const place = (a, b) => (axis === "x" ? [value, a, b] : axis === "y" ? [a, value, b] : [a, b, value]);
  const corners = [place(u[0], v[0]), place(u[1], v[0]), place(u[1], v[1]), place(u[0], v[1])];
  const ring = [...corners, corners[0]];
  return [
    quad(...corners, color, options),
    {
      type: "scatter3d",
      mode: "lines",
      x: ring.map((p) => p[0]),
      y: ring.map((p) => p[1]),
      z: ring.map((p) => p[2]),
      line: { color, width: options.width ?? 3 },
      name: options.name,
      showlegend: Boolean(options.name),
      hoverinfo: "skip",
    },
  ];
}

// ---------------------------------------------------------------------------
// 3D: Riemann columns
// ---------------------------------------------------------------------------
// A column cell is the solid between heights z0 and z1 over a plane cell
// bounded by two rails a and b (polylines with the same number of points):
// a rectangle has two-point rails, a polar rectangle has two arcs.
export function rectCell(x0, x1, y0, y1, z0, z1) {
  return {
    a: [
      [x0, y0],
      [x1, y0],
    ],
    b: [
      [x0, y1],
      [x1, y1],
    ],
    z0,
    z1,
  };
}

// The column over the polar rectangle r0 <= r <= r1, t0 <= theta <= t1.
export function polarCell(r0, r1, t0, t1, z0, z1, samples = 8) {
  const a = [];
  const b = [];
  for (let k = 0; k <= samples; k++) {
    const t = t0 + ((t1 - t0) * k) / samples;
    a.push([r0 * Math.cos(t), r0 * Math.sin(t)]);
    b.push([r1 * Math.cos(t), r1 * Math.sin(t)]);
  }
  return { a, b, z0, z1 };
}

// All cells as one mesh plus one trace of edges: [mesh, edges]. Options:
// opacity (default 1; opaque boxes under a translucent surface read best),
// edges (default true), edgeColor (default the fill color), edgeWidth (2),
// name (legend entry, carried by the edge trace), inset (default 0.006).
// WebGL draws a line lying exactly on a face only in patches (depth
// fighting), so the mesh of each cell is shrunk by the `inset` fraction
// toward its center and the edges stay on the true outline, just outside it.
export function columns(cells, color, options = {}) {
  if (!cells.length) return [];
  const inset = options.inset ?? 0.006;
  const x = [];
  const y = [];
  const z = [];
  const I = [];
  const J = [];
  const K = [];
  const ex = [];
  const ey = [];
  const ez = [];
  const quadFace = (p, q, r, s) => {
    I.push(p, p);
    J.push(q, r);
    K.push(r, s);
  };
  const line = (list, heights) => {
    list.forEach(([px, py], k) => {
      ex.push(px);
      ey.push(py);
      ez.push(heights[k]);
    });
    ex.push(null);
    ey.push(null);
    ez.push(null);
  };
  for (const { a, b, z0, z1 } of cells) {
    const n = a.length;
    const start = x.length;
    const all = [...a, ...b];
    const cx = all.reduce((sum, p) => sum + p[0], 0) / all.length;
    const cy = all.reduce((sum, p) => sum + p[1], 0) / all.length;
    const lift = inset * (z1 - z0);
    // vertex blocks: bottom of rail a, bottom of rail b, top of rail a, top of rail b
    for (const [height, rail] of [
      [z0 + lift, a],
      [z0 + lift, b],
      [z1 - lift, a],
      [z1 - lift, b],
    ]) {
      for (const [px, py] of rail) {
        x.push(cx + (px - cx) * (1 - inset));
        y.push(cy + (py - cy) * (1 - inset));
        z.push(height);
      }
    }
    const a0 = start;
    const b0 = start + n;
    const a1 = start + 2 * n;
    const b1 = start + 3 * n;
    for (let s = 0; s < n - 1; s++) {
      quadFace(a0 + s, a0 + s + 1, b0 + s + 1, b0 + s); // floor
      quadFace(a1 + s, a1 + s + 1, b1 + s + 1, b1 + s); // top
      quadFace(a0 + s, a0 + s + 1, a1 + s + 1, a1 + s); // wall along rail a
      quadFace(b0 + s, b0 + s + 1, b1 + s + 1, b1 + s); // wall along rail b
    }
    quadFace(a0, b0, b1, a1); // end wall at the first points
    quadFace(a0 + n - 1, b0 + n - 1, b1 + n - 1, a1 + n - 1); // end wall at the last points
    if (options.edges !== false) {
      const ring = [...a, ...[...b].reverse(), a[0]];
      line(ring, ring.map(() => z0));
      line(ring, ring.map(() => z1));
      for (const corner of [a[0], a[n - 1], b[0], b[n - 1]]) line([corner, corner], [z0, z1]);
    }
  }
  const group = options.name ?? "columns";
  const traces = [
    {
      type: "mesh3d",
      x,
      y,
      z,
      i: I,
      j: J,
      k: K,
      color,
      opacity: options.opacity ?? 1,
      flatshading: true,
      lighting: { ambient: 0.7, diffuse: 0.55, specular: 0.05, roughness: 0.9, fresnel: 0.1 },
      hoverinfo: "skip",
      showlegend: false,
      showscale: false,
      legendgroup: group,
    },
  ];
  if (options.edges !== false) {
    traces.push({
      type: "scatter3d",
      mode: "lines",
      x: ex,
      y: ey,
      z: ez,
      line: { color: options.edgeColor ?? color, width: options.edgeWidth ?? 2 },
      name: options.name,
      showlegend: Boolean(options.name),
      legendgroup: group,
      hoverinfo: "skip",
    });
  }
  return traces;
}

// Boxes from [x0, x1, y0, y1, z0, z1] lists (solid pieces of a triple
// integral, a single column): the same [mesh, edges] as columns().
export function boxes(list, color, options = {}) {
  return columns(list.map((b) => rectCell(...b)), color, options);
}

// Where the sample point sits in its cell, as fractions of the two sides
// (x then y for rectangles, r then theta for polar cells).
export const SAMPLE_RULES = {
  "upper-right": [1, 1],
  "upper-left": [0, 1],
  "lower-left": [0, 0],
  "lower-right": [1, 0],
  midpoint: [0.5, 0.5],
};

// The double Riemann sum of f over [x0, x1] x [y0, y1] with an m x n grid.
// rule: a SAMPLE_RULES key or a pair [s, t]. Returns { cells (columns from
// z = 0 to the sampled value), samples ([x*, y*, f]), sum, dA, dx, dy }.
export function riemannRect(f, x0, x1, y0, y1, m, n, rule = "midpoint") {
  const [s, t] = Array.isArray(rule) ? rule : SAMPLE_RULES[rule];
  const dx = (x1 - x0) / m;
  const dy = (y1 - y0) / n;
  const cells = [];
  const samples = [];
  let total = 0;
  for (let i = 0; i < m; i++) {
    for (let j = 0; j < n; j++) {
      const xs = x0 + (i + s) * dx;
      const ys = y0 + (j + t) * dy;
      const h = f(xs, ys);
      total += h;
      cells.push(rectCell(x0 + i * dx, x0 + (i + 1) * dx, y0 + j * dy, y0 + (j + 1) * dy, 0, h));
      samples.push([xs, ys, h]);
    }
  }
  return { cells, samples, sum: total * dx * dy, dA: dx * dy, dx, dy };
}

// The polar Riemann sum of f(x, y) over r0 <= r <= r1, t0 <= theta <= t1 with
// m radial and n angular pieces: the sum of f(r* cos theta*, r* sin theta*)
// times the cell area rbar dr dtheta (rbar the middle radius; for the midpoint
// rule r* = rbar, the form used in the text). Same return shape as riemannRect,
// plus dr and dt.
export function riemannPolar(f, r0, r1, t0, t1, m, n, rule = "midpoint") {
  const [s, t] = Array.isArray(rule) ? rule : SAMPLE_RULES[rule];
  const dr = (r1 - r0) / m;
  const dt = (t1 - t0) / n;
  const cells = [];
  const samples = [];
  let sum = 0;
  for (let i = 0; i < m; i++) {
    for (let j = 0; j < n; j++) {
      const ra = r0 + i * dr;
      const ta = t0 + j * dt;
      const rs = ra + s * dr;
      const ts = ta + t * dt;
      const xs = rs * Math.cos(ts);
      const ys = rs * Math.sin(ts);
      const h = f(xs, ys);
      sum += h * (ra + dr / 2) * dr * dt;
      cells.push(polarCell(ra, ra + dr, ta, ta + dt, 0, h, Math.max(2, Math.ceil(24 / n))));
      samples.push([xs, ys, h]);
    }
  }
  return { cells, samples, sum, dr, dt };
}

// ---------------------------------------------------------------------------
// 3D: vector fields
// ---------------------------------------------------------------------------
// Sparse arrows of F(x, y, z) -> [P, Q, R] at a grid of counts = [nx, ny, nz]
// (or one number) points over the ranges xr, yr, zr. The longest arrow is
// drawn `fill` (default 0.8) of the grid spacing unless `scale` (drawn length
// per unit of |F|) is given; normalize: true draws every arrow the same
// length (direction only). Returns [shafts, heads]. Keep it under ~150 arrows.
export function field3d(F, xr, yr, zr, counts, color, options = {}) {
  const [nx, ny, nz] = typeof counts === "number" ? [counts, counts, counts] : counts;
  const grid = [];
  for (const x of spread(xr[0], xr[1], nx)) {
    for (const y of spread(yr[0], yr[1], ny)) {
      for (const z of spread(zr[0], zr[1], nz)) grid.push([x, y, z]);
    }
  }
  const steps = [
    [xr, nx],
    [yr, ny],
    [zr, nz],
  ]
    .filter(([, count]) => count > 1)
    .map(([range, count]) => (range[1] - range[0]) / (count - 1));
  const spacing = steps.length ? Math.min(...steps) : 1;
  return fieldArrows3d(grid, grid.map((p) => F(...p)), spacing, color, options);
}

function fieldArrows3d(starts, values, spacing, color, options) {
  const fill = options.fill ?? 0.8;
  const longest = Math.max(...values.map(norm), 1e-12);
  const scale = options.scale ?? (fill * spacing) / longest;
  const x = [];
  const y = [];
  const z = [];
  const bases = [];
  const heads = [];
  starts.forEach((p, k) => {
    const v = values[k];
    const length = norm(v);
    if (length < 1e-9) return;
    const drawn = options.normalize ? fill * spacing : length * scale;
    const unit = v.map((c) => c / length);
    const head = Math.min(options.head ?? 0.3 * fill * spacing, 0.45 * drawn);
    const base = p.map((c, i) => c + unit[i] * (drawn - head));
    x.push(p[0], base[0], null);
    y.push(p[1], base[1], null);
    z.push(p[2], base[2], null);
    bases.push(base);
    heads.push(unit.map((c) => c * head));
  });
  return [
    {
      type: "scatter3d",
      mode: "lines",
      x,
      y,
      z,
      line: { color, width: options.width ?? 4 },
      name: options.name,
      showlegend: Boolean(options.name),
      hoverinfo: "skip",
    },
    cones(bases, heads, color),
  ];
}

// Arrows of a field at chosen points (on a curve, on a surface): starts is a
// list of points, values the vectors there; drawn lengths are values * scale
// (default: longest = 1). Returns [shafts, heads].
export function arrowsAt(starts, values, color, options = {}) {
  const longest = Math.max(...values.map(norm), 1e-12);
  return fieldArrows3d(starts, values, 1, color, { scale: options.scale ?? 1 / longest, fill: 1, ...options });
}

// ---------------------------------------------------------------------------
// 2D panels (use with planeLayout)
// ---------------------------------------------------------------------------
const BARB = 0.45; // half-angle of a 2D arrowhead, radians

function barbs(tip, unit, head) {
  const back = [-unit[0], -unit[1]];
  const turn = (angle) => [
    tip[0] + head * (back[0] * Math.cos(angle) - back[1] * Math.sin(angle)),
    tip[1] + head * (back[0] * Math.sin(angle) + back[1] * Math.cos(angle)),
  ];
  return [turn(BARB), tip, turn(-BARB)];
}

function lines2d(polylines, color, options) {
  const x = [];
  const y = [];
  for (const list of polylines) {
    for (const p of list) {
      x.push(p[0]);
      y.push(p[1]);
    }
    x.push(null);
    y.push(null);
  }
  return {
    type: "scatter",
    mode: "lines",
    x,
    y,
    line: { color, width: options.width ?? 2, dash: options.dash ?? "solid" },
    name: options.name,
    showlegend: options.legend ?? Boolean(options.name),
    hoverinfo: "skip",
    cliponaxis: true,
  };
}

// A plane curve t -> [x(t), y(t)].
export function path2d(f, t0, t1, color, name, options = {}) {
  const samples = options.samples ?? 200;
  const list = [];
  for (let k = 0; k <= samples; k++) list.push(f(t0 + ((t1 - t0) * k) / samples));
  return lines2d([list], color, { width: 3, ...options, name });
}

// Direction marks on a plane curve: `count` arrowheads at evenly spaced
// parameters, pointing the way t increases. Options: size (default 4% of the
// curve's bounding-box diagonal), width.
export function arrowHeads2d(f, t0, t1, count, color, options = {}) {
  const sample = Array.from({ length: 121 }, (_, k) => f(t0 + ((t1 - t0) * k) / 120));
  const span = (i) => Math.max(...sample.map((p) => p[i])) - Math.min(...sample.map((p) => p[i]));
  const size = options.size ?? 0.04 * (Math.hypot(span(0), span(1)) || 1);
  const h = (t1 - t0) * 1e-4;
  const marks = [];
  for (let k = 0; k < count; k++) {
    const t = t0 + ((t1 - t0) * (k + 0.5)) / count;
    const a = f(t + h);
    const b = f(t - h);
    const d = [a[0] - b[0], a[1] - b[1]];
    const length = Math.hypot(d[0], d[1]);
    if (length < 1e-12) continue;
    const unit = [d[0] / length, d[1] / length];
    const p = f(t);
    marks.push(barbs([p[0] + (unit[0] * size) / 2, p[1] + (unit[1] * size) / 2], unit, size));
  }
  return lines2d(marks, color, { width: 3, ...options, name: undefined, legend: false });
}

// The vector v applied at p in the plane (shaft plus a two-stroke head).
export function arrow2d(p, v, color, name, options = {}) {
  const length = Math.hypot(v[0], v[1]);
  const tip = [p[0] + v[0], p[1] + v[1]];
  if (length < 1e-9) return point2d(p, color, name);
  const unit = [v[0] / length, v[1] / length];
  const head = Math.min(options.head ?? 0.25, 0.45 * length);
  return lines2d([[p, tip], barbs(tip, unit, head)], color, { width: 3, ...options, name });
}

// Sparse arrows of the plane field F(x, y) -> [P, Q] on an nx x ny grid over
// xr x yr; scaling as in field3d (fill, scale, normalize, head). One trace.
export function field2d(F, xr, yr, counts, color, options = {}) {
  const [nx, ny] = typeof counts === "number" ? [counts, counts] : counts;
  const grid = [];
  for (const x of spread(xr[0], xr[1], nx)) for (const y of spread(yr[0], yr[1], ny)) grid.push([x, y]);
  const steps = [
    [xr, nx],
    [yr, ny],
  ]
    .filter(([, count]) => count > 1)
    .map(([range, count]) => (range[1] - range[0]) / (count - 1));
  const spacing = steps.length ? Math.min(...steps) : 1;
  const values = grid.map((p) => F(...p));
  const fill = options.fill ?? 0.8;
  const longest = Math.max(...values.map(norm), 1e-12);
  const scale = options.scale ?? (fill * spacing) / longest;
  const polylines = [];
  grid.forEach((p, k) => {
    const v = values[k];
    const length = norm(v);
    if (length < 1e-9) return;
    const drawn = options.normalize ? fill * spacing : length * scale;
    const unit = [v[0] / length, v[1] / length];
    const tip = [p[0] + unit[0] * drawn, p[1] + unit[1] * drawn];
    const head = Math.min(options.head ?? 0.3 * fill * spacing, 0.45 * drawn);
    polylines.push([p, tip], barbs(tip, unit, head));
  });
  return lines2d(polylines, color, { width: 1.6, ...options });
}

export function point2d(p, color, name, options = {}) {
  return {
    type: "scatter",
    mode: options.text ? "markers+text" : "markers",
    x: [p[0]],
    y: [p[1]],
    marker: { color, size: options.size ?? 8 },
    ...(options.text ? { text: [options.text], textposition: options.position ?? "top center" } : {}),
    textfont: { color, size: 12 },
    name,
    showlegend: options.legend ?? Boolean(name),
    hoverinfo: "skip",
  };
}

export function label2d(p, text, color, options = {}) {
  return {
    type: "scatter",
    mode: "text",
    x: [p[0]],
    y: [p[1]],
    text: [text],
    textposition: options.position ?? "top center",
    textfont: { color, size: options.size ?? 13 },
    showlegend: false,
    hoverinfo: "skip",
  };
}

// A straight segment in the plane, dashed by default.
export function segment2d(a, b, color, options = {}) {
  return lines2d([[a, b]], color, { width: 1.5, dash: "dash", ...options });
}

// A filled polygon (closed automatically). Options: opacity of the fill
// (default 0.2), width of the outline (0 hides it), name.
export function fill2d(list, color, options = {}) {
  const ring = [...list, list[0]];
  return {
    type: "scatter",
    mode: "lines",
    x: ring.map((p) => p[0]),
    y: ring.map((p) => p[1]),
    fill: "toself",
    fillcolor: withAlpha(color, options.opacity ?? 0.2),
    line: { color, width: options.width ?? 1.5 },
    name: options.name,
    showlegend: Boolean(options.name),
    hoverinfo: "skip",
  };
}

const boundarySamples = 80;

// The type I region a <= x <= b, g1(x) <= y <= g2(x) as a filled polygon.
export function regionTypeI2d(a, b, g1, g2, color, options = {}) {
  const lower = asFn(g1);
  const upper = asFn(g2);
  const xs = spread(a, b, boundarySamples + 1);
  return fill2d([...xs.map((x) => [x, lower(x)]), ...[...xs].reverse().map((x) => [x, upper(x)])], color, options);
}

// The type II region c <= y <= d, h1(y) <= x <= h2(y) as a filled polygon.
export function regionTypeII2d(c, d, h1, h2, color, options = {}) {
  const left = asFn(h1);
  const right = asFn(h2);
  const ys = spread(c, d, boundarySamples + 1);
  return fill2d([...ys.map((y) => [left(y), y]), ...[...ys].reverse().map((y) => [right(y), y])], color, options);
}

// The polar region t0 <= theta <= t1, r1(theta) <= r <= r2(theta) as a filled polygon.
export function regionPolar2d(t0, t1, r1, r2, color, options = {}) {
  const inner = asFn(r1);
  const outer = asFn(r2);
  const ts = spread(t0, t1, boundarySamples + 1);
  const at = (r, t) => [r * Math.cos(t), r * Math.sin(t)];
  return fill2d([...ts.map((t) => at(outer(t), t)), ...[...ts].reverse().map((t) => at(inner(t), t))], color, options);
}

// ---------------------------------------------------------------------------
// drawing
// ---------------------------------------------------------------------------
// Draw (or redraw) into `element`. Plotly.react keeps the camera thanks to
// uirevision; the ResizeObserver keeps the canvas in step with the column
// width (sidebar toggles, phone rotation). A layout without a 3D scene (from
// planeLayout) is drawn as a static 2D picture.
export function render(Plotly, element, traces, layout) {
  Plotly.react(element, traces, layout, layout.scene ? CONFIG_3D : CONFIG_2D);
  requestAnimationFrame(() => {
    if (element.isConnected) Plotly.Plots.resize(element);
  });
  if (!element.__sceneResize && typeof ResizeObserver !== "undefined") {
    element.__sceneResize = new ResizeObserver(() => {
      if (element.isConnected) Plotly.Plots.resize(element);
    });
    element.__sceneResize.observe(element);
  }
  return element;
}
