"""
DCA-B5-01 · CV Screening & Candidate Triage

Recruitment is classified as a premium, high-value automation category, and this
is the task inside it that is both most painful and most automatable: a job ad
attracts two hundred applications and somebody has to read them.

Why this template is written more carefully than the others
------------------------------------------------------------
Automated CV screening decides who gets considered for work. Get it wrong and
the cost is not a lost sale — it is a person filtered out of a job for a reason
that was never valid. That asymmetry drives every design decision here:

  * **It ranks, it does not reject.** No candidate is ever auto-rejected. Every
    application reaches a reviewable list; the template only decides what order
    a human reads them in.
  * **It scores against stated requirements only.** The recruiter writes the
    must-haves and nice-to-haves. The model is instructed to judge those and
    explicitly told to ignore names, photos, age, gender, nationality, marital
    status and personal details — the fields that carry bias and are irrelevant
    to whether someone can do the job.
  * **Every score carries its reasoning**, so a reviewer can see the basis for a
    ranking and overrule it. An unexplained ranking cannot be audited, and an
    unauditable hiring tool should not exist.
  * **A model failure ranks a candidate for manual review**, never removes them.

The honest limitation is on the canvas: this reduces reading time, it does not
make hiring decisions, and a human must read the shortlist.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "cv-screening-triage"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-B5-01 · CV Screening & Candidate Triage (ranks, never rejects)",
        slug=SLUG,
        category="b5-recruitment",
        summary="Reads every application against the requirements you wrote, ranks candidates with stated reasoning for each score, and produces a reviewable shortlist — without ever auto-rejecting anyone.",
        problem="A job ad brings two hundred applications and someone has to read them all, so the good candidates wait days and some are never reached at all.",
        outcome="Every application scored against your stated requirements with visible reasoning, ordered so the strongest are read first — and nobody filtered out by a machine.",
        version="1.0.0",
        tags=["ai-agent", "recruitment", "hiring", "screening", "hardened"],
        credentials_needed=[
            "An AI provider API key (Anthropic, OpenAI, or compatible)",
            "SMTP account for the shortlist digest",
        ],
        setup_minutes=18,
    )

    wf.sticky(
        "## 👥 CV Screening & Candidate Triage\n"
        "**Every application read → scored against YOUR requirements → ranked.**\n\n"
        "### Setup (about 18 minutes)\n"
        "1. **⚙️ Config** → write `roleTitle`, `mustHaves`, `niceToHaves`.\n"
        "   Be specific — vague requirements produce vague scoring.\n"
        "2. Set `aiEndpoint`/`aiModel`, add your API key as **Header Auth** on\n"
        "   **🧠 Assess the application**.\n"
        "3. POST each application:\n"
        "   ```json\n"
        "   { \"candidateId\": \"...\", \"name\": \"...\",\n"
        "     \"email\": \"...\", \"cvText\": \"...\" }\n"
        "   ```\n"
        "4. The digest arrives with the shortlist ranked.\n\n"
        "⚠️ **You must still read the shortlist.** This reduces reading time; it\n"
        "does not make hiring decisions.",
        (-700, -560),
        (600, 560),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🚫 It ranks. It NEVER rejects.\n"
        "No candidate is ever auto-rejected, and there is no setting to enable it.\n\n"
        "**Why this is not negotiable:** a wrong score here is not a lost sale, it\n"
        "is a person filtered out of a job for a reason that was never valid.\n\n"
        "Every application reaches a reviewable list. The template only decides\n"
        "what **order** you read them in.",
        (-80, -560),
        (480, 360),
        COLOR_RED,
    )

    wf.sticky(
        "### ⚖️ What the model is told to ignore\n"
        "Names · photos · age · gender · nationality · marital status · address ·\n"
        "personal interests.\n\n"
        "These carry bias and say nothing about whether someone can do the job.\n\n"
        "The model scores **only** against the must-haves and nice-to-haves you\n"
        "wrote — and every score comes back with the reasoning, so you can see the\n"
        "basis and overrule it.\n\n"
        "**An unexplained ranking cannot be audited.**",
        (420, -560),
        (500, 380),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🛟 When the model fails\n"
        "An unreadable response ranks the candidate for **manual review** — it\n"
        "never removes them and never scores them zero.\n\n"
        "A candidate must not lose their chance because an API had a bad minute.",
        (1140, 400),
        (440, 280),
        COLOR_GREEN,
    )

    hook = wf.webhook(
        "📄 Application received",
        (-700, 200),
        path="dca/application",
        notes="POST {candidateId, name, email, cvText}. Wire your form or ATS here.",
    )

    cfg = wf.config(
        {
            "roleTitle": "REPLACE: the job title",
            "mustHaves": [
                "REPLACE: a specific, checkable requirement",
                "REPLACE: another one",
            ],
            "niceToHaves": ["REPLACE: something that helps but is not essential"],
            "yearsExperienceExpected": 3,
            "aiEndpoint": "https://api.anthropic.com/v1/messages",
            "aiModel": "claude-sonnet-5",
            "maxTokens": 800,
            "shortlistSize": 20,
            "reviewerEmail": "you@yourdomain.com",
            "fromEmail": "hiring@yourdomain.com",
            "companyName": "YOUR_COMPANY",
            "historyTtlDays": 90,
        },
        (-480, 200),
        notes="mustHaves drive everything. Write requirements a person could check objectively, not aspirations.",
    )

    guard = wf.guard(
        (-260, 200),
        required=["body"],
        event_id_expr="(j.body?.candidateId ?? j.body?.email ?? '') + '|' + String(j.body?.cvText ?? '').slice(0, 40)",
        ttl_hours=168,
    )

    prepare = wf.code(
        "📥 Prepare the application",
        r"""
