// Motion components, shared core. Load after engine.js, before any other assets/motion/*.js.
// Everything here is a pure function of time t: no timers, no state between frames, no Math.random.
(function () {
  const E = window.E;
  const clamp = E.clamp;
  E.ease.eo = (u) => (u >= 1 ? 1 : (1 - Math.pow(2, -10 * u)) / (1 - Math.pow(2, -10)));   // expo.out
  E.ease.ei = (u) => (u <= 0 ? 0 : (Math.pow(2, 10 * u) - 1) / (Math.pow(2, 10) - 1));     // expo.in
  E.ease.p2i = (u) => u * u;                                                                // power2.in

  // closed-form spring step response 0 -> 1 from t0 (starts at rest; z < 1 = small overshoot).
  // w 11 / z 0.72 settles in ~0.5 s with ~4% overshoot.
  E.spring = function (t, t0, o) {
    const w = (o && o.w) || 11, z = (o && o.z) || 0.72, d = t - t0;
    if (d <= 0) return 0;
    if (z >= 1) return 1 - Math.exp(-w * d) * (1 + w * d);
    const r = Math.sqrt(1 - z * z), wd = w * r;
    return 1 - Math.exp(-z * w * d) * (Math.cos(wd * d) + (z / r) * Math.sin(wd * d));
  };
  // a value with many targets: keys [[t, v, springOpts?], ...] (v number or {k:number}).
  // The value is the sum of one spring per change, so it stays a pure function of t.
  E.sp = function (t, keys, o) {
    const v0 = keys[0][1];
    if (typeof v0 === 'number') {
      let v = v0;
      for (let i = 1; i < keys.length; i++) v += (keys[i][1] - keys[i - 1][1]) * E.spring(t, keys[i][0], keys[i][2] || o);
      return v;
    }
    const out = {};
    for (const k in v0) out[k] = E.sp(t, keys.map((q) => [q[0], q[1][k], q[2]]), o);
    return out;
  };
  // the per-video accent as a hex string: --clay (fills), --clayText (text on white), --band (highlight band).
  // base.css always defines them and accent.css overrides them per video, so never hard-code a colour.
  E.accent = (name) => getComputedStyle(document.documentElement).getPropertyValue(name || '--clay').trim();
  E.mix = (a, b, u) => a + (b - a) * u;
  const rgb = (h) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  E.mixColor = function (a, b, u) {
    const A = rgb(a), B = rgb(b), c = A.map((v, i) => Math.round(clamp(v + (B[i] - v) * u, 0, 255)));
    return `rgb(${c[0]},${c[1]},${c[2]})`;
  };
  // centre-based rect {x, y, w, h, r} -> absolutely positioned element
  E.rect = function (el, q) {
    el.style.left = (q.x - q.w / 2).toFixed(2) + 'px';
    el.style.top = (q.y - q.h / 2).toFixed(2) + 'px';
    el.style.width = Math.max(0, q.w).toFixed(2) + 'px';
    el.style.height = Math.max(0, q.h).toFixed(2) + 'px';
    el.style.borderRadius = Math.max(0, Math.min(q.r, q.w / 2, q.h / 2)).toFixed(2) + 'px';
  };
  E.mixRect = (a, b, u) => ({ x: E.mix(a.x, b.x, u), y: E.mix(a.y, b.y, u), w: E.mix(a.w, b.w, u), h: E.mix(a.h, b.h, u), r: E.mix(a.r, b.r, u) });
  E.el = function (parent, tag, cls, html) {
    const n = document.createElement(tag || 'div');
    if (cls) n.className = cls;
    if (html !== undefined) n.innerHTML = html;
    parent.appendChild(n);
    return n;
  };
})();
