/**
 * engine.mjs — a minimal n8n execution engine for testing templates.
 *
 * Why this exists
 * ---------------
 * The structural validator proves a workflow is well-formed: wired correctly,
 * secret-free, retry policies in place. It cannot prove the workflow *does the
 * right thing*. A template can be perfectly well-formed and still deliver a
 * product to a buyer whose payment is still pending, or hand a file to someone
 * whose signature does not verify.
 *
 * Those are the bugs that reach customers, so they need to be caught by
 * execution, not inspection. This engine walks the real workflow.json, runs the
 * real Code-node JavaScript, computes real HMACs, and evaluates real branch
 * conditions — so the tests exercise the file we actually ship rather than a
 * paraphrase of it.
 *
 * Scope and honesty
 * -----------------
 * This is not n8n. It implements the node types and the expression subset this
 * suite uses. It deliberately does NOT talk to any network: HTTP and email nodes
 * are recorded as intents so tests can assert "an email would have been sent to
 * X" without sending one. It cannot validate that a real Stripe key works —
 * only a real account can do that. What it does prove is that the *logic* is
 * right, which is where the customer-facing bugs actually live.
 */

import vm from 'node:vm';
import crypto from 'node:crypto';

const STICKY = 'n8n-nodes-base.stickyNote';

/** Resolve an n8n `={{ … }}` expression against the current item and node outputs. */
function evaluateExpression(expr, ctx) {
  if (typeof expr !== 'string' || !expr.startsWith('=')) return expr;
  const body = expr.slice(1);

  // A whole-string expression returns its native value; anything else is
  // interpolated into a string, which is how n8n behaves.
  const whole = body.match(/^\{\{([\s\S]*)\}\}$/);
  if (whole) return runJs(whole[1], ctx);

  return body.replace(/\{\{([\s\S]*?)\}\}/g, (_, code) => {
    const v = runJs(code, ctx);
    return v === undefined || v === null ? '' : String(v);
  });
}

function runJs(code, ctx) {
  try {
    return vm.runInNewContext(`(${code})`, buildSandbox(ctx), { timeout: 5000 });
  } catch {
    // Fall back to statement form for anything that is not an expression.
    try {
      return vm.runInNewContext(code, buildSandbox(ctx), { timeout: 5000 });
    } catch (e) {
      throw new Error(`expression failed: ${code.trim().slice(0, 120)} — ${e.message}`);
    }
  }
}

function buildSandbox(ctx) {
  const { item, items, outputs, staticData } = ctx;
  const nodeAccessor = (name) => {
    const rows = outputs[name];
    if (!rows) throw new Error(`$('${name}') referenced before it produced output`);
    return {
      first: () => rows[0],
      last: () => rows[rows.length - 1],
      all: () => rows,
      item: rows[0],
    };
  };
  return {
    $json: item?.json ?? {},
    $binary: item?.binary ?? {},
    $input: {
      all: () => items ?? [],
      first: () => (items ?? [])[0],
      last: () => (items ?? [])[(items?.length ?? 1) - 1],
    },
    $: nodeAccessor,
    $getWorkflowStaticData: () => staticData,
    $now: new Date(),
    JSON, Date, Math, Number, String, Boolean, Array, Object, RegExp, Error,
    URLSearchParams, Set, Map, isNaN, isFinite, parseInt, parseFloat,
    console: { log: () => {}, error: () => {}, warn: () => {} },
  };
}

function compareValues(left, right, op) {
  const { type, operation } = op;
  if (type === 'boolean') {
    // n8n's loose type validation coerces, so undefined/null/'' read as false.
    // Matching that here matters: getting it wrong sent every item down the
    // wrong branch and made two templates look broken when they were not.
    const truthy = left === true || left === 'true';
    const falsy = left === false || left === 'false' ||
                  left === undefined || left === null || left === '';
    if (operation === 'true') return truthy;
    if (operation === 'false') return falsy;
  }
  const l = type === 'number' ? Number(left) : left;
  const r = type === 'number' ? Number(right) : right;
  switch (operation) {
    case 'equals': return String(l) === String(r);
    case 'notEquals': return String(l) !== String(r);
    case 'contains': return String(l).includes(String(r));
    case 'gt': return Number(l) > Number(r);
    case 'gte': return Number(l) >= Number(r);
    case 'lt': return Number(l) < Number(r);
    case 'lte': return Number(l) <= Number(r);
    case 'exists': return l !== undefined && l !== null && l !== '';
    case 'notEmpty': return l !== undefined && l !== null && l !== '';
    default: return false;
  }
}

