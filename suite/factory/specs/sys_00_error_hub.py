"""
DCA-SYS-00 · Central Error Hub

The spine. This is the piece that turns seven separate templates into one
system, and it is the difference between a $49 file and a $449 product.

Why a system needs this
-----------------------
Every template in the suite already routes its failures to a structured error
record instead of swallowing them. That is necessary but not sufficient: seven
templates each shouting into their own execution log is still seven places to
look, and nobody checks seven places. In practice they check none, which returns
the seller to exactly the silent-failure problem the suite exists to remove.

n8n has a built-in mechanism for this — set a workflow's *Error Workflow* in its
settings and every unhandled failure is delivered here with full context. One
place to watch, one alert channel to configure, one habit to build.

What it adds beyond forwarding
------------------------------
A raw error forwarder would be trivial and nearly useless, because the failure
that matters is buried among the ones that do not. So this classifies:

  * **Severity by business impact, not by stack trace.** A failed delivery costs
    a customer and a refund; a failed analytics write costs nothing today. They
    should not page you the same way.
  * **Storm suppression.** When an upstream API goes down, the same error fires
    hundreds of times. Forwarding all of them buries every other signal and
    trains the seller to ignore alerts — which is worse than having none. Repeat
    errors are counted and summarised instead.
  * **A plain-language cause and fix.** The audience is a seller, not an
    engineer. "ECONNREFUSED" is not actionable; "your email provider refused the
    connection — check the SMTP credential" is.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "central-error-hub"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-SYS-00 · Central Error Hub (every failure, one place, in plain language)",
        slug=SLUG,
        category="sys-spine",
        summary="Receives failures from every template in the suite, ranks them by business impact, suppresses repeat storms, and explains each one in language a seller can act on.",
        problem="Seven templates each logging failures to their own execution history is still seven places to look — so nobody looks, and silent failure returns through the back door.",
        outcome="One workflow watches everything. Revenue-affecting failures alert immediately with a plain-language fix; noise is counted and summarised instead of drowning the signal.",
        version="1.0.0",
        tags=["system", "monitoring", "spine", "hardened"],
        credentials_needed=["SMTP account (or Slack/Telegram)"],
        setup_minutes=8,
    )

    wf.sticky(
        "## 🧭 Central Error Hub — the spine of the system\n"
        "**Every failure, from every template, in one place.**\n\n"
        "### Setup (about 8 minutes, do this ONCE)\n"
        "1. Import and **Activate** this workflow.\n"
        "2. Open **every other template** → `Settings` → **Error Workflow** →\n"
        "   choose **DCA-SYS-00 · Central Error Hub**.\n"
        "3. **⚙️ Config** → set `alertEmail`.\n"
        "4. Attach SMTP to **📨 Send alert**.\n\n"
        "That is it. From now on, if anything anywhere breaks, you hear about it\n"
        "**once**, in language you can act on.\n\n"
        "### Why this is worth more than any single template\n"
        "A template that fails silently costs you money for weeks. This is the\n"
        "difference between owning a system and owning a pile of files.",
        (-660, -480),
        (580, 520),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🎚️ Severity is business impact, not stack trace\n"
        "| Level | Means | You get |\n"
        "| --- | --- | --- |\n"
        "| 🔴 **critical** | a customer paid and did not get it | immediate alert |\n"
        "| 🟠 **high** | money at risk — fraud, dispute, dunning | immediate alert |\n"
        "| 🟡 **medium** | marketing/support degraded | immediate alert |\n"
        "| ⚪ **low** | logging, reporting | counted only |\n\n"
        "A failed delivery and a failed analytics write are not the same\n"
        "emergency, and treating them alike teaches you to ignore both.",
        (-40, -480),
        (500, 400),
        COLOR_RED,
    )

    wf.sticky(
        "### 🌊 Storm suppression\n"
        "When an upstream API goes down the same error fires hundreds of times.\n\n"
        "Forwarding every one buries all other signals and trains you to ignore\n"
        "alerts — **worse than having none at all**.\n\n"
        "So the first occurrence alerts. Repeats inside `stormWindowMinutes` are\n"
        "counted silently, and you get one summary instead of two hundred pages.",
        (500, -480),
        (460, 340),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🗣️ Written for a seller, not an engineer\n"
        "`ECONNREFUSED` is not actionable.\n\n"
        "*\"Your email provider refused the connection — check the SMTP\n"
        "credential in n8n\"* is.\n\n"
        "Every alert carries a likely cause and a concrete next step. Add your own\n"
        "patterns in **🔎 Explain the failure** as you learn your own recurring\n"
        "problems.",
        (1180, 200),
        (440, 300),
        COLOR_GREEN,
    )

    trigger = wf.node(
        "🚨 Any workflow failed",
        "n8n-nodes-base.errorTrigger",
        {},
        1,
        (-660, 160),
        notes="Fires when any workflow that names this one as its Error Workflow fails.",
    )

    cfg = wf.config(
        {
            "alertEmail": "you@yourdomain.com",
            "fromEmail": "alerts@yourdomain.com",
            "storeName": "YOUR_STORE_NAME",
            "stormWindowMinutes": 30,
            "alertOnLow": False,
            "criticalTemplates": ["instant-digital-delivery", "secure-download-endpoint"],
            "highTemplates": ["pre-payment-fraud-scoring", "chargeback-early-warning", "failed-payment-recovery"],
            "historyTtlHours": 48,
        },
        (-440, 160),
        notes="Set alertEmail and you are done. The template lists control severity ranking.",
    )

    classify = wf.code(
        "🎚️ Rank by business impact",
        r"""
