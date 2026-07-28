#!/usr/bin/env python3
"""
test_gate.py — prove the validator actually rejects bad templates.

    python3 test_gate.py

A gate that only ever reports PASS is decoration. This takes a known-good
template, injects one defect at a time, and asserts the validator catches each
one. It exists because the first version of the retry rule enumerated
integration node types and therefore missed `emailSend` — the most
failure-prone node in the delivery template. The rule is now default-deny, and
this file is what stops that class of gap from coming back.

Run this after any change to lib/validate.py.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from lib.validate import validate_workflow  # noqa: E402

REFERENCE = HERE.parent / "templates" / "a1-delivery" / "instant-digital-delivery" / "workflow.json"


def _add_node(wf, node, after):
    wf["nodes"].append(node)
    wf["connections"].setdefault(after, {}).setdefault("main", [[]])[0].append(
        {"node": node["name"], "type": "main", "index": 0}
    )


# Each case: (label, mutation, should_be_caught)
CASES = [
    ("baseline stays clean", lambda w: None, False),

    ("live Stripe key in code", lambda w: w["nodes"][5]["parameters"].update(
        jsCode='const k = "sk_live_51H8xQ2eZvKYlo2C0abcdef";'), True),

    ("OpenAI key in code", lambda w: w["nodes"][5]["parameters"].update(
        jsCode='const k = "sk-proj1234567890abcdefghijklmnopqrstuvwxyz";'), True),

    ("retry stripped from emailSend", lambda w: [
        n.pop("retryOnFail", None) for n in w["nodes"]
        if n["type"] == "n8n-nodes-base.emailSend"], True),

    ("new integration added without retry", lambda w: _add_node(w, {
        "id": "probe-slack", "name": "Slack alert", "type": "n8n-nodes-base.slack",
        "typeVersion": 2.2, "position": [0, 0], "parameters": {}},
        "🧾 Record the order"), True),

    ("connection to a node that does not exist", lambda w:
        w["connections"].setdefault("⚙️ Config", {}).setdefault("main", [[]])[0].append(
            {"node": "Ghost", "type": "main", "index": 0}), True),

    ("orphan node", lambda w: w["nodes"].append({
        "id": "probe-orphan", "name": "Stranded", "type": "n8n-nodes-base.code",
        "typeVersion": 2, "position": [0, 0], "parameters": {"jsCode": "return items;"}}), True),

    ("author's credential id pinned", lambda w: w["nodes"][6].update(
        credentials={"smtp": {"id": "AbC123xyz", "name": "author account"}}), True),

    ("all on-canvas docs removed", lambda w: w.__setitem__(
        "nodes", [n for n in w["nodes"] if not n["type"].endswith("stickyNote")]), True),

    ("duplicate node name", lambda w: w["nodes"][3].update(name=w["nodes"][4]["name"]), True),

    ("trigger removed", lambda w: w.__setitem__(
        "nodes", [n for n in w["nodes"] if n["type"] != "n8n-nodes-base.webhook"]), True),

    ("malformed position", lambda w: w["nodes"][4].update(position=["a", "b"]), True),

    # The error-path rule is checked per node. An earlier version asked only
    # whether *some* node had a wired error output, which let a file with one
    # handled node and several unhandled ones pass.
    ("onError stripped from a network node", lambda w: [
        n.pop("onError", None) for n in w["nodes"]
        if n["type"] == "n8n-nodes-base.emailSend"], True),

    ("error output declared but wired to nothing", lambda w:
        w["connections"].get("📧 Send the product", {}).get("main", [[], []]).__setitem__(1, []), True),
]


def main() -> int:
    if not REFERENCE.exists():
        print(f"reference template missing: {REFERENCE}\nRun build.py first.")
        return 1

    base = json.loads(REFERENCE.read_text(encoding="utf-8"))
    passed = 0

    print("Gate integrity probes\n" + "═" * 60)
    for label, mutate, should_catch in CASES:
        wf = copy.deepcopy(base)
        mutate(wf)
        errors = [f for f in validate_workflow(wf) if f.level == "error"]
        caught = bool(errors)
        ok = caught == should_catch
        passed += ok
        rule = f" | {errors[0].rule}" if errors else ""
        print(f"{'✅' if ok else '❌'} {label:42} {len(errors)} error(s){rule}")
        if not ok:
            expectation = "expected to be CAUGHT but passed" if should_catch else "expected CLEAN but was flagged"
            print(f"     ↳ {expectation}")

    print("═" * 60)
    print(f"{passed}/{len(CASES)} probes behaved correctly")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
