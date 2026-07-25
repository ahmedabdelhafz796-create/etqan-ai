import { ImageResponse } from "next/og";
import { siteConfig } from "@/config";

export const alt = `${siteConfig.name} — Premium Digital Library`;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/** Branded social share card (Open Graph + Twitter). */
export default function OgImage() {
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
            "radial-gradient(1000px 500px at 50% -10%, #141b2d 0%, #05070c 60%)",
          color: "#E6EAF2",
          fontFamily: "sans-serif",
        }}
      >
        {/* top row: brand + monogram */}
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: 46,
              height: 46,
              borderRadius: 12,
              fontSize: 26,
              fontWeight: 800,
              color: "#05070c",
              background: "linear-gradient(135deg,#F4D98B,#C9A227)",
            }}
          >
            E
          </div>
          <div style={{ fontSize: 30, fontWeight: 700, letterSpacing: -1 }}>
            {siteConfig.name}
          </div>
          <div
            style={{
              marginLeft: 12,
              fontSize: 18,
              color: "#E9C46A",
              border: "1px solid rgba(233,196,106,0.4)",
              borderRadius: 999,
              padding: "6px 16px",
            }}
          >
            Premium Digital Library
          </div>
        </div>

        {/* headline */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 78, fontWeight: 800, lineHeight: 1.05, letterSpacing: -2 }}>
            Learn the skills
          </div>
          <div
            style={{
              fontSize: 78,
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: -2,
              color: "#E9C46A",
            }}
          >
            that actually pay.
          </div>
          <div style={{ marginTop: 26, fontSize: 26, color: "#98A2B3", maxWidth: 940 }}>
            Programming · AI · Web · Design · Productivity · Trading — premium,
            trilingual courses (EN · AR · TR), delivered instantly.
          </div>
        </div>

        {/* bottom row */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 24, color: "#98A2B3" }}>14 courses & bundles · Lifetime access</div>
          <div
            style={{
              fontSize: 26,
              fontWeight: 700,
              color: "#05070c",
              background: "linear-gradient(90deg,#F4D98B,#C9A227)",
              borderRadius: 999,
              padding: "14px 30px",
            }}
          >
            From $4
          </div>
        </div>
      </div>
    ),
    size
  );
}
