"""
validate.py — the gate every template must pass before it can ship.

The market's quality problem is not that authors are careless; it is that
nothing checks their work. Marketplaces review for plausibility, not for
resilience, so templates with no retry policy and no error path pass review and
then fail in production.

This module encodes our published standard as executable checks. `build.py`
refuses to write a template that fails any ERROR-level rule, so the standard
cannot drift from what we actually ship.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STICKY = "n8n-nodes-base.stickyNote"

TRIGGER_HINTS = (
    "trigger",
    "n8n-nodes-base.webhook",
    "n8n-nodes-base.cron",
    "n8n-nodes-base.interval",
    "n8n-nodes-base.emailReadImap",
    "n8n-nodes-base.executeWorkflowTrigger",
)

# Calls that leave the box and can therefore fail for reasons outside our control.
NETWORK_NODES = (
    "n8n-nodes-base.httpRequest",
    "n8n-nodes-base.webhook",  # excluded from retry rule below; listed for clarity
)

# Patterns that must never appear in a shipped template. Credentials belong in
# n8n's credential store; a template carrying a live key is a security incident
# for whoever imports it and for whoever exported it.
SECRET_PATTERNS = [
    (re.compile(r"sk_live_[A-Za-z0-9]{8,}"), "Stripe live secret key"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAI-style API key"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "Google API key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{24,}"), "hardcoded bearer token"),
]

# Placeholders are how we tell a buyer "put your value here" without shipping a
# real one. They are expected and must not trip the secret scanner.
PLACEHOLDER_OK = re.compile(r"(YOUR_|<[A-Z_]+>|REPLACE_ME|xxxx|\{\{|\$json|\$env)", re.I)


@dataclass
class Finding:
    level: str  # "error" | "warn"
    rule: str
    detail: str

    def __str__(self) -> str:
        icon = "✗" if self.level == "error" else "!"
        return f"  {icon} [{self.rule}] {self.detail}"


def _walk_strings(obj: Any, path: str = ""):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_strings(v, f"{path}[{i}]")


def validate_workflow(wf: dict[str, Any]) -> list[Finding]:
    out: list[Finding] = []
    nodes = wf.get("nodes", [])
    conns = wf.get("connections", {})
    real = [n for n in nodes if n.get("type") != STICKY]
    stickies = [n for n in nodes if n.get("type") == STICKY]
    names = {n["name"] for n in nodes}

    # ---- structural integrity -------------------------------------------
    if not nodes:
        out.append(Finding("error", "structure", "workflow has no nodes"))
        return out

    if len(names) != len(nodes):
        seen, dupes = set(), set()
        for n in nodes:
            if n["name"] in seen:
                dupes.add(n["name"])
            seen.add(n["name"])
        out.append(Finding("error", "structure", f"duplicate node names: {sorted(dupes)}"))

    ids = [n.get("id") for n in nodes]
    if len(set(ids)) != len(ids):
        out.append(Finding("error", "structure", "duplicate node ids"))

    for n in nodes:
        for key in ("id", "name", "type", "typeVersion", "position", "parameters"):
            if key not in n:
                out.append(Finding("error", "structure", f"node {n.get('name')!r} missing {key!r}"))
        pos = n.get("position")
        if not (isinstance(pos, list) and len(pos) == 2 and all(isinstance(v, int) for v in pos)):
            out.append(Finding("error", "structure", f"node {n.get('name')!r} has a malformed position"))

    # Every connection must point at a node that exists, or the import silently
    # produces a broken graph.
    for src, types in conns.items():
        if src not in names:
            out.append(Finding("error", "connections", f"connection from unknown node {src!r}"))
        for ctype, outputs in types.items():
            for slot in outputs:
                for link in slot:
                    if link.get("node") not in names:
                        out.append(
                            Finding("error", "connections", f"{src!r} points at unknown node {link.get('node')!r}")
                        )

    # ---- reachability ----------------------------------------------------
    triggers = [
        n for n in real
        if any(h in n["type"].lower() for h in ("trigger",)) or n["type"] in TRIGGER_HINTS
    ]
    if not triggers:
        out.append(Finding("error", "trigger", "no trigger node — workflow can never start"))

    linked: set[str] = set()
    for src, types in conns.items():
        linked.add(src)
        for outputs in types.values():
            for slot in outputs:
                for link in slot:
                    linked.add(link["node"])
    orphans = [n["name"] for n in real if n["name"] not in linked]
    if orphans:
        out.append(Finding("error", "connections", f"orphan node(s) not wired to anything: {orphans}"))

    # ---- the hardening standard -----------------------------------------
    http_nodes = [n for n in real if n["type"] == "n8n-nodes-base.httpRequest"]
    for n in http_nodes:
        if not n.get("retryOnFail"):
            out.append(
                Finding("error", "hardening/retry", f"{n['name']!r} calls the network without a retry policy")
            )
        if not n.get("onError"):
            out.append(
                Finding("warn", "hardening/error-path", f"{n['name']!r} has no explicit onError route")
            )

    # An error branch only counts if something is actually wired to output 1 of
    # a node that declares continueErrorOutput.
    has_error_route = any(
        n.get("onError") == "continueErrorOutput" for n in real
    ) and any(
        len(types.get("main", [])) > 1 and types["main"][1]
        for types in conns.values()
    )
    if http_nodes and not has_error_route:
        out.append(
            Finding("error", "hardening/error-path", "no failure branch is wired — errors would vanish silently")
        )

    joined = json.dumps(wf, ensure_ascii=False)
    if "__config" not in joined and "CONFIG" not in joined:
        out.append(Finding("error", "hardening/config", "no CONFIG block — buyer has nowhere obvious to edit"))

    # Idempotency is only required where an external system can replay us.
    if any(n["type"] == "n8n-nodes-base.webhook" for n in real):
        if "__eventId" not in joined and "getWorkflowStaticData" not in joined:
            out.append(
                Finding("error", "hardening/idempotency", "webhook-triggered but no replay protection — duplicate deliveries will occur")
            )

    # ---- documentation ---------------------------------------------------
    if len(stickies) < 2:
        out.append(Finding("error", "docs", f"only {len(stickies)} sticky note(s); on-canvas docs are required"))
    doc_chars = sum(len(n["parameters"].get("content", "")) for n in stickies)
    if doc_chars < 300:
        out.append(Finding("warn", "docs", f"on-canvas documentation is thin ({doc_chars} chars)"))

    documented = sum(1 for n in real if n.get("notes"))
    if real and documented / len(real) < 0.4:
        out.append(
            Finding("warn", "docs", f"only {documented}/{len(real)} nodes carry inline notes")
        )

    # ---- security --------------------------------------------------------
    for path, s in _walk_strings(wf):
        for pat, label in SECRET_PATTERNS:
            m = pat.search(s)
            if m and not PLACEHOLDER_OK.search(m.group(0)):
                out.append(Finding("error", "security/secret", f"possible {label} at {path}"))

    for n in nodes:
        creds = n.get("credentials") or {}
        for cname, cval in creds.items():
            if isinstance(cval, dict) and cval.get("id"):
                out.append(
                    Finding("error", "security/creds", f"{n['name']!r} pins credential id {cval['id']!r} from the author's account")
                )

    if wf.get("active") is True:
        out.append(Finding("warn", "safety", "workflow ships as active; it should import switched off"))

    return out


def validate_file(path: Path) -> list[Finding]:
    try:
        wf = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [Finding("error", "json", f"not valid JSON: {e}")]
    return validate_workflow(wf)


def report(findings: list[Finding]) -> tuple[int, int]:
    errors = sum(1 for f in findings if f.level == "error")
    warns = sum(1 for f in findings if f.level == "warn")
    return errors, warns
