import { isDbConfigured } from "@/lib/db";
import { DbNotice } from "@/components/admin/ui";
import { CouponAdmin } from "@/components/admin/CouponAdmin";

export const dynamic = "force-dynamic";

export default function CouponsPage() {
  if (!isDbConfigured()) return <DbNotice />;
  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-soft">Coupons</h1>
      <p className="mt-1 text-sm text-soft/50">
        Percentage discount codes. Applied server-side at checkout — the amount a buyer
        pays is always recomputed on the server, never trusted from the browser.
      </p>
      <CouponAdmin />
    </div>
  );
}
