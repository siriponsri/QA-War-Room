// Browser acceptance check for the live chat and dashboard (frontend only).
//
// Drives a real local Chrome/Edge over the DevTools protocol against an ALREADY RUNNING
// QA War Room server. No npm packages: Node >= 22 (global WebSocket/fetch) is enough.
// It creates a few real demo rooms on that server (in-memory; they count toward the
// server's 50-rooms-per-process cap) and never touches backend files.
//
//   node scripts/ui_browser_check.mjs --out runs/claude-frontend-v1 [--base http://127.0.0.1:8765] [--chrome PATH]
//
// Output: <out>/screens/*.png and <out>/browser-check.json (every check with pass/fail).
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, readFileSync, existsSync, mkdtempSync, rmSync } from "node:fs";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, all) => (v.startsWith("--") ? [...acc, [v.slice(2), all[i + 1]]] : acc), []));
const BASE = args.base || "http://127.0.0.1:8765";
const OUT = resolve(args.out || "runs/claude-frontend-v1");
const CHROME = args.chrome || [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "/usr/bin/google-chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
].find((p) => existsSync(p));
const SHOTS = join(OUT, "screens");
mkdirSync(SHOTS, { recursive: true });

const results = [];
const consoleProblems = [];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function check(name, pass, detail = "") {
  results.push({ name, pass: Boolean(pass), detail: String(detail) });
  console.log(`${pass ? "PASS" : "FAIL"}  ${name}${detail ? `  — ${detail}` : ""}`);
}

// ---------- minimal CDP client ----------
class Page {
  constructor(ws) {
    this.ws = ws; this.id = 0; this.pending = new Map(); this.listeners = [];
    ws.addEventListener("message", (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve: ok, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        msg.error ? reject(new Error(`${msg.error.message}`)) : ok(msg.result);
      } else if (msg.method) {
        this.listeners.forEach((fn) => fn(msg));
      }
    });
  }
  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((ok, reject) => this.pending.set(id, { resolve: ok, reject }));
  }
  on(fn) { this.listeners.push(fn); }
  async eval(expression) {
    const r = await this.send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) throw new Error(`eval failed: ${r.exceptionDetails.exception?.description || r.exceptionDetails.text}`);
    return r.result.value;
  }
  async waitFor(expression, timeout = 15000, interval = 150) {
    const end = Date.now() + timeout;
    while (Date.now() < end) {
      try { if (await this.eval(`Boolean(${expression})`)) return true; } catch (_) { /* page loading */ }
      await sleep(interval);
    }
    return false;
  }
  async goto(url) {
    const loaded = new Promise((ok) => { const fn = (m) => { if (m.method === "Page.loadEventFired") { this.listeners = this.listeners.filter((x) => x !== fn); ok(); } }; this.on(fn); });
    await this.send("Page.navigate", { url });
    await Promise.race([loaded, sleep(10000)]);
    await sleep(300);
  }
  async viewport(width, height, mobile = false) {
    await this.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await this.send("Emulation.setTouchEmulationEnabled", { enabled: mobile });
  }
  async shot(name) {
    await sleep(250);
    const { data } = await this.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    writeFileSync(join(SHOTS, `${name}.png`), Buffer.from(data, "base64"));
    const overflow = await this.eval("document.documentElement.scrollWidth - document.documentElement.clientWidth");
    check(`no horizontal overflow: ${name}`, overflow <= 0, `overflow ${overflow}px`);
    return name;
  }
  async key(key, code = key, keyCode = 0) {
    await this.send("Input.dispatchKeyEvent", { type: "keyDown", key, code, windowsVirtualKeyCode: keyCode });
    await this.send("Input.dispatchKeyEvent", { type: "keyUp", key, code, windowsVirtualKeyCode: keyCode });
  }
}

