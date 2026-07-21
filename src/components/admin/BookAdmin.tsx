"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Check, Loader2, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  bookId: string;
  title: string;
  originalPrice: number;
  offerPrice: number;
  active: boolean;
}

export function BookAdmin({ bookId, title, originalPrice, offerPrice, active }: Props) {
  const router = useRouter();
  const [orig, setOrig] = React.useState(String(originalPrice));
  const [offer, setOffer] = React.useState(String(offerPrice));
  const [isActive, setIsActive] = React.useState(active);
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);
  const [uploadMsg, setUploadMsg] = React.useState("");
  const fileRef = React.useRef<HTMLInputElement>(null);

  async function savePricing() {
    setSaving(true);
    setSaved(false);
    try {
      const res = await fetch("/api/admin/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          [`book_${bookId}_original`]: orig,
          [`book_${bookId}_offer`]: offer,
          [`book_${bookId}_active`]: isActive ? "1" : "0",
        }),
      });
      if (res.ok) {
        setSaved(true);
        router.refresh();
      }
    } finally {
      setSaving(false);
    }
  }

  async function upload() {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setUploadMsg("Uploading…");
    const form = new FormData();
    form.append("bookId", bookId);
    form.append("file", file);
    const res = await fetch("/api/admin/upload", { method: "POST", body: form });
    if (res.ok) {
      const d = (await res.json()) as { size: number };
      setUploadMsg(`Uploaded (${(d.size / 1024 / 1024).toFixed(1)} MB) ✓`);
    } else {
      const d = (await res.json().catch(() => ({}))) as { message?: string };
      setUploadMsg(d.message || "Upload failed.");
    }
  }

  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg font-semibold text-soft">{title}</h3>
        <label className="flex items-center gap-2 text-xs text-soft/60">
          <input
            type="checkbox"
            checked={isActive}
            onChange={(e) => setIsActive(e.target.checked)}
            className="h-4 w-4 accent-gold"
          />
          Active
        </label>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-xs text-soft/60">Original price ($)</label>
          <input
            type="number"
            min="0"
            step="1"
            value={orig}
            onChange={(e) => setOrig(e.target.value)}
            className="h-11 w-full rounded-xl border border-white/15 bg-white/[0.05] px-4 text-sm text-soft outline-none focus:border-gold/50 focus:ring-2 focus:ring-gold/30"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-xs text-soft/60">Offer price ($)</label>
          <input
            type="number"
            min="0"
            step="1"
            value={offer}
            onChange={(e) => setOffer(e.target.value)}
            className="h-11 w-full rounded-xl border border-white/15 bg-white/[0.05] px-4 text-sm text-soft outline-none focus:border-gold/50 focus:ring-2 focus:ring-gold/30"
          />
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <Button onClick={savePricing} variant="gold" size="sm" disabled={saving}>
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save pricing"}
        </Button>
        {saved && (
          <span className="flex items-center gap-1 text-xs text-emerald-light">
            <Check className="h-4 w-4" /> Saved
          </span>
        )}
      </div>

      <div className="mt-5 border-t border-white/10 pt-4">
        <label className="mb-2 block text-xs text-soft/60">Product PDF</label>
        <div className="flex flex-wrap items-center gap-3">
          <input
            ref={fileRef}
            type="file"
            accept="application/pdf"
            className="text-xs text-soft/60 file:mr-3 file:rounded-lg file:border-0 file:bg-white/10 file:px-3 file:py-2 file:text-soft"
          />
          <Button onClick={upload} variant="outline" size="sm">
            <Upload className="h-4 w-4" /> Upload
          </Button>
          {uploadMsg && <span className="text-xs text-soft/60">{uploadMsg}</span>}
        </div>
      </div>
    </div>
  );
}
