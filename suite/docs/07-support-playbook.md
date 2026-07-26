# دليل الدعم — ردود جاهزة للنسخ واللصق

> إنت قلت: **"أنا مش هعرف أركبه أو أشغله"**. الملف ده هو الحل.
>
> كل سؤال هيجيلك، وتحته الرد **جاهز تنسخه وتبعته**. مش محتاج تفهم n8n.

---

## قبل أي حاجة — القاعدة الذهبية

**90% من مشاكل العملاء بيحلها سؤال واحد:**

> "من فضلك شغّل قالب **Setup Checker** وابعتلي صورة من نتيجته."

القالب ده بيفحص التركيب ويقول بالظبط إيه الناقص وإزاي يتصلح. في أغلب الحالات
العميل هيقرا النتيجة ويحل المشكلة بنفسه قبل ما يرد عليك.

**اجعل ده أول رد دايماً.**

---

## 🔴 المجموعة الأولى: مشاكل التركيب (الأكثر شيوعاً)

### 1. "القالب مش راضي يتستورد"

```
Thanks for flagging this.

Please check two things:

1. Which n8n version are you on? (bottom-left of the sidebar).
   These templates need 1.40 or newer.

2. Are you importing the .json file directly, or pasting its contents?
   Use Workflows → Import from File and select the .json file itself.

If it still fails, send me a screenshot of the error and I'll sort it out.
```

---

### 2. "التحميل مش شغال / invalid signature"

**دي أشهر مشكلة على الإطلاق. السبب دايماً واحد.**

```
This is almost always the same cause, and it's quick to fix.

Four workflows share ONE link-signing secret:
  - Instant Digital Delivery       (creates links)
  - Secure Download Endpoint       (checks links)
  - Download Problem Self-Service  (re-issues links)
  - Product Update Broadcast       (sends fresh links)

If any two of them have a different value, every download fails with
exactly this error.

Please open the Crypto node in each one you've installed and confirm the
secret is character-for-character identical. Two things to watch for:

  - A trailing space at the end (invisible on screen)
  - Quotes your text editor may have converted to curly quotes

Fastest way to confirm: run the Setup Checker workflow. It signs a test
value with each secret and tells you immediately if any disagree.
```

---

### 3. "الإيميل مش بيتبعت"

```
Let's narrow it down. Two things cause this almost every time:

1. PORT AND SSL MUST AGREE
   Port 587 → SSL/TLS must be OFF
   Port 465 → SSL/TLS must be ON
   A mismatch gives "wrong version number" in the error.

2. THE PASSWORD ISN'T YOUR ACCOUNT PASSWORD
   It's the SMTP key from your email provider. In Brevo:
   Settings → SMTP & API → SMTP tab → Generate a new SMTP key.

In n8n: Credentials → your SMTP credential → Save. It tests the
connection and shows a green tick if it's right.

If it's green and mail still doesn't arrive, check your spam folder and
your provider's sending log — the message may be going out and being
filtered.
```

---

### 4. "الويبهوك بيرجّع 404"

```
A 404 means the workflow isn't Activated.

In n8n, an imported workflow does nothing until you switch it on:
open it and toggle "Active" in the top-right.

One more thing to check: n8n gives every webhook TWO urls.

  - Test URL       — only works while you have the editor open
  - Production URL — works always, but only when the workflow is Active

Make sure you gave your payment provider the Production URL.
```

---

### 5. "غيّرت الإعدادات ولسه مش شغال"

```
Two possibilities:

1. Did you Save after editing? n8n keeps unsaved changes in the editor
   only — an active workflow keeps running the last SAVED version.

2. If the workflow was already Active, toggle it off and on again after
   saving. That forces it to reload.

Then run the Setup Checker to confirm everything reads as expected.
```

---

## 🟠 المجموعة الثانية: أسئلة السلوك

### 6. "العميل دفع ومستلمش المنتج"

```
Let's find out where it stopped. Open the delivery workflow and click
the "Executions" tab — that shows every run and where it ended.

Look for the most recent execution and tell me which node is red, or
whether there's no execution at all.

  No execution at all      → the webhook never arrived. Check the URL
                             in your payment provider's settings, and
                             that the workflow is Active.
  Stopped at "Verify sig"  → the signing secret doesn't match your
                             gateway's.
  Stopped at "Is the money
  really in?"              → the payment wasn't confirmed yet. Crypto
                             payments often arrive here first and pass
                             on the follow-up webhook. This is correct
                             behaviour, not a bug.
  Stopped at "Send"        → email problem. See the SMTP answer above.

Send me a screenshot of the Executions tab and I'll tell you exactly
which it is.
```

---

### 7. "وصل للعميل إيميلين بدل واحد"

```
That shouldn't happen — the template de-duplicates on the gateway's own
event id, and it's tested specifically for this.

Two things worth checking:

1. Do you have the SAME workflow imported twice? Two active copies both
   listening to the same webhook will each send.

2. Did you point two different gateway events at the same URL? For
   example both "checkout.completed" and "payment.succeeded" — those
   arrive as separate events with separate ids, so both deliver.

If neither of those, send me the two email timestamps and the order id
and I'll look into it properly.
```

---

### 8. "قالب الاحتيال بيرفض عملاء حقيقيين"

```
That's what shadow mode is for, and it's on by default for exactly this
reason.

While shadowMode is true the template scores every order and reports
what it WOULD have done, but allows everything through. Nothing is
blocked.

Run it that way for a week, then look at the orders it flagged. If real
customers are scoring high, raise "reviewAt" rather than lowering
"blockAt" — that widens the review queue instead of blocking more.

You can also add specific customers to "trustedEmails" in Config, and
whole domains to "trustedDomains". Those bypass scoring entirely.

Every score comes with the reasons that produced it, so you can see
exactly which signal is misfiring.
```

