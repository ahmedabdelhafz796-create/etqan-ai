import Script from "next/script";
import { analytics } from "@/config";

/**
 * Privacy-first analytics loader. Supports Google Analytics 4 and Plausible.
 * Renders nothing (loads no scripts, sets no cookies) unless the matching
 * environment variable is provided — so it's production-ready and inert
 * until you add an ID.
 *
 *   NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
 *   NEXT_PUBLIC_PLAUSIBLE_DOMAIN=your-domain.com
 */
export function Analytics() {
  const { gaId, plausibleDomain } = analytics;

  if (!gaId && !plausibleDomain) return null;

  return (
    <>
      {gaId && (
        <>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
            strategy="afterInteractive"
          />
          <Script id="ga-init" strategy="afterInteractive">
            {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${gaId}',{anonymize_ip:true});`}
          </Script>
        </>
      )}

      {plausibleDomain && (
        <Script
          defer
          data-domain={plausibleDomain}
          src="https://plausible.io/js/script.js"
          strategy="afterInteractive"
        />
      )}
    </>
  );
}
