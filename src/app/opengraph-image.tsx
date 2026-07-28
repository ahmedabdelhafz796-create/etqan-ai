import { ImageResponse } from "next/og";
import { siteConfig, automationProof } from "@/config";

export const alt = `${siteConfig.name} — AI automation systems, tools and templates`;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/**
 * Social share card.
 *
 * This is the first thing anyone sees when a link to the site is posted,
 * so it has to say what the homepage says. The previous card showed
 * three candlesticks and "Trade the way institutions actually do" — it
 * was advertising a different product.
 *
 * The mark is drawn with positioned divs rather than an asset so the
 * card stays self-contained and needs no image fetch at render time.
 */
export default function OgImage() {
  const node = (left: number, top: number, dia: number, color: string) => (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width: dia,
        height: dia,
        borderRadius: 999,
        border: `3px solid ${color}`,
        background: "#05070c",
      }}
    />
  );

  const proofLine =
    `${automationProof.workflows} workflows · ` +
    `${automationProof.nodes} nodes · ` +
    `${automationProof.behaviouralTests} behavioural tests passing`;

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: 72,
          background:
            "radial-gradient(1000px 520px at 50% -12%, #1a1b3d 0%, #05070c 62%)",
          color: "#E6EAF2",
          fontFamily: "sans-serif",
        }}
      >
        {/* brand row */}
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div
            style={{
              position: "relative",
              display: "flex",
              width: 54,
              height: 44,
            }}
          >
            {node(0, 14, 16, "#22D3EE")}
            {node(20, 0, 14, "#A5B4FC")}
            {node(20, 28, 14, "#A5B4FC")}
            {node(38, 14, 16, "#818CF8")}
          </div>
          <div style={{ fontSize: 30, fontWeight: 700, letterSpacing: -1 }}>
            {siteConfig.name}
          </div>
          <div
            style={{
              marginLeft: 12,
              fontSize: 18,
              color: "#A5B4FC",
              border: "1px solid rgba(129,140,248,0.45)",
              borderRadius: 999,
              padding: "6px 16px",
            }}
          >
            AI Automation Marketplace
          </div>
        </div>

        {/* headline */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              fontSize: 70,
              fontWeight: 800,
              lineHeight: 1.06,
              letterSpacing: -2,
            }}
          >
            Automation that survives
          </div>
          <div
            style={{
              fontSize: 70,
              fontWeight: 800,
              lineHeight: 1.06,
              letterSpacing: -2,
              color: "#A5B4FC",
            }}
          >
            real traffic — not just the demo.
          </div>
          <div
            style={{
              marginTop: 26,
              fontSize: 25,
              color: "#98A2B3",
              maxWidth: 940,
            }}
          >
            n8n systems · AI agents · workflow templates · secure delivery ·
            fraud scoring · revenue recovery
          </div>
        </div>

        {/* proof row */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          {/* One interpolation, not several: Satori treats each expression
              as a separate child and rejects a plain div with more than
              one unless it declares display explicitly. */}
          <div style={{ fontSize: 24, color: "#98A2B3" }}>{proofLine}</div>
          <div
            style={{
              fontSize: 26,
              fontWeight: 700,
              color: "#ffffff",
              background: "linear-gradient(90deg,#818CF8,#4338CA)",
              borderRadius: 999,
              padding: "14px 30px",
            }}
          >
            Start free
          </div>
        </div>
      </div>
    ),
    size
  );
}