// Deliberately minimal. Unlike the fraud and lead templates there is no
// deterministic pre-scoring here, because the cheap signals available in a CV —
// name, address, school — are exactly the ones that carry bias and say nothing
// about competence. Keyword matching on a CV rewards people who know to repeat
// the job ad's wording, which is a writing skill, not a job skill.
//
// So the only pre-processing is hygiene.
const cfg = $('⚙️ Config').first().json.__config;

return $input.all().map(item => {
  const b = item.json.body ?? item.json;

  const cvText = String(b.cvText ?? b.cv ?? b.resume ?? b.text ?? '').trim();
  const email = String(b.email ?? '').trim().toLowerCase();
  const candidateId = String(b.candidateId ?? b.candidate_id ?? email ?? '').trim();

  if (!cvText || !candidateId) {
    throw new Error('An application needs candidateId (or email) and cvText. Received keys: ' + Object.keys(b).join(', '));
  }

  // Very short submissions are flagged, not discarded — a link-only application
  // is a process problem to fix, not a candidate to drop.
  const tooShort = cvText.length < 200;

  return { json: {
    candidateId,
    name: String(b.name ?? '').trim(),
    email,
    cvText: cvText.slice(0, 12000),
    appliedFor: String(b.role ?? cfg.roleTitle).trim(),
    receivedAt: new Date().toISOString(),
    tooShort,
    __config: cfg,
  }};
});
""",
        (-40, 200),
        notes="No keyword pre-scoring — it rewards CV-writing skill, not job skill, and carries bias.",
    )

    assess = wf.http(
        "🧠 Assess the application",
        (200, 200),
        url="={{ $json.__config.aiEndpoint }}",
        method="POST",
        headers={"content-type": "application/json", "anthropic-version": "2023-06-01"},
        json_body=(
            "={{ JSON.stringify({\n"
            "  model: $json.__config.aiModel,\n"
            "  max_tokens: $json.__config.maxTokens,\n"
            "  system: 'You assess job applications for ' + $json.__config.companyName + '.\\n\\n'\n"
            "    + 'ROLE: ' + $json.__config.roleTitle + '\\n'\n"
            "    + 'MUST HAVE:\\n' + ($json.__config.mustHaves || []).map(m => '  - ' + m).join('\\n') + '\\n'\n"
            "    + 'NICE TO HAVE:\\n' + ($json.__config.niceToHaves || []).map(m => '  - ' + m).join('\\n') + '\\n\\n'\n"
            "    + 'RULES YOU MUST FOLLOW:\\n'\n"
            "    + '1. Judge ONLY against the requirements above. Ignore the candidate\\'s name, age, gender, '\n"
            "    + 'nationality, marital status, address, photo and personal interests entirely. These carry bias '\n"
            "    + 'and are irrelevant to whether someone can do this job.\\n'\n"
            "    + '2. You are RANKING, not rejecting. Nobody is removed on your assessment. Score fairly.\\n'\n"
            "    + '3. State your reasoning for every score. An unexplained ranking cannot be reviewed.\\n'\n"
            "    + '4. If the CV does not mention a requirement, say it is not evidenced — do not assume it is '\n"
            "    + 'absent, and do not assume it is present.\\n'\n"
            "    + '5. Note anything a reviewer should ask about rather than guessing at it yourself.\\n\\n'\n"
            "    + 'Reply with STRICT JSON only, no markdown fence:\\n'\n"
            "    + '{\"score\": <0..100>, \"mustHavesMet\": [\"<which ones, with evidence>\"], '\n"
            "    + '\"mustHavesMissing\": [\"<which ones are not evidenced>\"], '\n"
            "    + '\"strengths\": \"<one or two sentences>\", \"questionsForInterview\": [\"<what to ask>\"], '\n"
            "    + '\"reasoning\": \"<why this score>\"}',\n"
            "  messages: [ { role: 'user', content: 'APPLICATION:\\n\\n' + $json.cvText } ]\n"
            "}) }}"
        ),
        notes="Add your API key as a Header Auth credential. The prompt forbids scoring on personal characteristics.",
    )

    parse = wf.code(
        "📊 Record the assessment",
        r"""
