import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/admin-auth";
import { isDbConfigured } from "@/lib/db";
import { listCoupons, upsertCoupon, deleteCoupon, log } from "@/lib/repositories";

export const runtime = "nodejs";

function guard() {
  return isDbConfigured();
}

export async function GET() {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  if (!guard()) {
    return NextResponse.json({ error: "db_unconfigured", message: "Database not configured." }, { status: 503 });
  }
  return NextResponse.json({ coupons: await listCoupons() });
}

export async function POST(request: Request) {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  if (!guard()) {
    return NextResponse.json({ error: "db_unconfigured", message: "Database not configured." }, { status: 503 });
  }
  let body: { code?: string; percentOff?: number; active?: boolean; maxRedemptions?: number | null; expiresAt?: number | null };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "bad_request" }, { status: 400 });
  }
  const code = (body.code || "").trim();
  const percentOff = Number(body.percentOff);
  if (!code || !/^[A-Za-z0-9_-]{2,40}$/.test(code)) {
    return NextResponse.json({ error: "invalid_code", message: "Code must be 2–40 letters/numbers." }, { status: 422 });
  }
  if (!Number.isFinite(percentOff) || percentOff < 1 || percentOff > 100) {
    return NextResponse.json({ error: "invalid_percent", message: "Percent off must be 1–100." }, { status: 422 });
  }
  await upsertCoupon({
    code,
    percentOff,
    active: body.active !== false,
    maxRedemptions: body.maxRedemptions ?? null,
    expiresAt: body.expiresAt ?? null,
  });
  await log("info", "coupon_upserted", { code: code.toUpperCase(), percentOff });
  return NextResponse.json({ ok: true });
}

export async function DELETE(request: Request) {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  if (!guard()) {
    return NextResponse.json({ error: "db_unconfigured", message: "Database not configured." }, { status: 503 });
  }
  const code = new URL(request.url).searchParams.get("code") || "";
  if (!code) return NextResponse.json({ error: "bad_request" }, { status: 400 });
  await deleteCoupon(code);
  await log("info", "coupon_deleted", { code: code.toUpperCase() });
  return NextResponse.json({ ok: true });
}
