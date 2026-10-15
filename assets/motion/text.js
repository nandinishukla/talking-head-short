// maskRise: text rises line by line out of a mask line; outgoing and incoming text get separate timing.
// kineticNumber: a number that counts up while it grows out of a point ("62%").
// Ref: showreel-everything-transforms (also launch-film-one-take-glass: "text rises out of a mask line").
(function () {
  const E = window.E;
  // builds one mask per line inside el; returns the inner spans. lines: ['line one', 'line <b>two</b>']
  E.maskLines = function (el, lines) {
    el.innerHTML = '';
    return lines.map((h) => {
      const m = E.el(el, 'div');
      m.style.cssText = 'overflow:hidden;padding:0 .04em .08em;margin-bottom:-.08em;';
      const s = E.el(m, 'div', '', h);
      s.style.cssText = 'will-change:transform;';
      return s;
    });
  };
  // maskRiseAt(spans, t, {tin, tout, stagger:.07, din:.6, dout:.32, sout:.05})
  // in: each line rises from 110% below its mask (power3.out); out: each line exits upward (power3.in),
  // top line first. Start the next block's tin after tout + dout so the two never share a frame.
  E.maskRiseAt = function (spans, t, o) {
    const st = o.stagger === undefined ? 0.07 : o.stagger, din = o.din || 0.6, dout = o.dout || 0.32, sout = o.sout === undefined ? 0.05 : o.sout;
    spans.forEach((s, i) => {
      const a = o.tin + i * st;
      let y = E.kf(t, [[a, 110], [a + din, 0, 'p3o']]);
      if (o.tout !== undefined && t > o.tout + i * sout) y = E.kf(t, [[o.tout + i * sout, 0], [o.tout + i * sout + dout, -115, 'p3i']]);
      s.style.transform = `translateY(${y.toFixed(2)}%)`;
      s.style.visibility = y >= 109.9 || y <= -114.9 ? 'hidden' : 'visible';
    });
  };

  // kineticNumber(el, t, {t0, to, from:0, dur:1.1, dec:0, prefix:'', suffix:'%', origin:'50% 100%'})
  // grows from scale 0 out of `origin` on a spring with a small overshoot while it counts on expo.out.
  E.kineticNumber = function (el, t, o) {
    const dur = o.dur || 1.1, from = o.from || 0;
    const u = E.ease.eo(E.clamp((t - o.t0) / dur, 0, 1));
    const v = from + (o.to - from) * u;
    const txt = (o.dec ? v.toFixed(o.dec) : String(Math.round(v)));
    const html = `${o.prefix || ''}${txt}${o.suffix ? `<span style="font-size:${o.suffixScale || 0.55}em;margin-left:.04em">${o.suffix}</span>` : ''}`;
    if (el.innerHTML !== html) el.innerHTML = html;
    const s = E.spring(t, o.t0, o.spring || { w: 9, z: 0.68 });
    el.style.transformOrigin = o.origin || '50% 100%';
    el.style.transform = `scale(${Math.max(0, s).toFixed(4)})`;
    el.style.opacity = t <= o.t0 ? '0' : '1';
    el.style.fontVariantNumeric = 'tabular-nums';
    return v;
  };
})();