// Worst-case WCAG contrast of visible small-text samples against their effective background.
const CONTRAST = `(() => {
  const lum = (c) => { const [r, g, b] = c.match(/[0-9.]+/g).slice(0, 3).map(Number).map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const bg = (el) => { while (el) { const c = getComputedStyle(el).backgroundColor; if (c && c !== "rgba(0, 0, 0, 0)" && c !== "transparent") return c; el = el.parentElement; } return "rgb(255,255,255)"; };
  const sel = [".setup-intro", ".hint", ".case-text small", ".case-text strong", "#start-label", ".badge-muted", ".claim-label", ".eyebrow", ".side-label", ".history-empty", ".local-note", ".chip span", ".step legend"];
  return sel.flatMap((q) => [...document.querySelectorAll(q)].slice(0, 2)).filter((n) => n.offsetParent).map((n) => {
    const a = lum(getComputedStyle(n).color), b = lum(bg(n));
    return { q: n.className || n.id || n.tagName, ratio: Math.round(((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)) * 100) / 100 };
  });
})()`;

async function prefs(page, lang, theme) {
  await page.goto(`${BASE}/dashboard.html`);
  await page.eval(`localStorage.setItem("qawr-language-v1","${lang}");localStorage.setItem("qawr-theme-v1","${theme}");true`);
}

async function api(path) {
  const r = await fetch(BASE + path);
  return { status: r.status, type: r.headers.get("content-type"), body: await r.text() };
}

