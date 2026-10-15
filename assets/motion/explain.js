// Explainer components: show the idea with logos, icons, arrows and callouts instead of words.
// Load after engine.js and motion/core.js. Every function is a pure function of time t.
// Colours come from the per-video accent (var(--clay) / --clayText / --band); never hard-code the accent.
(function () {
  const E = window.E, clamp = E.clamp;
  const ICON = {   // simple line icons (24 grid, stroke = currentColor). Use the product's OFFICIAL logo instead where one exists.
    doc: '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 15h5M10 18h3"/>',
    mail: '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>',
    reply: '<path d="M10 8L5 12l5 4"/><path d="M5 12h9a5 5 0 0 1 5 5v1"/>',
    funnel: '<path d="M4 5h16l-6.5 7.5V19l-3 1.5v-8z"/>',
    calendar: '<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4M8.5 14h2M13.5 14h2"/>',
    laptop: '<rect x="5" y="5" width="14" height="10" rx="1.5"/><path d="M2.5 18.5h19"/>',
    github: '<path fill="currentColor" stroke="none" d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.3-3.4-1.3-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.4 1.1 2.9.8.1-.6.4-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.8 1a9.6 9.6 0 0 1 5 0c1.9-1.3 2.8-1 2.8-1 .5 1.4.2 2.4.1 2.7.6.7 1 1.6 1 2.7 0 3.9-2.3 4.7-4.6 5 .4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2z"/>',
    comment: '<path d="M4 5h16v11H9l-5 4z"/>',
  };
  E.icon = (name, size, stroke) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${stroke || 1.8}" stroke-linecap="round" stroke-linejoin="round">${ICON[name] || ''}</svg>`;

  // 1. logo / icon tile pop: arrives tilted and small, springs upright with a small overshoot
  //    (scale 0.8 -> 1, rotate -14deg -> 0, opacity in 0.1 s). Returns the props so callers can add their own x/y.
  E.iconPop = function (el, t, t0, o) {
    o = o || {};
    const s = E.spring(t, t0, { w: 13, z: 0.62 }), op = clamp((t - t0) / 0.1, 0, 1);
    const rot = (o.rot === undefined ? -14 : o.rot) * (1 - s);
    el.style.opacity = op.toFixed(3);
    el.style.transform = `translate(${(o.x || 0).toFixed(1)}px,${(o.y || 0).toFixed(1)}px) rotate(${rot.toFixed(2)}deg) scale(${(0.8 + 0.2 * s).toFixed(4)})`;
    return { s, op };
  };
  // a tile element: icon + small mono label under it; hero tiles get the accent border
  E.iconTile = function (parent, name, label, o) {
    o = o || {};
    const n = E.el(parent, 'div', 'xp-tile' + (o.hero ? ' hero' : ''),
      `<div class="ic" style="color:${o.hero ? 'var(--clay)' : '#111'}">${o.svg || E.icon(name, o.icon || 64)}</div><div class="lb">${label}</div>`);
    return n;
  };

  // 2. flow arrow: draws in the direction of flow (stroke dash), with a short travel along it.
  //    el must contain an <svg> with one <path class="ln"> and one <path class="hd"> (built by E.arrowEl).
  E.arrowEl = function (parent, len, dir) {
    const vert = dir === 'down';
    const w = vert ? 40 : len, h = vert ? len : 40;
    const d = vert ? `M20 4 V${len - 6}` : `M4 20 H${len - 6}`;
    const hd = vert ? `M10 ${len - 16} L20 ${len - 4} L30 ${len - 16}` : `M${len - 16} 10 L${len - 4} 20 L${len - 16} 30`;
    return E.el(parent, 'div', 'xp-arrow', `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" fill="none" stroke="var(--clay)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path class="ln" d="${d}" pathLength="100" stroke-dasharray="100" /><path class="hd" d="${hd}"/></svg>`);
  };
  E.arrowDraw = function (el, t, t0, dur) {
    const u = E.ease.p3o(clamp((t - t0) / (dur || 0.28), 0, 1));
    el.querySelector('.ln').setAttribute('stroke-dashoffset', (100 * (1 - u)).toFixed(2));
    el.querySelector('.hd').style.opacity = clamp((u - 0.6) / 0.4, 0, 1).toFixed(3);
    el.style.opacity = t >= t0 ? 1 : 0;
  };

  // 3. callout on a real capture: an accent outline box draws around one line, then a label arrow slides in
  //    from the side it points from ("<- WHAT YOU SELL"). box/label are absolutely positioned by the caller.
  E.callout = function (box, label, t, t0) {
    const u = E.ease.p3o(clamp((t - t0) / 0.3, 0, 1));
    box.style.opacity = clamp((t - t0) / 0.08, 0, 1).toFixed(3);
    box.style.clipPath = `inset(0 ${(100 * (1 - u)).toFixed(2)}% 0 0 round 10px)`;   // outline wipes on left -> right
    const v = E.spring(t, t0 + 0.18, { w: 14, z: 0.75 });
    label.style.opacity = clamp((t - t0 - 0.18) / 0.1, 0, 1).toFixed(3);
    label.style.transform = `translateX(${(40 * (1 - v)).toFixed(1)}px)`;
  };

  // 4. chips: numbered steps ("01 · FIND LEADS") or tags ("MIT license") pop in one per beat
  E.chipPop = function (el, t, t0) {
    const s = E.spring(t, t0, { w: 14, z: 0.68 });
    el.style.opacity = clamp((t - t0) / 0.08, 0, 1).toFixed(3);
    el.style.transform = `scale(${(0.6 + 0.4 * s).toFixed(4)})`;
  };

  // 5. stage timeline: dots on a line, a progress dot springs from stage to stage; filled line behind it
  E.stageTimeline = function (parent, labels) {
    const n = E.el(parent, 'div', 'xp-stages');
    E.el(n, 'div', 'track'); E.el(n, 'div', 'fill'); E.el(n, 'div', 'head');
    labels.forEach((l, i) => { const d = E.el(n, 'div', 'st', `<i></i><span>${l}</span>`); d.style.left = (100 * i / (labels.length - 1)) + '%'; });
    return n;
  };
  E.stageAt = function (el, t, keys) {   // keys: [[t, stageIndex], ...]
    const n = el.querySelectorAll('.st').length, p = E.sp(t, keys, { w: 12, z: 0.8 }) / (n - 1);
    el.querySelector('.fill').style.width = (100 * clamp(p, 0, 1)) + '%';
    el.querySelector('.head').style.left = (100 * clamp(p, 0, 1)) + '%';
    el.querySelectorAll('.st').forEach((d, i) => d.classList.toggle('on', i / (n - 1) <= p + 1e-3));
  };

  // 6. loop diagram: labels around a dashed circle, a dot travels the loop (one lap per `lap` seconds)
  E.loopDiagram = function (parent, labels, r) {
    const n = E.el(parent, 'div', 'xp-loop');
    n.style.width = n.style.height = (2 * r) + 'px';
    E.el(n, 'div', 'ring');
    labels.forEach((l, i) => { const a = -Math.PI / 2 + 2 * Math.PI * i / labels.length, d = E.el(n, 'div', 'lbl', l);
      d.style.left = (r + (r + 54) * Math.cos(a)) + 'px'; d.style.top = (r + (r + 34) * Math.sin(a)) + 'px'; });
    E.el(n, 'div', 'dot');
    return n;
  };
  E.loopAt = function (el, t, t0, lap) {
    const r = el.clientWidth / 2, a = -Math.PI / 2 + 2 * Math.PI * Math.max(0, t - t0) / (lap || 2.4);
    const d = el.querySelector('.dot'); d.style.left = (r + r * Math.cos(a)) + 'px'; d.style.top = (r + r * Math.sin(a)) + 'px';
    d.style.opacity = t >= t0 ? 1 : 0;
  };

  // 7. comment-pill CTA (style B): a big accent pill with a comment icon; "Comment" is there, then
  //    “KEYWORD” types in letter by letter; a small white link chip pops in under it.
  E.ctaPill = function (parent, keyword, chipHtml) {
    const n = E.el(parent, 'div', 'xp-cta');
    const pill = E.el(n, 'div', 'pill', `${E.icon('comment', 66, 2.2)}<span class="tx"></span>`);
    const chip = E.el(n, 'div', 'chip', chipHtml || '');
    n._k = keyword; return n;
  };
  E.ctaPillAt = function (el, t, t0, typeAt) {
    const pill = el.querySelector('.pill'), chip = el.querySelector('.chip'), kw = '“' + el._k.toUpperCase() + '”';
    const s = E.spring(t, t0, { w: 13, z: 0.8 });
    pill.style.opacity = (0.4 + 0.6 * clamp((t - t0) / 0.12, 0, 1)) * (t >= t0 ? 1 : 0);
    pill.style.transform = `scale(${(0.92 + 0.08 * s).toFixed(4)})`;
    const typed = E.typed(kw, typeAt, 12, t);
    el.querySelector('.tx').innerHTML = 'Comment ' + typed + (typed.length && typed.length < kw.length ? '<span class="cc"></span>' : '');
    const done = typeAt + kw.length / 12;
    E.chipPop(chip, t, done + 0.25);
  };
})();
