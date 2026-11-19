// Home hero: tracer particles, plus dye released at the separation points, in the flow past a circular cylinder
// with a von Kármán vortex street.
// Model: potential flow around the cylinder plus shed point vortices (Lamb–Oseen cores) with their
// Milne-Thomson images, so the cylinder surface stays a streamline. Shedding at St = fD/U ≈ 0.2,
// vortices convect at ≈ 0.85 U and slowly decay. Units: lengths in px, velocities in U.
(function () {
  const c = document.getElementById("flow");
  if (!c) return;
  const g = c.getContext("2d");
  const BG = "243,245,247", INK = "31,41,51", MAROON = "130,36,51";
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ST = 0.2, UC = 0.85, TWO_PI = 2 * Math.PI, DYE_RATE = 160;
  let W, H, R, cx, cy, S, T, P = [], D = [], emit = 0, V = [], t = 0, nextShed = 0, side = 1;
  let last = null, visible = true, running = false;

  function size() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = c.clientWidth; H = c.clientHeight;
    c.width = W * dpr; c.height = H * dpr;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    const wide = W > 720;
    R = Math.min(H * 0.09, W * 0.045);
    cx = W * (wide ? 0.6 : 0.3); cy = H * 0.5;
    S = W / 9;                       // px per second for U = 1
    T = 2 * R / (ST * S);            // shedding period, s
    t = 0; nextShed = 0; side = 1; V = []; D = []; emit = 0;
    // Develop the vortex street over the whole canvas before drawing.
    const warm = (W - cx) / (UC * S) + 2 * T;
    for (let k = 0; k < warm * 30; k++) vortices(1 / 30);
    g.fillStyle = "rgb(" + BG + ")"; g.fillRect(0, 0, W, H);
    const n = Math.round(W * H / 650);
    P = [];
    for (let i = 0; i < n; i++) P.push(spawn(Math.random() * W));
    for (let i = 0; i < Math.ceil((W - cx) / (UC * S) * 60); i++) step(1 / 60);
  }

  function spawn(x0) {
    let p;
    do {
      p = { x: x0, y: Math.random() * H };
      x0 = -10 - Math.random() * 40;
    } while (Math.hypot(p.x - cx, p.y - cy) < R * 1.05);
    return p;
  }

  // Vortex kinematics (coordinates relative to the cylinder centre, y up).
  function vortices(dt) {
    t += dt;
    if (t >= nextShed) {
      // Alternate sides: the upper shear layer sheds clockwise vortices (Γ < 0).
      V.push({ x: 1.1 * R, y: side * 0.55 * R, s: side, age: 0 });
      side = -side; nextShed += T / 2;
    }
    const Tf = T / 2, G = 3 * R;
    for (const v of V) {
      v.age += dt;
      if (v.age < Tf) {
        // Formation: the vortex grows behind the cylinder, fed by the shear layer.
        const a = v.age / Tf, sm = a * a * (3 - 2 * a);
        v.x = R * (1.1 + 1.0 * a); v.y = v.s * 0.55 * R;
        v.G = -v.s * G * sm;
      } else {
        const a = v.age - Tf;
        v.x += S * dt * (UC - (UC - 0.45) * Math.exp(-a / (0.6 * T)));
        v.y = v.s * R * (0.55 + 0.4 * (1 - Math.exp(-a / T)));
        v.G = -v.s * G * Math.exp(-a / (8 * T));
      }
      v.sig2 = (0.45 * R) ** 2 * (1 + v.age / T);
    }
    V = V.filter(v => v.x < W - cx + 4 * R);
  }

  function addVortex(out, x, y, x0, y0, G, sig2) {
    const dx = x - x0, dy = y - y0, r2 = dx * dx + dy * dy + 1e-6;
    const k = G / (TWO_PI * r2) * (sig2 ? 1 - Math.exp(-r2 / sig2) : 1);
    out[0] -= k * dy; out[1] += k * dx;
  }

  // Velocity at (px, py) in screen coordinates; returns [u, v] in screen axes.
  const out = [0, 0];
  function vel(px, py) {
    const x = px - cx, y = cy - py, r2 = x * x + y * y, R2 = R * R;
    out[0] = 1 - R2 * (x * x - y * y) / (r2 * r2);
    out[1] = -2 * R2 * x * y / (r2 * r2);
    for (const v of V) {
      addVortex(out, x, y, v.x, v.y, v.G, v.sig2);
      const q = R2 / (v.x * v.x + v.y * v.y);       // image point R²/conj(z0)
      addVortex(out, x, y, v.x * q, v.y * q, -v.G, 0);
      addVortex(out, x, y, 0, 0, v.G, 0);
    }
    return [out[0], -out[1]];
  }

  // Move one tracer by dt; returns false once it has left the canvas.
  function advance(p, dt) {
    const [u, v] = vel(p.x, p.y);
    let nx = p.x + u * S * dt, ny = p.y + v * S * dt;
    // Small-scale wake turbulence: a weak random walk downstream of the body.
    const wx = nx - cx;
    if (wx > R) {
      const amp = Math.exp(-((ny - cy) ** 2) / (2 * (1.6 * R) ** 2)) * Math.min(1, (wx - R) / (3 * R));
      nx += (Math.random() - 0.5) * 0.8 * amp; ny += (Math.random() - 0.5) * 0.8 * amp;
    }
    // No penetration: a tracer that a finite time step pushes inside is put back on the surface.
    const dx = nx - cx, dy = ny - cy, d = Math.hypot(dx, dy), R1 = R * 1.02;
    if (d < R1) { nx = cx + dx / d * R1; ny = cy + dy / d * R1; }
    g.beginPath(); g.moveTo(p.x, p.y); g.lineTo(nx, ny); g.stroke();
    p.x = nx; p.y = ny;
    return !(p.x > W + 10 || p.x < -60 || p.y < -10 || p.y > H + 10);
  }

  function step(dt) {
    vortices(dt);
    g.fillStyle = "rgba(" + BG + ",0.16)";
    g.fillRect(0, 0, W, H);
    g.lineCap = "round";
    g.lineWidth = 1.4; g.strokeStyle = "rgba(" + INK + ",0.4)";
    for (let i = 0; i < P.length; i++) if (!advance(P[i], dt)) P[i] = spawn(-10);
    // Dye released near the separation points (about 80° from the front stagnation point):
    // its streaklines show the separated shear layers rolling up into the vortex street.
    emit += dt * DYE_RATE * Math.min(1, R / 40);
    for (; emit >= 1; emit--) {
      const s = Math.random() < 0.5 ? 1 : -1, th = (100 + (Math.random() - 0.5) * 10) * Math.PI / 180;
      const r = R * (1.04 + Math.random() * 0.08);
      D.push({ x: cx + r * Math.cos(th), y: cy - s * r * Math.sin(th) });
    }
    g.lineWidth = 1.6; g.strokeStyle = "rgba(" + MAROON + ",0.7)";
    D = D.filter(p => advance(p, dt));
    g.fillStyle = "rgb(" + MAROON + ")";
    g.beginPath(); g.arc(cx, cy, R, 0, TWO_PI); g.fill();
  }

  function frame(now) {
    if (!visible || document.hidden) { running = false; last = null; return; }
    if (last === null) last = now;
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    step(dt);
    requestAnimationFrame(frame);
  }

  function start() {
    if (still || running) return;
    running = true;
    requestAnimationFrame(frame);
  }

  size();
  start();
  // Pause when the hero is off screen or the tab is hidden.
  new IntersectionObserver(e => { visible = e[0].isIntersecting; if (visible) start(); }).observe(c);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) start(); });
  let lastW = c.clientWidth, lastH = c.clientHeight;
  new ResizeObserver(() => {
    if (c.clientWidth !== lastW || c.clientHeight !== lastH) {
      lastW = c.clientWidth; lastH = c.clientHeight; size();
    }
  }).observe(c);
})();
