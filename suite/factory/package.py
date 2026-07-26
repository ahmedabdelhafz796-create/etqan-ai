#!/usr/bin/env python3
"""
package.py — turn the built templates into sellable bundles.

    python3 package.py

Produces `dist/` containing one folder and one zip per product tier, each
self-contained: the workflow files, an install guide written for that tier, a
licence, and a support note.

Why bundles rather than one big download
----------------------------------------
A buyer who purchases the delivery template should not receive nineteen other
workflows they did not pay for and cannot use — it makes the purchase feel
cluttered rather than generous, and it removes any reason to upgrade later.

Why the free tier exists
------------------------
One free template, not one per category. Eight free templates means eight
documentation and support burdens with no revenue, and eight weak entry points
instead of one strong one. `secure-download-endpoint` is chosen deliberately: it
is the weakest commercially (platforms already do it), so giving it away costs
little, and installing it creates demand for the paid template that mints the
links it verifies.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
TEMPLATES = ROOT / "templates"
DIST = ROOT / "dist"
DOCS = ROOT / "docs"

YEAR = 2026

# ── Product tiers ───────────────────────────────────────────────────────
# Ordered so each tier is a strict superset of the one before, which is what
# makes an upgrade path feel like an upgrade rather than a second purchase.
TIERS = [
    {
        "id": "00-free-secure-downloads",
        "name": "Secure Download Endpoint",
        "price": "Free",
        "tagline": "Stop losing customers to expired and leaked download links.",
        "templates": ["a1-delivery/secure-download-endpoint"],
        "spine": [],
    },
    {
        "id": "01-delivery-essentials",
        "name": "Delivery Essentials",
        "price": "$79",
        "tagline": "Every paid order delivered, verified, and recoverable.",
        "templates": [
            "a1-delivery/instant-digital-delivery",
            "a1-delivery/secure-download-endpoint",
            "a1-delivery/product-update-broadcast",
            "a4-support/download-problem-self-service",
        ],
        "spine": ["sys-spine/setup-checker", "sys-spine/central-error-hub"],
        "tools": ["z-tools/delivery-test-runner"],
    },
    {
        "id": "02-revenue-protection",
        "name": "Revenue Protection",
        "price": "$149",
        "tagline": "Stop losing money to fraud, disputes, failed cards and abandoned carts.",
        "templates": [
            "a3-fraud-security/pre-payment-fraud-scoring",
            "a3-fraud-security/chargeback-early-warning",
            "a3-fraud-security/leak-detection-watermarking",
            "a5-marketing-revenue/cart-abandonment-recovery",
            "b4-saas-subscriptions/failed-payment-recovery",
        ],
        "spine": ["sys-spine/setup-checker", "sys-spine/central-error-hub"],
    },
    {
        "id": "03-ai-agents",
        "name": "AI Agents",
        "price": "$149",
        "tagline": "AI that refuses to guess — support, lead scoring, translation, copy.",
        "templates": [
            "b1-ai-agents/ai-customer-support-agent",
            "b1-ai-agents/ai-lead-qualifier",
            "a6-content-localization/ai-product-translation",
            "a6-content-localization/ai-sales-page-writer",
            "b5-recruitment/cv-screening-triage",
        ],
        "spine": ["sys-spine/setup-checker", "sys-spine/central-error-hub"],
    },
    {
        "id": "04-complete-suite",
        "name": "Complete Suite",
        "price": "$399",
        "tagline": "The whole system: 20 templates, 3 system workflows, one install.",
        "templates": "ALL",
        "spine": "ALL",
    },
]

LICENCE = f"""Digital Commerce Automation Suite — Licence
Copyright (c) {YEAR}

WHAT YOU MAY DO
  - Use these workflows in your own business, on any number of your own
    n8n instances, for as long as you like.
  - Modify them however you want.
  - Use them in client work you are paid for.

WHAT YOU MAY NOT DO
  - Resell, redistribute or republish the workflow files themselves, whether
    modified or not.
  - Include them in a bundle, course or template pack that you sell.

NO WARRANTY
  These workflows are provided as-is. They have been validated structurally
  and tested behaviourally, but they run against services outside our control
  — payment gateways, email providers, AI APIs — and those change.

  You are responsible for testing them in your own environment before using
  them with real customers. The setup checker included in most bundles exists
  to make that straightforward.

  Nothing here is legal, tax or financial advice. The invoicing template
  applies rates you configure; it does not determine your tax liability. The
  takedown template drafts a notice; it is not a lawyer.
"""


def collect(tier: dict) -> list[Path]:
    """Resolve a tier's template list to actual directories on disk."""
    if tier["templates"] == "ALL":
        return sorted(p.parent for p in TEMPLATES.glob("*/*/workflow.json"))

    wanted = list(tier["templates"]) + list(tier.get("spine", [])) + list(tier.get("tools", []))
    out = []
    for rel in wanted:
        d = TEMPLATES / rel
        if not (d / "workflow.json").exists():
            raise SystemExit(f"tier {tier['id']}: missing template {rel}")
        out.append(d)
    return out


