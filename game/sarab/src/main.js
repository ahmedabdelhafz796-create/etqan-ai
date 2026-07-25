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
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.shadowMap.enabled = false;
  }
  onResize() {
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
  }

  /* ── scene ── */
  initScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x05070b);
    this.scene.fog = new THREE.FogExp2(0x070a10, 0.016);

    this.camera = new THREE.PerspectiveCamera(78, window.innerWidth / window.innerHeight, 0.1, 260);

    this.scene.add(new THREE.HemisphereLight(0x5f86c4, 0x0b1018, 1.35));
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
  }

  /** The arena: floor, outer walls, and props that still hold properties. */
  buildArena() {
    BOXES.length = 0;
    const S = 46;

    const floorMat = new THREE.MeshStandardMaterial({ color: 0x1d2735, roughness: 0.92, metalness: 0.06 });
    const floor = new THREE.Mesh(new THREE.BoxGeometry(S, 1, S), floorMat);
    floor.position.y = -0.5;
    this.scene.add(floor);

    const grid = new THREE.GridHelper(S, 23, 0x3f6fa8, 0x22344a);
    grid.position.y = 0.02;
    this.scene.add(grid);

    const wallMat = new THREE.MeshStandardMaterial({ color: 0x18212e, roughness: 1 });
    const h = 14;
    const walls = [
      [0, h / 2, -S / 2, S, h, 1],
      [0, h / 2, S / 2, S, h, 1],
      [-S / 2, h / 2, 0, 1, h, S],
      [S / 2, h / 2, 0, 1, h, S],
    ];
    const ceil = new THREE.Mesh(new THREE.BoxGeometry(S, 1, S), new THREE.MeshStandardMaterial({ color: 0x0c111a, roughness: 1 }));
    ceil.position.y = h + 0.5;
    this.scene.add(ceil);

    for (const [x, y, z, w, hh, d] of walls) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, hh, d), wallMat);
      m.position.set(x, y, z);
      this.scene.add(m);
      this.addCollider(m);
    }

    /* props — each one still owns a property you can take */
    this.props = [];
    const layout = [
      { x: -11, z: -9, w: 3, h: 4.4, d: 3, prop: "hardness" },
      { x: 10, z: -12, w: 3, h: 4.4, d: 3, prop: "hardness" },
      { x: 14, z: 8, w: 3.4, h: 3.2, d: 3.4, prop: "weight" },
      { x: -14, z: 10, w: 3.4, h: 3.2, d: 3.4, prop: "weight" },
      { x: 0, z: -16, w: 5, h: 2.2, d: 2.2, prop: "weight" },
      { x: -6, z: 14, w: 2.4, h: 5.4, d: 2.4, prop: "speed" },
      { x: 7, z: 15, w: 2.4, h: 5.4, d: 2.4, prop: "speed" },
      { x: 17, z: -3, w: 2.2, h: 6.2, d: 2.2, prop: "speed" },
      { x: -17, z: 2, w: 2.2, h: 6.2, d: 2.2, prop: "hardness" },
      { x: 4, z: 4, w: 6, h: 1.4, d: 6, prop: "weight" },
    ];
    for (const p of layout) this.addProp(p);
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
    const n = 260, pos = [];
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
  }

  /* ── input ── */
  initInput() {
    this.keys = {};
    this.touch = { move: null, look: null, moveVec: { x: 0, y: 0 } };

    addEventListener("keydown", (e) => {
      this.keys[e.code] = true;
      if (e.code === "Space") e.preventDefault();
      if (this.state === "menu" || this.state === "dead") this.begin();
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
  begin() {
    if (this.state === "play") return;
    this.audio.start();
    this.reset();
    this.state = "play";
    this.hud.setScreen(null);
    if (!this.isTouch()) this.canvas.requestPointerLock();
  }
  die() {
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
    ];
    const hit = ray.intersectObjects(meshes, false)[0];
    return hit ? hit.object : null;
  }

  steal() {
    const t = this.targetUnderCrosshair();
    if (!t) return;
    const p = this.player;

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
      if (t && t.userData.enemy) this.damageEnemy(t.userData.enemy, 34);
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
  spawnWave() {
    this.wave++;
    this.audio.wave();
    this.hud.flashWave(this.wave);
    const count = Math.min(3 + this.wave * 2, 16);
    for (let i = 0; i < count; i++) {
      const a = rand(0, Math.PI * 2), r = rand(16, 21);
      this.spawnEnemy(new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r));
    }
  }

  spawnEnemy(pos) {
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

    g.position.copy(pos);
    this.scene.add(g);

    const carries = ["weight", "hardness", "speed"][Math.floor(rand(0, 3))];
    const e = {
      group: g, hitbox, parts: { legL, legR, armL, armR, torso, head },
      alive: true, hp: 100, phase: rand(0, 6.28),
      speed: CFG.enemyBaseSpeed + this.wave * 0.16 + rand(-0.3, 0.3),
      atkCd: rand(0.4, 1.4), slowT: 0, carries,
    };
    hitbox.userData.enemy = e;
    this.enemies.push(e);
  }

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
    this.score += 20;
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
          const dmg = CFG.enemyDamage * (hard ? 0.35 : 1);
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

    /* waves */
    if (this.enemies.length === 0) {
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

    this.dust.rotation.y += 0.012 * dt;
    this.audio.tension(p.memory / CFG.memoryMax);
    this.hud.update();
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
    else {
      this.camera.position.set(Math.sin(performance.now() * 0.00012) * 20, 6, Math.cos(performance.now() * 0.00012) * 20);
      this.camera.lookAt(0, 2, 0);
    }
    this.renderer.render(this.scene, this.camera);
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
      "الحركة: W A S D · القفز: مسافة",
      "زر الفأرة الأيمن: اسرق صفة · الأيسر: ارمِها",
      "الوزن = تطير · الصلابة = تتحمّل · السرعة = العالم يبطؤ (Shift)",
      "أعِد الصفة لصاحبها لتستعيد ذاكرتك",
    ],
    dead: "انطفأت", again: "اضغط للإعادة", final: "نتيجتك",
    touch: ["اسحب يسار الشاشة للحركة", "اسحب يمينها للنظر · انقر للضرب", "زر السرقة تحت"],
  },
  en: {
    title: "SARAB", sub: "You carry no weapon. Steal a property from the world and throw it at what wants you dead.",
    start: "Click to begin", wave: "WAVE", score: "SCORE", memory: "MEMORY", hp: "BODY",
    hold: "IN HAND", empty: "EMPTY",
    help: [
      "Move: W A S D · Jump: Space",
      "Right mouse: steal a property · Left: throw it",
      "Weight = you fly · Hardness = you endure · Speed = world slows (Shift)",
      "Give a property back to restore memory",
    ],
    dead: "YOU WENT OUT", again: "Click to retry", final: "SCORE",
    touch: ["Drag left side to move", "Drag right side to look · tap to strike", "Steal button below"],
  },
};

