/**
 * ============================================================
 *  سَـرَاب — SARAB · Phase 0 (core prototype)
 * ============================================================
 *  You carry no weapon. You fight by stealing a *property* from
 *  the world and throwing it at what wants you dead: take a
 *  wall's hardness and your fist becomes stone; take an enemy's
 *  weight and it flies; take speed and the world crawls.
 *
 *  Every theft is permanent for the room — the arena degrades as
 *  you win — and every theft is paid for out of MEMORY. Empty
 *  memory, and you go out.
 *
 *  This file is the whole game: renderer, physics, AI, audio and
 *  UI. It is bundled and inlined into a single HTML file so it
 *  runs from any link with no network access at all.
 * ============================================================
 */
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";

/* ── tuning ─────────────────────────────────────────── */
const CFG = {
  memoryMax: 100,
  stealCost: 12,
  returnGain: 7,
  playerSpeed: 7.2,
  playerSpeedHard: 4.4,
  jump: 6.4,
  jumpLight: 11.5,
  gravity: 22,
  gravityLight: 9,
  reach: 26,
  slowScale: 0.35,
  slowDrain: 9,          // memory per second while time is slowed
  enemyBaseSpeed: 2.5,
  enemyDamage: 14,
  waveGap: 3.0,
};

const PROPS = {
  weight:   { id: "weight",   ar: "الوزن",    en: "WEIGHT",   color: 0x8ab4ff },
  hardness: { id: "hardness", ar: "الصلابة",  en: "HARDNESS", color: 0xffc46b },
  speed:    { id: "speed",    ar: "السرعة",   en: "SPEED",    color: 0x7fe3e0 },
};

/** Four things want you dead, and each one answers to a different property. */
const KINDS = {
  shade:  { hp: 100, speed: 1.0,  scale: 1.15, visor: 0xff6a5a, dmg: 1.0,  score: 20, ar: "ظل" },
  runner: { hp: 55,  speed: 1.95, scale: 0.92, visor: 0xffb04a, dmg: 0.7,  score: 30, ar: "راكض" },
  heavy:  { hp: 320, speed: 0.55, scale: 1.65, visor: 0xd14aff, dmg: 1.8,  score: 60, ar: "ثقيل" },
  debtor: { hp: 150, speed: 1.25, scale: 1.3,  visor: 0x7fe3e0, dmg: 0.4,  score: 45, ar: "الدائن" },
};

const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const lerp = (a, b, t) => a + (b - a) * t;
const rand = (a, b) => a + Math.random() * (b - a);

/* ════════════════════════════════════════════════════
   Audio — everything synthesised, no files
   ════════════════════════════════════════════════════ */
class Audio {
  constructor() {
    this.ctx = null;
    this.master = null;
  }
  start() {
    if (this.ctx) return;
    const AC = window.AudioContext || window.webkitAudioContext;
    this.ctx = new AC();
    this.master = this.ctx.createGain();
    this.master.gain.value = 0.55;
    this.master.connect(this.ctx.destination);
    this.drone();
  }
  drone() {
    const c = this.ctx;
    const g = c.createGain();
    g.gain.value = 0.055;
    const f = c.createBiquadFilter();
    f.type = "lowpass";
    f.frequency.value = 260;
    for (const hz of [55, 82.5, 110.3]) {
      const o = c.createOscillator();
      o.type = "sawtooth";
      o.frequency.value = hz;
      const og = c.createGain();
      og.gain.value = 0.34;
      o.connect(og); og.connect(f);
      o.start();
      const lfo = c.createOscillator();
      lfo.frequency.value = 0.05 + Math.random() * 0.08;
      const lg = c.createGain();
      lg.gain.value = 0.6;
      lfo.connect(lg); lg.connect(o.detune);
      lfo.start();
    }
    f.connect(g); g.connect(this.master);
    this.droneGain = g;
  }
  /** memory 0..1 → the score decays with the player */
  tension(mem) {
    if (!this.ctx) return;
    this.droneGain.gain.value = lerp(0.12, 0.04, mem);
  }
  blip({ freq = 440, type = "sine", dur = 0.12, gain = 0.2, slide = 0 }) {
    if (!this.ctx) return;
    const c = this.ctx, t = c.currentTime;
    const o = c.createOscillator(), g = c.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, t);
    if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(20, freq + slide), t + dur);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(gain, t + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(this.master);
    o.start(t); o.stop(t + dur + 0.02);
  }
  noise({ dur = 0.25, gain = 0.3, freq = 900, q = 1 }) {
    if (!this.ctx) return;
    const c = this.ctx, t = c.currentTime;
    const n = Math.floor(c.sampleRate * dur);
    const buf = c.createBuffer(1, n, c.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
    const src = c.createBufferSource(); src.buffer = buf;
    const f = c.createBiquadFilter(); f.type = "bandpass"; f.frequency.value = freq; f.Q.value = q;
    const g = c.createGain(); g.gain.value = gain;
    src.connect(f); f.connect(g); g.connect(this.master);
    src.start(t);
  }
  toggleMute() {
    if (!this.master) return;
    this.muted = !this.muted;
    this.master.gain.value = this.muted ? 0 : 0.55;
  }
  steal()  { this.blip({ freq: 220, type: "triangle", dur: 0.3, gain: 0.22, slide: 900 }); this.noise({ dur: 0.2, gain: 0.12, freq: 2200, q: 2 }); }
  give()   { this.blip({ freq: 900, type: "triangle", dur: 0.22, gain: 0.2, slide: -700 }); }
  hit()    { this.noise({ dur: 0.16, gain: 0.5, freq: 260, q: 0.7 }); this.blip({ freq: 90, type: "square", dur: 0.1, gain: 0.25, slide: -40 }); }
  kill()   { this.noise({ dur: 0.5, gain: 0.45, freq: 480, q: 0.4 }); this.blip({ freq: 140, type: "sawtooth", dur: 0.35, gain: 0.18, slide: -90 }); }
  hurt()   { this.blip({ freq: 160, type: "sawtooth", dur: 0.3, gain: 0.3, slide: -110 }); this.noise({ dur: 0.3, gain: 0.25, freq: 180, q: 0.5 }); }
  wave()   { this.blip({ freq: 300, type: "sine", dur: 0.7, gain: 0.16, slide: 240 }); }
  die()    { this.blip({ freq: 200, type: "sine", dur: 1.6, gain: 0.3, slide: -170 }); this.noise({ dur: 1.4, gain: 0.3, freq: 140, q: 0.3 }); }
}

/* ════════════════════════════════════════════════════
   World geometry
   ════════════════════════════════════════════════════ */
const BOXES = [];      // static colliders {min:Vector3, max:Vector3, prop}
const SPARK_MATS = {};

function sparkMaterial(color) {
  if (!SPARK_MATS[color]) {
    SPARK_MATS[color] = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 });
  }
  return SPARK_MATS[color];
}

class Game {
  constructor(canvas) {
    this.canvas = canvas;
    this.audio = new Audio();
    this.clock = new THREE.Clock();
    this.state = "menu";       // menu | play | dead
    this.lang = document.documentElement.lang === "en" ? "en" : "ar";

    this.initRenderer();
    this.initScene();
    this.initPost();
    this.initPlayer();
    this.initInput();
    this.hud = new HUD(this);
    this.reset();

    window.addEventListener("resize", () => this.onResize());
    this.loop = this.loop.bind(this);
    requestAnimationFrame(this.loop);
  }

