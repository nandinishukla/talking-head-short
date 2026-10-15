// morphShape: ONE shape that morphs continuously through states (chip -> bubble -> card -> pill ...).
// Size, radius, position and colour spring between states; the shape is its own text mask, and the
// outgoing text leaves before the incoming text rises, so swapped text never overlaps.
// Default fill = the video's accent (var(--clay), read via E.accent()). State fills must be hex.
// Ref: launch-film-one-take-glass ("one shape keeps morphing: Ordered ✓ -> Printing % -> ...").
//
// const m = E.morphShape(parent, [{t:0, x, y, w, h, r, html:'Ordered ✓'}, {t:1.2, w:300, h:300, r:150, html:'62%'}, ...]);
// in render(t): m.render(t);   (a state inherits anything it leaves out from the previous one)
(function () {
  const E = window.E;
  E.morphShape = function (parent, states, o) {
    o = Object.assign({ fill: E.accent(), color: '#fff', font: 52, weight: 700, spring: { w: 10, z: 0.74 }, outDur: 0.18, inDelay: 0.16, inDur: 0.42, colorDur: 0.14 }, o);
    const S = [];
    states.forEach((s, i) => S.push(Object.assign({}, i ? S[i - 1] : { fill: o.fill, color: o.color, font: o.font }, s)));
    const el = E.el(parent, 'div', 'obj');
    el.style.cssText = `position:absolute;overflow:hidden;box-shadow:var(--shadow);z-index:${o.z || 10};`;
    const spans = S.map((s) => {
      const n = E.el(el, 'div', '', s.html || '');
      n.style.cssText = `position:absolute;left:50%;top:50%;white-space:nowrap;font-weight:${o.weight};line-height:1.15;text-align:center;font-size:${s.font}px;color:${s.color};visibility:hidden;`;
      return n;
    });
    const m = { el, states: S };
    m.rectAt = function (t) {
      const keys = S.map((s) => [s.t, { x: s.x, y: s.y, w: s.w, h: s.h, r: s.r }, s.spring]);
      return E.sp(t, keys, o.spring);
    };
    m.render = function (t) {
      const q = m.rectAt(t);
      E.rect(el, q);
      // colour: a short switch (a long blend between two hues goes muddy halfway)
      let fill = S[0].fill;
      for (let i = 1; i < S.length; i++) if (S[i].fill !== S[i - 1].fill && t > S[i].t) fill = E.mixColor(S[i - 1].fill, S[i].fill, E.ease.p2io(E.clamp((t - S[i].t) / o.colorDur, 0, 1)));
      el.style.background = fill;
      S.forEach((s, i) => {
        // travel = half the shape plus half the text, so a line is fully outside the mask at either end
        const n = spans[i], travel = q.h / 2 + n.offsetHeight / 2 + 4;
        const tin = i === 0 && o.textAtStart !== false ? -1 : s.t + o.inDelay;
        const tout = i + 1 < S.length ? S[i + 1].t : 1e9;
        let y = E.kf(t, [[tin, travel], [tin + o.inDur, 0, 'p3o']]);
        if (t > tout) y = E.kf(t, [[tout, 0], [tout + o.outDur, -travel, 'p3i']]);
        const vis = t >= tin && t <= tout + o.outDur;
        n.style.visibility = vis ? 'visible' : 'hidden';
        if (!vis) return;
        n.style.transform = `translate(-50%,-50%) translateY(${y.toFixed(2)}px)`;
      });
      return q;
    };
    return m;
  };
})();
