"use client";

/**
 * Global cinematic backdrop rendered once behind the whole site.
 *  - Deep vignette base
 *  - Three slow-drifting aurora orbs (gold / royal / emerald)
 *  - Faint perspective grid
 *  - Film grain
 * All decorative & GPU-friendly (transform/opacity only).
 */
export function AmbientBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      {/* base vignette */}
      <div className="absolute inset-0 bg-night-900" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_-10%,rgba(20,27,45,0.9),transparent_60%)]" />

      {/* aurora orbs */}
      <div className="absolute -left-[10%] top-[-8%] h-[52vmax] w-[52vmax] rounded-full bg-[radial-gradient(circle,rgba(233,196,106,0.16),transparent_62%)] blur-3xl animate-aurora" />
      <div
        className="absolute right-[-12%] top-[18%] h-[48vmax] w-[48vmax] rounded-full bg-[radial-gradient(circle,rgba(37,99,235,0.14),transparent_60%)] blur-3xl animate-aurora"
        style={{ animationDelay: "-7s", animationDuration: "26s" }}
      />
      <div
        className="absolute bottom-[-18%] left-[30%] h-[46vmax] w-[46vmax] rounded-full bg-[radial-gradient(circle,rgba(18,185,129,0.12),transparent_60%)] blur-3xl animate-aurora"
        style={{ animationDelay: "-14s", animationDuration: "30s" }}
      />

      {/* perspective grid */}
      <div className="absolute inset-x-0 bottom-0 h-[60vh] grid-bg opacity-30" />

      {/* film grain */}
      <div className="absolute inset-0 grain opacity-[0.05] mix-blend-overlay" />
    </div>
  );
}
