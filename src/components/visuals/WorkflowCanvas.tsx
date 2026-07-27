"use client";

import * as React from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  FileCheck2,
  Mail,
  ShieldCheck,
  Webhook,
  type LucideIcon,
} from "lucide-react";

/**
 * The hero visual: a workflow canvas, the way n8n / Make / Zapier show one.
 *
 * This replaced a stack of 3D book covers on a candlestick field. The
 * homepage sells automation, so the first thing a visitor sees has to be
 * an automation — nodes, connectors, a run travelling through them, and a
 * branch that handles the failure case rather than pretending it can't
 * happen.
 *
 * The graph drawn here is the real shape of `instant-digital-delivery`:
 * webhook → verify signature → gate on payment → sign link → email, with
 * the rejected branch going somewhere instead of nowhere. That branch is
 * the product's whole argument, so it is on screen from the first second.
 */

type NodeSpec = {
  id: string;
  label: string;
  sub?: string;
  icon: LucideIcon;
  x: number;
  y: number;
  tone: "trigger" | "logic" | "action" | "guard" | "error";
};

const NODES: NodeSpec[] = [
  { id: "hook", label: "Payment webhook", sub: "6 gateways", icon: Webhook, x: 0, y: 118, tone: "trigger" },
  { id: "verify", label: "Verify signature", sub: "HMAC · timing-safe", icon: ShieldCheck, x: 232, y: 42, tone: "guard" },
  { id: "gate", label: "Paid, not replayed?", sub: "idempotency key", icon: FileCheck2, x: 232, y: 196, tone: "logic" },
  { id: "sign", label: "Sign download link", sub: "expiring · capped", icon: Bot, x: 470, y: 118, tone: "action" },
  { id: "mail", label: "Deliver to buyer", sub: "retry ×3, backoff", icon: Mail, x: 700, y: 42, tone: "action" },
  { id: "err", label: "Error hub", sub: "ranked · never silent", icon: AlertTriangle, x: 700, y: 196, tone: "error" },
];

const EDGES: Array<{ from: string; to: string; live?: boolean; label?: string }> = [
  { from: "hook", to: "verify", live: true },
  { from: "hook", to: "gate", live: true },
  { from: "verify", to: "sign", live: true },
  { from: "gate", to: "sign", live: true, label: "true" },
  { from: "sign", to: "mail", live: true },
  { from: "sign", to: "err", label: "on error" },
];

const NODE_W = 178;
const NODE_H = 62;
const VB_W = 878;
const VB_H = 292;

const TONE: Record<NodeSpec["tone"], { ring: string; fill: string; icon: string }> = {
  trigger: { ring: "rgba(34,211,238,0.55)", fill: "rgba(34,211,238,0.10)", icon: "#67E8F9" },
  guard: { ring: "rgba(99,102,241,0.55)", fill: "rgba(99,102,241,0.10)", icon: "#A5B4FC" },
  logic: { ring: "rgba(129,140,248,0.45)", fill: "rgba(129,140,248,0.08)", icon: "#A5B4FC" },
  action: { ring: "rgba(99,102,241,0.55)", fill: "rgba(99,102,241,0.10)", icon: "#A5B4FC" },
  error: { ring: "rgba(239,68,68,0.45)", fill: "rgba(239,68,68,0.08)", icon: "#FCA5A5" },
};

function nodeById(id: string) {
  const n = NODES.find((n) => n.id === id);
  if (!n) throw new Error(`unknown node ${id}`);
  return n;
}

/** Right edge of `from` to left edge of `to`, as a smooth cubic. */
function edgePath(fromId: string, toId: string) {
  const a = nodeById(fromId);
  const b = nodeById(toId);
  const x1 = a.x + NODE_W;
  const y1 = a.y + NODE_H / 2;
  const x2 = b.x;
  const y2 = b.y + NODE_H / 2;
  const dx = Math.max(46, (x2 - x1) * 0.55);
  return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
}

export function WorkflowCanvas({ className = "" }: { className?: string }) {
  return (
    <div
      className={`relative overflow-hidden rounded-2xl border border-white/[0.09] bg-night-800/60 backdrop-blur-xl ${className}`}
    >
      <div aria-hidden className="canvas-dots absolute inset-0 opacity-60" />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_35%_0%,rgba(99,102,241,0.16),transparent_70%)]"
      />

      {/* Editor chrome — reads instantly as "this is a real workflow tool". */}
      <div className="relative flex items-center justify-between border-b border-white/[0.07] px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-white/15" />
          <span className="h-2.5 w-2.5 rounded-full bg-white/15" />
          <span className="h-2.5 w-2.5 rounded-full bg-white/15" />
          <span className="ml-2 font-mono text-[11px] text-white/40">
            instant-digital-delivery.json
          </span>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald/25 bg-emerald/10 px-2.5 py-1 font-mono text-[10px] text-emerald-light">
          <CheckCircle2 className="h-3 w-3" />
          15 nodes · tests passing
        </span>
      </div>

      <div className="relative p-4">
        <svg
          viewBox={`0 0 ${VB_W} ${VB_H}`}
          className="h-auto w-full"
          role="img"
          aria-label="Workflow diagram: a payment webhook is signature-verified and checked for replay, then a signed download link is generated and emailed to the buyer, with failures routed to an error hub."
        >
          <defs>
            <linearGradient id="wf-edge" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#6366F1" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#22D3EE" stopOpacity="0.5" />
            </linearGradient>
          </defs>

          {EDGES.map((e, i) => {
            const d = edgePath(e.from, e.to);
            const isError = e.to === "err";
            return (
              <g key={`${e.from}-${e.to}`}>
                <path
                  d={d}
                  fill="none"
                  stroke={isError ? "rgba(239,68,68,0.34)" : "url(#wf-edge)"}
                  strokeWidth="1.75"
                  strokeDasharray={isError ? "4 5" : undefined}
                />
                {e.live && (
                  <path
                    d={d}
                    fill="none"
                    stroke="#A5B4FC"
                    strokeWidth="2"
                    className="flow-dash"
                    style={{ animationDelay: `${i * 0.18}s` }}
                    opacity="0.85"
                  />
                )}
              </g>
            );
          })}

          {NODES.map((n, i) => {
            const tone = TONE[n.tone];
            return (
              <motion.g
                key={n.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.15 + i * 0.09, ease: [0.22, 1, 0.36, 1] }}
              >
                <rect
                  x={n.x}
                  y={n.y}
                  width={NODE_W}
                  height={NODE_H}
                  rx="12"
                  fill="#0C1019"
                  stroke={tone.ring}
                  strokeWidth="1.25"
                />
                <rect
                  x={n.x}
                  y={n.y}
                  width={NODE_W}
                  height={NODE_H}
                  rx="12"
                  fill={tone.fill}
                />
                <foreignObject x={n.x} y={n.y} width={NODE_W} height={NODE_H}>
                  <div className="flex h-full items-center gap-2.5 px-3">
                    <span
                      className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg"
                      style={{ background: tone.fill, color: tone.icon }}
                    >
                      <n.icon className="h-4 w-4" strokeWidth={2} />
                    </span>
                    <span className="min-w-0">
                      <span className="block truncate text-[12.5px] font-semibold leading-tight text-white/85">
                        {n.label}
                      </span>
                      {n.sub && (
                        <span className="block truncate font-mono text-[10px] leading-tight text-white/35">
                          {n.sub}
                        </span>
                      )}
                    </span>
                  </div>
                </foreignObject>
              </motion.g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