  /* ── renderer ── */
  initRenderer() {
    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: false, powerPreference: "high-performance" });
    const coarse = matchMedia("(pointer: coarse)").matches;
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, coarse ? 1.2 : 1.75));
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.shadowMap.enabled = false;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.3;
  }

  /** bloom is what turns flat boxes into a lit place */
  initPost() {
    this.composer = new EffectComposer(this.renderer);
    this.composer.addPass(new RenderPass(this.scene, this.camera));
    const coarse = matchMedia("(pointer: coarse)").matches;
    this.bloom = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight).multiplyScalar(coarse ? 0.6 : 1),
      coarse ? 0.45 : 0.55, 0.6, 0.5
    );
    this.composer.addPass(this.bloom);
    this.composer.addPass(new OutputPass());
  }
  onResize() {
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.composer?.setSize(window.innerWidth, window.innerHeight);
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
  }

  /* ── scene ── */
  initScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x070b12);
    this.scene.fog = new THREE.FogExp2(0x080d15, 0.017);

    this.camera = new THREE.PerspectiveCamera(78, window.innerWidth / window.innerHeight, 0.1, 260);

    this.scene.add(new THREE.HemisphereLight(0x6f9bd8, 0x161d29, 1.9));
    const key = new THREE.DirectionalLight(0xbcd6ff, 1.15);
    key.position.set(-8, 18, 6);
    this.scene.add(key);
    this.torch = new THREE.PointLight(0xbfd8ff, 3.2, 34, 1.7);
    this.scene.add(this.torch);

    this.sparks = new THREE.Group();
    this.scene.add(this.sparks);
    this.debris = [];
    this.motes = [];
    this.buildArena();
    this.buildMotes();
    this.ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.9, 0.06, 8, 28),
      new THREE.MeshBasicMaterial({ color: 0x7fe3e0, transparent: true, opacity: 0.95 })
    );
    this.ring.rotation.x = Math.PI / 2;
    this.ring.visible = false;
    this.scene.add(this.ring);
  }

  /** A hall, not a box: pillars, ceiling strips, and props that still hold properties. */
  buildArena() {
    BOXES.length = 0;
    const S = 52, H = 11;

    const floor = new THREE.Mesh(
      new THREE.BoxGeometry(S, 1, S),
      new THREE.MeshStandardMaterial({ color: 0x232d3c, roughness: 0.6, metalness: 0.22 })
    );
    floor.position.y = -0.5;
    this.scene.add(floor);

    const grid = new THREE.GridHelper(S, 26, 0x2f4a6b, 0x1a2432);
    grid.position.y = 0.02;
    this.scene.add(grid);

    const ceil = new THREE.Mesh(
      new THREE.BoxGeometry(S, 1, S),
      new THREE.MeshStandardMaterial({ color: 0x0b0f16, roughness: 1 })
    );
    ceil.position.y = H + 0.5;
    this.scene.add(ceil);

    /* the only real light source in the fiction: failing ceiling strips */
    const stripMat = new THREE.MeshBasicMaterial({ color: 0x9dc0f2 });
    this.strips = [];
    for (let i = -2; i <= 2; i++) {
      const strip = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.16, S * 0.8), stripMat);
      strip.position.set(i * 10, H - 0.3, 0);
      this.scene.add(strip);
      const l = new THREE.PointLight(0x9dc2ff, 2.1, 34, 1.7);
      l.position.set(i * 10, H - 1.4, 0);
      this.scene.add(l);
      this.strips.push({ strip, light: l, phase: rand(0, 6.28), flick: Math.random() < 0.4 });
    }

    const wallMat = new THREE.MeshStandardMaterial({ color: 0x1b2431, roughness: 0.9, metalness: 0.15 });
    for (const [x, y, z, w, hh, d] of [
      [0, H / 2, -S / 2, S, H, 1], [0, H / 2, S / 2, S, H, 1],
      [-S / 2, H / 2, 0, 1, H, S], [S / 2, H / 2, 0, 1, H, S],
    ]) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, hh, d), wallMat);
      m.position.set(x, y, z);
      this.scene.add(m);
      this.addCollider(m);
    }

    /* structural pillars — cover, sightlines, and something to hide behind */
    const pillarMat = new THREE.MeshStandardMaterial({ color: 0x202b3a, roughness: 0.85, metalness: 0.2 });
    for (const [px, pz] of [[-16, -16], [16, -16], [-16, 16], [16, 16], [0, -20], [0, 20], [-20, 0], [20, 0]]) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(2.2, H, 2.2), pillarMat);
      m.position.set(px, H / 2, pz);
      this.scene.add(m);
      this.addCollider(m);
      const band = new THREE.Mesh(
        new THREE.BoxGeometry(2.34, 0.1, 2.34),
        new THREE.MeshBasicMaterial({ color: 0x2f6f8f })
      );
      band.position.set(px, 2.4, pz);
      this.scene.add(band);
    }

    /* props: the first one sits directly ahead of the spawn so the game can teach itself */
    this.props = [];
    const layout = [
      { x: 0, z: 4, w: 2, h: 4.6, d: 2, prop: "hardness" },       // tutorial target
      { x: -8, z: -2, w: 3, h: 4.2, d: 3, prop: "hardness" },
      { x: 9, z: -4, w: 3, h: 4.2, d: 3, prop: "hardness" },
      { x: 13, z: 9, w: 3.2, h: 3, d: 3.2, prop: "weight" },
      { x: -13, z: 10, w: 3.2, h: 3, d: 3.2, prop: "weight" },
      { x: 0, z: -14, w: 5, h: 2.2, d: 2.2, prop: "weight" },
      { x: -6, z: 16, w: 2.2, h: 5, d: 2.2, prop: "speed" },
      { x: 7, z: 17, w: 2.2, h: 5, d: 2.2, prop: "speed" },
      { x: 19, z: -8, w: 2.2, h: 5.6, d: 2.2, prop: "speed" },
      { x: -19, z: -6, w: 2.2, h: 5.6, d: 2.2, prop: "hardness" },
      { x: 5, z: -22, w: 6, h: 1.4, d: 3, prop: "weight" },
    ];
    for (const p of layout) this.addProp(p);
    this.tutorialTarget = this.props[0];
  }

  addProp({ x, z, w, h, d, prop }) {
    const def = PROPS[prop];
    const mat = new THREE.MeshStandardMaterial({
      color: 0x161d28, roughness: 0.8, metalness: 0.12,
      emissive: new THREE.Color(def.color), emissiveIntensity: 0.16,
    });
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    mesh.position.set(x, h / 2, z);
    mesh.userData.prop = prop;
    mesh.userData.baseY = h / 2;
    const edge = new THREE.LineSegments(
      new THREE.EdgesGeometry(mesh.geometry),
      new THREE.LineBasicMaterial({ color: def.color, transparent: true, opacity: 0.9 })
    );
    mesh.add(edge);
    mesh.userData.edge = edge;
    this.scene.add(mesh);
    this.addCollider(mesh);
    this.props.push(mesh);

    /* a slow halo of motes marks a prop that still has something to take */
    const halo = new THREE.Points(
      new THREE.BufferGeometry().setAttribute(
        "position",
        new THREE.Float32BufferAttribute(
          Array.from({ length: 22 }, () => [rand(-w, w) * 0.7, rand(0.2, h), rand(-d, d) * 0.7]).flat(), 3
        )
      ),
      new THREE.PointsMaterial({ color: def.color, size: 0.16, transparent: true, opacity: 0.85, depthWrite: false })
    );
    halo.position.set(x, 0, z);
    this.scene.add(halo);
    mesh.userData.halo = halo;
  }

  addCollider(mesh) {
    const b = new THREE.Box3().setFromObject(mesh);
    BOXES.push({ min: b.min.clone(), max: b.max.clone(), mesh });
    mesh.userData.collider = BOXES[BOXES.length - 1];
  }

  buildMotes() {
    const n = matchMedia("(pointer: coarse)").matches ? 120 : 260, pos = [];
    for (let i = 0; i < n; i++) pos.push(rand(-23, 23), rand(0.4, 12), rand(-23, 23));
    const g = new THREE.BufferGeometry().setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    this.dust = new THREE.Points(g, new THREE.PointsMaterial({
      color: 0x51708f, size: 0.06, transparent: true, opacity: 0.5, depthWrite: false,
    }));
    this.scene.add(this.dust);
  }

  /* ── player ── */
  initPlayer() {
    this.player = {
      pos: new THREE.Vector3(0, 1.7, 16),
      vel: new THREE.Vector3(),
      yaw: 0, pitch: 0,
      onGround: true,
      hp: 100,
      memory: CFG.memoryMax,
      held: null,          // property id in hand
      punchT: 0,
      hurtT: 0,
      shake: 0,
    };
    this.score = 0;
    this.wave = 0;
    this.timeScale = 1;
    this.hitStop = 0;
    this.tut = { step: 0, yaw0: 0, moved: 0, lastPos: new THREE.Vector3() };
    this.combo = 0; this.comboT = 0; this.returns = 0; this.steals = 0;
    this.best = Number(localStorage.getItem("sarab.best") || 0);
  }

  /* ── input ── */
  initInput() {
    this.keys = {};
    this.touch = { move: null, look: null, moveVec: { x: 0, y: 0 } };

    addEventListener("keydown", (e) => {
      this.keys[e.code] = true;
      if (e.code === "Space") e.preventDefault();
      if (e.code === "Escape" || e.code === "KeyP") return this.togglePause();
      if (e.code === "KeyM") return this.audio.toggleMute();
      if (this.state === "menu" || this.state === "dead" || this.state === "won") this.begin();
    });
    addEventListener("keyup", (e) => { this.keys[e.code] = false; });

    this.canvas.addEventListener("mousedown", (e) => {
      if (this.state !== "play") { this.begin(); return; }
      if (document.pointerLockElement !== this.canvas && !this.isTouch()) {
        this.canvas.requestPointerLock?.();
        this.dragLook = true;          // fallback: drag to look if lock is blocked
      }
      if (e.button === 0) this.give();
      if (e.button === 2) this.steal();
    });
    this.canvas.addEventListener("contextmenu", (e) => e.preventDefault());
    addEventListener("mouseup", () => { this.dragLook = false; });
    addEventListener("mousemove", (e) => {
      if (document.pointerLockElement === this.canvas) this.look(e.movementX, e.movementY);
      else if (this.dragLook && this.state === "play") this.look(e.movementX || 0, e.movementY || 0);
    });

    /* touch: left half drags to move, right half drags to look */
    const tstart = (e) => {
      if (this.state !== "play") { this.begin(); return; }
      for (const t of e.changedTouches) {
        const left = t.clientX < window.innerWidth * 0.5;
        if (left && !this.touch.move) this.touch.move = { id: t.identifier, x0: t.clientX, y0: t.clientY, x: t.clientX, y: t.clientY };
        else if (!left && !this.touch.look) this.touch.look = { id: t.identifier, x: t.clientX, y: t.clientY, moved: 0, t0: performance.now() };
      }
    };
    const tmove = (e) => {
      for (const t of e.changedTouches) {
        if (this.touch.move && t.identifier === this.touch.move.id) {
          this.touch.move.x = t.clientX; this.touch.move.y = t.clientY;
        } else if (this.touch.look && t.identifier === this.touch.look.id) {
          const dx = t.clientX - this.touch.look.x, dy = t.clientY - this.touch.look.y;
          this.touch.look.moved += Math.abs(dx) + Math.abs(dy);
          this.touch.look.x = t.clientX; this.touch.look.y = t.clientY;
          this.look(dx * 1.6, dy * 1.6);
        }
      }
      e.preventDefault();
    };
    const tend = (e) => {
      for (const t of e.changedTouches) {
        if (this.touch.move && t.identifier === this.touch.move.id) this.touch.move = null;
        if (this.touch.look && t.identifier === this.touch.look.id) {
          /* a tap on the right half is an attack */
          if (this.touch.look.moved < 14 && performance.now() - this.touch.look.t0 < 260) this.give();
          this.touch.look = null;
        }
      }
    };
    this.canvas.addEventListener("touchstart", tstart, { passive: false });
    this.canvas.addEventListener("touchmove", tmove, { passive: false });
    this.canvas.addEventListener("touchend", tend);
    this.canvas.addEventListener("touchcancel", tend);
  }
  isTouch() { return matchMedia("(pointer: coarse)").matches; }
  look(dx, dy) {
    const s = 0.0023;
    this.player.yaw -= dx * s;
    this.player.pitch = clamp(this.player.pitch - dy * s, -1.5, 1.5);
  }

  /* ── run control ── */
  reset() {
    for (const e of this.enemies || []) this.scene.remove(e.group);
    this.enemies = [];
    for (const d of this.debris) this.scene.remove(d.mesh);
    this.debris = [];
    this.player.pos.set(0, 1.7, 16);
    this.player.vel.set(0, 0, 0);
    this.player.hp = 100;
    this.player.memory = CFG.memoryMax;
    this.player.held = null;
    this.player.yaw = 0; this.player.pitch = 0;
    this.score = 0; this.wave = 0; this.waveTimer = 1.2;
    this.tut = { step: 0, yaw0: this.player.yaw, moved: 0, lastPos: this.player.pos.clone() };
    this.combo = 0; this.comboT = 0; this.returns = 0; this.steals = 0;
    this.boss = null; this.ending = null;
    if (this.ring) this.ring.visible = true;
    this.timeScale = 1;
    /* restore every prop the previous run drained */
    for (const p of this.props) {
      if (p.userData.drained) {
        p.userData.drained = false;
        p.material.emissiveIntensity = 0.16;
        p.visible = true;
        if (p.userData.halo) p.userData.halo.visible = true;
        if (p.userData.edge) p.userData.edge.material.opacity = 0.9;
        p.userData.collider.min.copy(new THREE.Box3().setFromObject(p).min);
        p.userData.collider.max.copy(new THREE.Box3().setFromObject(p).max);
      }
    }
  }
  setLang(lang) {
    if (!TXT[lang] || lang === this.lang) return;
    this.lang = lang;
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    this.hud = new HUD(this);
    this.hud.setScreen(this.state === "play" ? null : this.state === "menu" ? "menu" : this.state);
  }

  togglePause() {
    if (this.state === "play") {
      this.state = "paused";
      document.exitPointerLock?.();
      this.hud.setScreen("paused");
    } else if (this.state === "paused") {
      this.state = "play";
      this.hud.setScreen(null);
      if (!this.isTouch()) this.canvas.requestPointerLock?.();
    }
  }

  begin() {
    if (this.state === "play") return;
    if (this.state === "paused") return this.togglePause();
    this.audio.start();
    this.reset();
    this.state = "play";
    this.hud.setScreen(null);
    if (!this.isTouch()) this.canvas.requestPointerLock();
  }
  die() {
    if (this.state !== "play") return;
    this.saveBest();
    this.state = "dead";
    this.audio.die();
    document.exitPointerLock?.();
    this.hud.setScreen("dead");
  }

  /* ── the two verbs ── */
  targetUnderCrosshair() {
    const ray = new THREE.Raycaster();
    const dir = new THREE.Vector3(0, 0, -1).applyEuler(new THREE.Euler(this.player.pitch, this.player.yaw, 0, "YXZ"));
    ray.set(this.player.pos, dir);
    ray.far = CFG.reach;
    const meshes = [
      ...this.props.filter((p) => p.visible),
      ...this.enemies.filter((e) => e.alive).map((e) => e.hitbox),
      ...(this.boss ? this.boss.cores.filter((c) => c.alive).map((c) => c.core) : []),
    ];
    const hit = ray.intersectObjects(meshes, false)[0];
    return hit ? hit.object : null;
  }

  steal() {
    const t = this.targetUnderCrosshair();
    if (!t) return;
    const p = this.player;

    if (t.userData.boss) {
      if (p.memory < CFG.stealCost) return this.audio.blip({ freq: 120, dur: 0.1, gain: 0.15 });
      p.memory -= CFG.stealCost;
      p.held = "hardness";
      this.audio.steal();
      this.hitBossCore(t);
      return;
    }

    /* stealing from an enemy strips its behaviour — and kills the weak ones */
    if (t.userData.enemy) {
      const e = t.userData.enemy;
      if (p.memory < CFG.stealCost) return this.audio.blip({ freq: 120, dur: 0.1, gain: 0.15 });
      p.memory -= CFG.stealCost;
      p.held = e.carries;
      this.audio.steal();
      this.spawnSpark(e.group.position, PROPS[e.carries].color, 26);
      this.killEnemy(e, true);
      return;
    }

    const prop = t.userData.prop;
    if (!prop || t.userData.drained) return;
    if (p.memory < CFG.stealCost) return this.audio.blip({ freq: 120, dur: 0.1, gain: 0.15 });

    p.memory -= CFG.stealCost;
    p.held = prop;
    this.steals++;
    t.userData.drained = true;
    this.audio.steal();
    this.spawnSpark(t.position, PROPS[prop].color, 30);

    /* the room pays for it — permanently, for this run */
    if (prop === "hardness") {
      this.shatter(t);
    } else if (prop === "weight") {
      t.userData.floating = true;
      t.material.emissiveIntensity = 0.02;
      const idx = BOXES.indexOf(t.userData.collider);
      if (idx >= 0) BOXES.splice(idx, 1);      // it no longer blocks anything
    } else {
      t.material.emissiveIntensity = 0.02;
      t.userData.slowed = true;
    }
    if (t.userData.halo) t.userData.halo.visible = false;
    if (t.userData.edge) t.userData.edge.material.opacity = 0.12;
    this.player.shake = Math.max(this.player.shake, 0.35);
  }

  give() {
    const p = this.player;
    p.punchT = 0.22;
    const t = this.targetUnderCrosshair();

    if (!p.held) {
      /* bare hands still count — a weak shove */
      if (t && t.userData.enemy) {
        const e = t.userData.enemy;
        if (e.kind === "heavy") { this.audio.blip({ freq: 110, type: "square", dur: 0.12, gain: 0.2 }); this.hud.toast(TXT[this.lang].tooHard); }
        else this.damageEnemy(e, 34);
      }
      this.audio.blip({ freq: 260, type: "square", dur: 0.07, gain: 0.12 });
      return;
    }

    const prop = p.held;
    if (t && t.userData.enemy) {
      const e = t.userData.enemy;
      this.audio.give();
      this.spawnSpark(e.group.position, PROPS[prop].color, 22);
      if (prop === "weight") {
        /* crushed into the floor */
        this.killEnemy(e, false);
        this.score += 30;
      } else if (prop === "hardness") {
        /* petrified, then shatters */
        this.killEnemy(e, true);
        this.score += 25;
      } else {
        e.slowT = 6;
        e.speed *= 0.25;
        this.score += 10;
      }
      p.held = null;
      this.hitStop = 0.07;
      p.shake = Math.max(p.shake, 0.5);
      return;
    }

    /* giving it back to a drained prop restores memory — the only way up */
    if (t && t.userData.drained && t.userData.prop === prop) {
      t.userData.drained = false;
      t.userData.floating = false;
      t.userData.slowed = false;
      t.visible = true;
      t.material.emissiveIntensity = 0.16;
      if (t.userData.halo) t.userData.halo.visible = true;
      if (t.userData.edge) t.userData.edge.material.opacity = 0.9;
      if (!BOXES.includes(t.userData.collider)) BOXES.push(t.userData.collider);
      p.memory = clamp(p.memory + CFG.returnGain, 0, CFG.memoryMax);
      p.held = null;
      this.returns++;
      this.score += 15;
      this.audio.give();
      this.spawnSpark(t.position, PROPS[prop].color, 18);
      return;
    }

    /* thrown at nothing: the property escapes back into the air */
    this.audio.blip({ freq: 500, dur: 0.18, gain: 0.12, slide: -260 });
    this.spawnSpark(this.player.pos.clone().add(new THREE.Vector3(0, 0, -2)), PROPS[prop].color, 12);
    p.held = null;
  }

  shatter(mesh) {
    const idx = BOXES.indexOf(mesh.userData.collider);
    if (idx >= 0) BOXES.splice(idx, 1);
    mesh.visible = false;
    const geo = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    for (let i = 0; i < 16; i++) {
      const m = new THREE.Mesh(geo, mesh.material);
      m.position.copy(mesh.position).add(new THREE.Vector3(rand(-1.2, 1.2), rand(-1.4, 1.6), rand(-1.2, 1.2)));
      this.scene.add(m);
      this.debris.push({
        mesh: m, life: 2.6,
        vel: new THREE.Vector3(rand(-5, 5), rand(2, 8), rand(-5, 5)),
        spin: new THREE.Vector3(rand(-6, 6), rand(-6, 6), rand(-6, 6)),
      });
    }
    this.audio.hit();
  }

  spawnSpark(pos, color, n) {
    const geo = new THREE.SphereGeometry(0.09, 5, 4);
    const mat = sparkMaterial(color);
    for (let i = 0; i < n; i++) {
      const m = new THREE.Mesh(geo, mat);
      m.position.copy(pos).add(new THREE.Vector3(rand(-0.6, 0.6), rand(0, 1.6), rand(-0.6, 0.6)));
      this.scene.add(m);
      this.debris.push({
        mesh: m, life: rand(0.5, 1.1), spark: true,
        vel: new THREE.Vector3(rand(-4, 4), rand(1, 6), rand(-4, 4)),
        spin: new THREE.Vector3(),
      });
    }
  }

  /* ── enemies ── */
  /** Each wave introduces exactly one new idea, then mixes. */
  spawnWave() {
    this.wave++;
    this.audio.wave();
    this.hud.flashWave(this.wave);
    if (this.wave === 6) return this.spawnBoss();

    const mix = {
      1: { shade: 4 },
      2: { shade: 4, runner: 2 },
      3: { shade: 4, runner: 3, heavy: 1 },
      4: { shade: 5, runner: 4, heavy: 2 },
      5: { shade: 6, runner: 5, heavy: 3 },
    }[this.wave] || { shade: 6 + this.wave, runner: 4 + this.wave, heavy: 2 + Math.floor(this.wave / 2) };

    for (const [kind, n] of Object.entries(mix)) {
      for (let i = 0; i < n; i++) {
        const a = rand(0, Math.PI * 2), r = rand(11, 18);
        this.spawnEnemy(new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r), kind);
      }
    }
  }

  /**
   * الحاضنة — the Incubator. Not a monster: a machine keeping a ward alive by
   * pulling the warmth out of everything near it, including you. It has three
   * cores; each one you steal makes it more desperate.
   */
  spawnBoss() {
    const g = new THREE.Group();
    const shell = new THREE.Mesh(
      new THREE.OctahedronGeometry(3.2, 1),
      new THREE.MeshStandardMaterial({ color: 0x0d1420, roughness: 0.4, metalness: 0.7, flatShading: true })
    );
    g.add(shell);
    g.add(new THREE.LineSegments(
      new THREE.EdgesGeometry(shell.geometry),
      new THREE.LineBasicMaterial({ color: 0x7fe3e0, transparent: true, opacity: 0.7 })
    ));

    const cores = [];
    for (let i = 0; i < 3; i++) {
      const core = new THREE.Mesh(
        new THREE.IcosahedronGeometry(0.62, 0),
        new THREE.MeshBasicMaterial({ color: 0xffc46b })
      );
      const ring = new THREE.Group();
      ring.rotation.set(rand(-0.6, 0.6), (i / 3) * 6.28, rand(-0.6, 0.6));
      core.position.set(4.6, 0, 0);
      core.userData.boss = true;
      core.userData.coreIndex = i;
      ring.add(core);
      g.add(ring);
      const l = new THREE.PointLight(0xffc46b, 1.6, 12, 2);
      core.add(l);
      cores.push({ core, ring, alive: true });
    }
    g.position.set(0, 6.2, -6);
    this.scene.add(g);
    this.boss = { group: g, shell, cores, hp: 3, pulseT: 3, rage: 0 };
    this.hud.toast(TXT[this.lang].bossIn);
    this.audio.blip({ freq: 70, type: "sawtooth", dur: 2.2, gain: 0.32, slide: 40 });
  }

  updateBoss(dt) {
    const b = this.boss, p = this.player;
    if (!b) return;
    b.group.rotation.y += dt * (0.25 + b.rage * 0.2);
    b.shell.rotation.x += dt * 0.4;
    for (const c of b.cores) if (c.alive) c.ring.rotation.y += dt * (0.9 + b.rage * 0.5);

    b.pulseT -= dt;
    if (b.pulseT <= 0) {
      b.pulseT = Math.max(2.2, 5.2 - b.rage * 1.1);
      /* it drinks the room — and you are in the room */
      p.memory = clamp(p.memory - (7 + b.rage * 3), 0, CFG.memoryMax);
      p.shake = Math.max(p.shake, 0.7);
      this.audio.blip({ freq: 300, type: "sine", dur: 0.9, gain: 0.22, slide: -220 });
      this.hud.toast(TXT[this.lang].drain);
      this.spawnSpark(p.pos.clone().add(new THREE.Vector3(0, -0.4, -1.5)), 0x7fe3e0, 20);
      const a = rand(0, 6.28);
      this.spawnEnemy(new THREE.Vector3(Math.cos(a) * 12, 0, Math.sin(a) * 12), b.rage > 1 ? "runner" : "shade");
      if (p.memory <= 0) this.die();
    }
  }

  hitBossCore(core) {
    const b = this.boss;
    const c = b.cores[core.userData.coreIndex];
    if (!c || !c.alive) return;
    c.alive = false;
    c.core.visible = false;
    b.hp--; b.rage++;
    this.score += Math.round(400 * this.comboMul());
    this.audio.kill();
    this.hitStop = 0.12;
    this.player.shake = 1.2;
    this.spawnSpark(c.core.getWorldPosition(new THREE.Vector3()), 0xffc46b, 40);
    if (b.hp <= 0) this.winRun();
    else this.hud.toast(TXT[this.lang].coreOut.replace("{n}", b.hp));
  }

  /** Three endings, decided by how you played rather than what you clicked. */
  winRun() {
    const p = this.player;
    const memPct = p.memory / CFG.memoryMax;
    this.ending = memPct >= 0.5 && this.returns >= 3 ? "faithful"
      : this.returns === 0 && this.steals >= 8 ? "greedy"
      : "stranger";
    this.score += Math.round(1000 * memPct);
    for (const e of this.enemies) this.killEnemy(e, true);
    if (this.boss) { this.scene.remove(this.boss.group); this.boss = null; }
    this.state = "won";
    this.saveBest();
    document.exitPointerLock?.();
    this.hud.setScreen("won");
    this.audio.blip({ freq: 180, type: "sine", dur: 2.6, gain: 0.3, slide: 320 });
  }
  saveBest() {
    if (this.score > this.best) {
      this.best = this.score;
      try { localStorage.setItem("sarab.best", String(this.best)); } catch { /* private mode */ }
    }
  }

  spawnEnemy(pos, kind = "shade") {
    const K = KINDS[kind];
    const g = new THREE.Group();
    const mat = new THREE.MeshStandardMaterial({ color: 0x070a10, roughness: 0.5, metalness: 0.25, emissive: 0x18305e, emissiveIntensity: 0.3 });

    const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.34, 0.8, 4, 8), mat);
    torso.position.y = 1.26;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.24, 10, 8), mat);
    head.position.y = 1.95;
    const legL = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.86, 0.2), mat);
    const legR = legL.clone();
    legL.position.set(-0.17, 0.44, 0); legR.position.set(0.17, 0.44, 0);
    const armL = new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.74, 0.17), mat);
    const armR = armL.clone();
    armL.position.set(-0.48, 1.32, 0); armR.position.set(0.48, 1.32, 0);
    g.add(torso, head, legL, legR, armL, armR);

    const visor = new THREE.Mesh(
      new THREE.BoxGeometry(0.34, 0.07, 0.06),
      new THREE.MeshBasicMaterial({ color: K.visor })
    );
    visor.position.set(0, 1.97, 0.22);
    g.add(visor);
    const eye = new THREE.PointLight(K.visor, 0.9, 3.4, 2);
    eye.position.set(0, 1.97, 0.3);
    g.add(eye);
    for (const part of [torso, head]) {
      const e2 = new THREE.LineSegments(
        new THREE.EdgesGeometry(part.geometry, 40),
        new THREE.LineBasicMaterial({ color: 0x4d7fd6, transparent: true, opacity: 0.55 })
      );
      part.add(e2);
    }

    /* rim light so a black silhouette still reads against a black room */
    const rim = new THREE.PointLight(0x6fa0ff, 1.1, 6, 1.7);
    rim.position.y = 1.4;
    g.add(rim);

    const hitbox = new THREE.Mesh(
      new THREE.BoxGeometry(0.95, 2.1, 0.95),
      new THREE.MeshBasicMaterial({ visible: false })
    );
    hitbox.position.y = 1.05;
    g.add(hitbox);

    g.scale.setScalar(K.scale);
    g.position.copy(pos);
    this.scene.add(g);

    const carries = ["weight", "hardness", "speed"][Math.floor(rand(0, 3))];
    const e = {
      group: g, hitbox, parts: { legL, legR, armL, armR, torso, head },
      alive: true, kind, hp: K.hp, maxHp: K.hp, phase: rand(0, 6.28),
      speed: (CFG.enemyBaseSpeed + this.wave * 0.13 + rand(-0.25, 0.25)) * K.speed,
      atkCd: rand(0.4, 1.4), slowT: 0, carries, fleeT: 0,
    };
    hitbox.userData.enemy = e;
    this.enemies.push(e);
  }

  comboMul() { return 1 + Math.min(this.combo, 20) * 0.2; }

  damageEnemy(e, dmg) {
    if (!e.alive) return;
    e.hp -= dmg;
    this.audio.hit();
    this.hitStop = 0.045;
    this.player.shake = Math.max(this.player.shake, 0.3);
    this.spawnSpark(e.group.position.clone().setY(1.2), 0x6f8fc0, 6);
    if (e.hp <= 0) this.killEnemy(e, true);
  }

  killEnemy(e, burst) {
    if (!e.alive) return;
    e.alive = false;
    this.comboT = 2.6;
    this.combo = Math.min(this.combo + 1, 25);
    this.score += Math.round((KINDS[e.kind] || KINDS.shade).score * this.comboMul());
    this.audio.kill();
    const p = e.group.position;
    for (const part of Object.values(e.parts)) {
      const m = part;
      const world = new THREE.Vector3();
      m.getWorldPosition(world);
      this.scene.remove(m);
      m.position.copy(world);
      this.scene.add(m);
      this.debris.push({
        mesh: m, life: 2.2,
        vel: new THREE.Vector3(rand(-4, 4), burst ? rand(3, 8) : -8, rand(-4, 4)),
        spin: new THREE.Vector3(rand(-8, 8), rand(-8, 8), rand(-8, 8)),
      });
    }
    this.spawnSpark(p.clone().setY(1.2), PROPS[e.carries].color, 14);
    this.scene.remove(e.group);
  }

  /* ── simulation ── */
  update(dt) {
    const p = this.player;

    /* time scale: holding SPEED slows the world and drains memory */
    const wantSlow = p.held === "speed" && (this.keys.ShiftLeft || this.keys.ShiftRight || this.isTouch());
    this.timeScale = lerp(this.timeScale, wantSlow ? CFG.slowScale : 1, 1 - Math.pow(0.0015, dt));
    if (wantSlow) {
      p.memory -= CFG.slowDrain * dt;
      if (p.memory <= 0) { p.memory = 0; p.held = null; }
    }
    const wdt = dt * this.timeScale;

    /* movement */
    const light = p.held === "weight";
    const hard = p.held === "hardness";
    const speedMul = hard ? CFG.playerSpeedHard : CFG.playerSpeed;

    let ix = 0, iz = 0;
    if (this.keys.KeyW || this.keys.ArrowUp) iz -= 1;
    if (this.keys.KeyS || this.keys.ArrowDown) iz += 1;
    if (this.keys.KeyA || this.keys.ArrowLeft) ix -= 1;
    if (this.keys.KeyD || this.keys.ArrowRight) ix += 1;
    if (this.touch.move) {
      const dx = clamp((this.touch.move.x - this.touch.move.x0) / 60, -1, 1);
      const dy = clamp((this.touch.move.y - this.touch.move.y0) / 60, -1, 1);
      ix += dx; iz += dy;
    }
    const len = Math.hypot(ix, iz) || 1;
    ix /= len; iz /= len;

    const fwd = new THREE.Vector3(-Math.sin(p.yaw), 0, -Math.cos(p.yaw));
    const right = new THREE.Vector3(Math.cos(p.yaw), 0, -Math.sin(p.yaw));
    const wish = fwd.multiplyScalar(-iz).add(right.multiplyScalar(ix)).multiplyScalar(speedMul);

    p.vel.x = lerp(p.vel.x, wish.x, 1 - Math.pow(0.0001, wdt));
    p.vel.z = lerp(p.vel.z, wish.z, 1 - Math.pow(0.0001, wdt));
    p.vel.y -= (light ? CFG.gravityLight : CFG.gravity) * wdt;

    if ((this.keys.Space || (this.touch.move && this.touch.move.y - this.touch.move.y0 < -55)) && p.onGround) {
      p.vel.y = light ? CFG.jumpLight : CFG.jump;
      p.onGround = false;
      this.audio.blip({ freq: 300, type: "sine", dur: 0.09, gain: 0.1, slide: 160 });
    }

    this.movePlayer(p.vel.clone().multiplyScalar(wdt));

    /* props that lost their weight drift upward, out of the world */
    for (const pr of this.props) {
      if (pr.userData.floating) pr.position.y += 0.9 * wdt;
      if (pr.userData.halo) pr.userData.halo.rotation.y += 0.35 * wdt;
    }

    /* enemies */
    for (const e of this.enemies) {
      if (!e.alive) continue;
      if (e.slowT > 0) { e.slowT -= wdt; if (e.slowT <= 0) e.speed *= 4; }
      const to = new THREE.Vector3().subVectors(p.pos, e.group.position).setY(0);
      const d = to.length();
      to.normalize();
      if (d > 1.25) {
        e.group.position.addScaledVector(to, e.speed * wdt);
        e.phase += wdt * (5 + e.speed);
        const sw = Math.sin(e.phase) * 0.55;
        e.parts.legL.rotation.x = sw; e.parts.legR.rotation.x = -sw;
        e.parts.armL.rotation.x = -sw * 0.8; e.parts.armR.rotation.x = sw * 0.8;
        e.parts.torso.position.y = 1.26 + Math.abs(Math.sin(e.phase)) * 0.05;
      } else {
        e.atkCd -= wdt;
        if (e.atkCd <= 0) {
          e.atkCd = 1.1;
          if (e.kind === "debtor" && p.held) {
            p.held = null;
            this.hud.toast(TXT[this.lang].tookIt);
            this.audio.hurt();
            this.killEnemy(e, true);
            continue;
          }
          const dmg = CFG.enemyDamage * (KINDS[e.kind] || KINDS.shade).dmg * (hard ? 0.35 : 1);
          p.hp -= dmg;
          p.hurtT = 0.45;
          p.shake = Math.max(p.shake, 0.8);
          this.audio.hurt();
          if (p.hp <= 0) return this.die();
        }
      }
      e.group.rotation.y = Math.atan2(to.x, to.z);
    }
    this.enemies = this.enemies.filter((e) => e.alive);

    this.updateTutorial(dt);
    if (this.boss) this.updateBoss(dt);

    /* waves — held back until the player has been taught */
    if (this.tut.step >= 5 && !this.boss && this.enemies.length === 0) {
      this.waveTimer -= dt;
      if (this.waveTimer <= 0) { this.spawnWave(); this.waveTimer = CFG.waveGap + 1.5; }
    }

    /* debris */
    for (const d of this.debris) {
      d.life -= dt;
      d.vel.y -= 16 * wdt;
      d.mesh.position.addScaledVector(d.vel, wdt);
      if (d.mesh.position.y < 0.12) { d.mesh.position.y = 0.12; d.vel.y *= -0.32; d.vel.multiplyScalar(0.72); }
      d.mesh.rotation.x += d.spin.x * wdt;
      d.mesh.rotation.y += d.spin.y * wdt;
      if (d.spark) d.mesh.scale.setScalar(clamp(d.life, 0, 1));
      else d.mesh.scale.setScalar(clamp(d.life / 1.2, 0.25, 1));
    }
    for (const d of this.debris.filter((x) => x.life <= 0)) this.scene.remove(d.mesh);
    this.debris = this.debris.filter((d) => d.life > 0);

    this.comboT -= dt;
    if (this.comboT <= 0 && this.combo) { this.combo = 0; }

    /* hold a stolen property too long and the debt comes to collect */
    if (p.held) {
      this.debtT = (this.debtT || 0) + dt;
      if (this.debtT > 9 && this.tut.step >= 6 && !this.enemies.some((e) => e.kind === "debtor")) {
        const a = rand(0, 6.28);
        this.spawnEnemy(new THREE.Vector3(Math.cos(a) * 13, 0, Math.sin(a) * 13), "debtor");
        this.hud.toast(TXT[this.lang].debt);
        this.debtT = 0;
      }
    } else this.debtT = 0;

    /* memory bleeds while you hold a stolen property — you cannot hoard */
    if (p.held) p.memory -= 1.6 * dt;
    if (p.memory <= 0) { p.memory = 0; this.die(); return; }

    /* camera */
    p.punchT = Math.max(0, p.punchT - dt);
    p.hurtT = Math.max(0, p.hurtT - dt);
    p.shake = Math.max(0, p.shake - dt * 2.4);
    const bob = Math.sin(performance.now() * 0.008) * 0.03 * (Math.hypot(p.vel.x, p.vel.z) > 1 ? 1 : 0);
    const sh = p.shake * 0.12;
    this.camera.position.copy(p.pos).add(new THREE.Vector3(rand(-sh, sh), bob + rand(-sh, sh), rand(-sh, sh)));
    this.camera.rotation.set(p.pitch, p.yaw, p.punchT * 0.5, "YXZ");
    this.torch.position.copy(p.pos);
    this.torch.color.setHex(p.held ? PROPS[p.held].color : 0xbfd8ff);
    this.torch.intensity = p.held ? 4.4 : 3.2;

    for (const s2 of this.strips) {
      const f = s2.flick ? (Math.sin(performance.now() * 0.017 + s2.phase) > 0.82 ? 0.15 : 1) : 1;
      s2.light.intensity = 2.1 * f;
      
      s2.strip.visible = f > 0.5;
    }
    this.dust.rotation.y += 0.012 * dt;
    const aim = this.targetUnderCrosshair();
    this.hud.aim(aim ? (aim.userData.enemy ? "enemy" : (aim.userData.drained ? "spent" : "prop")) : null);
    this.audio.tension(p.memory / CFG.memoryMax);
    this.hud.update();
  }

  /**
   * Onboarding: one instruction on screen at a time, and the game will not
   * move on until that exact thing has been done. No text walls, no menus.
   */
  updateTutorial(dt) {
    const t = this.tut, p = this.player, T = TXT[this.lang].tut;
    if (t.step >= 6) { this.ring.visible = false; this.hud.objective(""); return; }

    const touch = this.isTouch();
    const target = this.tutorialTarget;

    if (t.step === 0) {                       /* look around */
      this.hud.objective(touch ? T.look_t : T.look);
      this.ring.visible = false;
      if (Math.abs(p.yaw - t.yaw0) > 0.9) this.step(1);
    } else if (t.step === 1) {                /* move */
      this.hud.objective(touch ? T.move_t : T.move);
      t.moved += p.pos.distanceTo(t.lastPos);
      t.lastPos.copy(p.pos);
      if (t.moved > 4) this.step(2);
    } else if (t.step === 2) {                /* aim at the glowing pillar */
      this.hud.objective(T.aim);
      this.markRing(target);
      if (this.targetUnderCrosshair() === target) this.step(3);
    } else if (t.step === 3) {                /* steal it */
      this.hud.objective(touch ? T.steal_t : T.steal);
      this.markRing(target);
      if (p.held) {                            /* the steal itself advances us */
        this.step(4);
        this.spawnEnemy(new THREE.Vector3(0, 0, -13));
        this.enemies[this.enemies.length - 1].speed = 1.5;
      }
    } else if (t.step === 4) {                /* throw it at the shadow */
      this.hud.objective(touch ? T.throw_t : T.throw);
      const e = this.enemies.find((x) => x.alive);
      if (e) this.markRing(e.group, 1.2);
      else { this.step(5); this.waveTimer = 2.2; }
    } else if (t.step === 5) {                /* memory */
      this.hud.objective(T.ready);
      this.ring.visible = false;
      t.readyT = (t.readyT || 0) + dt;
      if (t.readyT > 2.4) this.step(6);
    }
  }
  step(n) {
    this.tut.step = n;
    this.audio.blip({ freq: 620, type: "sine", dur: 0.16, gain: 0.16, slide: 260 });
    this.hud.pulse();
  }
  markRing(obj, yOff = 0) {
    this.ring.visible = true;
    const y = yOff || (obj.geometry?.parameters?.height || 3) + 0.8;
    this.ring.position.set(obj.position.x, y + Math.sin(performance.now() * 0.004) * 0.18, obj.position.z);
    this.ring.rotation.z += 0.02;
    const s2 = 1 + Math.sin(performance.now() * 0.006) * 0.09;
    this.ring.scale.setScalar(s2);
  }

  /** axis-separated box sweep — cheap, predictable, no physics engine */
  movePlayer(delta) {
    const p = this.player;
    const R = 0.42, H = 1.7;
    const tryAxis = (axis, amount) => {
      if (!amount) return;
      p.pos[axis] += amount;
      const min = new THREE.Vector3(p.pos.x - R, p.pos.y - H, p.pos.z - R);
      const max = new THREE.Vector3(p.pos.x + R, p.pos.y + 0.25, p.pos.z + R);
      for (const b of BOXES) {
        if (max.x < b.min.x || min.x > b.max.x || max.y < b.min.y || min.y > b.max.y || max.z < b.min.z || min.z > b.max.z) continue;
        if (axis === "y") {
          if (amount < 0) { p.pos.y = b.max.y + H; p.vel.y = 0; p.onGround = true; }
          else { p.pos.y = b.min.y - 0.26; p.vel.y = 0; }
        } else {
          p.pos[axis] -= amount;
          p.vel[axis] = 0;
        }
        return;
      }
    };
    tryAxis("x", delta.x);
    tryAxis("z", delta.z);
    p.onGround = false;
    tryAxis("y", delta.y);
    if (p.pos.y <= 1.7) { p.pos.y = 1.7; p.vel.y = 0; p.onGround = true; }
  }

  loop() {
    requestAnimationFrame(this.loop);
    let dt = Math.min(this.clock.getDelta(), 0.05);
    if (this.hitStop > 0) { this.hitStop -= dt; dt *= 0.08; }
    if (this.state === "play") this.update(dt);
    else if (this.state === "paused") { /* frozen */ }
    else {
      this.camera.position.set(Math.sin(performance.now() * 0.00012) * 20, 6, Math.cos(performance.now() * 0.00012) * 20);
      this.camera.lookAt(0, 2, 0);
    }
    (this.composer || this.renderer).render(this.scene, this.camera);
  }
}