// n8n's error trigger hands us the failing workflow, the node, and the message.
// Turn that into a business judgement: does this cost a customer right now?
const cfg = $('⚙️ Config').first().json.__config;

return $input.all().map(item => {
  const e = item.json;

  const wfName = String(e.workflow?.name ?? e.workflow?.id ?? 'unknown workflow');
  const nodeName = String(e.execution?.lastNodeExecuted ?? e.node?.name ?? 'unknown node');
  const message = String(
    e.execution?.error?.message ?? e.error?.message ?? e.message ?? 'no message supplied'
  );
  const stack = String(e.execution?.error?.stack ?? '').slice(0, 400);
  const executionId = e.execution?.id ?? null;
  const executionUrl = e.execution?.url ?? null;

  // Match against the slug we stamp into every template name.
  const haystack = wfName.toLowerCase();
  const isCritical = (cfg.criticalTemplates || []).some(s => haystack.includes(String(s).toLowerCase()));
  const isHigh = (cfg.highTemplates || []).some(s => haystack.includes(String(s).toLowerCase()));

  // A delivery or download failure means someone paid and is currently stuck.
  // That outranks everything, including our own template lists.
  const touchesCustomerMoney =
    /deliver|download|payment|order|invoice|refund/i.test(wfName + ' ' + nodeName);

  let severity = 'medium';
  if (isCritical || (touchesCustomerMoney && /send|deliver|serve/i.test(nodeName))) severity = 'critical';
  else if (isHigh) severity = 'high';
  else if (/log|report|analytic|summary|audit/i.test(nodeName)) severity = 'low';

  return { json: {
    severity,
    workflowName: wfName,
    nodeName,
    message,
    stack,
    executionId,
    executionUrl,
    failedAt: new Date().toISOString(),
    // Group identity for storm detection: same workflow + node + error shape.
    fingerprint: `${wfName}|${nodeName}|${message.slice(0, 80)}`,
    __config: cfg,
  }};
});
""",
        (-220, 160),
        notes="Severity reflects what it costs, not what it looks like in a stack trace.",
        always_output=True,
    )

    storm = wf.code(
        "🌊 Suppress repeat storms",
        r"""
