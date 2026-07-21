import { isDbConfigured } from "@/lib/db";
import { listCustomers } from "@/lib/repositories";
import { DbNotice, fmtDate } from "@/components/admin/ui";

export const dynamic = "force-dynamic";

export default async function CustomersPage() {
  if (!isDbConfigured()) return <DbNotice />;
  const customers = await listCustomers(1000);

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-soft">Customers</h1>
      <p className="mt-1 text-sm text-soft/50">{customers.length} customer(s).</p>

      <div className="glass mt-6 overflow-x-auto rounded-2xl">
        <table className="w-full min-w-[480px] text-left text-sm">
          <thead className="border-b border-white/10 text-xs uppercase text-soft/45">
            <tr>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">First seen</th>
            </tr>
          </thead>
          <tbody>
            {customers.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-4 py-8 text-center text-soft/40">
                  No customers yet.
                </td>
              </tr>
            ) : (
              customers.map((c) => (
                <tr key={String(c.email)} className="border-b border-white/5">
                  <td className="px-4 py-3 text-soft/80">{String(c.email)}</td>
                  <td className="px-4 py-3 text-soft/60">
                    {c.name ? String(c.name) : "—"}
                  </td>
                  <td className="px-4 py-3 text-soft/50">
                    {fmtDate(Number(c.created_at))}
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