/* ════════════════════════════════════════════════════
   HUD — diegetic, three languages
   ════════════════════════════════════════════════════ */
const TXT = {
  ar: {
    title: "سَـرَاب", sub: "لا سلاح معك. اسرق صفةً من العالم، وارمِها على من يريد قتلك.",
    start: "اضغط للبدء", wave: "الموجة", score: "النقاط", memory: "الذاكرة", hp: "الجسد",
    hold: "في يدك", empty: "لا شيء",
    help: [
      "اللعبة هتعلّمك خطوة بخطوة — ابدأ فقط",
      "لا سلاح: تسرق صفة من الغرفة وترميها على عدوّك",
      "كل سرقة تُنقص ذاكرتك — وإعادتها تستعيدها",
    ],
    dead: "انطفأت", again: "اضغط للإعادة", final: "نتيجتك",
    tut: {
      look: "حرّك الفأرة لتنظر حولك",
      look_t: "اسحب يمين الشاشة لتنظر حولك",
      move: "امشِ بالأزرار W A S D",
      move_t: "اسحب يسار الشاشة لتمشي",
      aim: "صوّب على العمود المُحاط بالدائرة",
      steal: "زر الفأرة الأيمن — اسرق صفته",
      steal_t: "اضغط زر ⟡ — اسرق صفته",
      throw: "الصفة في يدك. صوّب على الظل واضغط الزر الأيسر",
      throw_t: "الصفة في يدك. صوّب على الظل وانقر الشاشة",
      ready: "كلما سرقت، نقصت ذاكرتك. استعدّ.",
    },
    tooHard: "قبضتك لا تكفي — اسرق صلابة وارمِها عليه",
    debt: "الدَّيْن قادم ليأخذ ما سرقت",
    tookIt: "أخذ الصفة منك",
    bossIn: "الحاضنة استيقظت",
    drain: "إنها تشرب ذاكرتك",
    coreOut: "بقي {n} من نوياتها",
    best: "الأفضل", combo: "متتالية",
    won: "نجوت", endings: {
      faithful: { t: "الوفاء", d: "خرجت وأنت تتذكّر لماذا دخلت. أعدت ما أخذت، فبقيت أنت أنت." },
      stranger: { t: "الغريب", d: "انتصرت… ولم تعد تعرف على من انتصرت. الاسم الذي جئت من أجله لم يعد في رأسك." },
      greedy:   { t: "الجَشِع", d: "لم تُعد شيئًا قط. القاعة خلفك خاوية، وأنت أقوى ممّا ينبغي وأخف ممّا كنت." },
    },
    pause: "توقّف", resume: "متابعة", restart: "من البداية", sound: "الصوت",
    touch: ["اسحب يسار الشاشة للحركة", "اسحب يمينها للنظر · انقر للضرب", "زر السرقة تحت"],
  },
  en: {
    title: "SARAB", sub: "You carry no weapon. Steal a property from the world and throw it at what wants you dead.",
    start: "Click to begin", wave: "WAVE", score: "SCORE", memory: "MEMORY", hp: "BODY",
    hold: "IN HAND", empty: "EMPTY",
    help: [
      "The game teaches you step by step — just start",
      "No weapon: steal a property from the room, throw it at your enemy",
      "Every theft costs memory — giving it back restores it",
    ],
    dead: "YOU WENT OUT", again: "Click to retry", final: "SCORE",
    tut: {
      look: "Move the mouse to look around",
      look_t: "Drag the right side to look around",
      move: "Walk with W A S D",
      move_t: "Drag the left side to walk",
      aim: "Aim at the marked pillar",
      steal: "Right mouse button — steal its property",
      steal_t: "Press ⟡ — steal its property",
      throw: "It is in your hand. Aim at the shadow and press left mouse",
      throw_t: "It is in your hand. Aim at the shadow and tap the screen",
      ready: "Every theft costs memory. Get ready.",
    },
    tooHard: "Your fist is not enough — steal hardness first",
    debt: "The Debt is coming for what you took",
    tookIt: "It took the property back",
    bossIn: "THE INCUBATOR IS AWAKE",
    drain: "It is drinking your memory",
    coreOut: "{n} cores left",
    best: "BEST", combo: "COMBO",
    won: "YOU SURVIVED", endings: {
      faithful: { t: "THE FAITHFUL", d: "You walked out still remembering why you walked in. What you took, you returned." },
      stranger: { t: "THE STRANGER", d: "You won, and no longer know who you beat. The name you came for is gone." },
      greedy:   { t: "THE GREEDY", d: "You returned nothing. The hall behind you is empty, and you are lighter than you were." },
    },
    pause: "PAUSED", resume: "Resume", restart: "Restart", sound: "Sound",
    touch: ["Drag left side to move", "Drag right side to look · tap to strike", "Steal button below"],
  },
};
TXT.tr = {
  title: "SERAP", sub: "Silahın yok. Odadan bir özellik çal ve seni öldürmek isteyene fırlat.",
  start: "Başlamak için tıkla", wave: "DALGA", score: "SKOR", memory: "HAFIZA", hp: "BEDEN",
  hold: "ELİNDE", empty: "BOŞ",
  help: [
    "Oyun sana adım adım öğretir — sadece başla",
    "Silah yok: odadan özellik çal, düşmana fırlat",
    "Her hırsızlık hafızandan yer — geri vermek onu geri kazandırır",
  ],
  dead: "SÖNDÜN", again: "Tekrar denemek için tıkla", final: "SKOR",
  tut: {
    look: "Etrafa bakmak için fareyi hareket ettir",
    look_t: "Bakmak için ekranın sağını sürükle",
    move: "W A S D ile yürü",
    move_t: "Yürümek için ekranın solunu sürükle",
    aim: "İşaretli sütuna nişan al",
    steal: "Sağ tık — özelliğini çal",
    steal_t: "⟡ düğmesine bas — özelliğini çal",
    throw: "Elinde. Gölgeye nişan al ve sol tıkla",
    throw_t: "Elinde. Gölgeye nişan al ve ekrana dokun",
    ready: "Her hırsızlık hafızandan yer. Hazır ol.",
  },
  tooHard: "Yumruğun yetmez — önce sertlik çal",
  debt: "Borç, çaldığını almaya geliyor",
  tookIt: "Özelliği senden geri aldı",
  bossIn: "KULUÇKA UYANDI",
  drain: "Hafızanı içiyor",
  coreOut: "{n} çekirdek kaldı",
  best: "EN İYİ", combo: "KOMBO",
  won: "HAYATTA KALDIN", endings: {
    faithful: { t: "VEFALI", d: "Neden girdiğini hatırlayarak çıktın. Aldığını geri verdin." },
    stranger: { t: "YABANCI", d: "Kazandın ama kimi yendiğini bilmiyorsun. Uğruna geldiğin isim gitti." },
    greedy:   { t: "AÇGÖZLÜ", d: "Hiçbir şeyi geri vermedin. Arkandaki salon boş, sen ise olduğundan hafifsin." },
  },
  pause: "DURAKLATILDI", resume: "Devam", restart: "Baştan", sound: "Ses",
};

