#!/usr/bin/env python3
"""
build.py — generate every template, validate it, and refuse to ship failures.

    python3 build.py            # build + validate everything
    python3 build.py --check    # validate only, write nothing (use in CI)
    python3 build.py a1_01      # build one spec by name fragment

The gate is the point: a template that fails an ERROR-level rule is never
written to disk, so the published catalogue and the published standard cannot
drift apart.
"""

from __future__ import annotations

import argparse
import importlib
import json
import pkgutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from lib.validate import report, validate_workflow  # noqa: E402

TEMPLATES = HERE.parent / "templates"
SPECS = HERE / "specs"


def discover(fragment: str | None) -> list[str]:
    mods = [
        m.name
        for m in pkgutil.iter_modules([str(SPECS)])
        if not m.name.startswith("_")
    ]
    if fragment:
        mods = [m for m in mods if fragment in m]
    return sorted(mods)


def render_readme(wf) -> str:
    """Per-template install guide.

    Bad documentation is the top cause of templates failing at install time, so
    this is generated from the same metadata that builds the workflow — it
    cannot go stale relative to the file it documents.
    """
    d = wf.to_dict()
    real = [n for n in d["nodes"] if n["type"] != "n8n-nodes-base.stickyNote"]
    creds = "\n".join(f"- {c}" for c in wf.credentials_needed) or "- None"
    node_rows = "\n".join(
        f"| `{n['name']}` | `{n['type'].split('.')[-1]}` | {n.get('notes', '—')} |"
        for n in real
    )
    return f"""# {wf.name}

> {wf.summary}

**Category:** `{wf.category}` · **Version:** `{wf.version}` · **Nodes:** {len(real)} · **Setup:** ~{wf.setup_minutes} min

---

## The problem

{wf.problem}

## What you get

{wf.outcome}

---

## Install

1. In n8n choose **Workflows → Import from File** and pick `workflow.json`.
2. Open the **⚙️ Config** node and fill in your values. This is the only node
   you are required to edit.
3. Attach credentials where the canvas notes ask for them. Nothing is
   pre-filled — this file ships with no keys in it, by design.
4. Run once with the manual trigger (or with `testMode: true`) and confirm the
   output looks right.
5. Activate.

### Credentials required

{creds}

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
{node_rows}

---

## Reliability guarantees

This template is built through the suite's hardened core, so it ships with:

- **Replay protection** — duplicate webhook deliveries produce no duplicate side effects.
- **Input validation** — malformed payloads fail loudly at the entry point instead of corrupting data downstream.
- **Retry with backoff** — every outbound call retries 3× before giving up.
- **A wired failure path** — failures produce a structured alert, never silence.
- **No embedded credentials** — verified automatically before release.
- **On-canvas documentation** — every section is explained where you are working.

See [`../../../docs/03-hardening-standard.md`](../../../docs/03-hardening-standard.md) for the full standard and the checks that enforce it.

---

## Support

Something not working? Include your n8n version, the failing node's name and the
execution error, and it can usually be resolved in one reply.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("fragment", nargs="?", help="only build specs matching this")
    ap.add_argument("--check", action="store_true", help="validate without writing")
    args = ap.parse_args()

    mods = discover(args.fragment)
    if not mods:
        print("No specs found.")
        return 1

    total_err = total_warn = 0
    built = 0
    print(f"Building {len(mods)} template(s)\n" + "═" * 60)

    for name in mods:
        mod = importlib.import_module(f"specs.{name}")
        wf = mod.build()
        wf_dict = wf.to_dict()
        findings = validate_workflow(wf_dict)
        errs, warns = report(findings)
        total_err += errs
        total_warn += warns

        status = "FAIL" if errs else ("PASS" if not warns else "PASS*")
        real = len([n for n in wf_dict["nodes"] if n["type"] != "n8n-nodes-base.stickyNote"])
        print(f"\n[{status}] {wf.slug}  ({real} nodes, {errs} errors, {warns} warnings)")
        for f in findings:
            print(f)

        if errs:
            print(f"  → refusing to write {wf.slug}: fix the errors above")
            continue

        if not args.check:
            path = wf.save(TEMPLATES)
            (path.parent / "README.md").write_text(render_readme(wf), encoding="utf-8")
            # Round-trip proves the file we wrote parses back to what we built.
            reloaded = json.loads(path.read_text(encoding="utf-8"))
            assert reloaded == wf_dict, f"round-trip mismatch for {wf.slug}"
            built += 1
            print(f"  → {path.relative_to(TEMPLATES.parent)}")

    print("\n" + "═" * 60)
    print(f"built {built}/{len(mods)} · {total_err} errors · {total_warn} warnings")
    return 1 if total_err else 0


if __name__ == "__main__":
    raise SystemExit(main())
