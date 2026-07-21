"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Loader2, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/ui/reveal";
import { useT } from "@/components/providers/I18nProvider";

type Status = "idle" | "loading" | "success" | "error";

export function Newsletter() {
  const t = useT();
  const [email, setEmail] = React.useState("");
  const [status, setStatus] = React.useState<Status>("idle");
  const [message, setMessage] = React.useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (status === "loading") return;
    setStatus("loading");
    try {
      const res = await fetch("/api/newsletter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = (await res.json()) as { message?: string };
      if (res.ok) {
        setStatus("success");
        setMessage(data.message || t.newsletter.success);
        setEmail("");
      } else {
        setStatus("error");
        setMessage(data.message || "Something went wrong. Please try again.");
      }
    } catch {
      setStatus("error");
      setMessage("Network error. Please try again.");
    }
  }

  return (
    <section className="py-16 sm:py-20">
      <div className="container-tight">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl border border-gold/20 bg-gradient-to-br from-night-700/70 to-night-900/80 p-8 backdrop-blur-xl sm:p-12">
            <div className="absolute -right-16 -top-16 h-52 w-52 rounded-full bg-gold/15 blur-3xl" />

            <div className="relative grid items-center gap-8 lg:grid-cols-2">
              <div>
                <span className="flex h-11 w-11 items-center justify-center rounded-xl border border-gold/25 bg-gold/10 text-gold-light">
                  <Mail className="h-5 w-5" />
                </span>
                <h2 className="mt-5 font-display text-2xl font-semibold text-soft sm:text-3xl">
                  {t.newsletter.title}
                </h2>
                <p className="mt-3 max-w-md text-sm leading-relaxed text-soft/60">
                  {t.newsletter.description}
                </p>
              </div>

              <div>
                {status === "success" ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.96 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center gap-3 rounded-2xl border border-emerald/30 bg-emerald/10 p-5 text-emerald-light"
                  >
                    <CheckCircle2 className="h-6 w-6 shrink-0" />
                    <p className="text-sm">{message}</p>
                  </motion.div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-3">
                    <div className="flex flex-col gap-3 sm:flex-row">
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder={t.newsletter.placeholder}
                        className="h-12 w-full flex-1 rounded-full border border-white/15 bg-white/[0.05] px-5 text-sm text-soft placeholder:text-soft/40 outline-none transition-colors focus:border-gold/50 focus:bg-white/[0.08] focus:ring-2 focus:ring-gold/30"
                        aria-label={t.newsletter.emailLabel}
                      />
                      <Button
                        type="submit"
                        variant="gold"
                        size="lg"
                        disabled={status === "loading"}
                        className="shrink-0"
                      >
                        {status === "loading" ? (
                          <>
                            <Loader2 className="h-4 w-4 animate-spin" />
                            {t.newsletter.joining}
                          </>
                        ) : (
                          t.newsletter.subscribe
                        )}
                      </Button>
                    </div>
                    {status === "error" && (
                      <p className="px-2 text-xs text-loss">{message}</p>
                    )}
                    <p className="px-2 text-xs text-soft/40">
                      {t.newsletter.agree}
                    </p>
                  </form>
                )}
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
