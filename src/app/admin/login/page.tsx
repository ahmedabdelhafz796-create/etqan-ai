import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { isAuthenticated, isAdminConfigured } from "@/lib/admin-auth";
import { LoginForm } from "@/components/admin/LoginForm";

export const metadata: Metadata = {
  title: "Admin Login",
  robots: { index: false, follow: false },
};

export default async function AdminLoginPage() {
  if (await isAuthenticated()) redirect("/admin");
  const configured = isAdminConfigured();

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-24">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="font-display text-2xl font-semibold text-soft">
            Etqan · Admin
          </h1>
          <p className="mt-2 text-sm text-soft/50">
            Sign in to manage the store.
          </p>
        </div>

        {configured ? (
          <LoginForm />
        ) : (
          <div className="rounded-2xl border border-loss/30 bg-loss/10 p-5 text-sm text-soft/80">
            Admin is not configured yet. Set{" "}
            <code className="text-gold-light">ADMIN_PASSWORD</code> and{" "}
            <code className="text-gold-light">ADMIN_SESSION_SECRET</code> in your
            environment, then reload.
          </div>
        )}
      </div>
    </main>
  );
}