// Store the assessment. A model failure produces a "needs manual review" entry
// rather than a low score, because a candidate must not lose their chance
// because an API had a bad minute.
const cfg = $('⚙️ Config').first().json.__config;
const src = $('📥 Prepare the application').all();
const store = $getWorkflowStaticData('global');
store.candidates = store.candidates || {};

const now = Date.now();
const ttlMs = Number(cfg.historyTtlDays) * 24 * 60 * 60 * 1000;
for (const [k, c] of Object.entries(store.candidates)) {
  if (now - (c.at || 0) > ttlMs) delete store.candidates[k];
}

function extract(p) {
  return p?.content?.[0]?.text ?? p?.choices?.[0]?.message?.content ?? '';
}

return $input.all().map((item, idx) => {
  const o = src[idx]?.json ?? src[0].json;
  const raw = String(extract(item.json) || '').trim();

  let a = null;
  try {
    a = JSON.parse(raw.replace(/^```(?:json)?/i, '').replace(/```$/, '').trim());
  } catch {
    const m = raw.match(/\{[\s\S]*\}/);
    if (m) { try { a = JSON.parse(m[0]); } catch { /* fall through */ } }
  }

  const scored = a && Number.isFinite(Number(a.score));

  const record = {
    candidateId: o.candidateId,
    name: o.name,
    email: o.email,
    at: now,
    // A failed assessment is explicitly NOT a zero — it is an unknown, and it
    // sorts into the review queue rather than the bottom of the ranking.
    score: scored ? Math.max(0, Math.min(100, Number(a.score))) : null,
    needsManualReview: !scored || o.tooShort,
    reviewReason: !scored
      ? 'the assessment could not be read — this candidate has NOT been scored and needs a human'
      : (o.tooShort ? 'the application was very short — possibly a link-only submission' : null),
    mustHavesMet: scored ? (a.mustHavesMet || []) : [],
    mustHavesMissing: scored ? (a.mustHavesMissing || []) : [],
    strengths: scored ? String(a.strengths || '').trim() : '',
    questions: scored ? (a.questionsForInterview || []) : [],
    reasoning: scored ? String(a.reasoning || '').trim() : '',
  };

  store.candidates[o.candidateId] = record;

  return { json: { ...record, __config: cfg } };
});
""",
        (440, 200),
        notes="A failed assessment is an unknown, never a zero — it routes to manual review.",
    )

    ack = wf.respond(
        "↩️ 200 OK",
        (680, 200),
        body='={{ JSON.stringify({ ok: true, received: true }) }}',
    )

    # ── Shortlist digest ────────────────────────────────────────────────
    sched = wf.schedule("🕕 Daily shortlist", (-700, 620), hours=24)

    cfg2 = wf.code(
        "⚙️ Config (digest side)",
        r"""
// Mirror of the main Config — n8n cannot share a node across trigger branches.
const CONFIG = {
  "roleTitle": "REPLACE: the job title",
  "shortlistSize": 20,
  "reviewerEmail": "you@yourdomain.com",
  "fromEmail": "hiring@yourdomain.com",
  "companyName": "YOUR_COMPANY"
};
return [{ json: { __config: CONFIG } }];
""",
        (-480, 620),
        notes="⚠️ Mirror of the main Config. Change one, change both.",
        always_output=True,
    )

    rank = wf.code(
        "🏅 Build the shortlist",
        r"""
// Rank the scored candidates and surface the unscored ones separately. The
// review queue is listed FIRST, because those are the applications a machine
// could not read — and they are the ones most at risk of being quietly lost.
const cfg = $input.first().json.__config;
const store = $getWorkflowStaticData('global');
const all = Object.values(store.candidates || {});

const needsReview = all.filter(c => c.needsManualReview);
const scored = all.filter(c => !c.needsManualReview && c.score !== null)
                  .sort((a, b) => b.score - a.score);

