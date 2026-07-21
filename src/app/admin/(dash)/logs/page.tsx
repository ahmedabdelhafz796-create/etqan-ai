import { isDbConfigured } from "@/lib/db";
import { listLogs } from "@/lib/repositories";
import { DbNotice, fmtDate } from "@/components/admin/ui";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

const LEVEL_COLOR: Record<string, string> = {
  info: "text-soft/70",
  warn: "text-gold-light",
  error: "text-loss",
};

export default async function LogsPage() {
  if (!isDbConfigured()) return <DbNotice />;
  const logs = await listLogs(200);

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-soft">Logs</h1>
      <p className="mt-1 text-sm text-soft/50">Most recent {logs.length} events.</p>

      <div className="glass mt-6 overflow-x-auto rounded-2xl">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-white/10 text-xs uppercase text-soft/45">
            <tr>
              <th className="px-4 py-3">Time</th>
              <th className="px-4 py-3">Level</th>
              <th className="px-4 py-3">Event</th>
              <th className="px-4 py-3">Detail</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-soft/40">
                  No logs yet.
                </td>
              </tr>
            ) : (
              logs.map((l, i) => (
                <tr key={i} className="border-b border-white/5 align-top">
                  <td className="px-4 py-3 whitespace-nowrap text-soft/50">
                    {fmtDate(Number(l.created_at))}
                  </td>
                  <td className={cn("px-4 py-3 font-medium", LEVEL_COLOR[String(l.level)] || "text-soft/60")}>
                    {String(l.level)}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-soft/80">
                    {String(l.event)}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-soft/45">
                    {l.detail ? String(l.detail) : "—"}
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
