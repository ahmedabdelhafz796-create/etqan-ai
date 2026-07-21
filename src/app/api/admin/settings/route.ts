import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/admin-auth";
import { getAllSettings, setSetting, log } from "@/lib/repositories";
import { isDbConfigured } from "@/lib/db";
import { ALLOWED_SETTING_KEYS } from "@/lib/site-settings";

export const runtime = "nodejs";

export async function GET() {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  if (!isDbConfigured()) {
    return NextResponse.json(
      { error: "db_unconfigured", message: "Database not configured." },
      { status: 503 }
    );
  }
  return NextResponse.json({ settings: await getAllSettings() });
}

export async function POST(request: Request) {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  if (!isDbConfigured()) {
    return NextResponse.json(
      { error: "db_unconfigured", message: "Database not configured." },
      { status: 503 }
    );
  }

  let body: Record<string, unknown>;
  try {
    body = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "bad_request" }, { status: 400 });
  }

  const updated: string[] = [];
  for (const [key, value] of Object.entries(body)) {
    if (!ALLOWED_SETTING_KEYS.includes(key)) continue;
    await setSetting(key, String(value ?? ""));
    updated.push(key);
  }
  await log("info", "settings_updated", { keys: updated });
  return NextResponse.json({ ok: true, updated });
}
