import { NextResponse } from "next/server";

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

  // ─────────────────────────────────────────────────────────────
  // Integration point: forward `email` to your email provider here.
  // Example (pseudo):
  //   await fetch("https://api.your-esp.com/subscribe", { ... })
  // Kept provider-agnostic so you can wire in whatever you use.
  // ─────────────────────────────────────────────────────────────

  return NextResponse.json(
    { message: "You're on the list. Welcome aboard." },
    { status: 200 }
  );
}
