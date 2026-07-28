"use client";

import { motion } from "framer-motion";
import type { AutomationKind } from "@/config";

/**
 * The product illustration on every bundle card.
 *
 * A screenshot of an n8n canvas is unreadable at card size — the node
 * labels vanish and the buyer sees grey rectangles. A generated diagram
 * carries the two things that actually matter at a glance: how many
 * moving parts there are, and how they are wired.
 *
 *   tool   — one linear path. A single job, done properly.
 *   system — a path that branches on a decision and rejoins, with a
 *            failure branch peeling off. Several workflows cooperating.
 *   suite  — a hub with satellites: everything reporting into the shared
 *            error hub and pulse that the full suite installs.
 */
export function BundleDiagram({
  kind,
  className = "",
  accent = "iris",
}: {
  kind: AutomationKind;
  className?: string;
  accent?: "iris" | "aqua";
}) {
  const stroke = accent === "aqua" ? "rgba(34,211,238,0.34)" : "rgba(129,140,248,0.34)";
  const node = accent === "aqua" ? "#67E8F9" : "#A5B4FC";

  return (
    <div
      aria-hidden
      className={`canvas-dots relative overflow-hidden rounded-xl border border-white/[0.07] bg-gradient-to-br from-iris/[0.07] via-white/[0.01] to-transparent ${className}`}
    >
      <svg viewBox="0 0 320 132" className="h-full w-full" preserveAspectRatio="xMidYMid meet">
        {kind === "tool" && <Tool stroke={stroke} node={node} />}
        {kind === "system" && <System stroke={stroke} node={node} />}
        {kind === "suite" && <Suite stroke={stroke} node={node} />}
      </svg>
    </div>
  );
}

type P = { stroke: string; node: string };

function Node({ x, y, r = 6, color }: { x: number; y: number; r?: number; color: string }) {
  return (
    <>
      <circle cx={x} cy={y} r={r + 5} fill={color} opacity={0.12} />
      <circle cx={x} cy={y} r={r} fill="#0C1019" stroke={color} strokeWidth="1.5" />
    </>
  );
}

/** Draws itself in once on reveal. Subtle, and it never loops. */
function Edge({
  d,
  delay = 0,
  stroke,
  dashed,
}: {
  d: string;
  delay?: number;
  stroke: string;
  dashed?: boolean;
}) {
  return (
    <motion.path
      d={d}
      fill="none"
      stroke={stroke}
      strokeWidth="1.5"
      strokeDasharray={dashed ? "3 4" : undefined}
      initial={{ pathLength: 0 }}
      whileInView={{ pathLength: 1 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.75, delay, ease: "easeOut" }}
    />
  );
}

function Tool({ stroke, node }: P) {
  return (
    <g>
      <Edge d="M 46 66 H 160" stroke={stroke} />
      <Edge d="M 160 66 H 274" stroke={stroke} delay={0.15} />
      <Node x={46} y={66} color={node} />
      <Node x={160} y={66} r={9} color={node} />
      <Node x={274} y={66} color={node} />
    </g>
  );
}

function System({ stroke, node }: P) {
  return (
    <g>
      <Edge d="M 34 66 H 92" stroke={stroke} />
      <Edge d="M 92 66 C 122 66 122 32 154 32" stroke={stroke} delay={0.12} />
      <Edge d="M 92 66 C 122 66 122 100 154 100" stroke={stroke} delay={0.12} />
      <Edge d="M 154 32 C 194 32 194 66 224 66" stroke={stroke} delay={0.28} />
      <Edge d="M 154 100 C 194 100 194 66 224 66" stroke={stroke} delay={0.28} />
      <Edge d="M 224 66 H 286" stroke={stroke} delay={0.42} />
      {/* The failure branch. Present in every system here, so it is drawn. */}
      <Edge
        d="M 224 66 C 250 66 252 108 286 112"
        stroke="rgba(239,68,68,0.32)"
        delay={0.5}
        dashed
      />
      <Node x={34} y={66} r={5} color={node} />
      <Node x={92} y={66} color={node} />
      <Node x={154} y={32} color={node} />
      <Node x={154} y={100} color={node} />
      <Node x={224} y={66} color={node} />
      <Node x={286} y={66} r={5} color={node} />
      <Node x={286} y={112} r={4} color="#FCA5A5" />
    </g>
  );
}

function Suite({ stroke, node }: P) {
  const hub = { x: 160, y: 66 };
  const sats = [
    { x: 52, y: 30 },
    { x: 40, y: 66 },
    { x: 52, y: 102 },
    { x: 160, y: 18 },
    { x: 160, y: 114 },
    { x: 268, y: 30 },
    { x: 280, y: 66 },
    { x: 268, y: 102 },
  ];
  return (
    <g>
      {sats.map((s, i) => (
        <Edge
          key={i}
          d={`M ${hub.x} ${hub.y} L ${s.x} ${s.y}`}
          delay={i * 0.06}
          stroke={stroke}
        />
      ))}
      {sats.map((s, i) => (
        <Node key={i} x={s.x} y={s.y} r={5} color={node} />
      ))}
      <circle cx={hub.x} cy={hub.y} r={19} fill={node} opacity={0.09} />
      <Node x={hub.x} y={hub.y} r={11} color={node} />
    </g>
  );
}
