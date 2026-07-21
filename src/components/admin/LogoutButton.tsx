"use client";

import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";

export function LogoutButton() {
  const router = useRouter();
  async function logout() {
    await fetch("/api/admin/logout", { method: "POST" });
    router.replace("/admin/login");
    router.refresh();
  }
  return (
    <button
      onClick={logout}
      className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-soft/60 transition-colors hover:bg-white/5 hover:text-loss"
    >
      <LogOut className="h-4 w-4" />
      Sign out
    </button>
  );
}
