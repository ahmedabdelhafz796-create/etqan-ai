"use client";

import * as React from "react";
import { Loader2, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Coupon {
  code: string;
  percent_off: number;
  active: number;
  max_redemptions: number | null;
  redeemed: number;
  expires_at: number | null;
}

export function CouponAdmin() {
  const [coupons, setCoupons] = React.useState<Coupon[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [code, setCode] = React.useState("");
  const [percent, setPercent] = React.useState("15");
  const [max, setMax] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [err, setErr] = React.useState("");

  const load = React.useCallback(async () => {
    try {
      const res = await fetch("/api/admin/coupons");
      if (res.ok) {
        const d = (await res.json()) as { coupons: Coupon[] };
        setCoupons(d.coupons || []);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void load();
  }, [load]);

  async function create() {
    setErr("");
    setBusy(true);
    try {
      const res = await fetch("/api/admin/coupons", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code,
          percentOff: Number(percent),
          maxRedemptions: max ? Number(max) : null,
        }),
      });
      if (res.ok) {
        setCode("");
        setMax("");
        await load();
      } else {
        const d = (await res.json().catch(() => ({}))) as { message?: string };
        setErr(d.message || "Failed to create coupon.");
      }
    } finally {
      setBusy(false);
    }
  }

  async function remove(c: string) {
    await fetch(`/api/admin/coupons?code=${encodeURIComponent(c)}`, { method: "DELETE" });
    await load();
  }

  return (
    <div className="mt-6 space-y-6">
      <div className="glass rounded-2xl p-6">
        <h3 className="font-display text-lg font-semibold text-soft">Create coupon</h3>
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <div>
            <label className="mb-1.5 block text-xs text-soft/60">Code</label>
            <input
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              placeholder="WELCOME15"
              className="h-11 w-full rounded-xl border border-white/15 bg-white/[0.05] px-4 text-sm text-soft outline-none focus:border-gold/50 focus:ring-2 focus:ring-gold/30"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs text-soft/60">Percent off</label>
            <input
              type="number"
              min="1"
              max="100"
              value={percent}
              onChange={(e) => setPercent(e.target.value)}
              className="h-11 w-full rounded-xl border border-white/15 bg-white/[0.05] px-4 text-sm text-soft outline-none focus:border-gold/50 focus:ring-2 focus:ring-gold/30"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs text-soft/60">Max uses (optional)</label>
            <input
              type="number"
              min="1"
              value={max}
              onChange={(e) => setMax(e.target.value)}
              placeholder="unlimited"
              className="h-11 w-full rounded-xl border border-white/15 bg-white/[0.05] px-4 text-sm text-soft outline-none focus:border-gold/50 focus:ring-2 focus:ring-gold/30"
            />
          </div>
        </div>
        <div className="mt-4 flex items-center gap-3">
          <Button onClick={create} variant="gold" size="sm" disabled={busy || !code}>
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Plus className="h-4 w-4" /> Create</>}
          </Button>
          {err && <span className="text-xs text-loss">{err}</span>}
        </div>
      </div>

      <div className="glass overflow-x-auto rounded-2xl">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-white/10 text-xs uppercase text-soft/45">
            <tr>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Off</th>
              <th className="px-4 py-3">Used</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-soft/40">Loading…</td></tr>
            ) : coupons.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-soft/40">No coupons yet.</td></tr>
            ) : (
              coupons.map((c) => (
                <tr key={c.code} className="border-b border-white/5">
                  <td className="px-4 py-3 font-mono text-gold-light">{c.code}</td>
                  <td className="px-4 py-3 text-soft">{c.percent_off}%</td>
                  <td className="px-4 py-3 text-soft/60">
                    {c.redeemed}{c.max_redemptions ? ` / ${c.max_redemptions}` : ""}
                  </td>
                  <td className="px-4 py-3">
                    <span className={c.active ? "text-emerald-light" : "text-soft/40"}>
                      {c.active ? "Active" : "Disabled"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => remove(c.code)} className="text-soft/40 hover:text-loss" aria-label={`Delete ${c.code}`}>
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
