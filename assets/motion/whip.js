// whip: the house whip as E.path segments. 0.45 s out on power3.in, 0.6 s in on power3.out, with the
// turnover pose placed so both halves have the SAME velocity at the midpoint (no speed jump). The engine's
// E.camera then blurs the viewport along that velocity (directional smear, capped at 40 px).
// Refs: house-luxury-tech, product-sting-frame-exact (whip-tilt), launch-film-one-take-glass.
//
// const W = E.whip({ t0: 2.1, from: {x, y, s}, to: {x, y, s} });
// const cam = E.path(p0, [ ...earlierSegs, ...W.segs ]);   events: { t: W.mid, type: 'whoosh' }
(function () {
  const E = window.E;
  E.whip = function (o) {
    const dout = o.out || 0.45, din = o.in || 0.6;
    // power3.in ends at 3*(M-A)/dout, power3.out starts at 3*(B-M)/din: equal when M = A + (B-A)*dout/(dout+din)
    const f = dout / (dout + din), A = o.from, B = o.to;
    const M = { x: A.x + (B.x - A.x) * f, y: A.y + (B.y - A.y) * f, s: A.s + (B.s - A.s) * f };
    return {
      mid: o.t0 + dout,
      end: o.t0 + dout + din,
      turn: M,
      segs: [
        { t0: o.t0, t1: o.t0 + dout, to: M, ease: 'p3i' },
        { t0: o.t0 + dout, t1: o.t0 + dout + din, to: B, ease: 'p3o' },
      ],
    };
  };
})();