function evalConditionGroup(group, ctx) {
  const conds = group?.conditions ?? [];
  const results = conds.map((c) => {
    const left = evaluateExpression(c.leftValue, ctx);
    const right = evaluateExpression(c.rightValue, ctx);
    return compareValues(left, right, c.operator);
  });
  if (!results.length) return false;
  return group.combinator === 'or' ? results.some(Boolean) : results.every(Boolean);
}

/**
 * Execute a workflow.
 *
 * @param {object} workflow   parsed workflow.json
 * @param {object} opts
 * @param {object} opts.trigger        payload injected at the trigger node
 * @param {object} opts.secrets        { "Node Name": "secret" } for Crypto nodes
 * @param {object} opts.staticData     seed static data (carry between runs to test dedupe)
 * @param {object} opts.configOverride shallow-merged over the Config node's values
 * @param {string} opts.from           name (or substring) of the trigger to start
 *                                     from. Required for templates with more
 *                                     than one entry point — several here pair
 *                                     a webhook that captures events with a
 *                                     schedule that acts on them, and without
 *                                     this only the first-declared branch would
 *                                     ever be exercised.
 */
export function execute(workflow, opts = {}) {
  const {
    trigger = {},
    secrets = {},
    staticData = {},
    configOverride = null,
    from = null,
  } = opts;

  const nodes = new Map(
    workflow.nodes.filter((n) => n.type !== STICKY).map((n) => [n.name, n])
  );
  const conns = workflow.connections ?? {};

  const outputs = {};          // node name -> items produced
  const effects = {            // what the workflow *would* have done
    emails: [],
    httpCalls: [],
    responses: [],
    errors: [],
  };
  const executed = [];

  const triggers = [...nodes.values()].filter(
    (n) => n.type.toLowerCase().includes('trigger') || n.type === 'n8n-nodes-base.webhook'
  );
  if (!triggers.length) throw new Error('workflow has no trigger');

  const triggerNode = from
    ? triggers.find((n) => n.name === from || n.name.includes(from))
    : triggers[0];

  if (!triggerNode) {
    throw new Error(
      `no trigger matching ${JSON.stringify(from)}. Available: ${triggers.map((t) => t.name).join(' | ')}`
    );
  }

  const queue = [{ name: triggerNode.name, items: [{ json: trigger }] }];

  while (queue.length) {
    const { name, items } = queue.shift();
    const node = nodes.get(name);
    if (!node) continue;

    let produced;
    let outputIndex = 0;
    let extraOutputs = null;

    try {
      ({ produced, outputIndex, extraOutputs = null } = runNode(node, items, {
        outputs, staticData, effects, secrets, configOverride,
      }));
    } catch (e) {
      effects.errors.push({ node: name, message: e.message });
      // Mirror n8n: a node with an error output routes there; otherwise the
      // branch stops here.
      if (node.onError === 'continueErrorOutput') {
        produced = items.map((i) => ({ json: { ...i.json, error: { message: e.message } } }));
        outputIndex = 1;
      } else {
        executed.push({ node: name, items: 0, failed: true });
        continue;
      }
    }

    // Record the primary output for $('Node') lookups. When a router split the
    // batch, keep every branch's items visible so a later node referencing this
    // one by name still sees everything it produced.
    const allProduced = extraOutputs
      ? [...produced, ...Object.values(extraOutputs).flat()]
      : produced;
    outputs[name] = allProduced.length ? allProduced : produced;
    executed.push({ node: name, items: produced.length, output: outputIndex });

    const main = conns[name]?.main ?? [];

    const dispatch = (idx, batch) => {
      // No items means the branch is intentionally finished — the dedupe guard
      // returning zero is a success, not a failure.
      if (!batch || !batch.length) return;
      for (const link of main[idx] ?? []) queue.push({ name: link.node, items: batch });
    };

    dispatch(outputIndex, produced);
    if (extraOutputs) {
      for (const [idx, batch] of Object.entries(extraOutputs)) dispatch(Number(idx), batch);
    }
  }

  return { outputs, effects, executed, staticData };
}

