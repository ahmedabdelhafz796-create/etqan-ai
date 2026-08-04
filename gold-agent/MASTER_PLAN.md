# MASTER PLAN — Gold Trading Analysis Agent
### Consolidated final agreement, reconstructed exclusively from the PDF

---

## Context — why this document exists

The PDF is a 13-exchange Arabic conversation between أحمد and Claude titled
*"محادثة: بناء AI Agent للتداول في سوق الذهب"* (August 2026). Its arc:

1. Ahmed asks how to build an AI agent for gold trading.
2. Ahmed attaches four successive documents escalating the ambition — a 12-agent
   multi-mind system; 15 principles for professional automated trading; a market
   philosophy text; a risk register + Sharia controls; then two "prompt-engineering"
   documents trying to make Claude act as *project owner* who never simplifies.
3. Claude repeatedly refuses the parts that are **impossible for an individual at any
   budget** (not merely expensive), and repeatedly points out the loop: by message 12,
   *zero lines of code*.
4. Ahmed finally requests **one output only**: a *Technical Foundation Blueprint* — all
   hard-to-reverse engineering decisions, 19 items, no code — after which planning stops
   completely and Milestone 1 begins.
5. Claude produces it. Two amendments follow (Execution-is-not-deleted clarification;
   Event-Driven oversight → the Operating State Machine). Claude declares the
   architecture final and asks for the 6 Day-One credentials.
6. Ahmed's last message: *"اعملي المحادثة بتاعتنا دي كاملة pdf"* — export the conversation.

**This MASTER PLAN is that Blueprint, consolidated.** Where the PDF stated several
versions of an idea, the latest is taken. Nothing is imported from outside the PDF.

**Provenance marking** — `[PDF]` = stated explicitly in the conversation;
`[Derived]` = composed only from `[PDF]` elements (no new concepts);
`[Open]` = genuinely absent from the PDF, to be settled at implementation.

---

## 1. Final goal `[PDF]`

A **semi-automated system** that collects data, analyses it, and produces a decision
carrying a **confidence percentage and a reason**. Automatic execution is a **later
stage, after feasibility is proven**.

Name: **Gold Trading Analysis Agent** — Claude's closing clarification: this is *"تسمية
وصفية بس، مش تعريف يحصر الوظيفة"* (a descriptive name only, not a definition that
confines the function). The document represents the **final Architecture, not an MVP**.

## 2. Project boundaries — settled refusals `[PDF]`

These survived to the last message and are **not** reopened:

| Excluded | Reason given in the PDF |
|---|---|
| Bloomberg Terminal | $24,000–30,000/yr + institutional documentation |
| CME Order Book Level 2/3 | requires licensed exchange membership |
| Databento / detailed 13F / Dark Pool feeds | institutional subscriptions |
| RL + GNN + Vision model training | huge training data + GPU cluster + months; academic research |
| 12 separate specialised agents | one person, no DevOps team |
| "Zero-error" system | *"مفيش نظام زيرو خطأ"* — even Citadel & Renaissance lose trades |
| Fully autonomous execution with no kill switch / human oversight | no design prevents all scenarios; a stopping point is a **basic part of the design** |

Also standing: Claude is **not a financial advisor**; financial decisions are the user's
responsibility. Claude is **not a Sharia authority**; Sharia rules must come from a
fatwa the user determines.

## 3. Architecture — **Modular Monolith** `[PDF]`

Chosen because the operator is one person without a DevOps team.

| Alternative | Verdict |
|---|---|
| Microservices | **Rejected** — no DevOps team |
| Undivided Monolith | **Rejected** — maintenance difficulty |
| 12 independent agents | **Rejected** — same as microservices |

MCP Servers / Skills: **not applicable** to a standalone script. `[PDF]`

## 4. Modules — final list `[PDF]`

1. **Data Ingestion**
2. **News**
3. **Analysis / Scoring**
4. **Decision**
5. **Risk Gate** — *veto right*
6. **Sharia Gate** — *veto right (Hard Veto)*
7. **Notification**
8. **Execution (Placeholder)** — an official module inside the Architecture from day one
9. **Audit Log**
10. **Backtesting** — later

## 5. The four governing principles `[PDF]`

Distilled by Claude from Ahmed's 15-principle document as what M1 actually implements:

1. **Separate thinking from execution** — alerts only at the start.
2. **Scoring, not a binary decision.**
3. **An explanation attached to every decision.**
4. **Know when not to intervene** — low confidence → `WAIT`.

## 5.1 Operating State Machine `[PDF]` — final architectural amendment

Human oversight is **Event-Driven, not Trade-Driven**: no approval per trade;
intervention only on exceptional events.

| State | Behaviour |
|---|---|
| **Autonomous** | normal operation |
| **Safe Mode** | stop *new* trades — doubtful data, or severe conflict between models |
| **Emergency** | full stop + notification — critical Drawdown, connection loss, or a Bug |
| **Manual Recovery** | full stop until human review; **no automatic exit from Emergency** |