class HUD {
  constructor(game) {
    this.g = game;
    this.t = TXT[game.lang];
    this.root = document.getElementById("hud");
    this.root.innerHTML = `
      <div id="crosshair"></div>
      <div id="vignette"></div>
      <div id="bars">
        <div class="bar"><span class="lbl">${this.t.memory}</span><div class="track"><i id="mem"></i></div></div>
        <div class="bar"><span class="lbl">${this.t.hp}</span><div class="track"><i id="hp" class="hp"></i></div></div>
      </div>
      <div id="stats"><span id="wave"></span><span id="score"></span></div>
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
    const sb = this.root.querySelector("#stealbtn");
    sb.addEventListener("touchstart", (e) => { e.preventDefault(); e.stopPropagation(); this.g.steal(); });
    sb.addEventListener("click", (e) => { e.stopPropagation(); this.g.steal(); });
    if (!game.isTouch()) sb.style.display = "none";
    this.screen.addEventListener("pointerdown", (e) => { e.preventDefault(); this.g.begin(); });
    this.setScreen("menu");
  }
  setScreen(kind) {
    const t = this.t, g = this.g;
    if (!kind) { this.screen.style.display = "none"; return; }
    this.screen.style.display = "grid";
    const help = (g.isTouch() ? t.touch : t.help).map((h) => `<li>${h}</li>`).join("");
    this.screen.innerHTML = kind === "menu"
      ? `<div class="card">
           <h1>${t.title}</h1><p class="sub">${t.sub}</p>
           <ul class="help">${help}</ul>
           <div class="cta">${t.start}</div>
         </div>`
      : `<div class="card">
           <h1 class="dead">${t.dead}</h1>
           <p class="final">${t.final} <b>${g.score}</b> · ${t.wave} ${g.wave}</p>
           <div class="cta">${t.again}</div>
         </div>`;
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
