import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import {
  ADMIN_COOKIE,
  ADMIN_SESSION_TTL_MS,
  checkPassword,
  createSessionValue,
  isAdminConfigured,
} from "@/lib/admin-auth";
import { log } from "@/lib/repositories";

export const runtime = "nodejs";

export async function POST(request: Request) {
  if (!isAdminConfigured()) {
    return NextResponse.json(
      {
        error: "admin_unconfigured",
        message:
          "Admin is not configured. Set ADMIN_PASSWORD and ADMIN_SESSION_SECRET.",
      },
      { status: 503 }
    );
  }

  let password = "";
  try {
    const body = (await request.json()) as { password?: string };
    password = body.password || "";
  } catch {
    return NextResponse.json({ error: "bad_request" }, { status: 400 });
  }

  if (!checkPassword(password)) {
    await log("warn", "admin_login_failed");
    return NextResponse.json(
      { error: "invalid_credentials", message: "Incorrect password." },
      { status: 401 }
    );
  }

  const store = await cookies();
  store.set(ADMIN_COOKIE, createSessionValue(), {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: Math.floor(ADMIN_SESSION_TTL_MS / 1000),
  });
  await log("info", "admin_login_success");
  return NextResponse.json({ ok: true });
}
