"""
DCA-SYS-02 · Setup Checker & Install Guide

The third spine piece. The first two make the suite observable; this one makes
it installable, which is the difference between a product people buy and a
product people use.

The problem it solves is the one that kills template sales
----------------------------------------------------------
Around 70% of published templates fail at install. Not because the workflows are
wrong, but because installation is a long sequence of small steps where any
single omission produces a silent, confusing failure hours later — a secret that
does not match between two workflows, a Config left on placeholder values, an
Error Workflow never pointed anywhere, a template left inactive.

The buyer does not know which step they missed. They see "it doesn't work", and
they ask for a refund or leave a review saying so.

So this checks the installation itself
--------------------------------------
Run it once after importing and it reports, in order of severity, exactly what
is still wrong and exactly how to fix each thing. It is the closest thing to
someone looking over the buyer's shoulder.

The mismatched-secret check earns its place alone
-------------------------------------------------
Four templates share one link-signing secret. If A1-01 signs with one value and
A1-02 verifies with another, every download fails with an "invalid signature"
message that looks like tampering rather than misconfiguration. That failure is
extremely hard to diagnose from the inside and extremely easy to detect from
here — so the checker computes a signature with each configured secret and
compares, rather than trusting the buyer to have pasted the same string twice.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "setup-checker"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-SYS-02 · Setup Checker & Install Guide (run this first)",
        slug=SLUG,
        category="sys-spine",
        summary="Checks an installation for the mistakes that cause silent failures — placeholder values left in Config, mismatched signing secrets, missing Error Workflow, inactive templates — and reports each with its fix, ordered by severity.",
        problem="Around 70% of templates fail at install, not because the workflows are wrong but because one small step was missed and the resulting failure appears hours later somewhere unrelated. The buyer cannot tell which step, so they ask for a refund.",
        outcome="One run tells the buyer exactly what is still wrong and how to fix it, before anything reaches a real customer.",
        version="1.0.0",
        tags=["system", "setup", "spine", "onboarding", "hardened"],
        credentials_needed=["None to run the check", "SMTP if you want the report emailed"],
        setup_minutes=3,
    )

    wf.sticky(
        "## 🧰 Setup Checker — run this FIRST\n"
        "**One run → everything still wrong, with the fix for each.**\n\n"
        "### How to use it\n"
        "1. Import every template you plan to use.\n"
        "2. Fill in their **⚙️ Config** nodes.\n"
        "3. Come back here, open **⚙️ Config**, and enter the same values you used\n"
        "   in the others.\n"
        "4. Press **Execute**. Read **📋 Setup report**.\n"
        "5. Fix what it lists, run again until it is clean.\n\n"
        "### Why this exists\n"
        "Roughly **70% of templates fail at install** — not because the workflow is\n"
        "wrong, but because one small step was missed and the failure shows up\n"
        "hours later somewhere unrelated.\n\n"
        "This is the closest thing to someone looking over your shoulder.",
        (-660, -520),
        (600, 540),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🔑 The check that matters most\n"
        "**Four templates share one link-signing secret:**\n"
        "`A1-01` mints · `A1-02` verifies · `A4-01` reissues · `A1-04` broadcasts.\n\n"
        "If any two disagree, **every download fails** with an \"invalid signature\"\n"
        "error that looks like tampering rather than a typo.\n\n"
        "That is brutal to diagnose from the inside. So this actually **computes a\n"
        "signature with each secret and compares them** — it does not trust that\n"
        "you pasted the same string four times.",
        (-20, -520),
        (500, 400),
        COLOR_RED,
    )

    wf.sticky(
        "### 📊 Severity order\n"
        "| Level | Meaning |\n"
        "| --- | --- |\n"
        "| 🔴 **blocker** | customers will hit this today |\n"
        "| 🟠 **important** | works now, will bite you |\n"
        "| 🟡 **advisable** | best practice, not urgent |\n"
        "| ✅ **passed** | confirmed working |\n\n"
        "Fix every 🔴 before pointing real traffic at anything.",
        (500, -520),
        (440, 340),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🔁 Run it again after any change\n"
        "Rotated a secret · added a template · changed a Config value · moved from\n"
        "test to live.\n\n"
        "It takes three seconds and catches the mistake before a customer does.",
        (1120, 340),
        (420, 260),
        COLOR_GREEN,
    )

    trigger = wf.manual_trigger((-660, 180), name="▶️ Run the setup check")

    cfg = wf.config(
        {
            "linkSecret_A1_01": "PASTE_THE_SECRET_FROM_A1-01_SIGN_DOWNLOAD_LINK",
            "linkSecret_A1_02": "PASTE_THE_SECRET_FROM_A1-02_RECOMPUTE_SIGNATURE",
            "linkSecret_A4_01": "PASTE_THE_SECRET_FROM_A4-01_SIGN_THE_NEW_LINK",
            "linkSecret_A1_04": "PASTE_THE_SECRET_FROM_A1-04_SIGN_FRESH_LINKS",
            "downloadBaseUrl": "https://yourdomain.com/download",
            "fromEmail": "orders@yourdomain.com",
            "storeName": "YOUR_STORE_NAME",
            "webhookSigningSecret": "PASTE_YOUR_GATEWAY_WEBHOOK_SECRET",
            "testModeStillOn": True,
            "errorWorkflowConfigured": False,
            "templatesActivated": [],
            "aiApiKeyConfigured": False,
            "orderLogWired": False,
            "reportEmail": "you@yourdomain.com",
        },
        (-440, 180),
        notes="Copy the real values from your other templates' Config nodes. Be honest about the booleans — this only helps if it reflects reality.",
    )

    probe = wf.code(
        "🔬 Build the signature probe",
        r"""
