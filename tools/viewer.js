// Vista 3D: diagramma di irradiazione e geometria dell'antenna, con three.js
// incluso nel sito (nessun CDN). Dati da <script type="application/json" id="antenna-data">.
import * as THREE from "three";
import { OrbitControls } from "three/addons/OrbitControls.js";

const data = JSON.parse(document.getElementById("antenna-data").textContent);
const host = document.getElementById("viewer3d");
const FLOOR = -30;                                   // dB sotto il massimo mostrati
const { th, ph, g, gmax, wires, feed } = data;
const rad = Math.PI / 180;

// palette MeshCore ITA: dal blu notte al verde accento, giallo, rosso accento
const STOPS = [[0, 0x1e3a8a], [0.45, 0x22c55e], [0.75, 0xfacc15], [1, 0xe11d48]].map(([t, c]) => [t, new THREE.Color(c)]);
function ramp(t) {
  t = Math.min(1, Math.max(0, t));
  for (let k = 1; k < STOPS.length; k++) {
    if (t <= STOPS[k][0]) {
      const [t0, c0] = STOPS[k - 1], [t1, c1] = STOPS[k];
      return c0.clone().lerp(c1, (t - t0) / (t1 - t0));
    }
  }
  return STOPS[STOPS.length - 1][1].clone();
}

// --- scena -------------------------------------------------------------------
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
host.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 100);
camera.up.set(0, 0, 1);                               // NEC: z verso l'alto
camera.position.set(2.6, -2.2, 1.6);

scene.add(new THREE.HemisphereLight(0xffffff, 0x0b1220, 1.1));
const key = new THREE.DirectionalLight(0xffffff, 1.6);
key.position.set(3, -2, 4);
scene.add(key);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.8;
controls.minDistance = 1.2;
controls.maxDistance = 8;
controls.addEventListener("start", () => { controls.autoRotate = false; });

// piano dell'orizzonte con cerchi a -10/-20 dB e raggi ogni 30°
const grid = new THREE.PolarGridHelper(1.05, 12, 3, 96, 0x3a3a3a, 0x262626);
grid.rotation.x = Math.PI / 2;
scene.add(grid);
const axes = new THREE.AxesHelper(1.25);
axes.material.transparent = true;
axes.material.opacity = 0.55;
scene.add(axes);

// --- diagramma ---------------------------------------------------------------
const pattern = new THREE.Group();
{
  const nth = th.length, nph = ph.length;
  const pos = new Float32Array(nth * nph * 3), col = new Float32Array(nth * nph * 3);
  for (let i = 0; i < nth; i++) {
    for (let j = 0; j < nph; j++) {
      const t = (Math.max(g[i][j] - gmax, FLOOR) - FLOOR) / -FLOOR;
      const s = Math.sin(th[i] * rad), k = (i * nph + j) * 3;
      pos[k] = t * s * Math.cos(ph[j] * rad);
      pos[k + 1] = t * s * Math.sin(ph[j] * rad);
      pos[k + 2] = t * Math.cos(th[i] * rad);
      ramp(t).toArray(col, k);
    }
  }
  const idx = [];
  for (let i = 0; i < nth - 1; i++) {
    for (let j = 0; j < nph; j++) {
      const a = i * nph + j, b = i * nph + (j + 1) % nph, c = (i + 1) * nph + (j + 1) % nph, d = (i + 1) * nph + j;
      idx.push(a, d, b, b, d, c);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  pattern.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    vertexColors: true, roughness: 0.5, metalness: 0.05, transparent: true, opacity: 0.55,
    side: THREE.DoubleSide, depthWrite: false,
  })));
  pattern.add(new THREE.LineSegments(new THREE.WireframeGeometry(geo),
    new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.06 })));
}
scene.add(pattern);

// --- antenna -----------------------------------------------------------------
const antenna = new THREE.Group();
{
  const pts = wires.flatMap(w => [w.slice(0, 3), w.slice(3, 6)]);
  const lo = [0, 1, 2].map(k => Math.min(...pts.map(p => p[k])));
  const hi = [0, 1, 2].map(k => Math.max(...pts.map(p => p[k])));
  const ctr = lo.map((v, k) => (v + hi[k]) / 2);
  const ext = Math.max(...pts.map(p => Math.hypot(p[0] - ctr[0], p[1] - ctr[1], p[2] - ctr[2]))) || 1;
  const sc = 0.55 / ext;
  const metal = new THREE.MeshStandardMaterial({ color: 0xd4a373, metalness: 0.85, roughness: 0.3 });
  wires.forEach((w, n) => {
    const a = new THREE.Vector3(...w.slice(0, 3).map((v, k) => (v - ctr[k]) * sc));
    const b = new THREE.Vector3(...w.slice(3, 6).map((v, k) => (v - ctr[k]) * sc));
    const r = Math.max((w[6] || 0.001) * sc, 0.008);
    const len = a.distanceTo(b);
    const tube = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 16), metal);
    tube.position.copy(a).add(b).multiplyScalar(0.5);
    tube.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
    antenna.add(tube);
    if (n === feed) {
      const dot = new THREE.Mesh(new THREE.SphereGeometry(Math.max(r * 2.2, 0.022), 20, 12),
        new THREE.MeshStandardMaterial({ color: 0x22c55e, emissive: 0x22c55e, emissiveIntensity: 0.6 }));
      dot.position.copy(tube.position);
      antenna.add(dot);
    }
  });
}
scene.add(antenna);

// --- controlli pagina --------------------------------------------------------
document.querySelectorAll("[data-mode]").forEach(btn => btn.addEventListener("click", () => {
  const m = btn.dataset.mode;
  pattern.visible = m !== "geom";
  antenna.visible = m !== "pattern";
  document.querySelectorAll("[data-mode]").forEach(x => x.setAttribute("aria-pressed", String(x === btn)));
}));

function resize() {
  const w = host.clientWidth, h = host.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(host);
resize();

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (reduce) controls.autoRotate = false;
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