async function main() {
  if (!CHROME) throw new Error("No Chrome/Edge executable found; pass --chrome PATH");
  const health = await api("/api/health").catch(() => null);
  if (!health || health.status !== 200) throw new Error(`Server not reachable at ${BASE}`);
  const profile = mkdtempSync(join(tmpdir(), "qawr-ui-"));
  const chrome = spawn(CHROME, ["--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars", "about:blank"], { stdio: "ignore" });
  try {
    let port = null;
    for (let i = 0; i < 100 && !port; i += 1) {
      await sleep(100);
      const file = join(profile, "DevToolsActivePort");
      if (existsSync(file)) port = readFileSync(file, "utf8").split("\n")[0].trim();
    }
    if (!port) throw new Error("Chrome did not start");
    const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" })).json();
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((ok, reject) => { ws.addEventListener("open", ok); ws.addEventListener("error", reject); });
    const page = new Page(ws);
    await page.send("Page.enable");
    await page.send("Runtime.enable");
    await page.send("Log.enable");
    await page.send("Network.enable");
    page.on((m) => {
      if (m.method === "Runtime.consoleAPICalled" && ["error", "warning", "assert"].includes(m.params.type)) consoleProblems.push({ type: m.params.type, text: m.params.args.map((a) => a.value ?? a.description).join(" ") });
      if (m.method === "Runtime.exceptionThrown") consoleProblems.push({ type: "exception", text: m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text });
      if (m.method === "Log.entryAdded" && m.params.entry.level === "error" && !page.expectNetworkErrors) consoleProblems.push({ type: "log", text: `${m.params.entry.text} ${m.params.entry.url || ""}` });
    });

    const D = [1440, 900, false];
    const M = [390, 844, true];

    // ---- 1. Setup screen, both languages and themes ----
    for (const [lang, theme] of [["th", "light"], ["th", "dark"], ["en", "light"], ["en", "dark"]]) {
      await prefs(page, lang, theme);
      for (const [w, h, mobile] of [D, M]) {
        await page.viewport(w, h, mobile);
        await page.goto(`${BASE}/`);
        await page.waitFor(`document.querySelectorAll('#case-list input[name=case]').length === 8`);
        const state = await page.eval(`({lang: document.documentElement.lang, theme: document.documentElement.dataset.theme, start: document.querySelector('#start-label').textContent, checked: document.querySelector('input[name=case]:checked')?.value})`);
        check(`setup ${lang}/${theme}/${mobile ? "mobile" : "desktop"} applies saved prefs`, state.lang === lang && state.theme === theme, JSON.stringify(state));
        check(`setup ${lang}/${mobile ? "mobile" : "desktop"} preselects a case`, state.checked === "MFG-001", state.checked);
        await page.shot(`setup-${lang}-${theme}-${mobile ? "mobile" : "desktop"}`);
        if (!mobile && lang === "th") {
          const worst = await page.eval(CONTRAST);
          check(`text contrast >= 4.5:1 on setup (${theme})`, worst.every((w) => w.ratio >= 4.5), JSON.stringify(worst.filter((w) => w.ratio < 4.5).slice(0, 4)));
        }
      }
    }
    await page.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
    const motion = await page.eval(`getComputedStyle(document.querySelector('.dot-live')).animationDuration`);
    check("prefers-reduced-motion disables animation", parseFloat(motion) < 0.01, motion);
    await page.send("Emulation.setEmulatedMedia", { features: [] });

    // ---- 2. Language + theme toggles persist ----
    await prefs(page, "th", "light");
    await page.viewport(...D);
    await page.goto(`${BASE}/`);
    await page.waitFor(`document.querySelector('#case-list input')`);
    await page.eval(`document.getElementById('language-toggle').click(); document.getElementById('theme-toggle').click(); true`);
    await page.goto(`${BASE}/`);
    const persisted = await page.eval(`({lang: document.documentElement.lang, theme: document.documentElement.dataset.theme, label: document.getElementById('start-label').textContent})`);
    check("language/theme toggles persist across reload", persisted.lang === "en" && persisted.theme === "dark" && persisted.label === "Start conversation", JSON.stringify(persisted));

    // ---- 3. Full run: start, pause, note, manual request, record viewer, resume, complete ----
    await prefs(page, "th", "light");
    await page.viewport(...D);
    await page.goto(`${BASE}/`);
    await page.waitFor(`document.querySelector('#case-list input')`);
    await page.eval(`document.querySelector('input[name=case][value="MFG-001"]').click();
      document.getElementById('advanced').open = true;
      document.getElementById('pace').value = '1200';
      document.querySelector('input[name=time][value="120"]').click(); true`);
    await page.shot("setup-th-light-desktop-advanced");
    await page.eval(`document.getElementById('start-button').click(); true`);
    check("start opens a live room", await page.waitFor(`!document.getElementById('room-view').hidden && /room=room_/.test(location.search)`), await page.eval("location.search"));
    const roomId = await page.eval(`new URLSearchParams(location.search).get('room')`);
    check("agents post real messages while running", await page.waitFor(`document.querySelectorAll('#message-list .msg-agent').length >= 3`, 20000));
    check("typing indicator names the next role", await page.eval(`!document.getElementById('typing').hidden && document.getElementById('typing-text').textContent.length > 0`));
    await page.shot("room-running-th-light-desktop");
    await page.eval(`document.getElementById('pause-button').click(); true`);
    check("pause reaches server state", await page.waitFor(`document.querySelector('#room-subtitle .badge-warn') && !document.getElementById('paused-hint').hidden`));
    const serverPaused = JSON.parse((await api(`/api/rooms/${roomId}`)).body).status;
    check("server reports paused", serverPaused === "paused", serverPaused);
    check("typing indicator hidden while paused", await page.eval(`document.getElementById('typing').hidden`));
    await page.eval(`const i=document.getElementById('note-input'); i.value='ตรวจขอบเขตวันที่ก่อน <b>not html</b>'; document.getElementById('composer').requestSubmit(); true`);
    check("note is posted verbatim as own bubble (escaped)", await page.waitFor(`[...document.querySelectorAll('.msg-own .bubble-text')].some(n => n.textContent === 'ตรวจขอบเขตวันที่ก่อน <b>not html</b>') && !document.querySelector('.msg-own b')`));
    check("details panel is closed by default (minimal layout)", await page.eval(`!document.getElementById('app').classList.contains('details-open')`));
    await page.eval(`document.getElementById('paused-evidence').click(); true`);
    check("paused hint opens the evidence panel", await page.waitFor(`document.getElementById('app').classList.contains('details-open')`, 3000));
    const before = await page.eval(`document.querySelectorAll('.evidence-row.is-received').length`);
    const reqId = await page.eval(`(() => { const b = [...document.querySelectorAll('#evidence-list .btn-outline')].find(x => !x.disabled); if (!b) return null; const id = b.getAttribute('aria-label'); b.click(); return id; })()`);
    check("a manual request button is enabled while paused", Boolean(reqId), reqId);
    check("manual request delivers or reports a record", await page.waitFor(`document.querySelectorAll('.evidence-row.is-received, .evidence-row.is-unavailable').length > ${before}`));
    await page.shot("room-paused-th-light-desktop");
    await page.eval(`document.querySelector('.attach').click(); true`);
    check("record viewer opens a received record with facts", await page.waitFor(`document.getElementById('record-dialog').open && document.querySelectorAll('#record-facts .fact').length > 0`));
    await page.shot("record-viewer-th-light-desktop");
    await page.key("Escape", "Escape", 27);
    check("Escape closes the record viewer", await page.waitFor(`!document.getElementById('record-dialog').open`, 3000));
    await page.eval(`document.getElementById('pause-button').click(); true`);
    check("resume returns to running", await page.waitFor(`document.querySelector('#room-subtitle .badge-live')`));
    check("room completes", await page.waitFor(`document.querySelector('#outcome .tone-done')`, 90000), await page.eval(`document.querySelector('#room-subtitle .badge')?.textContent`));
    const done = await page.eval(`({verdict: !!document.querySelector('#outcome .verdict-row'), compare: !!document.querySelector('#outcome details.compare'), dock: document.querySelector('.dock-row').hidden, ended: !document.getElementById('ended-row').hidden})`);
    check("completed room shows draft verdict, labelled reference, ended dock", done.verdict && done.compare && done.dock && done.ended, JSON.stringify(done));
    // Persona voices: display-only templates must keep every record ID and verdict from the system text.
    const voice = await page.eval(`(() => {
      const rows = [...document.querySelectorAll('#message-list .msg-agent')];
      const voiced = rows.filter((li) => li.querySelector('.orig > p:not([lang])'));
      const lost = rows.filter((li) => {
        const shown = li.querySelector('.bubble-text').textContent;
        const sys = li.querySelector('.orig > p:not([lang])')?.textContent || shown;
        return (sys.match(/D[0-9]+/g) || []).some((id) => !shown.includes(id));
      }).length;
      const names = [...new Set(rows.map((li) => li.querySelector('.msg-name')?.textContent).filter(Boolean))];
      const phum = rows.find((li) => li.querySelector('.msg-name')?.textContent === 'ภูมิ')?.querySelector('.bubble-text').textContent || '';
      const mind = rows.find((li) => li.querySelector('.msg-name')?.textContent === 'มายด์')?.querySelector('.bubble-text').textContent || '';
      return { total: rows.length, voiced: voiced.length, lost, names, phum: phum.includes('ครับ'), mind: mind.includes('ค่ะ') };
    })()`);
    check("each character speaks in its own voice", voice.phum && voice.mind && voice.names.length >= 3 && voice.voiced >= voice.total - 2, JSON.stringify(voice));
    check("persona voice keeps every record ID from the system wording", voice.lost === 0, `${voice.lost} messages lost an ID`);
    check("system prompt is viewable in the team panel", await page.eval(`document.querySelectorAll('#participants .persona-prompt p').length === 4`));
    await page.shot("room-completed-th-light-desktop");
    for (const lang of ["th", "en"]) {
      const href = await page.eval(`document.getElementById('download-${lang}').getAttribute('href')`);
      const r = await api(href);
      check(`readable ${lang} report downloads`, r.status === 200 && r.type.startsWith("text/markdown") && r.body.length > 200, `${r.status} ${r.type} ${r.body.length} bytes`);
    }
    await page.eval(`document.getElementById('language-toggle').click(); document.getElementById('theme-toggle').click(); true`);
    await sleep(300);
    check("language switch re-renders the conversation", await page.eval(`document.getElementById('outcome-title').textContent === 'The team finished its review'`));
    await page.shot("room-completed-en-dark-desktop");
    await page.viewport(...M);
    await page.goto(`${BASE}/?room=${roomId}`);
    await page.waitFor(`document.querySelector('#outcome .outcome-card')`);
    await page.shot("room-completed-en-dark-mobile");
    await page.eval(`document.getElementById('details-toggle').click(); true`);
    await sleep(400);
    await page.shot("room-details-en-dark-mobile");
    await page.key("Escape", "Escape", 27);
    check("Escape closes the mobile details drawer", await page.waitFor(`!document.getElementById('app').classList.contains('details-open')`, 3000));

    // ---- 4. Time limit: unfinished work, no forced verdict ----
    await prefs(page, "th", "dark");
    await page.viewport(...M);
    await page.goto(`${BASE}/`);
    await page.waitFor(`document.querySelector('#case-list input')`);
    await page.eval(`document.querySelector('input[name=case][value="MFG-006"]').click();
      document.querySelector('input[name=time][value="custom"]').click();
      document.getElementById('custom-time').value = '4';
      document.getElementById('advanced').open = true; document.getElementById('pace').value = '1200';
      document.getElementById('start-button').click(); true`);
    check("timed room starts", await page.waitFor(`/room=room_/.test(location.search)`));
    const timedId = await page.eval(`new URLSearchParams(location.search).get('room')`);
    await sleep(1500);
    await page.shot("room-running-th-dark-mobile");
    check("time limit ends the room as unfinished", await page.waitFor(`document.querySelector('#outcome .tone-partial')`, 15000));
    const partial = await page.eval(`({verdict: !!document.querySelector('#outcome .verdict-row'), compare: !!document.querySelector('#outcome .compare'), title: document.getElementById('outcome-title').textContent})`);
    check("timed-out room has no verdict or reference", !partial.verdict && !partial.compare && partial.title === "เก็บเป็นงานค้างแล้ว", JSON.stringify(partial));
    const timedState = JSON.parse((await api(`/api/rooms/${timedId}`)).body);
    check("server status is time_limit without decision/feedback", timedState.status === "time_limit" && !timedState.session.decision && !timedState.session.feedback, timedState.status);
    const partialReport = await api(`/api/rooms/${timedId}/report?format=markdown&lang=th`);
    check("partial Thai report downloads", partialReport.status === 200 && partialReport.body.includes("time_limit"), `${partialReport.status}`);
    await page.shot("room-timeout-th-dark-mobile");

    // ---- 5. Stop with confirmation ----
    await page.viewport(...D);
    await page.goto(`${BASE}/`);
    await page.waitFor(`document.querySelector('#case-list input')`);
    await page.eval(`document.querySelector('input[name=case][value="MFG-003"]').click(); document.getElementById('advanced').open = true; document.getElementById('pace').value = '1200'; document.getElementById('start-button').click(); true`);
    await page.waitFor(`!document.getElementById('stop-button').disabled`);
    await page.eval(`document.getElementById('stop-button').click(); true`);
    check("stop asks for confirmation", await page.waitFor(`document.getElementById('stop-dialog').open`, 3000));
    await page.shot("stop-confirm-th-dark-desktop");
    await page.eval(`document.querySelector('#stop-dialog button[value=stop]').click(); true`);
    check("confirmed stop saves unfinished work", await page.waitFor(`document.querySelector('#outcome .tone-partial') && document.querySelector('#room-subtitle .badge-partial')`));
    await page.shot("room-stopped-th-dark-desktop");

    // ---- 6. Stale room and error states ----
    page.expectNetworkErrors = true; // the 404 below and blocked requests are intentional
    await page.goto(`${BASE}/?room=room_${"0".repeat(32)}`);
    check("unknown room shows a clear notice and returns to setup", await page.waitFor(`!document.getElementById('banner').hidden && !document.getElementById('setup-view').hidden`));
    await page.shot("stale-room-th-dark-desktop");
    await page.send("Network.setBlockedURLs", { urls: ["*/api/cases*"] });
    await page.goto(`${BASE}/`);
    check("case loading failure shows retry", await page.waitFor(`document.querySelector('#case-list .inline-error button')`));
    await page.shot("cases-error-th-dark-desktop");
    await page.send("Network.setBlockedURLs", { urls: ["*/api/rooms*"] });
    await page.goto(`${BASE}/dashboard.html`);
    check("dashboard shows connection error", await page.waitFor(`!document.getElementById('banner').hidden`));
    await page.shot("dashboard-error-th-dark-desktop");
    await page.send("Network.setBlockedURLs", { urls: [] });
    page.expectNetworkErrors = false;

    // ---- 7. Dashboard uses real counts ----
    for (const [lang, theme] of [["th", "light"], ["en", "dark"]]) {
      await prefs(page, lang, theme);
      for (const [w, h, mobile] of [D, M]) {
        await page.viewport(w, h, mobile);
        await page.goto(`${BASE}/dashboard.html`);
        await page.waitFor(`!document.getElementById('kpi-rooms').classList.contains('is-loading')`);
        const overview = JSON.parse((await api("/api/rooms")).body);
        const shown = await page.eval(`({cases: +document.getElementById('kpi-cases').textContent, rooms: +document.getElementById('kpi-rooms').textContent, completed: +document.getElementById('kpi-completed').textContent, rows: document.querySelectorAll('.room-row').length})`);
        const expected = { cases: overview.case_count, rooms: overview.rooms.length, completed: overview.rooms.filter((r) => r.status === "completed").length, rows: overview.rooms.length };
        check(`dashboard ${lang}/${mobile ? "mobile" : "desktop"} counts match /api/rooms`, JSON.stringify(shown) === JSON.stringify(expected), `${JSON.stringify(shown)} vs ${JSON.stringify(expected)}`);
        await page.shot(`dashboard-${lang}-${theme}-${mobile ? "mobile" : "desktop"}`);
      }
    }

    // ---- 7b. AI settings page (read-only checks: never saves a key) ----
    const hasSettings = (await api("/api/settings")).status === 200;
    check("settings API available on this server", hasSettings, hasSettings ? "" : "restart the server to load /api/settings");
    if (hasSettings) {
      for (const [lang, theme, [w, h, mobile]] of [["th", "light", D], ["en", "dark", D], ["th", "dark", M]]) {
        await prefs(page, lang, theme);
        await page.viewport(w, h, mobile);
        await page.goto(`${BASE}/settings.html#anthropic`);
        await page.waitFor(`!document.getElementById('provider-form').hidden && document.querySelectorAll('#models .model-row').length > 0`);
        const view = await page.eval(`({providers: document.querySelectorAll('#providers .provider-item').length, models: document.querySelectorAll('#models .model-row').length, priced: [...document.querySelectorAll('#models .model-price strong')].filter(n => n.textContent.includes('$')).length, keyValue: document.getElementById('api-key').value, keyType: document.getElementById('api-key').type, testDisabled: document.getElementById('test').disabled})`);
        check(`settings ${lang}/${theme}/${mobile ? "mobile" : "desktop"} lists providers and priced models`, view.providers === 6 && view.models >= 4 && view.priced >= 4 && view.keyValue === "" && view.keyType === "password" && view.testDisabled, JSON.stringify(view));
        await page.shot(`settings-${lang}-${theme}-${mobile ? "mobile" : "desktop"}`);
      }
      await page.goto(`${BASE}/settings.html#ollama`);
      await page.waitFor(`!document.getElementById('url-section').hidden`);
      await page.eval(`document.getElementById('test').click(); true`);
      check("Ollama test reports a clear result (no key needed)", await page.waitFor(`!document.getElementById('test-result').hidden`, 15000), await page.eval(`document.getElementById('test-result').textContent`));
      await page.shot("settings-ollama-test-th-dark-mobile");
    }

    // ---- 8. Manual desk preserved ----
    await page.viewport(...D);
    await page.goto(`${BASE}/manual.html`);
    check("manual desk still loads", await page.waitFor(`document.documentElement.outerHTML.includes('Evidence workspace')`));
    await page.shot("manual-desk-desktop");

    check("no console errors, warnings or exceptions", consoleProblems.length === 0, JSON.stringify(consoleProblems.slice(0, 5)));
    ws.close();
  } finally {
    chrome.kill();
    await sleep(500);
    try { rmSync(profile, { recursive: true, force: true }); } catch (_) { /* Chrome may still hold files */ }
  }
}

const started = new Date();
main().catch((error) => check("harness completed", false, error.stack || error.message)).finally(() => {
  const failed = results.filter((r) => !r.pass).length;
  writeFileSync(join(OUT, "browser-check.json"), JSON.stringify({
    tool: "scripts/ui_browser_check.mjs", base: BASE, browser: CHROME, started: started.toISOString(), finished: new Date().toISOString(),
    passed: results.length - failed, failed, console_problems: consoleProblems, results,
  }, null, 2));
  console.log(`\n${results.length - failed}/${results.length} checks passed`);
  process.exitCode = failed ? 1 : 0;
});