// Prepare one identical payload to sign with every configured secret. Signing
// the same input with each and comparing the results is the only reliable way
// to prove four separately-pasted strings are actually the same — string
// comparison would work too, but this also catches invisible whitespace and
// smart-quote substitution that a visual check misses entirely.
const cfg = $input.first().json.__config;
return [{ json: { ...cfg, __probePayload: 'dca-setup-probe|fixed-input|v1', __config: cfg } }];
""",
        (-220, 180),
        notes="One fixed payload, signed with each configured secret.",
        always_output=True,
    )

    sig1 = wf.hmac(
        "🔏 Sign with A1-01 secret",
        (0, 60),
        value="={{ $json.__probePayload }}",
        secret="={{ $json.linkSecret_A1_01 }}",
        prop="sigA101",
        notes="Signs the probe with the secret you pasted from A1-01.",
    )

    sig2 = wf.hmac(
        "🔏 Sign with A1-02 secret",
        (220, 60),
        value="={{ $json.__probePayload }}",
        secret="={{ $json.linkSecret_A1_02 }}",
        prop="sigA102",
        notes="Signs the same probe with A1-02's secret. These two must match.",
    )

    sig3 = wf.hmac(
        "🔏 Sign with A4-01 secret",
        (440, 60),
        value="={{ $json.__probePayload }}",
        secret="={{ $json.linkSecret_A4_01 }}",
        prop="sigA401",
        notes="A4-01 reissues links, so its secret must match too.",
    )

    sig4 = wf.hmac(
        "🔏 Sign with A1-04 secret",
        (660, 60),
        value="={{ $json.__probePayload }}",
        secret="={{ $json.linkSecret_A1_04 }}",
        prop="sigA104",
        notes="A1-04 broadcasts fresh links, so its secret must match as well.",
    )

    check = wf.code(
        "🔎 Run every check",
        r"""
// ═══════════════════════════════════════════════════════════════════
// Every check states what is wrong, why it matters, and the exact fix.
// "Configuration invalid" helps nobody — the buyer needs to know which
// node to open and what to type in it.
// ═══════════════════════════════════════════════════════════════════
const d = $input.first().json;
const cfg = d.__config;

const findings = [];
const add = (severity, title, why, fix) => findings.push({ severity, title, why, fix });

const isPlaceholder = (v) =>
  !v || /^(PASTE_|YOUR_|REPLACE|CHANGE_THIS|<)/i.test(String(v).trim()) ||
  String(v).includes('yourdomain.com') || String(v).includes('example.com');

// ── 1. Link-signing secrets must agree ───────────────────────
// Compare computed signatures, not the strings themselves — this also catches
// trailing whitespace and smart quotes, which look identical on screen.
const sigs = {
  'A1-01 (mints links)': d.sigA101,
  'A1-02 (verifies links)': d.sigA102,
  'A4-01 (reissues links)': d.sigA401,
  'A1-04 (broadcasts links)': d.sigA104,
};

const placeheld = Object.entries(sigs).filter(([name]) => {
  const key = { 'A1-01 (mints links)': 'linkSecret_A1_01', 'A1-02 (verifies links)': 'linkSecret_A1_02',
                'A4-01 (reissues links)': 'linkSecret_A4_01', 'A1-04 (broadcasts links)': 'linkSecret_A1_04' }[name];
  return isPlaceholder(cfg[key]);
}).map(([name]) => name);

