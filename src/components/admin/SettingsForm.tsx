"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Loader2, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

type Fields = {
  offer_ends_at: string;
  telegram_url: string;
  payment_url: string;
  seo_title: string;
  seo_description: string;
};

const LABELS: Record<keyof Fields, { label: string; hint?: string; type?: string }> = {
  offer_ends_at: {
    label: "Offer ends at (ISO)",
    hint: "e.g. 2026-07-30T23:59:00 — when the countdown expires, discounts hide automatically.",
  },
  telegram_url: { label: "Telegram URL" },
  payment_url: { label: "Payment URL (direct checkout fallback)" },
  seo_title: { label: "SEO title" },
  seo_description: { label: "SEO description" },
};

export function SettingsForm({ initial }: { initial: Fields }) {
  const router = useRouter();
  const [values, setValues] = React.useState<Fields>(initial);
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);
  const [error, setError] = React.useState("");

  function update<K extends keyof Fields>(key: K, value: string) {
    setValues((v) => ({ ...v, [key]: value }));
    setSaved(false);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const res = await fetch("/api/admin/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (res.ok) {
        setSaved(true);
        router.refresh();
      } else {
        const d = (await res.json()) as { message?: string };
        setError(d.message || "Save failed.");
      }
    } catch {
      setError("Network error.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="glass max-w-2xl space-y-5 rounded-2xl p-6">
      {(Object.keys(LABELS) as (keyof Fields)[]).map((key) => (
        <div key={key}>
          <label htmlFor={key} className="mb-1.5 block text-xs text-soft/60">
            {LABELS[key].label}
          </label>
          {key === "seo_description" ? (
            <textarea
              id={key}
              rows={3}
              value={values[key]}
              onChange={(e) => update(key, e.target.value)}
              className="w-full rounded-xl border border-white/15 bg-white/[0.05] px-4 py-2.5 text-sm text-soft outline-none focus:border-gold/50 focus:ring-2 focus:ring-gold/30"
            />
          ) : (
            <input
              id={key}
              type="text"
              value={values[key]}
              onChange={(e) => update(key, e.target.value)}
              className="h-11 w-full rounded-xl border border-white/15 bg-white/[0.05] px-4 text-sm text-soft outline-none focus:border-gold/50 focus:ring-2 focus:ring-gold/30"
            />
          )}
          {LABELS[key].hint && (
            <p className="mt-1 text-xs text-soft/40">{LABELS[key].hint}</p>
          )}
        </div>
      ))}

      {error && <p className="text-xs text-loss">{error}</p>}

      <div className="flex items-center gap-3">
        <Button type="submit" variant="gold" size="md" disabled={saving}>
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save settings"}
        </Button>
        {saved && (
          <span className="flex items-center gap-1 text-xs text-emerald-light">
            <Check className="h-4 w-4" /> Saved
          </span>
        )}
      </div>
    </form>
  );
}