function runNode(node, items, env) {
  const { outputs, staticData, effects, secrets, configOverride } = env;
  const ctxFor = (item) => ({ item, items, outputs, staticData });
  const t = node.type;

  if (t === 'n8n-nodes-base.webhook' || t.toLowerCase().includes('trigger')) {
    return { produced: items, outputIndex: 0 };
  }

  if (t === 'n8n-nodes-base.code') {
    let js = node.parameters.jsCode;

    // Allow a test to override Config values without editing the template.
    if (configOverride && node.name.includes('Config')) {
      js = js.replace(/const CONFIG = \{[\s\S]*?\n\};/, `const CONFIG = ${JSON.stringify(configOverride)};`);
    }

    const sandbox = buildSandbox(ctxFor(items[0]));
    const result = vm.runInNewContext(`(function(){ ${js} })()`, sandbox, { timeout: 10000 });
    const arr = Array.isArray(result) ? result : result == null ? [] : [result];
    return {
      produced: arr.map((r) => (r && r.json !== undefined ? r : { json: r })),
      outputIndex: 0,
    };
  }

  if (t === 'n8n-nodes-base.crypto') {
    const p = node.parameters;
    const secret = secrets[node.name];
    if (secret === undefined) {
      throw new Error(`no test secret supplied for Crypto node '${node.name}'`);
    }
    const produced = items.map((item) => {
      const value = String(evaluateExpression(p.value, ctxFor(item)) ?? '');
      const digest = crypto
        .createHmac(String(p.type).toLowerCase(), secret)
        .update(value)
        .digest(p.encoding === 'base64' ? 'base64' : 'hex');
      return { json: { ...item.json, [p.dataPropertyName]: digest }, binary: item.binary };
    });
    return { produced, outputIndex: 0 };
  }

  // IF and Switch route each item independently in n8n. Evaluating only the
  // first item and sending the whole batch one way silently broke every
  // template that emits a mixed batch — the scheduled branches here emit due
  // records plus a trailing summary record, and those must separate.
  if (t === 'n8n-nodes-base.if') {
    const branches = [[], []];
    for (const item of items) {
      const pass = evalConditionGroup(node.parameters.conditions, ctxFor(item));
      branches[pass ? 0 : 1].push(item);
    }
    return { produced: branches[0], outputIndex: 0, extraOutputs: { 1: branches[1] } };
  }

  if (t === 'n8n-nodes-base.switch') {
    const rules = node.parameters.rules?.values ?? [];
    const fb = node.parameters.options?.fallbackOutput;
    const branches = {};
    for (const item of items) {
      let idx = typeof fb === 'number' ? fb : 0;
      for (let i = 0; i < rules.length; i++) {
        if (evalConditionGroup(rules[i].conditions, ctxFor(item))) { idx = i; break; }
      }
      (branches[idx] = branches[idx] || []).push(item);
    }
    const first = Object.keys(branches).map(Number).sort((a, b) => a - b)[0] ?? 0;
    const extra = { ...branches };
    delete extra[first];
    return { produced: branches[first] ?? [], outputIndex: first, extraOutputs: extra };
  }

  if (t === 'n8n-nodes-base.emailSend') {
    for (const item of items) {
      const c = ctxFor(item);
      // Capture BOTH bodies. Several templates send plain-text alerts rather
      // than HTML, and reading only `html` made their body invisible to tests —
      // an assertion on alert content would pass against undefined.
      const html = evaluateExpression(node.parameters.html ?? '', c);
      const text = evaluateExpression(node.parameters.text ?? '', c);
      effects.emails.push({
        node: node.name,
        to: evaluateExpression(node.parameters.toEmail, c),
        from: evaluateExpression(node.parameters.fromEmail, c),
        subject: evaluateExpression(node.parameters.subject, c),
        format: node.parameters.emailFormat ?? 'html',
        html,
        text,
        // Whatever body this email actually carries, for assertions that do not
        // care which format was used.
        body: node.parameters.emailFormat === 'text' ? text : (html || text),
      });
    }
    return { produced: items, outputIndex: 0 };
  }

  if (t === 'n8n-nodes-base.httpRequest') {
    for (const item of items) {
      effects.httpCalls.push({
        node: node.name,
        url: evaluateExpression(node.parameters.url, ctxFor(item)),
        method: node.parameters.method ?? 'GET',
      });
    }
    return { produced: items, outputIndex: 0 };
  }

  if (t === 'n8n-nodes-base.respondToWebhook') {
    const c = ctxFor(items[0]);
    effects.responses.push({
      node: node.name,
      with: node.parameters.respondWith,
      body: evaluateExpression(node.parameters.responseBody ?? '', c),
      redirect: evaluateExpression(node.parameters.redirectURL ?? '', c),
      code: node.parameters.options?.responseCode ?? 200,
    });
    return { produced: items, outputIndex: 0 };
  }

  // Unknown node types pass through rather than failing the run, so adding an
  // integration does not break existing tests.
  return { produced: items, outputIndex: 0 };
}

export function loadWorkflow(path) {
  return JSON.parse(require('node:fs').readFileSync(path, 'utf8'));
}