---

### 9. "الـ AI بيرفض يرد على أسئلة كتير"

```
That's deliberate, and it's usually telling you something useful.

The agent answers only from the knowledge base you gave it. If it's
escalating a lot, it means those questions aren't covered by what's in
"knowledgeBase" — and the escalation reasons tell you exactly which
gaps.

The fix is to add those topics to knowledgeBase in Config. Refunds,
delivery times, file formats and "does it work with X" are the usual
missing ones.

I'd rather it escalate than invent a refund policy you'd then be held
to — a confidently wrong answer costs more than a slow one.

Note that some categories ALWAYS escalate regardless of confidence:
refunds, billing disputes, legal requests, and angry messages. That's
not tunable, on purpose.
```

---

### 10. "استخدمت الـ AI وجالي فاتورة كبيرة"

```
The AI templates use your own API key, so you're billed directly by the
provider — I don't see or control that.

A few ways to bring it down:

1. Switch to a smaller model in Config (aiModel). For support triage and
   lead scoring a smaller model is usually fine.

2. Lower maxTokens. The default is generous.

3. For translation specifically: make sure skipUnchanged is true. It
   hashes your source text and skips anything that hasn't changed, so
   re-running a catalogue costs almost nothing.

4. Check whether you're accidentally sending the same content
   repeatedly — the Executions tab will show you.

Also worth knowing: the support agent and lead qualifier both run
deterministic checks BEFORE calling the model, so obvious spam and
sensitive requests never cost you an API call.
```

---

## 🟡 المجموعة الثالثة: أسئلة قبل الشراء

### 11. "هل ده شغال مع [منصة]؟"

```
The delivery template handles Stripe, PayPal, Lemon Squeezy, Gumroad,
Paddle and NOWPayments out of the box — it normalises all six into one
internal format.

If your platform can send a webhook when a payment completes, it will
almost certainly work; you may just need to set "provider" in Config
rather than leaving it on auto.

Tell me which platform and I'll confirm before you buy.
```

---

### 12. "أنا مش تقني — هقدر أركبه؟"

```
Yes, and it's designed around that.

Each template has ONE node you edit — it's called ⚙️ Config and it's
the first thing in the flow. Everything else is documented on the canvas
right next to the thing it explains, so you're never guessing what a
node is for.

Most take 10-15 minutes. There's an install guide with the exact order
to do things in, and a Setup Checker workflow that tells you if you've
missed anything before you go live.

If you get stuck, send me the Setup Checker's output and I'll tell you
what to change.
```

---

### 13. "إيه اللي بيفرقكم عن القوالب المجانية؟"

```
Fair question — there are thousands of free n8n workflows.

The difference is what happens when things go wrong, which is where most
templates fall over:

  - Payment gateways retry webhooks. Without de-duplication, one purchase
    delivers twice. These handle that.
  - APIs fail temporarily. Every outbound call here retries with backoff.
  - When something does fail, you get told — with a plain-language
    explanation of what broke and what to do. Most templates fail
    silently into a log nobody reads.
  - No credentials are embedded anywhere. That's checked automatically
    before release.

These are also tested behaviourally — 151 tests that actually run the
workflows and verify things like "a replayed webhook does not deliver
twice" and "an unpaid order delivers nothing". I'm happy to send you
the test output.

Try the free one first. It's the same standard as the paid ones.
```

---

### 14. "فيه استرداد؟"

```
Yes — if it doesn't work for you, tell me within 14 days and I'll refund
it, no argument.

I'd rather refund you than have you stuck with something that doesn't
fit. And if you tell me what went wrong, that usually helps me fix it
for the next person.
```

---

### 15. "ينفع أبيعه لعملائي؟"

```
You can use these in client work you're paid for — set them up for
clients, charge whatever you like for that.

What you can't do is resell or redistribute the workflow files
themselves, or include them in a template pack you sell.

Full terms are in LICENCE.txt in your download.
```

---

## 🆘 لما متعرفش الإجابة

**متخترعش رد.** ده الرد المحترف اللي بيحل الموقف:

```
Good question — I want to give you an accurate answer rather than a
guess, so let me check properly and come back to you today.

In the meantime, could you send me:
  - your n8n version (bottom-left of the sidebar)
  - the name of the node that's failing
  - the error text from the Executions tab

That usually contains the answer.
```

بعدين ابعتلي التفاصيل دي وأنا أديك الرد الصح.

---

## ⚠️ حاجات متقولهاش أبداً

| ❌ متقولش | ✅ قول |
| --- | --- |
| "مستحيل يحصل ده" | "خليني أشوف الحصل بالظبط" |
| "غلطتك إنت" | "خلينا نشوف وقف فين" |
| "القالب مثالي" | "دي حدوده، وده اللي بيعمله" |
| تخترع سبب تقني | "هتأكد وأرد عليك النهاردة" |
| تتجاهل رسالة | ترد حتى لو "بشوفها وأرد" |

**الرد السريع الصادق بيبني سمعة أسرع من الرد المثالي المتأخر.**

---

## 📌 جهّز دول قبل أول بيعة

- [ ] إيميل دعم مخصص (مش إيميلك الشخصي)
- [ ] الملف ده مفتوح في تاب جنبك
- [ ] جرّبت `Setup Checker` بنفسك مرة عشان تعرف شكل نتيجته
- [ ] عارف تجيب لقطة شاشة من تاب `Executions` (ده اللي هتطلبه من العملاء أكتر حاجة)
