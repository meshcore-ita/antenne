// Vista 3D: diagramma di irradiazione, correnti sui fili e geometria dell'antenna, con three.js
// incluso nel sito (nessun CDN). Dati da <script type="application/json" id="antenna-data">,
// controlli da .vtools, righe del file NEC spiegato da #nec (.nl[data-tag]) per i collegamenti 3D <-> listato.
import * as THREE from "three";
import { OrbitControls } from "three/addons/OrbitControls.js";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
const fmt = (x, d = 1) => x.toLocaleString("it-IT", { minimumFractionDigits: d, maximumFractionDigits: d }).replace("-", "−");

async function copyText(text) {
  try { await navigator.clipboard.writeText(text); return true; } catch { /* permessi o contesto non sicuro: ripiego sotto */ }
  const ta = Object.assign(document.createElement("textarea"), { value: text });
  ta.style.cssText = "position:fixed;opacity:0";
  document.body.appendChild(ta);
  ta.select();
  try { return document.execCommand("copy"); } catch { return false; } finally { ta.remove(); }
}

// --- bottone "Copia" del file NEC (funziona anche senza WebGL) ---------------------------------
function setupCopy() {
  const btn = $("#copy-nec"), msg = $("#copy-msg");
  if (!btn) return;
  let timer;
  const say = t => { msg.textContent = t; clearTimeout(timer); timer = setTimeout(() => { msg.textContent = ""; }, 2500); };
  btn.addEventListener("click", async () => {
    let text;
    try {
      const res = await fetch("antenna.nec");
      if (!res.ok) throw new Error(res.status);
      text = await res.text();
    } catch {
      text = $$("#nec .src").map(e => e.textContent).join("\n") + "\n";
    }
    say(await copyText(text) ? "Copiato negli appunti." : "Copia non riuscita: usa Scarica.");
  });
}

// --- palette: MeshCore ITA per il diagramma, "calore" per le correnti ---------------------------
const PAT_STOPS = [[0, "#1e3a8a"], [0.45, "#22c55e"], [0.75, "#facc15"], [1, "#e11d48"]];
const HEAT_STOPS = [[0, "#52607a"], [0.3, "#7c3aed"], [0.65, "#f97316"], [1, "#fde047"]];
const cssGradient = stops => `linear-gradient(90deg,${stops.map(([t, c]) => `${c} ${t * 100}%`).join(",")})`;
function makeLut(stops) {                         // 256 colori RGB (spazio di lavoro lineare di three.js)
  const cs = stops.map(([t, c]) => [t, new THREE.Color(c)]), lut = new Float32Array(256 * 3), tmp = new THREE.Color();
  for (let i = 0; i < 256; i++) {
    const t = i / 255;
    let k = 1;
    while (k < cs.length - 1 && t > cs[k][0]) k++;
    const [t0, c0] = cs[k - 1], [t1, c1] = cs[k];
    tmp.copy(c0).lerp(c1, Math.min(1, Math.max(0, (t - t0) / (t1 - t0)))).toArray(lut, i * 3);
  }
  return lut;
}

