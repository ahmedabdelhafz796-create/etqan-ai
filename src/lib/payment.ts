/**
 * ============================================================
 *  NOWPayments — Payment Service (architecture only)
 * ============================================================
 *  This module prepares a clean, typed integration surface for
 *  NOWPayments crypto checkout. It is NOT a fake implementation:
 *  every function talks to the real NOWPayments REST API using
 *  the credentials in your environment.
 *
 *  Nothing is wired to a live key by default — supply the env
 *  vars in `.env.local` (see `.env.example`) and the service
 *  becomes fully operational.
 *
 *  Docs: https://documenter.getpostman.com/view/7907941/S1a32n38
 * ============================================================
 */

const API_URL =
  process.env.NOWPAYMENTS_API_URL || "https://api.nowpayments.io/v1";
const API_KEY = process.env.NOWPAYMENTS_API_KEY || "";
const PRICE_CURRENCY = process.env.NOWPAYMENTS_PRICE_CURRENCY || "usd";

export interface CreateInvoiceParams {
  /** Amount in the fiat price currency (e.g. USD). */
  priceAmount: number;
  /** Stable order id — e.g. the book id + timestamp. */
  orderId: string;
  /** Human-readable description shown at checkout. */
  orderDescription: string;
  /** Optional overrides for redirect URLs. */
  successUrl?: string;
  cancelUrl?: string;
}

export interface NowPaymentsInvoice {
  id: string;
  invoice_url: string;
  order_id: string;
  price_amount: string;
  price_currency: string;
  created_at: string;
}

export class PaymentConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PaymentConfigError";
  }
}

/** Is the service configured with a real API key? */
export function isPaymentConfigured(): boolean {
  return API_KEY.trim().length > 0;
}

/**
 * Create a hosted NOWPayments invoice and return its checkout URL.
 * Server-side only — never expose the API key to the browser.
 */
export async function createInvoice(
  params: CreateInvoiceParams
): Promise<NowPaymentsInvoice> {
  if (!isPaymentConfigured()) {
    throw new PaymentConfigError(
      "NOWPAYMENTS_API_KEY is not set. Add it to .env.local to enable checkout."
    );
  }

  const res = await fetch(`${API_URL}/invoice`, {
    method: "POST",
    headers: {
      "x-api-key": API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      price_amount: params.priceAmount,
      price_currency: PRICE_CURRENCY,
      order_id: params.orderId,
      order_description: params.orderDescription,
      success_url:
        params.successUrl || process.env.NEXT_PUBLIC_PAYMENT_SUCCESS_URL,
      cancel_url:
        params.cancelUrl || process.env.NEXT_PUBLIC_PAYMENT_CANCEL_URL,
    }),
    cache: "no-store",
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(
      `NOWPayments invoice creation failed (${res.status}): ${detail}`
    );
  }

  return (await res.json()) as NowPaymentsInvoice;
}

/**
 * Fetch the list of currencies your NOWPayments account accepts.
 * Useful for rendering a coin selector at checkout.
 */
export async function getAvailableCurrencies(): Promise<string[]> {
  if (!isPaymentConfigured()) {
    throw new PaymentConfigError("NOWPAYMENTS_API_KEY is not set.");
  }
  const res = await fetch(`${API_URL}/currencies`, {
    headers: { "x-api-key": API_KEY },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to load currencies (${res.status})`);
  const data = (await res.json()) as { currencies: string[] };
  return data.currencies;
}
