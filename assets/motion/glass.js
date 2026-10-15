// glassBox: frosted glass panel = a blurred, lightened clone of the scene behind it, clipped to a
// rounded rect, with a bright top rim. It springs out of a point (small overshoot, closed-form spring).
// Refs: launch-film-one-take-glass, product-sting-frame-exact.
//
// const g = E.glassBox(root, { source: sceneEl });   // sceneEl fills root (inset 0) and holds what's behind
// in render(t):  renderScene(t); g.mirror(); g.render(g.springOut(t, t0, from, to));
(function () {
  const E = window.E;
  E.glassBox = function (parent, o) {
    o = Object.assign({ blur: 28, wash: 0.42, bright: 1.1, sat: 1.2, z: 20 }, o);
    const shadow = E.el(parent, 'div');
    shadow.style.cssText = `position:absolute;box-shadow:var(--shadow);z-index:${o.z};`;
    const layer = E.el(parent, 'div');
    layer.style.cssText = `position:absolute;overflow:hidden;z-index:${o.z};background:#F6F6F3;`;  // the window onto the clone
    let clone = null, frozen = [];
    // the clone drops its ids (no duplicates), so it keeps the original's look as frozen computed styles
    // (skip visibility: the renderer keeps the page hidden while it boots, and that would freeze in)
    const SKIP = /^(visibility|will-change|transition|animation)/;
    const freeze = (n) => { const cs = getComputedStyle(n); let s = ''; for (let i = 0; i < cs.length; i++) if (!SKIP.test(cs[i])) s += `${cs[i]}:${cs.getPropertyValue(cs[i])};`; return s; };
    const reclone = () => {
      if (clone) clone.remove();
      const src = [o.source, ...o.source.querySelectorAll('*')];
      frozen = src.map(freeze);
      clone = o.source.cloneNode(true);
      const dst = [clone, ...clone.querySelectorAll('*')];
      dst.forEach((n, i) => { n.removeAttribute('id'); n.style.cssText = frozen[i] + src[i].style.cssText; });
      clone.style.left = '0px'; clone.style.top = '0px';
      clone.style.filter = `blur(${o.blur}px) brightness(${o.bright}) saturate(${o.sat})`;
      layer.insertBefore(clone, layer.firstChild);
    };
    reclone();
    const wash = E.el(layer, 'div');
    wash.style.cssText = `position:absolute;inset:0;background:rgba(255,255,255,${o.wash});`;
    const rim = E.el(parent, 'div');
    rim.style.cssText = `position:absolute;z-index:${o.z};overflow:hidden;
      box-shadow:inset 0 3px 0 rgba(255,255,255,.95), inset 0 0 0 2px rgba(255,255,255,.55), 0 0 0 1px rgba(24,24,32,.05);
      background:linear-gradient(180deg, rgba(255,255,255,.35) 0%, rgba(255,255,255,0) 38%);`;
    const content = E.el(rim, 'div');
    content.style.cssText = 'position:absolute;inset:0;';
    const g = { layer, rim, shadow, content };
    // copy the source's per-frame inline styles onto the clone (call after the scene's own render)
    g.mirror = function () {
      const a = [o.source, ...o.source.querySelectorAll('*')], b = [clone, ...clone.querySelectorAll('*')];
      if (a.length !== b.length) { reclone(); return; }
      for (let i = 1; i < a.length; i++) {
        const css = a[i].style.cssText;
        if (b[i]._css !== css) { b[i].style.cssText = frozen[i] + css; b[i]._css = css; }
        if (!a[i].children.length && b[i].textContent !== a[i].textContent) b[i].textContent = a[i].textContent;
      }
    };
    // rect {x, y, w, h, r} (centre-based); op = opacity of the whole panel
    g.render = function (q, op) {
      const vis = q.w > 0.5 && q.h > 0.5 && (op === undefined || op > 0.001);
      for (const n of [layer, rim, shadow]) n.style.display = vis ? 'block' : 'none';
      if (!vis) return;
      const l = q.x - q.w / 2, tp = q.y - q.h / 2;
      // the clone stays registered to the scene behind: offset it by the window's own position
      clone.style.left = (-l).toFixed(2) + 'px'; clone.style.top = (-tp).toFixed(2) + 'px';
      E.rect(layer, q); E.rect(rim, q); E.rect(shadow, q);
      const oo = op === undefined ? 1 : op;
      for (const n of [layer, rim, shadow]) n.style.opacity = oo.toFixed(3);
    };
    // springs out of point `from` {x, y} into rect `to`; width overshoots a little, height follows 40 ms later
    g.springOut = function (t, t0, from, to, d) {
      d = d || 26;
      const c = E.spring(t, t0, { w: 12, z: 0.8 });
      const sw = E.spring(t, t0, { w: 11, z: 0.6 }), sh = E.spring(t, t0 + 0.04, { w: 11, z: 0.66 });
      if (t <= t0) return { x: from.x, y: from.y, w: 0, h: 0, r: 0 };
      return { x: E.mix(from.x, to.x, c), y: E.mix(from.y, to.y, c), w: E.mix(d, to.w, sw), h: E.mix(d, to.h, sh), r: E.mix(d / 2, to.r, Math.min(1, sh)) };
    };
    return g;
  };
})();