// One alert per distinct failure per window. When an upstream API dies the same
// error arrives hundreds of times; forwarding all of them destroys the value of
// every alert you will ever send.
const store = $getWorkflowStaticData('global');
store.errors = store.errors || {};

const now = Date.now();

return $input.all().map(item => {
  const o = item.json;
  const cfg = o.__config;
  const windowMs = Number(cfg.stormWindowMinutes) * 60 * 1000;
  const ttlMs = Number(cfg.historyTtlHours) * 60 * 60 * 1000;

  for (const [k, r] of Object.entries(store.errors)) {
    if (now - r.firstAt > ttlMs) delete store.errors[k];
  }

  const key = o.fingerprint;
  const rec = store.errors[key];

  if (rec && now - rec.firstAt < windowMs) {
    rec.count += 1;
    rec.lastAt = now;
    store.errors[key] = rec;
    return { json: { ...o,
      shouldAlert: false,
      repeatCount: rec.count,
      suppressedNote: `Same failure ${rec.count}× in the last ${cfg.stormWindowMinutes} min — alert suppressed.`,
    }};
  }

  // First occurrence, or the window expired. Alert — and if this is a fresh
  // window after a storm, say how many were swallowed so the scale is visible.
  const previous = rec ? rec.count : 0;
  store.errors[key] = { firstAt: now, lastAt: now, count: 1 };

  return { json: { ...o,
    shouldAlert: true,
    repeatCount: 1,
    previousBurst: previous > 1 ? previous : null,
  }};
});
""",
        (0, 160),
        notes="First occurrence alerts; repeats inside the window are counted silently.",
        always_output=True,
    )

    explain = wf.code(
        "🔎 Explain the failure",
        r"""
// Translate the error into something a non-engineer can act on. This list is a
// starting set covering the failures these templates actually produce — extend
// it as you learn your own recurring problems.
const PATTERNS = [
  { re: /ECONNREFUSED|ETIMEDOUT|ENOTFOUND|socket hang up/i,
    cause: 'The service you were calling did not answer.',
    fix: 'Usually temporary. Check the service\'s status page. If it persists, verify the host/URL in the failing node.' },

  { re: /invalid.?login|authentication failed|535|EAUTH/i,
    cause: 'Your email provider rejected the login.',
    fix: 'Open Credentials → your SMTP account. The password must be the SMTP key from your provider, not your account password.' },

  { re: /wrong version number|SSL routines/i,
    cause: 'SSL setting does not match the port.',
    fix: 'Port 587 → turn SSL/TLS OFF. Port 465 → turn SSL/TLS ON. They must agree.' },

  { re: /401|unauthorized|invalid.?api.?key|x-api-key/i,
    cause: 'An API key was rejected.',
    fix: 'The key is missing, expired, or lacks permission. Re-add it in Credentials on the failing node.' },

  { re: /429|rate.?limit|too many requests/i,
    cause: 'You hit the provider\'s rate limit.',
    fix: 'The node retries automatically. If it keeps happening, reduce how often the schedule runs, or upgrade your plan with that provider.' },

  { re: /signature verification failed/i,
    cause: 'A webhook signature did not match.',
    fix: 'Either the signing secret is wrong, or someone is posting fake requests to your endpoint. Check the secret first — and note this template correctly refused to deliver.' },

  { re: /missing required field/i,
    cause: 'The incoming payload was missing something essential.',
    fix: 'The error names the missing field. Check that the sending system includes it — customer email is the usual culprit.' },

  { re: /Unrecognised webhook payload|Unrecognized/i,
    cause: 'The payment provider was not recognised.',
    fix: 'Open ⚙️ Config and set "provider" explicitly instead of leaving it on "auto".' },

  { re: /no buyer email|No customer email|No email on/i,
    cause: 'The event carried no customer email, so nothing could be sent.',
    fix: 'Configure your gateway or form to include the customer email in its webhook payload.' },

  { re: /cannot read propert|undefined is not|is not a function/i,
    cause: 'The data arrived in an unexpected shape.',
    fix: 'Open the execution, look at the input to the failing node, and compare it with what the template expects. Send this to support if unclear.' },
];