return [{ json: {
  total: all.length,
  needsReview,
  shortlist: scored.slice(0, Number(cfg.shortlistSize)),
  remainder: Math.max(0, scored.length - Number(cfg.shortlistSize)),
  hasCandidates: all.length > 0,
  __config: cfg,
}}];
""",
        (-260, 620),
        notes="Unscored candidates are listed first — they are the ones most at risk of being lost.",
        always_output=True,
    )

    has_candidates = wf.if_(
        "📋 Any applications?",
        (-20, 620),
        left="={{ $json.hasCandidates }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    digest = wf.code(
        "✍️ Write the shortlist digest",
        r"""
const o = $input.first().json;
const cfg = o.__config;

const reviewBlock = o.needsReview.length
  ? `\n⚠️ NEEDS A HUMAN — NOT SCORED (${o.needsReview.length})\n${'─'.repeat(52)}\n` +
    o.needsReview.map(c =>
      `  ${c.name || c.candidateId} <${c.email || 'no email'}>\n   ${c.reviewReason}`
    ).join('\n\n') +
    `\n\n   These were NOT assessed. Read them yourself — do not skip them.\n`
  : '';

const listBlock = o.shortlist.length
  ? `\n🏅 RANKED (${o.shortlist.length}${o.remainder ? ` of ${o.shortlist.length + o.remainder}` : ''})\n${'─'.repeat(52)}\n` +
    o.shortlist.map((c, i) =>
`  ${i + 1}. ${c.name || c.candidateId}  —  ${c.score}/100
     <${c.email || 'no email'}>
     ${c.reasoning}
${c.mustHavesMet.length ? `     ✓ Evidenced: ${c.mustHavesMet.join('; ')}\n` : ''}${c.mustHavesMissing.length ? `     ? Not evidenced: ${c.mustHavesMissing.join('; ')}\n` : ''}${c.questions.length ? `     Ask: ${c.questions.join(' · ')}` : ''}`
    ).join('\n\n')
  : '';

const text =
`👥 Shortlist — ${cfg.roleTitle} at ${cfg.companyName}
${new Date().toISOString().slice(0, 10)}

${o.total} application(s) received.
${reviewBlock}${listBlock}
${o.remainder ? `\n   …and ${o.remainder} more below the shortlist cut.\n` : ''}
─────────────────────────────────────
⚠️ Nobody has been rejected. This is a reading order, not a decision.
Scores reflect only the requirements you wrote. If a ranking looks wrong,
it probably means the requirements need rewording — the reasoning above
shows you exactly what was judged.`;

return [{ json: { ...o, digestText: text,
  subject: `👥 ${o.total} application(s) for ${cfg.roleTitle}${o.needsReview.length ? ` (${o.needsReview.length} need a human)` : ''}` }}];
""",
        (220, 540),
        notes="States plainly that nobody was rejected and that a wrong ranking usually means the requirements need rewording.",
    )

    send = wf.node(
        "📨 Send the shortlist",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.__config.reviewerEmail }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "text",
            "text": "={{ $json.digestText }}",
            "options": {},
        },
        2.1,
        (460, 540),
        retry=True,
        max_tries=3,
        wait_ms=2000,
        on_error="continueRegularOutput",
        notes="Goes to the reviewer. Nothing is ever sent to candidates by this template.",
    )

    none = wf.code(
        "🤫 No applications yet",
        r"""
return [{ json: { checkedAt: new Date().toISOString(), total: 0,
                  note: 'No applications received.' }}];
""",
        (220, 720),
        notes="Logged so an empty day is distinguishable from a stopped schedule.",
    )

    fail = wf.error_sink((440, 380), context="cv-screening")

    log = wf.code(
        "📒 Screening log",
        r"""
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  total: i.json.total ?? null,
  shortlisted: (i.json.shortlist ?? []).length,
  needsReview: (i.json.needsReview ?? []).length,
}}));
""",
        (700, 620),
        notes="Track how many needed manual review — a high number means the intake format needs fixing.",
    )

    wf.chain(hook, cfg, guard, prepare, assess)
    wf.connect(assess, parse, out=0)
    wf.connect(assess, fail, out=1)
    wf.connect(parse, ack)
    wf.connect(fail, ack)

    wf.chain(sched, cfg2, rank, has_candidates)
    wf.connect(has_candidates, digest, out=0)
    wf.connect(has_candidates, none, out=1)
    wf.connect(digest, send)
    wf.connect(send, log)
    wf.connect(none, log)

    return wf