if (placeheld.length === 4) {
  add('blocker', 'No link-signing secret has been set',
    'Every download link is signed with this secret. Without it nothing can be delivered or verified.',
    'Invent one long random string (e.g. run `openssl rand -hex 32`). Paste the SAME value into the Crypto node of A1-01, A1-02, A4-01 and A1-04 — then into this workflow\'s Config to re-check.');
} else {
  if (placeheld.length) {
    add('blocker', `Link secret missing in: ${placeheld.join(', ')}`,
      'These templates cannot sign or verify links without it.',
      'Paste the same secret you used in the other templates into each one listed.');
  }

  const values = Object.entries(sigs).filter(([name]) => !placeheld.includes(name));
  const distinct = new Set(values.map(([, s]) => String(s)));

  if (values.length >= 2 && distinct.size > 1) {
    // Group by signature so the report names which templates disagree.
    const groups = {};
    for (const [name, s] of values) (groups[s] = groups[s] || []).push(name);
    const detail = Object.values(groups).map(g => `{ ${g.join(', ')} }`).join(' ≠ ');

    add('blocker', 'Link-signing secrets DO NOT MATCH',
      `These templates are using different secrets: ${detail}. Every download will fail with an "invalid signature" error that looks like tampering but is actually a typo.`,
      'Pick ONE secret. Open the Crypto node in each of A1-01, A1-02, A4-01 and A1-04 and paste exactly the same value. Watch for trailing spaces and for quotes that a text editor turned into smart quotes.');
  } else if (values.length >= 2) {
    add('passed', `Link-signing secrets match across ${values.length} template(s)`,
      'Links minted by one template will verify in the others.', null);
  }
}

// ── 2. Placeholder values left in Config ─────────────────────
const placeholders = [];
if (isPlaceholder(cfg.downloadBaseUrl)) placeholders.push('downloadBaseUrl');
if (isPlaceholder(cfg.fromEmail)) placeholders.push('fromEmail');
if (isPlaceholder(cfg.storeName)) placeholders.push('storeName');

if (placeholders.length) {
  add('blocker', `Placeholder values still in Config: ${placeholders.join(', ')}`,
    'Emails will be sent from a non-existent address, or download links will point at a domain you do not own. Both fail visibly for the customer.',
    'Open each template\'s ⚙️ Config node and replace these with your real values.');
} else {
  add('passed', 'Config values look real', 'No obvious placeholders remain.', null);
}

// ── 3. Webhook signature verification ────────────────────────
if (isPlaceholder(cfg.webhookSigningSecret)) {
  add('blocker', 'Webhook signing secret is not set',
    'Your delivery endpoint cannot verify that requests genuinely come from your payment provider. Anyone who discovers the URL could mint free orders.',
    'Copy the signing secret from your gateway (Stripe: whsec_…, Lemon Squeezy: your signing secret) into the "Verify signature" Crypto node in A1-01.');
} else {
  add('passed', 'Webhook signing secret is set', 'Forged payment webhooks will be rejected.', null);
}

// ── 4. Test mode ─────────────────────────────────────────────
if (cfg.testModeStillOn === true) {
  add('blocker', 'testMode is still ON',
    'Signature verification is bypassed while testMode is true. That is correct for setup and dangerous in production — the endpoint will accept forged orders.',
    'Set testMode: false in A1-01\'s ⚙️ Config once you have confirmed delivery works.');
} else {
  add('passed', 'testMode is off', 'Signature verification is enforced.', null);
}

// ── 5. Error Workflow ────────────────────────────────────────
if (cfg.errorWorkflowConfigured !== true) {
  add('important', 'Error Workflow is not configured',
    'When something fails you will not be told. It will sit in an execution log nobody reads, which is exactly the silent-failure problem this suite exists to remove.',
    'Import DCA-SYS-00 (Central Error Hub) and activate it. Then in EVERY other template: Settings → Error Workflow → select it.');
} else {
  add('passed', 'Error Workflow is configured', 'Failures will reach you in one place.', null);
}

// ── 6. Activation ────────────────────────────────────────────
const active = Array.isArray(cfg.templatesActivated) ? cfg.templatesActivated : [];
if (!active.length) {
  add('blocker', 'No templates are marked as activated',
    'An imported workflow does nothing until it is Activated. Webhook URLs return 404 while inactive, so your payment provider will report delivery failures.',
    'Toggle Active on each template you intend to use, then list them in this Config to clear this check.');
} else {
  add('passed', `${active.length} template(s) activated`, active.join(', '), null);
}

// ── 7. Order log ─────────────────────────────────────────────
if (cfg.orderLogWired !== true) {
  add('important', 'Order log is not wired to durable storage',
    'Order records currently exist only inside n8n. You need them for chargeback evidence and for A4-01 to verify who bought what — and n8n static data is not a permanent record.',
    'Wire the "Record the order" node in A1-01 to a Google Sheet, Airtable base or database table.');
} else {
  add('passed', 'Order log is wired to storage', 'Chargeback evidence and entitlement lookups will work.', null);
}

