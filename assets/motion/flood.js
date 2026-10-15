// flood / contract: a shape scales past all four corners in ~0.3 s, holds, then contracts into the
// next element. iris: six blades close around a hexagonal aperture and snap open on the next scene.
// Ref: launch-film-one-take-glass. Swap the scene underneath while the frame is covered.
(function () {
  const E = window.E;
  // floodAt(t, {from:{x,y,w,h,r}, t0, dur:.3, t1, cdur:.42, to:{x,y,w,h,r}, W, H}) -> {rect, covered}
  E.floodAt = function (t, o) {
    const W = o.W || 1080, H = o.H || 1920, f = o.from, dur = o.dur || 0.3, cdur = o.cdur || 0.42;
    const R = 1.08 * Math.max(...[[0, 0], [W, 0], [0, H], [W, H]].map(([cx, cy]) => Math.hypot(cx - f.x, cy - f.y)));
    const full = { x: f.x, y: f.y, w: 2 * R, h: 2 * R, r: R };
    if (t <= o.t0) return { rect: f, covered: false };
    if (t < o.t0 + dur) return { rect: E.mixRect(f, full, E.ease[o.ease || 'p3i'](E.clamp((t - o.t0) / dur, 0, 1))), covered: false };
    if (!o.to || t <= o.t1) return { rect: full, covered: true };
    const u = E.ease[o.cease || 'p3o'](E.clamp((t - o.t1) / cdur, 0, 1));
    // contract: shrink the circle onto the target first, then let its corners square up
    const q = E.mixRect(full, o.to, u);
    q.r = E.mix(R, o.to.r, Math.pow(u, 0.6));
    return { rect: q, covered: false };
  };
  // contract-only (a full-frame shape contracts into an element)
  E.contractAt = (t, o) => E.floodAt(t, Object.assign({ t0: -2, dur: 0.01 }, o));

  // iris: E.irisEl(parent) -> svg; E.irisAt(t, {t0, dur:.38, t1, odur:.3}) -> aperture 0 (closed) .. 1 (open)
  E.irisEl = function (parent, o) {
    const ac = E.accent();
    o = Object.assign({ fill: [ac, E.mixColor(ac, '#000000', 0.06)], edge: 'rgba(255,255,255,.75)', z: 40 }, o);
    const W = parent.offsetWidth || 1080, H = parent.offsetHeight || 1920;
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('width', W); svg.setAttribute('height', H);
    svg.style.cssText = `position:absolute;left:0;top:0;z-index:${o.z};`;
    const blades = [], edges = [];
    for (let k = 0; k < 6; k++) {
      const p = document.createElementNS(ns, 'path'); p.setAttribute('fill', o.fill[k % o.fill.length]); svg.appendChild(p); blades.push(p);
    }
    for (let k = 0; k < 6; k++) {
      const p = document.createElementNS(ns, 'path'); p.setAttribute('stroke', o.edge); p.setAttribute('stroke-width', '4'); p.setAttribute('fill', 'none'); svg.appendChild(p); edges.push(p);
    }
    parent.appendChild(svg);
    return { svg, blades, edges, W, H, cx: o.cx === undefined ? W / 2 : o.cx, cy: o.cy === undefined ? H / 2 : o.cy };
  };
  E.irisAt = function (t, o) {
    const d = o.dur || 0.38, od = o.odur || 0.3;
    if (o.t1 !== undefined && t > o.t1) return E.ease.p3o(E.clamp((t - o.t1) / od, 0, 1));
    return 1 - E.ease.p2io(E.clamp((t - o.t0) / d, 0, 1));
  };
  // draw the iris at aperture a (0 closed .. 1 open). Each blade = its two hexagon vertices, both edge
  // extensions out to a far circle, and the short arc between them, so the six blades tile the frame.
  E.irisRender = function (I, a) {
    const amax = 1.02 * Math.hypot(I.W, I.H) / 2 / Math.cos(Math.PI / 6) + 20;
    const vis = a < 0.999;
    I.svg.style.display = vis ? 'block' : 'none';
    if (!vis) return;
    const ra = Math.max(0.0001, a * amax), rot = (1 - a) * 60 * Math.PI / 180 - Math.PI / 2, F = 6000;
    const V = [], D = [];
    for (let k = 0; k < 6; k++) V.push([I.cx + ra * Math.cos(rot + k * Math.PI / 3), I.cy + ra * Math.sin(rot + k * Math.PI / 3)]);
    for (let k = 0; k < 6; k++) { const n = V[(k + 1) % 6], dx = n[0] - V[k][0], dy = n[1] - V[k][1], l = Math.hypot(dx, dy); D.push([dx / l, dy / l]); }
    // far point: walk from vertex v along dir until the circle of radius F around the centre
    const far = (v, d) => { const ox = v[0] - I.cx, oy = v[1] - I.cy, b = ox * d[0] + oy * d[1], c = ox * ox + oy * oy - F * F; const s = -b + Math.sqrt(b * b - c); return [v[0] + d[0] * s, v[1] + d[1] * s]; };
    const f = (p) => p[0].toFixed(1) + ' ' + p[1].toFixed(1);
    for (let k = 0; k < 6; k++) {
      const v0 = V[k], v1 = V[(k + 1) % 6], P = far(v1, D[k]), Q = far(v0, D[(k + 5) % 6]);
      I.blades[k].setAttribute('d', `M${f(v0)} L${f(v1)} L${f(P)} A${F} ${F} 0 0 0 ${f(Q)} Z`);
      I.edges[k].setAttribute('d', `M${f(v0)} L${f(P)}`);
    }
  };
})();
