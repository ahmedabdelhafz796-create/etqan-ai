"use client";

import { motion } from "framer-motion";
import type { AutomationKind } from "@/config";

/**
 * A generated diagram standing in for a product screenshot.
 *
 * Screenshots of a workflow canvas photograph badly at card size — the node
 * labels are unreadable, so what the buyer actually sees is grey rectangles.
 * A stylised diagram communicates the same thing at a glance: how many moving
 * parts there are and how they connect.
 *
 * The shape encodes the product's `kind`, so a tool and a suite are
 * distinguishable before reading a word:
 *
 *   tool   — one linear path, a single job done well
 *   system — a path that branches and rejoins, several parts coordinating
 *   suite  — a hub with satellites, everything wired to a shared spine
 */
export function SystemGlyph({
  kind,
  className = "",
}: {
  kind: AutomationKind;
  className?: string;
}) {
  return (
    <div
      aria-hidden
      className={`relative overflow-hidden rounded-xl border border-white/[0.06] bg-gradient-to-br from-white/[0.04] to-transparent ${className}`}
    >
      <svg
        viewBox="0 0 320 120"
        className="h-full w-full"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <linearGradient id={`g-${kind}`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#E9C46A" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#C9A227" stopOpacity="0.35" />
          </linearGradient>
        </defs>

        {kind === "tool" && <ToolShape />}
        {kind === "system" && <SystemShape />}
        {kind === "suite" && <SuiteShape />}
      </svg>
    </div>
  );
}

const EDGE = "rgba(233,196,106,0.28)";
const NODE = "rgba(233,196,106,0.9)";

function Node({ x, y, r = 6 }: { x: number; y: number; r?: number }) {
  return (
    <>
      <circle cx={x} cy={y} r={r + 5} fill={NODE} opacity={0.1} />
      <circle cx={x} cy={y} r={r} fill="#0C1019" stroke={NODE} strokeWidth="1.5" />
    </>
  );
}

/** Draws itself in, once, on reveal. Motion is subtle and runs a single time. */
function Edge({ d, delay = 0 }: { d: string; delay?: number }) {
  return (
    <motion.path
      d={d}
      fill="none"
      stroke={EDGE}
      strokeWidth="1.5"
      initial={{ pathLength: 0 }}
      whileInView={{ pathLength: 1 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.8, delay, ease: "easeOut" }}
    />
  );
}

function ToolShape() {
  return (
    <g>
      <Edge d="M 40 60 H 160" />
      <Edge d="M 160 60 H 280" delay={0.15} />
      <Node x={40} y={60} />
      <Node x={160} y={60} r={8} />
      <Node x={280} y={60} />
    </g>
  );
}

function SystemShape() {
  return (
    <g>
      <Edge d="M 34 60 H 96" />
      {/* branch out */}
      <Edge d="M 96 60 C 128 60 128 28 160 28" delay={0.12} />
      <Edge d="M 96 60 C 128 60 128 92 160 92" delay={0.12} />
      {/* rejoin */}
      <Edge d="M 160 28 C 200 28 200 60 232 60" delay={0.28} />
      <Edge d="M 160 92 C 200 92 200 60 232 60" delay={0.28} />
      <Edge d="M 232 60 H 288" delay={0.42} />
      <Node x={34} y={60} r={5} />
      <Node x={96} y={60} />
      <Node x={160} y={28} />
      <Node x={160} y={92} />
      <Node x={232} y={60} />
      <Node x={288} y={60} r={5} />
    </g>
  );
}

function SuiteShape() {
  // Hub-and-spoke: the spine workflows every other template reports into.
  const hub = { x: 160, y: 60 };
  const sats = [
    { x: 62, y: 30 },
    { x: 62, y: 90 },
    { x: 160, y: 18 },
    { x: 160, y: 102 },
    { x: 258, y: 30 },
    { x: 258, y: 90 },
  ];
  return (
    <g>
      {sats.map((s, i) => (
        <Edge
          key={i}
          d={`M ${hub.x} ${hub.y} L ${s.x} ${s.y}`}
          delay={i * 0.07}
        />
      ))}
      {sats.map((s, i) => (
        <Node key={i} x={s.x} y={s.y} r={5} />
      ))}
      <circle cx={hub.x} cy={hub.y} r={17} fill={NODE} opacity={0.08} />
      <Node x={hub.x} y={hub.y} r={10} />
    </g>
  );
}
