// cursor: macOS arrow that glides in on an exponential ease-out, turns to face where it is heading,
// grows on hover and shrinks on press. Refs: product-sting-frame-exact, product-showreel-throughline.
(function () {
  const E = window.E;
  const TIP = [3, 2], AXIS = -115; // tip in the 32x39 viewBox; tail -> tip direction in degrees (screen coords)
  const PATH = 'M3 2 L3 31.5 L10.4 24.6 L15.3 35.8 L20.6 33.5 L15.8 22.4 L25.6 22.4 Z';
  E.cursorEl = function (parent, size) {
    const w = size || 58, k = w / 32;
    const el = E.el(parent, 'div', 'obj cursor');
    el.style.cssText = `position:absolute;left:0;top:0;width:${w}px;height:${39 * k}px;transform-origin:${TIP[0] * k}px ${TIP[1] * k}px;z-index:50;`;
    el.innerHTML = `<svg viewBox="0 0 32 39" width="${w}" height="${39 * k}" style="overflow:visible;filter:drop-shadow(0 6px 8px rgba(24,24,32,.28))">
      <path d="${PATH}" fill="#111" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/></svg>`;
    el._k = k;
    return el;
  };
  // path position: keys [{t, x, y}, {t, x, y, dur?, ease?}, ...]; each move ARRIVES at its t after dur (0.7 s)
  function pos(t, keys) {
    let x = keys[0].x, y = keys[0].y;
    for (let i = 1; i < keys.length; i++) {
      const k = keys[i], d = k.dur || 0.7, t0 = k.t - d;
      if (t <= t0) break;
      const u = E.ease[k.ease || 'eo'](E.clamp((t - t0) / d, 0, 1));
      x = x + (k.x - x) * u; y = y + (k.y - y) * u;
      if (t < k.t) break;
    }
    return { x, y };
  }
  // cursorAt(t, keys, {hover:[[t0,t1]], press:[t], show:[t0,t1], maxTurn:35}) -> {x, y, rot, s, o}
  E.cursorAt = function (t, keys, o) {
    o = o || {};
    const p = pos(t, keys), q = pos(t - 0.1, keys);
    const vx = (p.x - q.x) / 0.1, vy = (p.y - q.y) / 0.1, sp = Math.hypot(vx, vy);
    let rot = 0;
    if (sp > 1) {
      let d = Math.atan2(vy, vx) * 180 / Math.PI - AXIS;
      d = ((d + 540) % 360) - 180;
      // lean into the heading only when moving roughly tip-first; a cursor dragged backwards stays upright
      const m = o.maxTurn === undefined ? 35 : o.maxTurn, ahead = E.clamp((125 - Math.abs(d)) / 45, 0, 1);
      rot = E.clamp(d, -m, m) * ahead * Math.min(1, sp / 700);
    }
    const hk = [[-1, 1]];
    for (const [a, b] of o.hover || []) hk.push([a, 1.5], [b, 1]);
    let s = E.sp(t, hk, { w: 14, z: 0.8 });
    for (const tp of o.press || []) s *= 1 - 0.15 * E.kf(t, [[tp, 0], [tp + 0.07, 1, 'p2o'], [tp + 0.22, 0, 'p2io']]);
    const sh = o.show || [keys[0].t - 0.15, 1e9];
    const op = E.kf(t, [[sh[0], 0], [sh[0] + 0.15, 1], [sh[1], 1], [sh[1] + 0.15, 0]]);
    return { x: p.x, y: p.y, rot, s, o: op };
  };
  E.cursorApply = function (el, c) {
    const k = el._k;
    el.style.opacity = c.o.toFixed(3);
    el.style.transform = `translate(${(c.x - TIP[0] * k).toFixed(2)}px,${(c.y - TIP[1] * k).toFixed(2)}px) rotate(${c.rot.toFixed(2)}deg) scale(${c.s.toFixed(4)})`;
  };
})();
