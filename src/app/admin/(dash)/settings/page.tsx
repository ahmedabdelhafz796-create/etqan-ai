import { isDbConfigured } from "@/lib/db";
import { getEffectiveConfig } from "@/lib/site-settings";
import { DbNotice } from "@/components/admin/ui";
import { SettingsForm } from "@/components/admin/SettingsForm";

export const dynamic = "force-dynamic";

export default async function SettingsPage() {
  if (!isDbConfigured()) return <DbNotice />;
  const cfg = await getEffectiveConfig();

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-soft">Settings</h1>
      <p className="mt-1 text-sm text-soft/50">
        Offer, links and SEO. Changes apply to the live storefront.
      </p>
      <div className="mt-6">
        <SettingsForm
          initial={{
            offer_ends_at: cfg.offerEndsAt,
            telegram_url: cfg.telegramUrl,
            payment_url: cfg.paymentUrl,
            seo_title: cfg.seoTitle,
            seo_description: cfg.seoDescription,
          }}
        />
      </div>
    </div>
  );
}