function init(data, ui) {
  const { th, ph, g, gmax, theta, phi, ground, wires, cur, feed, nets } = data;
  const host = ui.host;
  const FLOOR = -30, UP = 3, D2R = Math.PI / 180;
  const PAT = makeLut(PAT_STOPS), HEAT = makeLut(HEAT_STOPS);

  // --- renderer, scena, camera -----------------------------------------------------------------
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    if (!renderer.getContext()) throw new Error("no context");
  } catch {
    return false;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  host.insertBefore(renderer.domElement, host.firstChild);
  const dom = renderer.domElement;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 100);
  camera.up.set(0, 0, 1);                           // NEC: z verso l'alto
  scene.add(new THREE.HemisphereLight(0xffffff, 0x0b1220, 1.1));
  const key = new THREE.DirectionalLight(0xffffff, 1.6);
  key.position.set(3, -2, 4);
  scene.add(key);

  const controls = new OrbitControls(camera, dom);
  controls.enableDamping = true;
  controls.autoRotateSpeed = 0.8;
  controls.minDistance = 1.2;
  controls.maxDistance = 8;

  const state = { mode: "both", scale: "db", cur: true, phase: false, cuts: false, rot: !reduceMotion };
  let visible = true, raf = 0, tween = null, hoverPause = false;
  function request() { if (!raf && visible) raf = requestAnimationFrame(frame); }

  // --- campo del diagramma: dB sotto il massimo, interpolazione di Catmull-Rom ------------------
  const nth = th.length, NPH = ph[ph.length - 1] - ph[0] >= 360 - 1e-6 ? ph.length - 1 : ph.length;
  const dth = th[1] - th[0], dph = ph[1] - ph[0];
  const fullSphere = th[nth - 1] >= 179.99;         // spazio libero: due poli; sul terreno solo l'emisfero superiore
  const half = Math.round(NPH / 2);
  const V = g.map(row => Float32Array.from(row.slice(0, NPH), v => Math.max(v - gmax, FLOOR)));
  function node(i, j) {                             // campione con chiusura ai poli e in φ
    if (i < 0) { i = -i; j += half; }
    else if (i > nth - 1) { if (fullSphere) { i = 2 * (nth - 1) - i; j += half; } else i = nth - 1; }
    return V[i][((j % NPH) + NPH) % NPH];
  }
  const cr = (a, b, c, d, t) => b + 0.5 * t * (c - a + t * (2 * a - 5 * b + 4 * c - d + t * (3 * (b - c) + d - a)));
  function sample(t, p) {                           // dB relativi al massimo in (θ, φ) gradi
    const fi = (t - th[0]) / dth, fj = ((((p - ph[0]) / dph) % NPH) + NPH) % NPH;
    const i = Math.floor(fi), j = Math.floor(fj), u = fi - i, w = fj - j;
    const row = a => cr(node(i + a, j - 1), node(i + a, j), node(i + a, j + 1), node(i + a, j + 2), w);
    return Math.min(0, Math.max(FLOOR, cr(row(-1), row(0), row(1), row(2), u)));
  }
  const radiusOf = db => state.scale === "db" ? (db - FLOOR) / -FLOOR : 10 ** (db / 10);
  const dirOf = (t, p, out) => out.set(Math.sin(t * D2R) * Math.cos(p * D2R), Math.sin(t * D2R) * Math.sin(p * D2R), Math.cos(t * D2R));

  // --- trasformazione della geometria: centrata e ingrandita dentro il diagramma -----------------
  const pts = wires.flatMap(w => [w.slice(0, 3), w.slice(3, 6)]);
  const lo = [0, 1, 2].map(k => Math.min(...pts.map(p => p[k])));
  const hi = [0, 1, 2].map(k => Math.max(...pts.map(p => p[k])));
  const ctr = lo.map((v, k) => (v + hi[k]) / 2);
  if (ground) ctr[2] = lo[2];                       // sul terreno l'antenna poggia sul disco
  const ext = Math.max(...pts.map(p => Math.hypot(p[0] - ctr[0], p[1] - ctr[1], p[2] - ctr[2]))) || 1;
  const sc = 0.55 / ext;
  const T = p => new THREE.Vector3((p[0] - ctr[0]) * sc, (p[1] - ctr[1]) * sc, (p[2] - ctr[2]) * sc);

  // --- etichette HTML proiettate sullo schermo --------------------------------------------------
  const labels = [];
  const labelHost = $(".vlabels", host);
  function addLabel(text, pos, cls = "", group = () => true) {
    const el = Object.assign(document.createElement("span"), { className: `vlab ${cls}`, textContent: text });
    labelHost.appendChild(el);
    const lab = { el, pos, group };
    labels.push(lab);
    return lab;
  }
  const _p = new THREE.Vector3();
  let W = 1, H = 1;
  function updateLabels() {
    const q0 = _p.copy(ringLabels[0].pos).project(camera), x0 = q0.x * W, y0 = q0.y * H;
    const q2 = _p.copy(ringLabels[2].pos).project(camera);
    ringsFit = Math.hypot(q2.x * W - x0, q2.y * H - y0) > 90;
    for (const l of labels) {
      _p.copy(l.pos).project(camera);
      const show = l.group() && _p.z < 1 && Math.abs(_p.x) < 1.2 && Math.abs(_p.y) < 1.2;
      l.el.style.display = show ? "" : "none";
      if (!show) continue;
      l.w ??= l.el.offsetWidth;                    // le etichette larghe restano dentro il riquadro
      const x = Math.min(W - l.w / 2 - 4, Math.max(l.w / 2 + 4, (_p.x + 1) / 2 * W));
      l.el.style.transform = `translate(${x.toFixed(1)}px,${((1 - _p.y) / 2 * H).toFixed(1)}px) translate(-50%,-50%)`;
    }
  }

  // --- assi, orizzonte, terreno ------------------------------------------------------------------
  const axes = new THREE.AxesHelper(1.25);
  axes.material.transparent = true;
  axes.material.opacity = 0.55;
  scene.add(axes);
  [["X", [1.34, 0, 0], "#f87171"], ["Y", [0, 1.34, 0], "#4ade80"], ["Z", [0, 0, 1.34], "#60a5fa"]].forEach(([t, p, c]) =>
    addLabel(t, new THREE.Vector3(...p), "").el.style.color = c);

  const gridGroup = new THREE.Group();
  scene.add(gridGroup);
  let ringsFit = true;                              // le etichette dei cerchi si nascondono quando si sovrappongono
  const ringLabels = [0, 1, 2].map(() => addLabel("", new THREE.Vector3(), "dim", () => state.mode !== "geom" && ringsFit));
  if (ground) {
    const disk = new THREE.Mesh(new THREE.CircleGeometry(1.08, 72), new THREE.MeshBasicMaterial({
      color: 0x16311f, transparent: true, opacity: 0.55, side: THREE.DoubleSide, depthWrite: false }));
    disk.position.z = -0.003;
    scene.add(disk);
    addLabel("terreno", new THREE.Vector3(-0.75, -0.75, 0), "dim");
  }

  // --- diagramma ---------------------------------------------------------------------------------
  const pattern = new THREE.Group();
  scene.add(pattern);
  const surfMat = new THREE.MeshStandardMaterial({
    vertexColors: true, roughness: 0.5, metalness: 0.05, transparent: true, opacity: 0.55,
    side: THREE.DoubleSide, depthWrite: false });
  const surface = new THREE.Mesh(new THREE.BufferGeometry(), surfMat);
  const graticule = new THREE.LineSegments(new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.1 }));
  const pickMesh = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
  const cutsGroup = new THREE.Group();
  pattern.add(surface, graticule, cutsGroup);
  const cutLabels = [
    addLabel(`taglio conico θ = ${theta}°`, new THREE.Vector3(), "", () => cutsGroup.visible),
    addLabel(`taglio verticale φ = ${phi}°`, new THREE.Vector3(), "", () => cutsGroup.visible)];
  let coneOk = true;
  cutLabels[0].group = () => cutsGroup.visible && coneOk;
  cutLabels[0].el.style.color = "#38bdf8";
  cutLabels[1].el.style.color = "#f472b6";

  function surfaceGeometry(up, withColor) {         // reticolo (θ, φ) sovracampionato di `up`; φ chiuso modulo NPH
    const R = (nth - 1) * up + 1, C = NPH * up;
    const pos = new Float32Array(R * C * 3), col = withColor ? new Float32Array(R * C * 3) : null, d = new THREE.Vector3();
    for (let r = 0; r < R; r++) {
      for (let c = 0; c < C; c++) {
        const t = th[0] + r * dth / up, p = ph[0] + c * dph / up;
        const db = sample(t, p), rr = radiusOf(db), k = (r * C + c) * 3;
        dirOf(t, p, d).multiplyScalar(rr).toArray(pos, k);
        if (col) { const i = Math.round(Math.min(1, Math.max(0, radiusOf(db))) * 255) * 3; col.set(PAT.subarray(i, i + 3), k); }
      }
    }
    const idx = new Uint32Array((R - 1) * C * 6);
    let n = 0;
    for (let r = 0; r < R - 1; r++) {
      for (let c = 0; c < C; c++) {
        const a = r * C + c, b = r * C + (c + 1) % C, e = (r + 1) * C + (c + 1) % C, f = (r + 1) * C + c;
        idx.set([a, f, b, b, f, e], n);
        n += 6;
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    if (col) geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
    geo.setIndex(new THREE.BufferAttribute(idx, 1));
    return { geo, R, C };
  }

  function buildScale() {                           // tutto ciò che dipende dalla scala (dB o lineare)
    surface.geometry.dispose();
    graticule.geometry.dispose();
    pickMesh.geometry.dispose();
    const { geo, R, C } = surfaceGeometry(UP, true);
    geo.computeVertexNormals();
    geo.computeBoundingSphere();
    surface.geometry = geo;
    const lines = [];                                // meridiani e paralleli ogni 10° (si appoggiano ai vertici della mesh)
    const step = Math.max(1, Math.round(10 / dph)) * UP;
    for (let c = 0; c < C; c += step) for (let r = 0; r < R - 1; r++) lines.push(r * C + c, (r + 1) * C + c);
    for (let r = step; r < R - (fullSphere ? 1 : 0); r += Math.max(1, Math.round(10 / dth)) * UP) for (let c = 0; c < C; c++) lines.push(r * C + c, r * C + (c + 1) % C);
    const gl = new THREE.BufferGeometry();
    gl.setAttribute("position", geo.getAttribute("position"));
    gl.setIndex(lines);
    graticule.geometry = gl;
    pickMesh.geometry = surfaceGeometry(1, false).geo;
    pickMesh.geometry.computeBoundingSphere();

    // orizzonte: raggi ogni 30° e cerchi ai livelli di riferimento
    gridGroup.children.slice().forEach(o => { o.geometry.dispose(); o.material.dispose(); gridGroup.remove(o); });
    const radii = state.scale === "db" ? [[1 / 3, "−20 dB"], [2 / 3, "−10 dB"], [1, "0 dB"]] : [[0.1, "−10 dB"], [0.5, "−3 dB"], [1, "0 dB"]];
    const gp = [];
    for (let a = 0; a < 360; a += 30) gp.push(0, 0, 0, 1.05 * Math.cos(a * D2R), 1.05 * Math.sin(a * D2R), 0);
    for (const [rr] of radii) for (let s = 0; s < 96; s++) {
      const a0 = s / 96 * 2 * Math.PI, a1 = (s + 1) / 96 * 2 * Math.PI;
      gp.push(rr * Math.cos(a0), rr * Math.sin(a0), 0, rr * Math.cos(a1), rr * Math.sin(a1), 0);
    }
    const gg = new THREE.BufferGeometry();
    gg.setAttribute("position", new THREE.Float32BufferAttribute(gp, 3));
    gridGroup.add(new THREE.LineSegments(gg, new THREE.LineBasicMaterial({ color: 0x4b5a50, transparent: true, opacity: 0.55 })));
    radii.forEach(([rr, t], k) => { ringLabels[k].el.textContent = t; ringLabels[k].pos.set(rr * Math.cos(2.36), rr * Math.sin(2.36), 0); });

    // i due tagli dei grafici SVG: conico a θmax e piano verticale per φmax
    cutsGroup.children.slice().forEach(o => { o.geometry.dispose(); o.material.dispose(); cutsGroup.remove(o); });
    const at = (t, p) => dirOf(t, p, new THREE.Vector3()).multiplyScalar(radiusOf(sample(t, p)) * 1.004);
    const tube = (list, closed, color) => {
      const geoT = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(list, closed), list.length * 2, 0.007, 5, closed);
      cutsGroup.add(new THREE.Mesh(geoT, new THREE.MeshBasicMaterial({ color })));
    };
    const tMax = th[nth - 1], cone = [], vert = [];
    coneOk = theta > 1 && theta < (fullSphere ? 179 : Infinity);      // ai poli il taglio conico degenera in un punto
    if (coneOk) {
      for (let p = 0; p < 360; p += 2.5) cone.push(at(theta, p));
      tube(cone, true, 0x38bdf8);
      cutLabels[0].pos.copy(at(theta, phi + 200));
    }
    for (let t = tMax; t >= 0; t -= 2.5) vert.push(at(t, phi + 180));
    for (let t = 2.5; t <= tMax - (fullSphere ? 2.5 : 0); t += 2.5) vert.push(at(t, phi));
    tube(vert, fullSphere, 0xf472b6);
    cutLabels[1].pos.copy(at(tMax * 0.62, phi));

    ui.legend.pat.lo.textContent = state.scale === "db" ? `${FLOOR} dB`.replace("-", "−") : "0";
    ui.legend.pat.hi.textContent = state.scale === "db" ? `${fmt(gmax)} dBi` : `100% · ${fmt(gmax)} dBi`;
    request();
  }

  // freccia del lobo principale
  const lobeDir = dirOf(theta, phi, new THREE.Vector3());
  {
    const mat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), lobeDir);
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.007, 1.08, 8), mat);
    shaft.position.copy(lobeDir).multiplyScalar(0.54);
    const head = new THREE.Mesh(new THREE.ConeGeometry(0.035, 0.12, 14), mat);
    head.position.copy(lobeDir).multiplyScalar(1.14);
    shaft.quaternion.copy(q);
    head.quaternion.copy(q);
    pattern.add(shaft, head);
    addLabel(`lobo principale ${fmt(gmax)} dBi`, lobeDir.clone().multiplyScalar(1.3), "lobe", () => pattern.visible);
  }
  // marcatore del punto sotto il mouse sul diagramma
  const marker = new THREE.Group();
  marker.visible = false;
  const markerLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]),
    new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.6 }));
  const markerDot = new THREE.Mesh(new THREE.SphereGeometry(0.018, 14, 10), new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false }));
  markerDot.renderOrder = 6;
  marker.add(markerLine, markerDot);
  pattern.add(marker);

  // --- antenna: un cilindro istanziato per segmento, colorato dalla corrente -----------------------
  const antenna = new THREE.Group();
  scene.add(antenna);
  const total = wires.reduce((s, w) => s + w[8], 0);
  const inst = new THREE.InstancedMesh(new THREE.CylinderGeometry(1, 1, 1, 8, 1),
    new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.25, roughness: 0.4 }), total);
  inst.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(total * 3), 3);
  inst.frustumCulled = false;
  antenna.add(inst);
  const amp = new Float32Array(total), phs = new Float32Array(total);
  const METAL = new THREE.Color(0xd4a373).toArray();
  const Y = new THREE.Vector3(0, 1, 0), unitHl = new THREE.CylinderGeometry(1, 1, 1, 12, 1);
  const byTag = new Map(), wd = [];
  {
    const m = new THREE.Matrix4(), q = new THREE.Quaternion(), pa = new THREE.Vector3(), pb = new THREE.Vector3(), s = new THREE.Vector3();
    let k = 0;
    wires.forEach(w => {
      const a = T(w.slice(0, 3)), b = T(w.slice(3, 6)), r = Math.max(w[6] * sc, 0.011), segs = w[8];
      const rec = { a, b, r, tag: w[7], line: w[9], segs, off: k };
      wd.push(rec);
      if (!byTag.has(rec.tag)) byTag.set(rec.tag, []);
      byTag.get(rec.tag).push(rec);
      pb.subVectors(b, a);
      s.set(r, pb.length() / segs, r);
      q.setFromUnitVectors(Y, pb.normalize());
      for (let i = 0; i < segs; i++, k++) {
        inst.setMatrixAt(k, m.compose(pa.copy(a).lerp(b, (i + 0.5) / segs), q, s));
        const c = cur[k] || [0, 0];
        amp[k] = c[0];
        phs[k] = c[1] * D2R;
      }
    });
  }
  function paintSegments(now) {
    const arr = inst.instanceColor.array, wt = now * 0.00262;   // un periodo ogni ≈2,4 s
    for (let k = 0; k < total; k++) {
      if (!state.cur) { arr[k * 3] = METAL[0]; arr[k * 3 + 1] = METAL[1]; arr[k * 3 + 2] = METAL[2]; continue; }
      let a = amp[k];
      if (state.phase) a *= 0.3 + 0.7 * (0.5 + 0.5 * Math.cos(wt + phs[k]));
      const i = Math.min(255, Math.round(a * 255)) * 3;
      arr[k * 3] = HEAT[i]; arr[k * 3 + 1] = HEAT[i + 1]; arr[k * 3 + 2] = HEAT[i + 2];
    }
    inst.instanceColor.needsUpdate = true;
  }

  // punto di alimentazione e filo che lo contiene
  const feedP = T(feed);
  let feedWire = wd[0], feedSeg = 0;
  {
    let best = Infinity;
    for (const w of wd) {
      const ab = new THREE.Vector3().subVectors(w.b, w.a);
      const u = Math.min(1, Math.max(0, new THREE.Vector3().subVectors(feedP, w.a).dot(ab) / ab.lengthSq()));
      const d = new THREE.Vector3().copy(w.a).addScaledVector(ab, u).distanceTo(feedP);
      if (d < best) { best = d; feedWire = w; feedSeg = Math.min(w.segs - 1, Math.floor(u * w.segs)); }
    }
  }
  const feedMesh = new THREE.Mesh(new THREE.SphereGeometry(Math.max(feedWire.r * 2.2, 0.022), 20, 12),
    new THREE.MeshStandardMaterial({ color: 0x22c55e, emissive: 0x22c55e, emissiveIntensity: 0.6 }));
  feedMesh.position.copy(feedP);
  antenna.add(feedMesh);

  // linee di trasmissione e reti fra segmenti: tratteggiate
  if (nets.length) {
    const np = nets.flatMap(n => [...T(n.slice(0, 3)).toArray(), ...T(n.slice(3, 6)).toArray()]);
    const geoN = new THREE.BufferGeometry();
    geoN.setAttribute("position", new THREE.Float32BufferAttribute(np, 3));
    const ln = new THREE.LineSegments(geoN, new THREE.LineDashedMaterial({ color: 0xfacc15, dashSize: 0.03, gapSize: 0.02 }));
    ln.computeLineDistances();
    antenna.add(ln);
    nets.forEach(n => addLabel(n[6], T(n.slice(0, 3)).add(T(n.slice(3, 6))).multiplyScalar(0.5), "", () => antenna.visible));
  }

  // --- evidenziazione: collegamento fra vista 3D e listato NEC ------------------------------------
  const necBox = $("#nec");
  const rows = $$(".nl[data-tag]", necBox || document.createElement("div"));
  const exRow = rows.find(r => r.dataset.card === "EX");
  const hlGroup = new THREE.Group();
  antenna.add(hlGroup);
  const hlMat = new THREE.MeshBasicMaterial({ color: 0x67e8f9, transparent: true, opacity: 0.5, depthTest: false });
  let hov3d = null, hovRow = null, pin = null, shown = null;
  const rowsByTag = new Map();
  rows.forEach(r => { const t = Number(r.dataset.tag); rowsByTag.set(t, [...(rowsByTag.get(t) || []), r]); });
  const rowsOf = a => a ? (rowsByTag.get(a.tag) || []).filter(r => (r.dataset.card === "EX") === a.feed) : [];
  const mark = (cls, prev, next) => { prev.forEach(r => r.classList.remove(cls)); next.forEach(r => r.classList.add(cls)); return next; };
  let hlRows = [], selRows = [];
  const same = (a, b) => (a && a.tag) === (b && b.tag) && (a && a.feed) === (b && b.feed);
  function refreshActive() {
    const a = hovRow || hov3d || pin;
    hlRows = mark("hl", hlRows, rowsOf(a));
    selRows = mark("sel", selRows, rowsOf(pin));
    if (same(a, shown)) return;
    shown = a;
    hlGroup.children.slice().forEach(o => hlGroup.remove(o));
    const q = new THREE.Quaternion(), d = new THREE.Vector3();
    for (const w of (a && byTag.get(a.tag)) || []) {
      const m = new THREE.Mesh(unitHl, hlMat);
      d.subVectors(w.b, w.a);
      m.position.copy(w.a).addScaledVector(d, 0.5);
      m.quaternion.copy(q.setFromUnitVectors(Y, d.clone().normalize()));
      m.scale.set(w.r * 1.7 + 0.004, d.length() * 1.002, w.r * 1.7 + 0.004);
      m.renderOrder = 5;
      hlGroup.add(m);
    }
    feedMesh.scale.setScalar(a && a.feed ? 1.9 : 1);
    request();
  }

  function reveal(line) {                           // apre l'eventuale serie compressa e porta la riga in vista
    const row = document.getElementById(`L${line}`);
    if (!row) return;
    const det = row.closest("details");
    if (det && !det.open) det.open = true;
    row.scrollIntoView({ block: "center", behavior: reduceMotion ? "auto" : "smooth" });
    row.classList.remove("flash");
    void row.offsetWidth;
    row.classList.add("flash");
  }
  if (necBox) {
    const rowOf = e => e.target.closest?.(".nl[data-tag]");
    const asSel = r => ({ tag: Number(r.dataset.tag), feed: r.dataset.card === "EX" });
    necBox.addEventListener("pointerover", e => { const r = rowOf(e); if (r && hovRow?.row !== r) { hovRow = { ...asSel(r), row: r }; refreshActive(); } });
    necBox.addEventListener("pointerout", e => { const r = rowOf(e); if (r && !r.contains(e.relatedTarget)) { hovRow = null; refreshActive(); } });
    necBox.addEventListener("focusin", e => { const r = rowOf(e); if (r) { hovRow = { ...asSel(r), row: r }; refreshActive(); } });
    necBox.addEventListener("focusout", e => { if (rowOf(e)) { hovRow = null; refreshActive(); } });
    necBox.addEventListener("click", e => {
      const r = rowOf(e);
      if (!r || e.target.closest("a.ln")) return;
      const s = asSel(r);
      pin = e.target.closest("a.to3d") || !same(pin, s) ? s : null;
      refreshActive();
    });
    necBox.addEventListener("keydown", e => {
      const r = rowOf(e);
      if (r && r === e.target && (e.key === "Enter" || e.key === " ")) {
        e.preventDefault();
        const s = asSel(r);
        pin = same(pin, s) ? null : s;
        refreshActive();
      }
    });
  }

  // --- puntamento: filo/alimentazione sullo schermo, diagramma con raycast -------------------------
  const raycaster = new THREE.Raycaster();
  const sa = new THREE.Vector3(), sb = new THREE.Vector3();
  const toPx = (v, out) => { out.copy(v).project(camera); out.x = (out.x + 1) / 2 * W; out.y = (1 - out.y) / 2 * H; return out; };
  function pick(x, y, touch) {
    if (antenna.visible) {
      const thr = touch ? 22 : 10;
      toPx(feedP, sa);
      if (sa.z < 1 && Math.hypot(sa.x - x, sa.y - y) < thr + 3) return { kind: "feed" };
      let best = null;
      for (const w of wd) {
        toPx(w.a, sa);
        toPx(w.b, sb);
        if (sa.z > 1 && sb.z > 1) continue;
        const dx = sb.x - sa.x, dy = sb.y - sa.y, l2 = dx * dx + dy * dy;
        const u = l2 ? Math.min(1, Math.max(0, ((x - sa.x) * dx + (y - sa.y) * dy) / l2)) : 0;
        const d = Math.hypot(sa.x + dx * u - x, sa.y + dy * u - y), z = sa.z + (sb.z - sa.z) * u;
        if (d < thr && (!best || d < best.d - 2 || (d < best.d + 2 && z < best.z))) best = { kind: "wire", w, u, d, z };
      }
      if (best) return best;
    }
    if (pattern.visible) {
      raycaster.setFromCamera({ x: x / W * 2 - 1, y: -(y / H) * 2 + 1 }, camera);
      const hit = raycaster.intersectObject(pickMesh, false)[0];
      if (hit) {
        const p = hit.point, r = p.length();
        const t = Math.acos(p.z / r) / D2R, f = (Math.atan2(p.y, p.x) / D2R + 360) % 360;
        const i = Math.min(nth - 1, Math.max(0, Math.round((t - th[0]) / dth))), j = Math.round((f - ph[0]) / dph) % NPH;
        return { kind: "pattern", point: p, i, j };
      }
    }
    return null;
  }

  const tip = $(".vtip", host);
  function showTip(x, y, title, lines, color, hint) {
    const b = document.createElement("b");
    if (color) { const i = document.createElement("i"); i.style.background = color; b.appendChild(i); }
    b.append(title);
    const line = (tag, text) => { const e = document.createElement(tag); e.textContent = text; e.style.display = "block"; return e; };
    tip.replaceChildren(b, ...lines.map(t => line("span", t)), ...(hint ? [line("small", hint)] : []));
    tip.hidden = false;
    const tw = tip.offsetWidth, tipH = tip.offsetHeight;
    const px = x + 16 + tw > W - 4 ? Math.max(4, x - 16 - tw) : x + 16, py = y + 16 + tipH > H - 4 ? Math.max(4, y - 16 - tipH) : y + 16;
    tip.style.transform = `translate(${px}px,${py}px)`;
  }
  const hideTip = () => { tip.hidden = true; };

  let hoverHit = null;
  function hoverAt(x, y, touch) {
    const hit = pick(x, y, touch);
    hoverHit = hit;
    hov3d = hit?.kind === "wire" ? { tag: hit.w.tag, feed: false } : hit?.kind === "feed" ? { tag: feedWire.tag, feed: true } : null;
    refreshActive();
    marker.visible = hit?.kind === "pattern";
    host.style.cursor = hit && hit.kind !== "pattern" ? "pointer" : "";
    if (!hit) { hideTip(); request(); return; }
    if (hit.kind === "wire") {
      const w = hit.w, k = Math.min(w.segs - 1, Math.floor(hit.u * w.segs)), c = cur[w.off + k] || [0, 0];
      showTip(x, y, `Filo ${w.tag} — riga ${w.line}`,
        [`segmento ${k + 1} di ${w.segs}`, `corrente ${fmt(c[0] * 100, 0)}% del massimo, fase ${fmt(c[1], 0)}°`],
        null, `${touch ? "tocca" : "clic"}: vai alla riga del file NEC`);
    } else if (hit.kind === "feed") {
      const line = exRow ? ` — riga ${exRow.dataset.line}` : "";
      showTip(x, y, `Alimentazione${line}`, [`filo ${feedWire.tag}, segmento ${feedSeg + 1}`, "qui si collega il cavo"], "#22c55e", `${touch ? "tocca" : "clic"}: vai alla riga EX`);
    } else {
      const gv = g[hit.i][hit.j], rel = gv - gmax, t = Math.min(1, Math.max(0, radiusOf(Math.max(rel, FLOOR))));
      const c = new THREE.Color().fromArray(PAT, Math.round(t * 255) * 3).getStyle();
      showTip(x, y, `${fmt(gv)} dBi`, [`θ ${th[hit.i]}° · φ ${ph[hit.j]}°`,
        rel > -0.05 ? "massimo del diagramma" : `${fmt(rel)} dB dal massimo`], c);
      const pa = markerLine.geometry.getAttribute("position");
      pa.setXYZ(1, hit.point.x, hit.point.y, hit.point.z);
      pa.needsUpdate = true;
      markerDot.position.copy(hit.point);
    }
    request();
  }
  let hoverRaf = 0, ptr = null, down = null;
  const local = e => { const r = dom.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  dom.addEventListener("pointerdown", e => { down = { x: e.clientX, y: e.clientY }; hideTip(); });
  dom.addEventListener("pointermove", e => {
    if (e.buttons) return;
    ptr = { e, touch: e.pointerType === "touch" };
    if (!ptr.touch && !hoverRaf) hoverRaf = requestAnimationFrame(() => { hoverRaf = 0; if (ptr) hoverAt(...local(ptr.e), false); });
  });
  dom.addEventListener("pointerenter", e => { if (e.pointerType === "mouse") { hoverPause = true; request(); } });
  dom.addEventListener("pointerleave", e => {
    ptr = null;
    hoverPause = false;
    if (e.pointerType !== "touch") { hoverHit = null; hov3d = null; refreshActive(); marker.visible = false; hideTip(); host.style.cursor = ""; }
    request();
  });
  dom.addEventListener("pointerup", e => {          // tocco o clic senza trascinamento
    if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 6) { down = null; return; }
    down = null;
    const [x, y] = local(e);
    hoverAt(x, y, e.pointerType === "touch");
    const h = hoverHit;
    if (h?.kind === "wire") { pin = { tag: h.w.tag, feed: false }; refreshActive(); reveal(h.w.line); }
    else if (h?.kind === "feed") { pin = { tag: feedWire.tag, feed: true }; refreshActive(); if (exRow) reveal(exRow.dataset.line); }
    else if (pin) { pin = null; refreshActive(); }
  });
  controls.addEventListener("start", () => {
    hideTip();
    if (state.rot) setToggle("rot", false);
  });
  controls.addEventListener("change", request);

  // --- visibilità, viste, pulsanti ----------------------------------------------------------------
  function applyVisibility() {
    pattern.visible = state.mode !== "geom";
    antenna.visible = state.mode !== "pattern";
    cutsGroup.visible = state.cuts && pattern.visible;
    ui.legend.pat.box.hidden = !pattern.visible;
    ui.legend.cur.hidden = !(antenna.visible && state.cur);
    if (!pattern.visible) { marker.visible = false; hideTip(); }
    request();
  }
  const pressed = (sel, on) => $$(sel, ui.bar).forEach(b => b.setAttribute("aria-pressed", String(on(b))));
  function setToggle(name, on) {
    state[name] = on;
    if (name === "phase" && on) state.cur = true;
    if (name === "cur" && !on) state.phase = false;
    for (const n of ["cur", "phase", "cuts", "rot"]) pressed(`[data-toggle=${n}]`, () => state[n]);
    if (name === "cur" || name === "phase") paintSegments(performance.now());
    applyVisibility();
  }

  const lobeH = new THREE.Vector3(lobeDir.x, lobeDir.y, 0);
  if (lobeH.length() < 0.1) lobeH.set(1, 0, 0);
  lobeH.normalize();
  const VIEWS = {                                   // di fronte e di lato sono rispetto al lobo principale
    iso: new THREE.Vector3(2.6, -2.2, 1.6),
    top: new THREE.Vector3(-lobeH.x * 0.02, -lobeH.y * 0.02, 1),
    front: new THREE.Vector3(lobeH.x, lobeH.y, 0.14),
    side: new THREE.Vector3(lobeH.y, -lobeH.x, 0.14),
  };
  function flyTo(name, dist) {                      // name: vista predefinita o null per restare nella direzione attuale
    const dir = name ? VIEWS[name] : camera.position;
    const to = dir.clone().normalize().multiplyScalar(dist ?? Math.min(5, Math.max(1.8, camera.position.length())));
    if (reduceMotion) { camera.position.copy(to); controls.update(); request(); return; }
    tween = { t0: performance.now(), dur: 450, from: camera.position.clone(), to };
    request();
  }
  camera.position.copy(VIEWS.iso).normalize().multiplyScalar(VIEWS.iso.length());

  ui.bar.addEventListener("click", e => {
    const b = e.target.closest("button");
    if (!b || b.disabled) return;
    const d = b.dataset;
    if (d.mode) {
      const wasGeom = state.mode === "geom";
      state.mode = d.mode;
      pressed("[data-mode]", x => x.dataset.mode === d.mode);
      applyVisibility();
      if ((d.mode === "geom") !== wasGeom) flyTo(null, d.mode === "geom" ? 2.1 : 3.7);   // solo antenna: più vicino
    }
    else if (d.scale) {
      state.scale = d.scale;
      pressed("[data-scale]", x => x.dataset.scale === d.scale);
      buildScale();
    } else if (d.toggle) setToggle(d.toggle, !state[d.toggle]);
    else if (d.view) { if (state.rot) setToggle("rot", false); flyTo(d.view); }
    else if (d.act === "reset") {
      controls.target.set(0, 0, 0);
      setToggle("rot", !reduceMotion);
      flyTo("iso", VIEWS.iso.length());
    } else if (d.act === "fs") {
      if (document.fullscreenElement || document.webkitFullscreenElement) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      else (ui.root.requestFullscreen || ui.root.webkitRequestFullscreen).call(ui.root);
    }
  });
  const fsBtn = $("[data-act=fs]", ui.bar);
  if (ui.root.requestFullscreen || ui.root.webkitRequestFullscreen) fsBtn.hidden = false;
  const onFs = () => {
    const on = ui.root === (document.fullscreenElement || document.webkitFullscreenElement);
    fsBtn.setAttribute("aria-pressed", String(on));
    fsBtn.textContent = on ? "Esci da schermo intero" : "Schermo intero";
  };
  document.addEventListener("fullscreenchange", onFs);
  document.addEventListener("webkitfullscreenchange", onFs);

  // --- ciclo di rendering solo quando serve ---------------------------------------------------------
  function frame(now) {
    raf = 0;
    if (!visible) return;
    let more = false;
    if (tween) {
      const u = Math.min(1, (now - tween.t0) / tween.dur), e = u * u * (3 - 2 * u);
      const len = THREE.MathUtils.lerp(tween.from.length(), tween.to.length(), e);
      camera.position.copy(tween.from).lerp(tween.to, e).setLength(len);
      if (u >= 1) tween = null;
      more = true;
    }
    controls.autoRotate = state.rot && !hoverPause;
    if (controls.update()) more = true;
    if (state.phase && antenna.visible) { paintSegments(now); more = true; }
    renderer.render(scene, camera);
    updateLabels();
    if (more) request();
  }
  function resize() {
    W = host.clientWidth; H = host.clientHeight;
    if (!W || !H) return;
    renderer.setSize(W, H, false);
    camera.aspect = W / H;
    camera.fov = camera.aspect < 1 ? 2 * Math.atan(Math.tan(20 * D2R) / camera.aspect) / D2R : 40;   // su schermi stretti mantiene l'ampiezza orizzontale
    camera.updateProjectionMatrix();
    request();
  }
  new ResizeObserver(resize).observe(host);
  new IntersectionObserver(([en]) => { visible = en.isIntersecting; if (visible) request(); }).observe(host);
  dom.addEventListener("webglcontextlost", e => e.preventDefault());
  dom.addEventListener("webglcontextrestored", request);

  ui.legend.pat.box.querySelector("i").style.background = cssGradient(PAT_STOPS);
  ui.legend.cur.querySelector("i").style.background = cssGradient(HEAT_STOPS);
  paintSegments(0);
  buildScale();
  setToggle("rot", state.rot);
  resize();
  return true;
}

// --- avvio ------------------------------------------------------------------------------------------
setupCopy();
const dataEl = $("#antenna-data"), host = $("#viewer3d");
if (dataEl && host) {
  const root = $("#v3d"), bar = $(".vtools", root);
  const leg = $(".vleg", host), pat = $("#lg-pat", host), curL = $("#lg-cur", host);
  const ui = { host, root, bar, legend: { pat: { box: pat, lo: pat.children[1], hi: pat.children[3] }, cur: curL } };
  let ok = false;
  try { ok = init(JSON.parse(dataEl.textContent), ui); } catch (e) { console.error(e); }
  if (!ok) {
    $(".vfail", host).hidden = false;
    leg.hidden = true;
    $$("button", bar).forEach(b => { b.disabled = true; });
    host.style.cursor = "default";
  }
}
