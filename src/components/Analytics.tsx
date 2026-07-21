import Script from "next/script";
import { analytics } from "@/config";

/**
 * Privacy-first analytics loader. Supports Google Analytics 4, Google Tag
 * Manager, Meta (Facebook) Pixel and Plausible.
 *
 * Renders nothing (loads no scripts, sets no cookies) unless the matching
 * environment variable is provided — so it is production-ready and fully
 * inert until you add an ID:
 *
 *   NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
 *   NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
 *   NEXT_PUBLIC_META_PIXEL_ID=1234567890
 *   NEXT_PUBLIC_PLAUSIBLE_DOMAIN=your-domain.com
 */
export function Analytics() {
  const { gaId, gtmId, metaPixelId, plausibleDomain } = analytics;

  if (!gaId && !gtmId && !metaPixelId && !plausibleDomain) return null;

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

      {gtmId && (
        <Script id="gtm-init" strategy="afterInteractive">
          {`(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','${gtmId}');`}
        </Script>
      )}

      {metaPixelId && (
        <Script id="meta-pixel" strategy="afterInteractive">
          {`!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','${metaPixelId}');fbq('track','PageView');`}
        </Script>
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

/**
 * GTM / Meta Pixel <noscript> fallbacks. Rendered at the top of <body>.
 * Inert unless the corresponding ID is set.
 */
export function AnalyticsNoscript() {
  const { gtmId, metaPixelId } = analytics;
  if (!gtmId && !metaPixelId) return null;
  return (
    <>
      {gtmId && (
        <noscript>
          <iframe
            title="gtm"
            src={`https://www.googletagmanager.com/ns.html?id=${gtmId}`}
            height="0"
            width="0"
            style={{ display: "none", visibility: "hidden" }}
          />
        </noscript>
      )}
      {metaPixelId && (
        <noscript>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            alt=""
            height="1"
            width="1"
            style={{ display: "none" }}
            src={`https://www.facebook.com/tr?id=${metaPixelId}&ev=PageView&noscript=1`}
          />
        </noscript>
      )}
    </>
  );
}
