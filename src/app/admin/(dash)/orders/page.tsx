import { isDbConfigured } from "@/lib/db";
import { listOrders } from "@/lib/repositories";
import { DbNotice, StatusPill, fmtDate, fmtMoney } from "@/components/admin/ui";

export const dynamic = "force-dynamic";

export default async function OrdersPage() {
  if (!isDbConfigured()) return <DbNotice />;
  const orders = await listOrders(500);

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-soft">Orders</h1>
      <p className="mt-1 text-sm text-soft/50">{orders.length} order(s).</p>

      <div className="glass mt-6 overflow-x-auto rounded-2xl">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-white/10 text-xs uppercase text-soft/45">
            <tr>
              <th className="px-4 py-3">Order ID</th>
              <th className="px-4 py-3">Payment ID</th>
              <th className="px-4 py-3">Book</th>
              <th className="px-4 py-3">Customer</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Date</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-soft/40">
                  No orders yet.
                </td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr key={String(o.id)} className="border-b border-white/5">
                  <td className="px-4 py-3 font-mono text-xs text-soft/70">
                    {String(o.id)}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-soft/50">
                    {o.payment_id ? String(o.payment_id) : "—"}
                  </td>
                  <td className="px-4 py-3">{String(o.book_id)}</td>
                  <td className="px-4 py-3 text-soft/70">
                    {o.customer_email ? String(o.customer_email) : "—"}
                  </td>
                  <td className="px-4 py-3">{fmtMoney(Number(o.amount))}</td>
                  <td className="px-4 py-3">
                    <StatusPill status={String(o.status)} />
                  </td>
                  <td className="px-4 py-3 text-soft/50">
                    {fmtDate(Number(o.created_at))}
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
