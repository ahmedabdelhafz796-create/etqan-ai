# Video & Asset Specs — E-tqan

Exact export settings, thumbnail composition, trailer cut and per-platform
versions. Pair with `PROMO_PACKAGE.md` (storyboard, VO, animation prompts) and
`subtitles/{en,ar,tr}.srt`. Everything needed to render immediately.

## Brand constants

| Token | Value |
|---|---|
| Near-black | `#0B0906` |
| Ivory | `#FCFBF7` |
| Gold light → deep | `#F4D98B` → `#C9A227` |
| Emerald | `#12B981` · Royal `#2F5FD0` · Violet `#7A42C9` · Cyan `#0E7C93` |
| Display font | Sora 700/800 |
| Serif | Source Serif 4 |
| UI | Inter 400/600 |
| Arabic | Cairo 400/700 |
| Support handle | `@Ahm_t_AHZ01` |

## Master export (16:9)

- 3840×2160, 60 fps (deliver 1080p60 proxy too), H.264 high profile, ~40 Mbps.
- Audio: AAC 320 kbps, stereo, **-14 LUFS** integrated, true peak ≤ -1 dBTP.
- Duration 2:30. Color: Rec.709, warm gold grade, subtle grain + vignette.
- Subtitles: burn Arabic for the AR master; ship SRT sidecars for all three.

## Per-platform versions

| Version | Ratio | Res | Length | Scenes (from storyboard) | Notes |
|---|---|---|---|---|---|
| YouTube master | 16:9 | 3840×2160 | 2:30 | 1–10 | End screen last 8 s |
| Short trailer | 16:9 | 1920×1080 | 0:30 | 1, 2, 5, 7, 10 | Hook in first 2 s |
| TikTok | 9:16 | 1080×1920 | 0:30 | 2, 3, 5, 7, 10 | Burned captions, safe area 250 px top / 380 px bottom |
| Instagram Reels | 9:16 | 1080×1920 | 0:30 | 2, 3, 5, 7, 10 | Same as TikTok, no watermark |
| YouTube Shorts | 9:16 | 1080×1920 | 0:45 | 1–5, 10 | Title card at 0:00 |
| Instagram feed | 1:1 | 1080×1080 | 0:20 | 2, 5, 10 | One VO hook line |
| Story teaser | 9:16 | 1080×1920 | 0:10 | 1, 10 | "Launch offer" sticker zone free |
| X / LinkedIn | 16:9 | 1920×1080 | 0:45 | 1–5 + CTA | Captions on by default |

## Thumbnail (YouTube 1280×720)

- Background: near-black with a soft gold radial glow, upper-right.
- Left 55%: two lines of Sora 800 — **"Learn the skills"** (ivory) /
  **"that actually pay"** (gold gradient). Cap height ≈ 120 px.
- Right 45%: three premium book covers fanned in 3D (Python emerald,
  AI Arsenal gold, CSS violet), soft rim light, drop shadow.
- Bottom-left chip: `EN · AR · TR` in Inter 600, gold on 20% white.
- Bottom-right: E-tqan monogram (44 px rounded square, gold gradient).
- No more than 6 words of text. Export PNG + JPG (< 2 MB).
- Arabic variant: mirror the layout (text right, books left), Cairo 700,
  headline **"تعلّم المهارات التي تُدِرّ دخلًا"**.

## Motion & camera reference

| Beat | Camera | Easing |
|---|---|---|
| Ignition (0:00) | Slow dolly-in from black, 8% scale | ease-out 1.2 s |
| Book float (0:06) | Orbit right 12°, parallax layers | cubic (0.22, 1, 0.36, 1) |
| Montage (0:16) | Hard cuts on downbeats, micro push 2% | none (cuts) |
| Shelf build (0:30) | Lateral truck left→right, 6 s | ease-in-out |
| Page turns (0:45) | Top-down, shallow DOF rack focus | ease-out |
| Blueprint (1:05) | Pull back revealing the 17-point grid | ease-in-out |
| Checkout (1:25) | Macro push on the button, 4% | ease-out 0.6 s |
| Library reveal (2:05) | Wide pull back + gold bloom | ease-in-out 3 s |
| Logo (2:22) | Static, stroke-reveal then gold fill | ease-out 1 s |

## Audio bed

- 150 s, cinematic-inspirational: soft piano + warm pads + light percussive ticks.
- Build at 2:05, resolve 2:22. Suno/Udio prompt in `PROMO_PACKAGE.md` §5.
- Foley: UI click (1:27), success chime (1:32), page turns (0:46–1:02),
  three language whooshes (0:31, 0:36, 0:41), final gold sting (2:23).

## Editor deliverables checklist

- [ ] `etqan-master-16x9-2160p60.mp4`
- [ ] `etqan-trailer-16x9-1080p.mp4` (0:30)
- [ ] `etqan-9x16-tiktok.mp4` / `-reels.mp4` / `-shorts.mp4`
- [ ] `etqan-1x1-feed.mp4`, `etqan-9x16-story.mp4`
- [ ] `etqan-thumbnail-en.png`, `etqan-thumbnail-ar.png`
- [ ] Burned-in AR master + `subtitles/{en,ar,tr}.srt`
- [ ] Project file (Premiere `.prproj` / After Effects `.aep` / CapCut) + LUT