Escalation triggers `[PDF]`: corrupt data · connection interruption · Drawdown beyond a
limit · severe model conflict · abnormal market change · Bug discovery.

**Kill Switch: necessary, 100%.** Execution is designed to be *able* to run
automatically but always inside strict risk limits and **stopped by default** until
consciously activated after real testing.

## 6. Data Flow `[Derived from §4]`

```
Data Ingestion (XAU/USD, DXY, bond yields, VIX)  ┐
                                                 ├─→ Analysis / Scoring ─→ Decision
News (NewsAPI / RSS)                             ┘        (indicators + LLM brain)
                                                                 │
                        Risk Gate (veto) ─→ Sharia Gate (Hard Veto) ─→ Notification
                                                                 │
                                            Execution (Placeholder, OFF) ─→ Audit Log
```

Data sources `[PDF]`: gold price, **DXY**, **bond yields**, **VIX** from cheap/free
providers; news from NewsAPI/RSS. The "infer, don't buy" resolution stands: build an
**Inference Layer** linking dollar · gold · bonds · ETF Flows · VIX into one inference;
infer institutional activity from public data instead of direct access.

Claude's standing caveat `[PDF]`: Options / Smart-Money / Liquidity agents need data
unavailable free at sufficient quality. **Meta Agent** is implementable with simple
logic — *if 3 of 5 indicators agree, allow the trade*.

## 7. Decision Flow `[Derived from §4 + §5]`

```
indicators (RSI, MACD, MA)  ─┐
                             ├─→ weighted Score ─→ LLM brain (Claude API) merges into
news / macro signal         ─┘                      ONE inference: confidence % + reason
                                          │
                       confidence < threshold ─→ WAIT (no alert-to-act)
                                          │
                       Risk Gate    → veto → blocked + logged
                       Sharia Gate  → Hard Veto → blocked + logged (Sharia Audit Log)
                                          │
                            Telegram alert: action + confidence % + reason
                                          │
                                  Audit Log (every decision & verdict)
```

## 8. Sharia controls `[PDF]`

A **Sharia Compliance Agent** holding a **Hard Veto**, verifying:

- the **contract type**
- **no overnight interest (Swap)**
- the **taqābuḍ** (spot possession/settlement) mechanism
- **no financial leverage**
- **no borrowing**
- a **Sharia Audit Log**

Rules are **configurable per the chosen jurisprudential school (المدرسة الفقهية)** —
Claude builds the *Sharia Rule Checker* as a module; the rule content comes from the
user's fatwa. Ships as an editable config file the user fills in.

## 9. Tech Stack `[PDF]`

- **Python 3.11+**
- **pandas-ta** — RSI, MACD, Moving Averages
- **SQLite** (Phase 1) → PostgreSQL later
- **Anthropic API (Sonnet 5)** — the "brain"
- **python-telegram-bot**
- **GitHub Actions**
- Backtesting: **backtrader** or **vectorbt**
- Broker (later): **MT5 Python API** or **OANDA**

## 10. Claude tooling, subscription, model per stage `[PDF]`

| Decision | Choice | Reason from the PDF |
|---|---|---|
| Tool | **Claude Code**, *not* Cowork | dedicated to iterative software projects |
| Subscription | **Pro ($20/mo)** | enough for the build stage; **Max** only if limits actually bind |
| Daily code | **Sonnet 5** | — |
| Complex architectural decisions | **Opus 4.8** | — |
| Billing note | Claude **API** runtime calls are billed **separately** from the Pro subscription | — |

## 11. Accounts / APIs — classified `[PDF]`

**Required from Day One — the "6 elements":**
1. Anthropic API key
2. Claude Pro
3. Twelve Data **or** Alpha Vantage
4. NewsAPI **or** RSS
5. Telegram Bot Token
6. GitHub

**Required Later:** VPS · PostgreSQL · Broker API
**Optional:** —
**Explicitly not needed / unobtainable:** Bloomberg, CME data.
**MCP / Skills:** N/A for a standalone script.

## 12–18. Cross-cutting concerns `[PDF item list; specifics Derived]`

- **Database** — SQLite in Phase 1; records every decision, verdict and trade
  (this doubles as the *Self-Learning* substrate in Phase 3).
