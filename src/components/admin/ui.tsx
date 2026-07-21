import { cn } from "@/lib/utils";

export function fmtMoney(n: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(n || 0);
}

export function fmtDate(ms: number): string {
  if (!ms) return "—";
  return new Date(ms).toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

const STATUS_STYLES: Record<string, string> = {
  finished: "border-emerald/30 bg-emerald/10 text-emerald-light",
  confirmed: "border-emerald/30 bg-emerald/10 text-emerald-light",
  waiting: "border-gold/30 bg-gold/10 text-gold-light",
  confirming: "border-gold/30 bg-gold/10 text-gold-light",
  partially_paid: "border-gold/30 bg-gold/10 text-gold-light",
  failed: "border-loss/30 bg-loss/10 text-loss",
  expired: "border-loss/30 bg-loss/10 text-loss",
  refunded: "border-white/15 bg-white/5 text-soft/60",
};

export function StatusPill({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-block rounded-full border px-2.5 py-0.5 text-xs",
        STATUS_STYLES[status] || "border-white/15 bg-white/5 text-soft/60"
      )}
    >
      {status}
    </span>
  );
}

export function DbNotice() {
  return (
    <div className="mx-auto max-w-lg rounded-2xl border border-gold/25 bg-gold/[0.06] p-6 text-center">
      <h2 className="font-display text-lg font-semibold text-soft">
        Database not configured
      </h2>
      <p className="mt-2 text-sm text-soft/60">
        Set <code className="text-gold-light">TURSO_DATABASE_URL</code> and{" "}
        <code className="text-gold-light">TURSO_AUTH_TOKEN</code> (or{" "}
        <code className="text-gold-light">DATABASE_URL</code>) to enable orders,
        customers, settings and logs. The storefront and payments work without
        it.
      </p>
    </div>
  );
}