class HUD {
  constructor(game) {
    this.g = game;
    this.t = TXT[game.lang];
    this.root = document.getElementById("hud");
    this.root.innerHTML = `
      <div id="crosshair"></div>
      <div id="objective"><span></span></div>
      <div id="vignette"></div>
      <div id="bars">
        <div class="bar"><span class="lbl">${this.t.memory}</span><div class="track"><i id="mem"></i></div></div>
        <div class="bar"><span class="lbl">${this.t.hp}</span><div class="track"><i id="hp" class="hp"></i></div></div>
      </div>
      <div id="stats"><span id="wave"></span><span id="score"></span><span id="combo"></span></div>
      <div id="toast"></div>
      <div id="hand"><span class="lbl">${this.t.hold}</span><b id="handv">${this.t.empty}</b></div>
      <button id="stealbtn" aria-label="steal">⟡</button>
      <div id="wavemsg"></div>
      <div id="screen"></div>`;
    this.mem = this.root.querySelector("#mem");
    this.hp = this.root.querySelector("#hp");
    this.waveEl = this.root.querySelector("#wave");
    this.scoreEl = this.root.querySelector("#score");
    this.handEl = this.root.querySelector("#handv");
    this.screen = this.root.querySelector("#screen");
    this.wavemsg = this.root.querySelector("#wavemsg");
    this.vig = this.root.querySelector("#vignette");
    this.obj = this.root.querySelector("#objective");
    this.objText = this.obj.firstElementChild;
    this.cross = this.root.querySelector("#crosshair");
    this.comboEl = this.root.querySelector("#combo");
    this.toastEl = this.root.querySelector("#toast");
    const sb = this.root.querySelector("#stealbtn");
    sb.addEventListener("touchstart", (e) => { e.preventDefault(); e.stopPropagation(); this.g.steal(); });
    sb.addEventListener("click", (e) => { e.stopPropagation(); this.g.steal(); });
    if (!game.isTouch()) sb.style.display = "none";
    this.screen.addEventListener("pointerdown", (e) => { e.preventDefault(); this.g.begin(); });
    this.setScreen("menu");
  }
  setScreen(kind) {
    const t = this.t, g = this.g;
    if (!kind) { this.screen.style.display = "none"; this.root.classList.remove("screened"); return; }
    this.screen.style.display = "grid";
    this.root.classList.add("screened");
    const best = g.best ? `<p class="best">${t.best} <b>${g.best}</b></p>` : "";
    const langs = `<div class="langs">${["ar", "en", "tr"]
      .map((l) => `<button data-lang="${l}" class="${l === g.lang ? "on" : ""}">${{ ar: "العربية", en: "English", tr: "Türkçe" }[l]}</button>`)
      .join("")}</div>`;

    if (kind === "menu") {
      this.screen.innerHTML = `<div class="card">
        <h1>${t.title}</h1><p class="sub">${t.sub}</p>
        <ul class="help">${t.help.map((h) => `<li>${h}</li>`).join("")}</ul>
        ${best}<div class="cta">${t.start}</div>${langs}</div>`;
    } else if (kind === "dead") {
      this.screen.innerHTML = `<div class="card">
        <h1 class="dead">${t.dead}</h1>
        <p class="final">${t.final} <b>${g.score}</b> · ${t.wave} ${g.wave}</p>
        ${best}<div class="cta">${t.again}</div></div>`;
    } else if (kind === "won") {
      const e = t.endings[g.ending] || t.endings.stranger;
      this.screen.innerHTML = `<div class="card">
        <p class="kicker">${t.won}</p>
        <h1 class="win">${e.t}</h1>
        <p class="sub">${e.d}</p>
        <p class="final">${t.final} <b>${g.score}</b></p>
        ${best}<div class="cta">${t.again}</div></div>`;
    } else if (kind === "paused") {
      this.screen.innerHTML = `<div class="card">
        <h1 class="pause">${t.pause}</h1>
        <p class="final">${t.final} <b>${g.score}</b></p>
        <div class="cta">${t.resume}</div>${langs}</div>`;
    }
    for (const btn of this.screen.querySelectorAll("[data-lang]")) {
      btn.addEventListener("pointerdown", (ev) => {
        ev.stopPropagation();
        this.g.setLang(btn.dataset.lang);
      });
    }
  }
  toast(text) {
    this.toastEl.textContent = text;
    this.toastEl.classList.remove("show");
    void this.toastEl.offsetWidth;
    this.toastEl.classList.add("show");
  }
  objective(text) {
    if (this.objText.textContent === text) return;
    this.objText.textContent = text;
    this.obj.style.opacity = text ? "1" : "0";
  }
  pulse() {
    this.obj.classList.remove("pulse");
    void this.obj.offsetWidth;
    this.obj.classList.add("pulse");
  }
  aim(kind) {
    if (this._aim === kind) return;
    this._aim = kind;
    this.cross.dataset.aim = kind || "";
  }
  flashWave(n) {
    this.wavemsg.textContent = `${this.t.wave} ${n}`;
    this.wavemsg.classList.remove("show");
    void this.wavemsg.offsetWidth;
    this.wavemsg.classList.add("show");
  }
  update() {
    const g = this.g, p = g.player;
    const m = p.memory / CFG.memoryMax;
    this.mem.style.width = (m * 100).toFixed(1) + "%";
    this.hp.style.width = clamp(p.hp, 0, 100).toFixed(0) + "%";
    this.waveEl.textContent = `${this.t.wave} ${g.wave}`;
    this.scoreEl.textContent = `${this.t.score} ${g.score}`;
    this.comboEl.textContent = g.combo > 1 ? `${this.t.combo} ×${g.comboMul().toFixed(1)}` : "";
    const held = p.held ? PROPS[p.held] : null;
    this.handEl.textContent = held ? held[g.lang] || held.en : this.t.empty;
    this.handEl.style.color = held ? "#" + held.color.toString(16).padStart(6, "0") : "#6d7a8c";
    /* the screen itself degrades with memory — the horror lives here */
    const bad = 1 - m;
    this.vig.style.opacity = (0.25 + bad * 0.6).toFixed(2);
    this.root.style.filter = `saturate(${(1 - bad * 0.7).toFixed(2)}) contrast(${(1 + bad * 0.25).toFixed(2)})`;
    document.body.style.setProperty("--glitch", bad > 0.6 ? "1" : "0");
    if (p.hurtT > 0) this.vig.style.boxShadow = "inset 0 0 18rem rgba(190,40,40,.55)";
    else this.vig.style.boxShadow = "";
  }
}

/* ── boot ── */
const canvas = document.getElementById("c");
window.__sarab = new Game(canvas);