return $input.all().map(item => {
  const o = item.json;
  const hit = PATTERNS.find(p => p.re.test(o.message)) || {
    cause: 'An unexpected error occurred.',
    fix: 'Open the execution in n8n and inspect the failing node\'s input and error detail.',
  };

  const icon = { critical: '🔴', high: '🟠', medium: '🟡', low: '⚪' }[o.severity] || '⚪';

  const impact = {
    critical: 'A customer may have paid and not received their product. Check this now.',
    high: 'Money is at risk — fraud screening, a dispute deadline, or a payment recovery did not run.',
    medium: 'A marketing or support step did not run. Not urgent, but do not leave it.',
    low: 'Logging or reporting only. No customer impact.',
  }[o.severity];

  const alertText =
`${icon} ${String(o.severity).toUpperCase()} — ${o.__config.storeName}

${impact}

Workflow: ${o.workflowName}
Node:     ${o.nodeName}
Time:     ${o.failedAt}
${o.executionUrl ? `Execution: ${o.executionUrl}` : (o.executionId ? `Execution id: ${o.executionId}` : '')}

── WHAT HAPPENED ───────────────────
${hit.cause}

Raw error: ${o.message}

── WHAT TO DO ──────────────────────
${hit.fix}
${o.previousBurst ? `\n⚠️ This failure occurred ${o.previousBurst}× in the previous window before this alert.` : ''}`;

  return { json: { ...o, cause: hit.cause, fix: hit.fix, alertText,
    subject: `${icon} ${o.severity.toUpperCase()} — ${o.workflowName} failed` } };
});
""",
        (240, 160),
        notes="Plain-language cause and fix. Extend PATTERNS as you learn your own recurring errors.",
    )

    should_alert = wf.code(
        "🔔 Alert or just record?",
        r"""
// Low severity is recorded but does not interrupt anyone unless the seller has
// opted in. Suppressed storm repeats are recorded too.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;
  const lowAndQuiet = o.severity === 'low' && cfg.alertOnLow !== true;
  return { json: { ...o, __alert: o.shouldAlert && !lowAndQuiet } };
});
""",
        (480, 160),
        notes="Applies the alertOnLow preference on top of storm suppression.",
    )

    gate = wf.if_(
        "📣 Send it?",
        (720, 160),
        left="={{ $json.__alert }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    send = wf.node(
        "📨 Send alert",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.__config.alertEmail }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "text",
            "text": "={{ $json.alertText }}",
            "options": {},
        },
        2.1,
        (960, 60),
        retry=True,
        max_tries=3,
        wait_ms=2000,
        on_error="continueRegularOutput",
        notes="Attach SMTP. Swap for Slack/Telegram if you prefer — the text is ready either way.",
    )

    log = wf.code(
        "📒 Failure log",
        r"""
// Every failure, alerted or not. Reviewed monthly this tells you which template
// is actually costing you time — and that is what to fix or replace first.
return $input.all().map(i => ({ json: {
  ts: i.json.failedAt,
  severity: i.json.severity,
  workflow: i.json.workflowName,
  node: i.json.nodeName,
  cause: i.json.cause,
  message: String(i.json.message).slice(0, 300),
  alerted: !!i.json.__alert,
  repeatCount: i.json.repeatCount ?? 1,
}}));
""",
        (1200, 160),
        notes="Append to Sheets/Airtable. Review monthly — the pattern tells you what to fix.",
    )

    wf.chain(trigger, cfg, classify, storm, explain, should_alert, gate)
    wf.connect(gate, send, out=0)
    wf.connect(gate, log, out=1)
    wf.connect(send, log)

    return wf