- **Logging** — every decision persisted with its reason; separate **Sharia Audit Log**.
- **Monitoring** — **data-health monitoring** and **agent-performance monitoring**
  (both named in Ahmed's 15-principle document and affirmed by Claude); these feed the
  Safe Mode / Emergency transitions.
- **Error Handling** — failures escalate through the State Machine, never silently.
- **Security** — secrets in environment variables, never committed; `.env` git-ignored.
- **Testing** — the system must be runnable and verifiable before any capital is at risk;
  Backtesting replays historical data through the same pipeline.
- **Deployment** — GitHub Actions; VPS is a *Required Later* item, so M1 runs locally.

## 19. Milestone 1 — the only thing built first `[PDF]`

> A script that fetches the **gold price + DXY**, computes **RSI/MACD**, produces a
> **Score**, and sends a **simplified analysis with its reason to Telegram, daily**.

Nothing beyond this ships in M1. Execution stays a disabled placeholder.

---

## Roadmap `[PDF]`

| Phase | Duration | Contents |
|---|---|---|
| **1** | 1–2 weeks | Data Agent (gold + DXY + bond yields + VIX) · News Agent (NewsAPI/RSS) · Strategy Agent (simple RSI, MACD, MA) |
| **2** | ~1 month | Macro Agent · Correlation Agent · **Claude API as the brain** merging sources into one inference |
| **3** | 2+ months | Risk Agent (code rules) · Self-Learning (DB logging every trade) · Backtesting |
| **Activation** | after months of alerts | auto-execution enabled consciously, only after real testing |

**Deferred but affirmed** (Claude called these *"مبادئ حقيقية معمول بيها في الصناعة"*):
permanent memory · learning from mistakes · not relying on the LLM alone · market
simulator · not trading in abnormal conditions · multiple strategies · monitoring
dashboard · the "investment council" idea.

**Risk register** (Ahmed's third document, uncontested by Claude): data · AI
(overconfidence, bias, **Overfitting**) · market · execution · programming · agent ·
capital-management · security · self-learning · operational · legal risks — plus the
core warning that **believing in a 100% success rate is the biggest mistake**. The Risk
Gate and the State Machine are the implementation of the proposed sequential safety gates.

---

## Implementation decisions I am settling myself
*(the PDF instructs: "إذا وجدت قرارًا لم يُحسم، فاحسمه أنت واذكر سبب الاختيار")*

| Decision | Choice | Reason |
|---|---|---|
| Location | new self-contained `gold-agent/` project directory on branch `claude/new-session-4hi0cd` | the PDF names GitHub as Day-One but never names a repo; this is the only repo in session scope, and a subdirectory keeps the agent fully isolated from the unrelated existing app |
| Runs without keys | mock data providers + rule-based fallback brain | the PDF requires testing before capital is at risk; the system must be verifiable before the 6 credentials exist |
| Indicators | implemented natively, `pandas-ta`-compatible API | keeps tests offline and deterministic; PDF names pandas-ta as the stack choice, which this honours |
| Doc language | MASTER_PLAN/BLUEPRINT bilingual AR/EN; Telegram alerts Arabic | the entire source conversation is Arabic; code and identifiers stay English |
| `[Open]` values | score weights, confidence threshold, drawdown %, position size | never specified in the PDF — exposed in `config.yaml` with conservative defaults, not hardcoded |

## Build order

```
gold-agent/
  MASTER_PLAN.md · BLUEPRINT.md · README.md · requirements.txt · .env.example
  config/config.yaml            # weights, thresholds, risk limits, schedule
  config/sharia_rules.yaml      # fatwa-driven, user-editable
  src/gold_agent/
    main.py · config.py · state_machine.py          # §5.1 four states + kill switch
    core/models.py · core/pipeline.py               # §6 data flow, §7 decision flow
    data/       market.py (TwelveData|AlphaVantage|Mock) · news.py (NewsAPI|RSS|Mock)
    analysis/   indicators.py (RSI/MACD/MA) · scoring.py
    brain/      llm_brain.py                        # Claude API → confidence % + reason
    decision/   decision_engine.py                  # WAIT below threshold
    risk/       risk_gate.py                        # veto
    sharia/     sharia_gate.py                      # Hard Veto + Sharia Audit Log
    notification/ telegram.py                       # console fallback
    execution/  placeholder.py                      # OFF by default
    audit/      db.py (SQLite)
    monitoring/ health.py                           # data health + agent performance
    backtesting/ backtester.py                      # Phase 3 stub, same pipeline
  scripts/run_once.py · scripts/run_backtest.py
  tests/                                            # pytest, offline
```

1. Write `MASTER_PLAN.md` + `BLUEPRINT.md` (the 19 items + §5.1).
2. Scaffold config, models, state machine, audit DB.
3. Data + News modules with mock providers.
4. Indicators → Scoring → LLM brain (with rule-based fallback) → Decision.
5. Risk Gate, Sharia Gate, Notification, Execution placeholder.
6. Tests + monitoring; wire `run_once.py` end to end.
7. Commit and push to `claude/new-session-4hi0cd`.

## Verification

- `python -m pytest` — unit + end-to-end mock tests pass **offline, with no keys**.
- `python scripts/run_once.py` with no credentials — full cycle on mock data prints
  action + confidence % + reason to console and writes an audit row.
- Confirm `WAIT` is emitted when confidence is below threshold.
- Force a Risk Gate veto and a Sharia Gate Hard Veto; confirm both block and log.
- Drive the State Machine through Autonomous → Safe → Emergency → Manual Recovery and
  confirm **no automatic exit from Emergency**.
- Confirm Execution placeholder refuses to act while disabled.
- With the 6 Day-One credentials present — live data + real Telegram alert.
