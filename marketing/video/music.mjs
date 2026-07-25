/**
 * ============================================================
 *  E-tqan — generative score
 * ============================================================
 *  A dependency-free, deterministic cinematic-inspirational bed:
 *  warm pads + soft piano + sub heartbeat + percussive ticks,
 *  arranged to the promo's shape (calm intro → build → swell at
 *  ~83% → resolve → gold sting). Any duration; the arrangement
 *  scales with it, so the cut-downs get their own coherent mix.
 *
 *    node music.mjs out.wav 150
 *  or  import { renderMusic } from "./music.mjs"
 * ============================================================
 */

const SR = 48000;
const TAU = Math.PI * 2;

/* D minor family — Dm · Bb · F · C (semitones from A4 = 0). */
const PROG = [
  { root: -7, ch: [-7, -3, 0, 5] },     // Dm
  { root: -11, ch: [-11, -4, 0, 4] },   // Bb
  { root: -4, ch: [-4, 0, 3, 8] },      // F
  { root: 3, ch: [3, 7, 10, 15] },      // C
];
const hz = (semi, oct = 0) => 440 * Math.pow(2, (semi + oct * 12) / 12);
const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const lerp = (a, b, t) => a + (b - a) * t;

function mulberry(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let x = Math.imul(s ^ (s >>> 15), 1 | s);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

/** One-pole low-pass, used to warm up every layer. */
function lowpass(buf, cutoff) {
  const a = 1 - Math.exp((-TAU * cutoff) / SR);
  let z = 0;
  for (let i = 0; i < buf.length; i++) { z += a * (buf[i] - z); buf[i] = z; }
  return buf;
}

export function renderMusic(duration = 150, seed = 20260725) {
  const n = Math.round(duration * SR);
  const L = new Float32Array(n);
  const R = new Float32Array(n);
  const rnd = mulberry(seed);

  const bpm = 84;
  const beat = 60 / bpm;
  const bar = beat * 4;
  const bars = Math.ceil(duration / bar);

  /* Arrangement intensity as a function of normalised time. */
  const shape = (u) =>
    u < 0.08 ? lerp(0.25, 0.42, u / 0.08)
    : u < 0.35 ? lerp(0.42, 0.6, (u - 0.08) / 0.27)
    : u < 0.62 ? lerp(0.6, 0.76, (u - 0.35) / 0.27)
    : u < 0.83 ? lerp(0.76, 0.9, (u - 0.62) / 0.21)
    : u < 0.95 ? lerp(1.0, 0.86, (u - 0.83) / 0.12)
    : lerp(0.7, 0.2, (u - 0.95) / 0.05);

  const add = (i, l, r) => { if (i >= 0 && i < n) { L[i] += l; R[i] += r; } };

  /* ── pads: slow, detuned, wide ─────────────────────── */
  const pad = new Float32Array(n);
  for (let b = 0; b < bars; b++) {
    const chord = PROG[b % PROG.length];
    const t0 = Math.round(b * bar * SR);
    const len = Math.round(bar * SR * 1.12);
    for (const note of chord.ch) {
      for (const det of [-0.09, 0, 0.11]) {
        const f = hz(note + det, -1);
        const ph = rnd() * TAU;
        for (let i = 0; i < len; i++) {
          const idx = t0 + i;
          if (idx >= n) break;
          const e = Math.min(i / (SR * 0.9), 1) * Math.max(0, 1 - Math.max(0, i - len * 0.6) / (len * 0.4));
          const u = idx / n;
          const s = (Math.sin(TAU * f * (i / SR) + ph) + 0.32 * Math.sin(TAU * 2 * f * (i / SR) + ph)) * e;
          pad[idx] += s * 0.055 * shape(u);
        }
      }
    }
  }
  lowpass(pad, 1400);

  /* ── piano-ish plucks: sparse in the intro, flowing later ── */
  const keys = new Float32Array(n);
  for (let b = 0; b < bars; b++) {
    const u = (b * bar) / duration;
    const chord = PROG[b % PROG.length];
    const density = u < 0.08 ? 1 : u < 0.35 ? 2 : u < 0.83 ? 4 : 3;
    for (let k = 0; k < density; k++) {
      const at = b * bar + (k * bar) / density + (rnd() - 0.5) * 0.012;
      const note = chord.ch[(k + b) % chord.ch.length] + (k % 2 === 0 ? 12 : 0);
      const f = hz(note, 0);
      const t0 = Math.round(at * SR);
      const len = Math.round(SR * 1.9);
      const pan = 0.5 + (rnd() - 0.5) * 0.5;
      for (let i = 0; i < len; i++) {
        const idx = t0 + i;
        if (idx >= n) break;
        const e = Math.exp(-i / (SR * 0.42)) * Math.min(i / 220, 1);
        const s = (Math.sin(TAU * f * (i / SR)) + 0.28 * Math.sin(TAU * 2.01 * f * (i / SR)) +
                   0.12 * Math.sin(TAU * 3.02 * f * (i / SR))) * e * 0.09 * shape(idx / n);
        keys[idx] += s;
        L[idx] += s * (1 - pan) * 0.6;
        R[idx] += s * pan * 0.6;
      }
    }
  }

  /* ── sub heartbeat + downbeat kick ─────────────────── */
  for (let b = 0; b < bars; b++) {
    const u = (b * bar) / duration;
    const hits = u < 0.35 ? [0] : u < 0.83 ? [0, 2] : [0, 1.5, 2, 3];
    for (const h of hits) {
      const t0 = Math.round((b * bar + h * beat) * SR);
      const len = Math.round(SR * 0.55);
      for (let i = 0; i < len; i++) {
        const idx = t0 + i;
        if (idx >= n) break;
        const tt = i / SR;
        const f = lerp(78, 44, clamp(tt / 0.12, 0, 1));
        const e = Math.exp(-tt * 9) * 0.5 * shape(idx / n);
        const s = Math.sin(TAU * f * tt) * e;
        add(idx, s, s);
      }
    }
  }

  /* ── percussive ticks (filtered noise) from the montage on ── */
  const tick = new Float32Array(n);
  for (let b = 0; b < bars; b++) {
    const u = (b * bar) / duration;
    if (u < 0.2 || u > 0.97) continue;
    const div = u < 0.62 ? 2 : 4;
    for (let k = 0; k < div * 2; k++) {
      const t0 = Math.round((b * bar + (k * bar) / (div * 2)) * SR);
      const len = Math.round(SR * 0.05);
      const amp = (k % 2 === 0 ? 0.5 : 0.24) * shape(u);
      for (let i = 0; i < len; i++) {
        const idx = t0 + i;
        if (idx >= n) break;
        tick[idx] += (rnd() * 2 - 1) * Math.exp(-i / (SR * 0.008)) * 0.055 * amp;
      }
    }
  }
  lowpass(tick, 7200);

  /* ── swell riser into the climax ───────────────────── */
  const swellAt = duration * 0.83;
  {
    const t0 = Math.round((swellAt - 3.2) * SR);
    const len = Math.round(3.2 * SR);
    for (let i = 0; i < len; i++) {
      const idx = t0 + i;
      if (idx < 0 || idx >= n) continue;
      const p = i / len;
      const f = lerp(180, 900, p * p);
      const s = (rnd() * 2 - 1) * 0.06 * p * p + Math.sin(TAU * f * (i / SR)) * 0.035 * p;
      add(idx, s, s * 0.92);
    }
  }

  /* ── final gold sting: bell + shimmer ──────────────── */
  {
    const t0 = Math.round(Math.max(0, duration - 7.6) * SR);
    const partials = [1, 2.01, 2.99, 4.21, 5.43];
    for (let pi = 0; pi < partials.length; pi++) {
      const f = hz(5, 0) * partials[pi];
      const len = Math.round(SR * 6.5);
      for (let i = 0; i < len; i++) {
        const idx = t0 + i;
        if (idx >= n) break;
        const e = Math.exp(-i / (SR * (1.9 - pi * 0.24))) * Math.min(i / 160, 1);
        const s = Math.sin(TAU * f * (i / SR)) * e * (0.075 / (pi + 1));
        add(idx, s, s);
      }
    }
  }

  /* ── mix, widen, soft-clip, fades ──────────────────── */
  const preDelay = Math.round(0.021 * SR);
  for (let i = 0; i < n; i++) {
    const p = pad[i], k = keys[i] * 0.35, t = tick[i];
    L[i] += p * 0.95 + k + t;
    R[i] += (i > preDelay ? pad[i - preDelay] : p) * 0.95 + k + t * 0.85;
  }
  const fi = Math.round(1.6 * SR), fo = Math.round(2.4 * SR);
  let peak = 0;
  for (let i = 0; i < n; i++) {
    const g = Math.min(1, i / fi) * Math.min(1, (n - i) / fo);
    L[i] *= g; R[i] *= g;
    L[i] = Math.tanh(L[i] * 1.25) * 0.8;
    R[i] = Math.tanh(R[i] * 1.25) * 0.8;
    peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  }
  const norm = peak > 0 ? 0.89 / peak : 1;

  /* ── 16-bit stereo WAV ─────────────────────────────── */
  const bytes = n * 4;
  const buf = Buffer.alloc(44 + bytes);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + bytes, 4); buf.write("WAVE", 8);
  buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28);
  buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34);
  buf.write("data", 36); buf.writeUInt32LE(bytes, 40);
  for (let i = 0; i < n; i++) {
    buf.writeInt16LE(Math.round(clamp(L[i] * norm, -1, 1) * 32767), 44 + i * 4);
    buf.writeInt16LE(Math.round(clamp(R[i] * norm, -1, 1) * 32767), 46 + i * 4);
  }
  return buf;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [, , out = "music.wav", dur = "150"] = process.argv;
  const { writeFileSync } = await import("fs");
  writeFileSync(out, renderMusic(Number(dur)));
  console.log(`[music] ${out} · ${dur}s`);
}
