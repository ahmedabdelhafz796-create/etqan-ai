import { links, siteConfig } from "@/config";

/**
 * Transactional email — the buyer's copy of their purchase.
 *
 * Provider-agnostic over plain HTTP (Resend by default: no SDK, no bundle
 * cost). Completely inert until `RESEND_API_KEY` and `EMAIL_FROM` are set, so
 * the store works exactly as before without it; once configured, every paid
 * order also lands in the buyer's inbox with a receipt link that stays valid
 * long after the instant download expires.
 *
 * Nothing here ever throws: a failed send must never fail a webhook, because
 * the payment has already happened.
 */

const API = "https://api.resend.com/emails";

export function isEmailConfigured(): boolean {
  return Boolean(process.env.RESEND_API_KEY && process.env.EMAIL_FROM);
}

export interface DeliveryEmail {
  to: string;
  productTitle: string;
  orderId: string;
  receiptUrl: string;
  amount?: number;
  currency?: string;
}

export type SendResult = { sent: boolean; reason?: string };

/** Send the "your download is ready" email. Safe to call unconditionally. */
export async function sendDeliveryEmail(msg: DeliveryEmail): Promise<SendResult> {
  if (!isEmailConfigured()) return { sent: false, reason: "unconfigured" };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(msg.to)) return { sent: false, reason: "bad_address" };

  const body = {
    from: process.env.EMAIL_FROM,
    to: [msg.to],
    ...(process.env.EMAIL_REPLY_TO ? { reply_to: process.env.EMAIL_REPLY_TO } : {}),
    subject: `${siteConfig.name} — your download is ready · تحميلك جاهز`,
    html: deliveryHtml(msg),
    text: deliveryText(msg),
  };

  try {
    const res = await fetch(API, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      // A slow ESP must not hold a payment webhook open.
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      return { sent: false, reason: `http_${res.status}${detail ? `: ${detail.slice(0, 180)}` : ""}` };
    }
    return { sent: true };
  } catch (err) {
    return { sent: false, reason: err instanceof Error ? err.message : "send_failed" };
  }
}

/* ── templates ──────────────────────────────────────────────────────── */

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function deliveryHtml(m: DeliveryEmail): string {
  const price =
    typeof m.amount === "number" && m.amount > 0
      ? `${m.amount.toFixed(2)} ${(m.currency || "USD").toUpperCase()}`
      : "";
  return `<!doctype html>
<html><body style="margin:0;padding:0;background:#07070a;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#07070a;padding:32px 12px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#0d0d12;border:1px solid #24242c;border-radius:16px;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;">
        <tr><td style="padding:28px 32px 8px;">
          <table role="presentation" cellpadding="0" cellspacing="0"><tr>
            <td style="width:38px;height:38px;background:linear-gradient(135deg,#F4D98B,#C9A227);border-radius:10px;color:#0b0906;font-size:20px;font-weight:800;text-align:center;line-height:38px;">E</td>
            <td style="padding-left:12px;color:#E6EAF2;font-size:17px;font-weight:700;">${esc(siteConfig.name)}</td>
          </tr></table>
        </td></tr>
        <tr><td style="padding:16px 32px 0;">
          <h1 style="margin:0;color:#E6EAF2;font-size:22px;line-height:1.3;">Your download is ready</h1>
          <p style="margin:10px 0 0;color:#98A2B3;font-size:15px;line-height:1.6;">
            Thank you for your purchase of <strong style="color:#E9C46A;">${esc(m.productTitle)}</strong>.
            Tap the button below to get your files.
          </p>
        </td></tr>
        <tr><td style="padding:24px 32px 0;">
          <a href="${esc(m.receiptUrl)}" style="display:inline-block;background:linear-gradient(135deg,#F4D98B,#C9A227);color:#120D04;text-decoration:none;font-weight:700;font-size:15px;padding:14px 26px;border-radius:10px;">Download now</a>
          <p style="margin:14px 0 0;color:#6D7585;font-size:13px;line-height:1.6;">
            This link stays valid for ${esc(String(process.env.RECEIPT_TTL_DAYS || 30))} days and can issue a
            fresh download whenever you open it — save the files to your device once you have them.
          </p>
        </td></tr>
        <tr><td style="padding:22px 32px 0;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #24242c;padding-top:16px;">
            <tr><td style="color:#6D7585;font-size:13px;padding-top:16px;">Order</td>
                <td align="right" style="color:#98A2B3;font-size:13px;padding-top:16px;font-family:monospace;">${esc(m.orderId)}</td></tr>
            ${price ? `<tr><td style="color:#6D7585;font-size:13px;padding-top:6px;">Total</td>
                <td align="right" style="color:#98A2B3;font-size:13px;padding-top:6px;">${esc(price)}</td></tr>` : ""}
          </table>
        </td></tr>
        <tr><td dir="rtl" style="padding:22px 32px 0;text-align:right;">
          <p style="margin:0;color:#98A2B3;font-size:14px;line-height:1.9;">
            شكرًا لشرائك <strong style="color:#E9C46A;">${esc(m.productTitle)}</strong>.
            اضغط على الزر بالأعلى لتحميل ملفاتك. الرابط صالح لمدة
            ${esc(String(process.env.RECEIPT_TTL_DAYS || 30))} يومًا ويمنحك رابط تحميل جديدًا في كل مرة تفتحه.
          </p>
        </td></tr>
        <tr><td style="padding:22px 32px 30px;">
          <p style="margin:0;color:#6D7585;font-size:13px;line-height:1.7;">
            Need help? Support · الدعم:
            <a href="${esc(links.telegramUrl)}" style="color:#E9C46A;text-decoration:none;">Telegram</a>
          </p>
        </td></tr>
      </table>
      <p style="max-width:560px;margin:16px auto 0;color:#4A5060;font-size:11px;text-align:center;font-family:Arial,sans-serif;">
        ${esc(siteConfig.name)} · ${esc(siteConfig.url)}
      </p>
    </td></tr>
  </table>
</body></html>`;
}

function deliveryText(m: DeliveryEmail): string {
  const days = process.env.RECEIPT_TTL_DAYS || 30;
  return [
    `${siteConfig.name} — your download is ready`,
    "",
    `Thank you for your purchase of ${m.productTitle}.`,
    `Download: ${m.receiptUrl}`,
    `This link stays valid for ${days} days and issues a fresh download each time you open it.`,
    "",
    `Order: ${m.orderId}`,
    `Support: ${links.telegramUrl}`,
    "",
    `شكرًا لشرائك ${m.productTitle} — رابط التحميل بالأعلى صالح لمدة ${days} يومًا.`,
  ].join("\n");
}
