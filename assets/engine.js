// Shared, seek-safe scene engine: every visual is a pure function of time t.
(function () {
  const E = {};
  E.ease = {
    lin: (u) => u,
    sio: (u) => -(Math.cos(Math.PI * u) - 1) / 2,                 // sine.inOut
    p2io: (u) => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2), // power2.inOut
    p3io: (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2), // power3.inOut
    p3i: (u) => u * u * u,                                         // power3.in
    p3o: (u) => 1 - Math.pow(1 - u, 3),                            // power3.out
    p2o: (u) => 1 - Math.pow(1 - u, 2),
    hold: (u) => (u < 1 ? 0 : 1),
  };
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  E.clamp = clamp;
  // keys: [[t, value], [t, value, ease], ...]; value may be number or {k:number}
  E.kf = function (t, keys) {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      if (t <= keys[i][0]) {
        const [t0, v0] = keys[i - 1];
        const [t1, v1, e] = keys[i];
        const u = E.ease[e || 'p2io'](clamp((t - t0) / Math.max(1e-6, t1 - t0), 0, 1));
        if (typeof v0 === 'number') return v0 + (v1 - v0) * u;
        const o = {};
        for (const k in v1) o[k] = v0[k] + (v1[k] - v0[k]) * u;
        return o;
      }
    }
    return keys[keys.length - 1][1];
  };
  // element props: o opacity, x/y offsets, s scale, b blur(px)
  E.apply = function (el, p) {
    if (p.o !== undefined) el.style.opacity = p.o.toFixed(4);
    const x = p.x || 0, y = p.y || 0, s = p.s === undefined ? 1 : p.s;
    el.style.transform = `translate(${x.toFixed(2)}px,${y.toFixed(2)}px) scale(${s.toFixed(4)})`;
    el.style.filter = p.b && p.b > 0.05 ? `blur(${p.b.toFixed(2)}px)` : 'none';
  };
  E.track = function (el, t, tracks) {
    const p = {};
    for (const k in tracks) p[k] = E.kf(t, tracks[k]);
    E.apply(el, p);
    return p;
  };
  // card landing: dull pop arrives at t0+0.3
  E.land = (t0) => ({
    o: [[t0, 0], [t0 + 0.3, 1, 'p3o']],
    y: [[t0, 70], [t0 + 0.45, 0, 'p3o']],
    s: [[t0, 0.93], [t0 + 0.45, 1, 'p3o']],
  });
  // depth of field state helpers (focus = sharp; side = neighbour while pushing; back = old hero)
  E.dof = { focus: { b: 0, o: 1 }, side: { b: 14, o: 0.7 }, back: { b: 9, o: 0.4 } };

  // camera: cam(t) -> {x,y,s} world point shown at the focus point, with scale s
  const K = (0.29 * 0.75) / 60;
  E.camera = function (opts) {
    const { world, viewport, blurNode, fx, fy, cam } = opts;
    return function (t) {
      const c = cam(t);
      world.style.transform = `translate(${(fx - c.x * c.s).toFixed(2)}px,${(fy - c.y * c.s).toFixed(2)}px) scale(${c.s.toFixed(5)})`;
      const dt = 1 / 240;
      const p = cam(Math.max(0, t - dt)), n = cam(t + dt);
      // central-difference screen velocity of the content under the focus point
      const sx = (q) => fx - q.x * q.s + c.x * q.s, sy = (q) => fy - q.y * q.s + c.y * q.s;
      const vx = (sx(n) - sx(p)) / (2 * dt) * -1, vy = (sy(n) - sy(p)) / (2 * dt) * -1;
      const zs = (Math.abs(n.s - p.s) / (2 * dt) / c.s) * 420;
      let bx = Math.min(40, K * (Math.abs(vx) + zs)), by = Math.min(40, K * (Math.abs(vy) + zs));
      if (t < 1e-6) { bx = 0; by = 0; }
      if (bx < 0.3 && by < 0.3) viewport.style.filter = 'none';
      else { blurNode.setAttribute('stdDeviation', `${bx.toFixed(2)} ${by.toFixed(2)}`); viewport.style.filter = `url(#${blurNode.parentNode.id})`; }
      return { c, bx, by };
    };
  };
  // camera path from segments: [{t0,t1,to:{x,y,s},ease}], start pose p0
  E.path = function (p0, segs) {
    return function (t) {
      let cur = p0;
      for (const sg of segs) {
        if (t <= sg.t0) return cur;
        const u = clamp((t - sg.t0) / (sg.t1 - sg.t0), 0, 1);
        const e = E.ease[sg.ease || 'p2io'](u);
        const nx = { x: cur.x + (sg.to.x - cur.x) * e, y: cur.y + (sg.to.y - cur.y) * e, s: cur.s + (sg.to.s - cur.s) * e };
        if (t < sg.t1) return nx;
        cur = sg.to;
      }
      return cur;
    };
  };
  // typed text: n chars visible from t0 at cps
  E.typed = (text, t0, cps, t) => text.slice(0, clamp(Math.floor((t - t0) * cps + 1e-6), 0, text.length));
  E.caret = (t, on) => (on && Math.floor(t * 2) % 2 === 0 ? '<span class="caret"></span>' : (on ? '<span class="caret off"></span>' : ''));
  // register one paused root timeline that drives render(t)
  E.run = function (id, dur, render) {
    const tl = gsap.timeline({ paused: true });
    const P = { v: 0 };
    tl.to(P, { v: 1, duration: dur, ease: 'none', onUpdate: () => render(tl.time()) }, 0);
    window.__timelines = window.__timelines || {};
    window.__timelines[id] = tl;
    render(0);
  };
  window.E = E;
})();