def install_guide(tier: dict, dirs: list[Path]) -> str:
    """Per-tier install guide. Order matters more than completeness here."""
    has_checker = any(d.name == "setup-checker" for d in dirs)
    has_hub = any(d.name == "central-error-hub" for d in dirs)
    signing = [d.name for d in dirs if d.name in {
        "instant-digital-delivery", "secure-download-endpoint",
        "download-problem-self-service", "product-update-broadcast",
    }]

    lines = [
        f"# {tier['name']} — install guide",
        "",
        f"> {tier['tagline']}",
        "",
        f"**{len(dirs)} workflow(s).** Set-up is roughly "
        f"{sum(15 for _ in dirs) // max(1, len(dirs))} minutes per template, "
        "and the order below matters.",
        "",
        "---",
        "",
        "## Before you start",
        "",
        "You need an n8n account (Cloud or self-hosted — these work identically on",
        "both) and an SMTP account for sending email. Brevo's free tier is enough",
        "to begin with.",
        "",
        "---",
        "",
        "## Install in this order",
        "",
    ]

    step = 1
    if has_hub:
        lines += [
            f"### {step}. Central Error Hub — first",
            "",
            "Import it, activate it, and set your alert email. Then, in **every**",
            "other workflow you install: `Settings → Error Workflow → Central Error",
            "Hub`.",
            "",
            "Do this first and any mistake you make later arrives explained instead",
            "of vanishing into an execution log.",
            "",
        ]
        step += 1

    if len(signing) >= 2:
        lines += [
            f"### {step}. Choose your link-signing secret",
            "",
            "Invent one long random string now — for example:",
            "",
            "```bash",
            "openssl rand -hex 32",
            "```",
            "",
            f"You will paste **the same value** into the Crypto node of "
            f"{len(signing)} workflow(s) in this bundle:",
            "",
        ] + [f"- `{n}`" for n in signing] + [
            "",
            "⚠️ If any two differ, every download fails with an \"invalid signature\"",
            "error that looks like tampering. Watch for trailing spaces and for",
            "quotes your text editor may have turned into smart quotes.",
            "",
        ]
        step += 1

    lines += [
        f"### {step}. Import the workflows",
        "",
        "In n8n: `Workflows → Import from File`, then pick each `workflow.json`.",
        "",
        "Open each one's **⚙️ Config** node and fill in your values. That is the",
        "only node you are required to edit — everything else is documented on the",
        "canvas next to the thing it explains.",
        "",
    ]
    step += 1

    if has_checker:
        lines += [
            f"### {step}. Run the Setup Checker",
            "",
            "Open it, fill in its Config with the same values you just used, and",
            "press **Execute**. It reports exactly what is still wrong and how to",
            "fix each thing, ordered by severity.",
            "",
            "**Fix every 🔴 before pointing real traffic at anything.**",
            "",
        ]
        step += 1

    lines += [
        f"### {step}. Test before going live",
        "",
        "Most templates ship with a safe way to try them: `testMode`, `shadowMode`,",
        "or `autoReply: false`. Use it. Read a few days of output before letting",
        "anything touch a real customer.",
        "",
        "---",
        "",
        "## What's included",
        "",
        "| Workflow | What it does |",
        "| --- | --- |",
    ]

    for d in dirs:
        try:
            wf = json.loads((d / "workflow.json").read_text(encoding="utf-8"))
            summary = wf.get("meta", {}).get("slug", d.name)
        except Exception:
            summary = d.name
        readme = d / "README.md"
        blurb = ""
        if readme.exists():
            for line in readme.read_text(encoding="utf-8").splitlines():
                if line.startswith("> "):
                    blurb = line[2:].strip()
                    break
        lines.append(f"| `{d.name}` | {blurb or summary} |")

    lines += [
        "",
        "Each folder has its own `README.md` with the full node-by-node breakdown.",
        "",
        "---",
        "",
        "## If something does not work",
        "",
        "Send three things and it can usually be resolved in one reply:",
        "",
        "1. Your n8n version (bottom-left of the n8n sidebar).",
        "2. The **name of the node** that failed.",
        "3. The error text from the execution.",
        "",
        "The Setup Checker's output is also worth attaching — it usually contains",
        "the answer already.",
        "",
    ]
    return "\n".join(lines) + "\n"


def build_tier(tier: dict) -> Path:
    dirs = collect(tier)
    out = DIST / tier["id"]
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for d in dirs:
        dest = out / "workflows" / d.name
        dest.mkdir(parents=True)
        shutil.copy2(d / "workflow.json", dest / "workflow.json")
        if (d / "README.md").exists():
            shutil.copy2(d / "README.md", dest / "README.md")

    (out / "INSTALL.md").write_text(install_guide(tier, dirs), encoding="utf-8")
    (out / "LICENCE.txt").write_text(LICENCE, encoding="utf-8")

    # The hardening standard travels with every bundle. It is the argument for
    # the price, and a buyer comparing us with a $19 pack should be able to read
    # exactly what they are paying for.
    if (DOCS / "03-hardening-standard.md").exists():
        shutil.copy2(DOCS / "03-hardening-standard.md", out / "WHY-THIS-IS-DIFFERENT.md")

    archive = DIST / f"{tier['id']}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(out.parent))

    return archive


def main() -> int:
    if not TEMPLATES.exists():
        print("No templates found. Run build.py first.")
        return 1

    DIST.mkdir(exist_ok=True)
    print(f"Packaging {len(TIERS)} tier(s)\n" + "═" * 60)

    for tier in TIERS:
        archive = build_tier(tier)
        dirs = collect(tier)
        size_kb = archive.stat().st_size / 1024
        print(f"\n{tier['price']:>7}  {tier['name']}")
        print(f"         {len(dirs)} workflow(s) · {size_kb:.0f} KB")
        print(f"         → {archive.relative_to(ROOT)}")

    print("\n" + "═" * 60)
    print(f"{len(TIERS)} bundle(s) written to {DIST.relative_to(ROOT)}/")
    print("\nEach bundle is self-contained: workflows, install guide, licence,")
    print("and the hardening standard as the argument for the price.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