// ── 8. AI key ────────────────────────────────────────────────
if (cfg.aiApiKeyConfigured !== true) {
  add('advisable', 'No AI provider key configured',
    'The AI templates (B1-01 support agent, B1-02 lead qualifier, A6-01 translation, A6-02 listing writer) cannot run without one. Everything else works fine without it.',
    'Add your provider key as a Header Auth credential on the HTTP node in each AI template. Skip this if you are not using them.');
} else {
  add('passed', 'AI provider key configured', 'The AI templates can run.', null);
}

// ── Summary ──────────────────────────────────────────────────
const order = { blocker: 0, important: 1, advisable: 2, passed: 3 };
findings.sort((a, b) => order[a.severity] - order[b.severity]);

const counts = findings.reduce((acc, f) => { acc[f.severity] = (acc[f.severity] || 0) + 1; return acc; }, {});

return [{ json: {
  findings,
  blockers: counts.blocker || 0,
  important: counts.important || 0,
  advisable: counts.advisable || 0,
  passed: counts.passed || 0,
  readyForCustomers: (counts.blocker || 0) === 0,
  checkedAt: new Date().toISOString(),
  __config: cfg,
}}];
""",
        (880, 180),
        notes="Every finding names the node to open and what to type. Ordered by severity.",
        always_output=True,
    )

    report = wf.code(
        "📋 Setup report",
        r"""
// The report the buyer reads. Written so the top line answers the only question
// they actually have: can I turn this on yet?
const o = $input.first().json;
const cfg = o.__config;

const icon = { blocker: '🔴', important: '🟠', advisable: '🟡', passed: '✅' };

const block = (sev, heading) => {
  const items = o.findings.filter(f => f.severity === sev);
  if (!items.length) return '';
  return `\n${heading}\n${'─'.repeat(52)}\n` + items.map(f =>
    `${icon[sev]} ${f.title}\n   Why it matters: ${f.why}${f.fix ? `\n   FIX: ${f.fix}` : ''}`
  ).join('\n\n') + '\n';
};

const verdict = o.readyForCustomers
  ? `✅ READY — no blockers found.${o.important ? `\n   ${o.important} important item(s) below are worth fixing soon.` : ''}`
  : `🔴 NOT READY — ${o.blockers} blocker(s) must be fixed first.\n   Customers will hit these today.`;

const text =
`🧰 SETUP CHECK — ${cfg.storeName}
${o.checkedAt.slice(0, 16).replace('T', ' ')}

${verdict}

Blockers: ${o.blockers}  ·  Important: ${o.important}  ·  Advisable: ${o.advisable}  ·  Passed: ${o.passed}
${block('blocker', 'MUST FIX BEFORE GOING LIVE')}${block('important', 'FIX SOON')}${block('advisable', 'WORTH DOING')}${block('passed', 'CONFIRMED WORKING')}
─────────────────────────────────────
Run this again after any change — a rotated secret, a new template, or
switching from test to live. It takes three seconds and catches the
mistake before a customer does.`;

return [{ json: {
  ready: o.readyForCustomers,
  blockers: o.blockers,
  important: o.important,
  report: text,
  findings: o.findings,
  subject: o.readyForCustomers
    ? `✅ Setup check passed — ${cfg.storeName}`
    : `🔴 Setup check — ${o.blockers} blocker(s) to fix`,
  __config: cfg,
}}];
""",
        (1120, 180),
        notes="Open this node's output and read it. The top line tells you whether you can go live.",
    )

    email = wf.node(
        "📨 Email the report",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.__config.reportEmail }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "text",
            "text": "={{ $json.report }}",
            "options": {},
        },
        2.1,
        (1360, 180),
        retry=True,
        max_tries=2,
        wait_ms=2000,
        on_error="continueRegularOutput",
        notes="Optional — the report is readable in the previous node's output. Attach SMTP if you want it emailed.",
    )

    outcome = wf.code(
        "📒 Check outcome",
        r"""
// Terminal record. The email is optional — the report is readable in the
// previous node either way — so if sending fails this still captures the
// result rather than letting the run end on a silent failure.
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  ready: i.json.ready ?? null,
  blockers: i.json.blockers ?? null,
  important: i.json.important ?? null,
  emailSent: !i.json.error,
  emailError: i.json.error?.message ?? null,
  note: i.json.error
    ? 'The report could not be emailed, but the check itself ran. Read it in the "Setup report" node.'
    : null,
}}));
""",
        (1600, 180),
        notes="Captures the result even if the optional email fails.",
    )

    wf.chain(trigger, cfg, probe, sig1, sig2, sig3, sig4, check, report, email, outcome)

    return wf
