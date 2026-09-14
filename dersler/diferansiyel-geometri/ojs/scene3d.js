// Interactive 3D scene helpers for the "Diferansiyel Geometri" book.
//
// The chapters embed Observable JS cells that import these helpers. The code
// runs in the reader's browser only: nothing is executed when the book is
// built, and every scene is wrapped in `content-visible when-format="html:js"`
// so the PDF and EPUB exports keep the static SVG figures instead.
//
// Plotly is loaded once per page with OJS `require(PLOTLY)` and passed in, so
// this module makes no network request of its own. Colors come from the
// site's CSS custom properties and are re-read whenever the reader toggles
// the light/dark theme (Quarto flips the `quarto-dark` class on <body>).

export const PLOTLY = "plotly.js-dist-min@2.35.2";

const CONFIG = {
  responsive: true,
  displaylogo: false,
  scrollZoom: false, // the page must keep scrolling when the wheel passes over a scene
  modeBarButtonsToRemove: ["toImage", "resetCameraLastSave3d", "hoverClosest3d"],
};

// ---------------------------------------------------------------------------
// theme
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

// Turkish number formatting for the read-outs: 0.5 -> "0,50".
export function fmt(x, digits = 2) {
  const value = Math.abs(x) < 0.5 * 10 ** -digits ? 0 : x;
  return value.toLocaleString("tr-TR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

// ---------------------------------------------------------------------------
// layout
// ---------------------------------------------------------------------------
export function sceneLayout(theme, options = {}) {
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
  // When all three ranges are fixed, keep the box proportional to them instead.
  const spans = [options.x, options.y, options.z].map((range) => (range ? range[1] - range[0] : 0));
  const fixedBox = !options.aspectmode && !options.aspectratio && spans.every((span) => span > 0);
  const meanSpan = Math.cbrt(spans[0] * spans[1] * spans[2]);
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    font: { color: theme.text },
    margin: { l: 0, r: 0, t: legend ? 30 : 0, b: 0 },
    showlegend: legend,
    legend: {
      orientation: "h",
      x: 0,
      y: 1,
      yanchor: "bottom",
      font: { size: 11, color: theme.text },
      bgcolor: "rgba(0,0,0,0)",
    },
    // A constant uirevision keeps the reader's camera when a slider redraws the scene.
    uirevision: options.revision ?? "scene",
    scene: {
      aspectmode: fixedBox ? "manual" : options.aspectmode ?? "data",
      ...(fixedBox
        ? { aspectratio: { x: spans[0] / meanSpan, y: spans[1] / meanSpan, z: spans[2] / meanSpan } }
        : options.aspectratio ? { aspectratio: options.aspectratio } : {}),
      xaxis: axis("x", options.x),
      yaxis: axis("y", options.y),
      zaxis: axis("z", options.z),
      camera: { eye: options.eye ?? { x: 1.55, y: 1.35, z: 0.85 } },
      dragmode: "turntable",
    },
  };
}

// ---------------------------------------------------------------------------
// traces
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

// The tangent vector v applied at p: a shaft from p plus a cone whose tip is
// exactly at p + v. Returns an array of traces; spread it into the trace list.
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
    {
      type: "cone",
      x: [base[0]],
      y: [base[1]],
      z: [base[2]],
      u: [unit[0]],
      v: [unit[1]],
      w: [unit[2]],
      anchor: "tail",
      sizemode: "absolute",
      sizeref: head,
      colorscale: [
        [0, color],
        [1, color],
      ],
      showscale: false,
      showlegend: false,
      hoverinfo: "skip",
      name,
    },
  ];
}

function surfaceTrace(x, y, z, color, options) {
  return {
    type: "surface",
    x,
    y,
    z,
    surfacecolor: z.map((row) => row.map(() => 0)),
    colorscale: [
      [0, color],
      [1, color],
    ],
    cmin: 0,
    cmax: 1,
    showscale: false,
    opacity: options.opacity ?? 0.18,
    lighting: { ambient: 0.9, diffuse: 0.35, specular: 0.05 },
    hoverinfo: "skip",
    showlegend: false,
  };
}

// A parametric surface (u, v) -> f(u, v) on [u0, u1] x [v0, v1].
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

// ---------------------------------------------------------------------------
// drawing
// ---------------------------------------------------------------------------
// Draw (or redraw) into `element`. Plotly.react keeps the camera thanks to
// uirevision; the ResizeObserver keeps the canvas in step with the column
// width (sidebar toggles, phone rotation).
export function render(Plotly, element, traces, layout) {
  Plotly.react(element, traces, layout, CONFIG);
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
