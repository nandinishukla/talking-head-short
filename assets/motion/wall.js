// cardWall: cards on a gently curved wall in CSS 3D, a wave of accent light running along it (each card
// tilts as the wave passes), and a film camera making ONE named move over it (crane, dolly, orbit, push).
// Ref: gallery-3d-film-camera.
//
// const w = E.cardWall(root, { cols: 5, rows: 4, cw: 300, ch: 380, gap: 40, R: 2600, card: (i, j) => html });
// in render(t): w.render(t, { cam: E.filmCam(t, shot), wave: { t0, t1 } });
(function () {
  const E = window.E;
  E.cardWall = function (parent, o) {
    o = Object.assign({ cols: 5, rows: 4, cw: 300, ch: 380, gap: 40, R: 2600, P: 1500, origin: '50% 42%', tilt: 22, lift: 70 }, o);
    const view = E.el(parent, 'div');
    view.style.cssText = `position:absolute;inset:0;perspective:${o.P}px;perspective-origin:${o.origin};overflow:hidden;`;
    const stage = E.el(view, 'div');
    const [ox, oy] = o.origin.split(' ').map((v) => parseFloat(v) / 100);
    stage.style.cssText = `position:absolute;left:${ox * 100}%;top:${oy * 100}%;width:0;height:0;transform-style:preserve-3d;`;
    const cards = [];
    for (let j = 0; j < o.rows; j++) for (let i = 0; i < o.cols; i++) {
      const phi = (i - (o.cols - 1) / 2) * (o.cw + o.gap) / o.R;
      const c = E.el(stage, 'div', 'card');
      c.style.cssText = `position:absolute;left:${-o.cw / 2}px;top:${-o.ch / 2}px;width:${o.cw}px;height:${o.ch}px;border-radius:32px;overflow:hidden;backface-visibility:hidden;`;
      const inner = E.el(c, 'div', '', o.card ? o.card(i, j) : '');
      inner.style.cssText = 'position:absolute;inset:0;';
      const light = E.el(c, 'div');
      light.style.cssText = 'position:absolute;inset:0;background:linear-gradient(160deg, color-mix(in srgb, var(--clay) 95%, transparent) 0%, color-mix(in srgb, var(--clay) 55%, transparent) 55%, color-mix(in srgb, var(--band) 20%, transparent) 100%);opacity:0;mix-blend-mode:multiply;';
      cards.push({ el: c, light, i, j, x: o.R * Math.sin(phi), y: (j - (o.rows - 1) / 2) * (o.ch + o.gap), z: o.R * (1 - Math.cos(phi)), phi });
    }
    const w = { view, stage, cards, o };
    // wave: {t0, t1, from:-1.5, to:cols+.5, sigma:.85, skew:.45 (row lag in columns)}
    w.render = function (t, s) {
      const c = s.cam || {};
      const P = o.P;
      stage.style.transform = `translateZ(${P}px) rotateX(${(c.rx || 0).toFixed(3)}deg) rotateY(${(c.ry || 0).toFixed(3)}deg) translateZ(${-P}px) translate3d(${(-(c.x || 0)).toFixed(2)}px,${(-(c.y || 0)).toFixed(2)}px,${(-(c.z || 0)).toFixed(2)}px)`;
      const wv = s.wave;
      for (const k of cards) {
        let a = 0;
        if (wv) {
          const pos = E.kf(t, [[wv.t0, wv.from === undefined ? -1.5 : wv.from], [wv.t1, wv.to === undefined ? o.cols + 0.5 : wv.to, wv.ease || 'sio']]);
          const d = k.i + k.j * (wv.skew === undefined ? 0.45 : wv.skew) - pos, sg = wv.sigma || 0.85;
          a = Math.exp(-(d * d) / (2 * sg * sg));
        }
        // tilt toward the camera as the light passes, lifting off the wall a little
        k.el.style.transform = `translate3d(${k.x.toFixed(2)}px,${k.y.toFixed(2)}px,${(k.z + a * o.lift).toFixed(2)}px) rotateY(${(-k.phi * 180 / Math.PI + a * o.tilt * 0.55).toFixed(3)}deg) rotateX(${(a * o.tilt * 0.45).toFixed(3)}deg)`;
        k.light.style.opacity = (a * 0.85).toFixed(3);
      }
    };
    return w;
  };
  // film camera, ONE named move per shot, eased in and out (default sine.inOut):
  // shot = {move:'crane'|'dolly'|'orbit'|'push', t0, t1, from:{x,y,z,rx,ry}, to:{...}, ease}
  // pose: x/y = the wall point in the middle of the frame (y down), z < 0 = closer to the wall,
  // rx > 0 = looking up, ry > 0 = looking right. Presets when from/to are omitted: crane = rises from low and
  // close, looking up, to level; dolly = travels along the wall; orbit = swings around it; push = moves in.
  E.filmMoves = {
    crane: { from: { y: 380, z: -350, rx: 9 }, to: { y: -60, z: 0, rx: 0 } },
    dolly: { from: { x: -450, z: -150, ry: 5 }, to: { x: 450, z: -150, ry: -5 } },
    orbit: { from: { x: -350, ry: 14 }, to: { x: 350, ry: -14 } },
    push: { from: { z: 0 }, to: { z: -450 } },
  };
  E.filmCam = function (t, shot) {
    const pre = E.filmMoves[shot.move] || {};
    const a = Object.assign({ x: 0, y: 0, z: 0, rx: 0, ry: 0 }, shot.from || pre.from), b = Object.assign({ x: 0, y: 0, z: 0, rx: 0, ry: 0 }, shot.to || pre.to);
    return E.kf(t, [[shot.t0, a], [shot.t1, b, shot.ease || 'sio']]);
  };
})();
