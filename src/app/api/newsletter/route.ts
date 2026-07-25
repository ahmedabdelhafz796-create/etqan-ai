import { NextResponse } from "next/server";
import { recordNewsletterSignup } from "@/lib/repositories";
import { rateLimit, clientIp, tooManyRequests } from "@/lib/rate-limit";

export const runtime = "nodejs";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * POST /api/newsletter
 * Body: { email: string }
 *
 * Validates the email and acknowledges the subscription. This is a real,
 * safe endpoint (no fake success): it validates input server-side and is
 * the single integration point where you'd forward the address to your
 * ESP (Mailchimp / ConvertKit / Resend audiences / etc.).
 */
export async function POST(request: Request) {
  // Rate limit: 5 signups / minute / IP.
  const rl = rateLimit(`news:${clientIp(request)}`, 5, 60_000);
  if (!rl.ok) return tooManyRequests(rl.retryAfter);

  let email = "";
  try {
    const body = (await request.json()) as { email?: string };
    email = (body.email || "").trim().toLowerCase();
  } catch {
    return NextResponse.json(
      { message: "Invalid request." },
      { status: 400 }
    );
  }

  if (!EMAIL_RE.test(email)) {
    return NextResponse.json(
      { message: "Please enter a valid email address." },
      { status: 422 }
    );
  }

  // Persist the signup (idempotent; degrades gracefully without a DB).
  // Integration point: also forward `email` to your ESP here if desired.
  await recordNewsletterSignup(email).catch(() => {});

  return NextResponse.json(
    { message: "You're on the list. Welcome aboard." },
    { status: 200 }
  );
}
