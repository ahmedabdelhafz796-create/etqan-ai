import { DollarSign, ShoppingBag, TrendingUp, Users } from "lucide-react";
import { isDbConfigured } from "@/lib/db";
import { orderStats, listOrders, listCustomers } from "@/lib/repositories";
import { DbNotice, StatusPill, fmtDate, fmtMoney } from "@/components/admin/ui";

export const dynamic = "force-dynamic";

export default async function AdminDashboard() {
  if (!isDbConfigured()) return <DbNotice />;

  const [stats, orders, customers] = await Promise.all([
    orderStats(),
    listOrders(6),
    listCustomers(1000),
  ]);

  const cards = [
    { label: "Total Orders", value: String(stats.total), icon: ShoppingBag },
    { label: "Paid Orders", value: String(stats.paid), icon: TrendingUp },
    { label: "Revenue", value: fmtMoney(stats.revenue), icon: DollarSign },
    { label: "Customers", value: String(customers.length), icon: Users },
  ];

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-soft">Dashboard</h1>
      <p className="mt-1 text-sm text-soft/50">Overview of your store.</p>

      <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {cards.map((c) => (
          <div key={c.label} className="glass rounded-2xl p-5">
            <c.icon className="h-5 w-5 text-gold-light" />
            <div className="mt-3 font-display text-2xl font-semibold text-soft">
              {c.value}
            </div>
            <div className="text-xs text-soft/50">{c.label}</div>
          </div>
        ))}
      </div>

      <h2 className="mt-10 mb-3 text-sm font-semibold uppercase tracking-wide text-soft/60">
        Recent orders
      </h2>
      <div className="glass overflow-hidden rounded-2xl">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-white/10 text-xs uppercase text-soft/45">
            <tr>
              <th className="px-4 py-3">Order</th>
              <th className="px-4 py-3">Book</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Date</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-soft/40">
                  No orders yet.
                </td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr key={String(o.id)} className="border-b border-white/5">
                  <td className="px-4 py-3 font-mono text-xs text-soft/70">
                    {String(o.id)}
                  </td>
                  <td className="px-4 py-3">{String(o.book_id)}</td>
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
