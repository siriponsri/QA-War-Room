"use strict";
/*
 * AI model settings page. Talks only to the local server (/api/settings*). The server stores
 * keys in a local file and returns a masked hint; this page never receives a saved key back and
 * clears the key field after saving. "Test" asks the server to call the provider's free
 * account/model-list endpoint; no prompt or case data is sent anywhere.
 */
(() => {
  const { t, el, icon } = UI;
  const $ = (id) => document.getElementById(id);
  const app = $("app");
  const TIERS = ["budget", "balanced", "best"];
  const s = { data: null, selected: null, live: {}, busy: false, confirmRemove: false, lastTest: {} };

  async function api(path, body) {
    let response;
    try {
      response = await fetch(path, body === undefined ? { cache: "no-store" }
        : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    } catch (_) {
      throw Object.assign(new Error("network"), { code: "network" });
    }
    let value = null;
    try { value = await response.json(); } catch (_) { /* ignore */ }
    if (!response.ok) throw Object.assign(new Error(value?.error?.message || `HTTP ${response.status}`), { code: value?.error?.code, status: response.status });
    return value;
  }

  function banner(text, tone = "info", retry = false) {
    $("banner").hidden = !text;
    if (!text) return;
    $("banner").className = `banner banner-${tone}`;
    $("banner-icon").replaceChildren(icon(tone === "ok" ? "check" : tone === "info" ? "info" : "alert"));
    $("banner-text").textContent = text;
    $("banner-retry").hidden = !retry;
  }
  function formError(text) { $("form-error").hidden = !text; $("form-error").textContent = text || ""; }

  const spec = () => s.data?.providers.find((p) => p.id === s.selected);
  const conf = (id = s.selected) => s.data?.configured[id] || {};
  // Up to 3 decimals so published prices such as $0.182 or $4.125 are not rounded away.
  const money = (v) => (v === null || v === undefined ? null : v === 0 ? t("free") : `$${v.toFixed(3).replace(/0$/, "")}`);
  const ctx = (n) => (n ? (n >= 1_000_000 ? `${(n / 1_000_000).toFixed(n % 1_000_000 ? 2 : 0)}M` : `${Math.round(n / 1000)}K`) : "");

  function statusOf(id) {
    const c = conf(id);
    const p = s.data.providers.find((x) => x.id === id);
    if (s.data.active === id && c.ready) return ["active", "done"];
    if (c.ready) return ["ready", "done"];
    if (c.has_key) return ["keySaved", "muted"];
    if (!p.needs_key) return ["noKeyNeeded", "muted"];
    return ["notSet", "muted"];
  }

  function renderProviders() {
    const list = $("providers");
    list.replaceChildren();
    s.data.providers.forEach((p) => {
      const li = el("li");
      const button = el("button", `provider-item ${p.id === s.selected ? "is-current" : ""}`);
      button.type = "button";
      if (p.id === s.selected) button.setAttribute("aria-current", "true");
      const [key, tone] = statusOf(p.id);
      const text = el("span", "provider-text");
      text.append(el("strong", "", p.name));
      const small = el("small");
      small.append(el("span", `dot dot-${tone}`), document.createTextNode(t(key)));
      if (p.thai) small.append(document.createTextNode(` · ${t("thaiFocus")}`));
      text.append(small);
      button.append(text);
      button.addEventListener("click", () => select(p.id));
      li.append(button);
      list.append(li);
    });
  }

  function renderModels() {
    const p = spec();
    const c = conf();
    const box = $("models");
    box.replaceChildren();
    const known = new Set(p.models.map((m) => m.id));
    TIERS.forEach((tier) => {
      const models = p.models.filter((m) => m.tier === tier);
      if (!models.length) return;
      const group = el("div", "model-group");
      group.append(el("h3", `tier-title tier-${tier}`, t(`tier_${tier}`)));
      models.forEach((m) => {
        const row = el("label", "model-row");
        const input = el("input");
        input.type = "radio";
        input.name = "model";
        input.value = m.id;
        input.checked = c.model === m.id || (!c.model && m.recommended);
        const main = el("span", "model-main");
        const name = el("span", "model-name");
        name.append(el("code", "", m.id));
        if (m.recommended) name.append(el("span", "badge badge-live", t("recommended")));
        main.append(name);
        const note = m.note?.[UI.lang];
        if (note) main.append(el("small", "", note));
        const price = el("span", "model-price");
        const inp = money(m.input_usd);
        if (inp === null) price.append(el("span", "quiet", t("priceUnknown")));
        else if (m.input_usd === 0 && m.output_usd === 0) price.append(el("strong", "", t("free")));
        else price.append(el("strong", "", `${inp} / ${money(m.output_usd)}`));
        if (m.context) price.append(el("small", "", `${ctx(m.context)} ${t("contextLbl")}`));
        row.append(input, main, price);
        group.append(row);
      });
      box.append(group);
    });
    const custom = document.querySelector('input[name="model"][value="__custom"]');
    custom.checked = Boolean(c.model) && !known.has(c.model);
    $("custom-model").value = custom.checked ? c.model : "";
    renderLiveModels();
  }

  function renderLiveModels() {
    const list = $("live-models");
    list.replaceChildren();
    (s.live[s.selected] || []).forEach((id) => { const o = el("option"); o.value = id; list.append(o); });
  }

  function renderPanel() {
    const p = spec();
    if (!p) return;
    const c = conf();
    $("provider-form").hidden = false;
    $("provider-name").textContent = p.name;
    const [key, tone] = statusOf(p.id);
    const status = $("provider-status");
    status.replaceChildren(el("span", `badge badge-${tone === "done" ? "done" : "muted"}`, t(key)));
    $("get-key").href = p.site;
    $("get-key").hidden = !p.needs_key;
    $("price-source").href = p.pricing_source;
    $("key-section").hidden = !p.needs_key;
    $("url-section").hidden = p.id !== "ollama";
    $("base-url").value = c.base_url || p.default_base_url || "";
    $("key-current").textContent = c.has_key ? `${t("keySaved")}: ${c.key_hint}` : t("noKeyYet");
    $("api-key").value = "";
    $("api-key").type = "password";
    $("toggle-key").textContent = t("show");
    $("toggle-key").setAttribute("aria-pressed", "false");
    $("price-checked").textContent = t("priceChecked").replace("{date}", s.data.price_checked);
    $("price-note").textContent = p.price_note?.[UI.lang] || "";
    $("make-default").checked = s.data.active === p.id;
    $("remove").hidden = !(c.has_key || c.model);
    s.confirmRemove = false;
    $("remove-label").textContent = t("removeKey");
    formError("");
    renderModels();
    renderTest();
    buttons();
  }

  function renderTest() {
    const box = $("test-result");
    const r = s.lastTest[s.selected];
    if (!r) { box.hidden = true; return; }
    box.hidden = false;
    box.className = `test-result ${r.ok ? "is-ok" : "is-error"}`;
    box.replaceChildren(icon(r.ok ? "check" : "alert"));
    const text = el("div");
    if (r.ok) {
      text.append(el("strong", "", t("testOk").replace("{n}", r.model_count)));
      if (r.model_found === true) text.append(el("p", "", t("modelFound")));
      if (r.model_found === false) text.append(el("p", "", t("modelMissing")));
      if (r.model_count) text.append(el("p", "hint", t("liveHint")));
    } else {
      text.append(el("strong", "", t(`err_${r.message}`) || r.message), el("p", "hint", r.status ? `HTTP ${r.status}` : ""));
    }
    box.append(text);
  }

  function buttons() {
    ["save", "test", "remove"].forEach((id) => { $(id).disabled = s.busy; });
    const p = spec();
    if (p && p.needs_key && !conf().has_key) $("test").disabled = true;
  }

  function chosenModel() {
    const radio = document.querySelector('input[name="model"]:checked');
    if (!radio) return "";
    return radio.value === "__custom" ? $("custom-model").value.trim() : radio.value;
  }

  function select(id) {
    s.selected = id;
    try { history.replaceState(null, "", `#${id}`); } catch (_) { /* ignore */ }
    renderProviders();
    renderPanel();
    if (!window.matchMedia("(min-width: 960px)").matches) $("provider-form").scrollIntoView({ block: "start" });
  }

  async function run(work) {
    if (s.busy) return;
    s.busy = true;
    buttons();
    formError("");
    try { await work(); } catch (error) { formError(UI.errorText(error)); } finally { s.busy = false; buttons(); }
  }

  async function save(event) {
    event.preventDefault();
    const p = spec();
    const model = chosenModel();
    if (!model) { formError(t("chooseModel")); return; }
    const payload = { provider: p.id, model, active: $("make-default").checked };
    const key = $("api-key").value.trim();
    if (key) payload.api_key = key;
    if (p.id === "ollama") payload.base_url = $("base-url").value.trim();
    await run(async () => {
      s.data = await api("/api/settings", payload);
      $("api-key").value = ""; // never keep the key in the page after saving
      banner(t("saved"), "ok");
      renderProviders();
      renderPanel();
    });
  }

  async function test() {
    const id = s.selected;
    $("test-label").textContent = t("testing");
    await run(async () => {
      const result = await api("/api/settings/test", { provider: id });
      s.lastTest[id] = result;
      if (result.ok) s.live[id] = result.models;
      if (id === s.selected) { renderTest(); renderLiveModels(); }
    });
    $("test-label").textContent = t("test");
  }

  async function remove() {
    if (!s.confirmRemove) { s.confirmRemove = true; $("remove-label").textContent = t("confirmRemove"); return; }
    const id = s.selected;
    await run(async () => {
      s.data = await api("/api/settings/clear", { provider: id });
      delete s.lastTest[id];
      banner(t("removed"), "info");
      renderProviders();
      renderPanel();
    });
  }

  async function load() {
    try {
      s.data = await api("/api/settings");
      banner("");
      const hash = location.hash.slice(1);
      const ids = s.data.providers.map((p) => p.id);
      s.selected = ids.includes(hash) ? hash : (s.data.active && ids.includes(s.data.active) ? s.data.active : ids[0]);
      renderProviders();
      renderPanel();
    } catch (error) {
      $("providers").replaceChildren(el("li", "hint", t("setLoadError")));
      banner(t("setLoadError"), "danger", true);
    }
  }

  UI.mount();
  const sidebar = UI.bindSidebar(app);
  $("provider-form").addEventListener("submit", save);
  $("test").addEventListener("click", test);
  $("remove").addEventListener("click", remove);
  $("banner-retry").addEventListener("click", load);
  $("toggle-key").addEventListener("click", () => {
    const show = $("api-key").type === "password";
    $("api-key").type = show ? "text" : "password";
    $("toggle-key").textContent = t(show ? "hide" : "show");
    $("toggle-key").setAttribute("aria-pressed", String(show));
  });
  $("custom-model").addEventListener("focus", () => { document.querySelector('input[name="model"][value="__custom"]').checked = true; });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && app.classList.contains("nav-open")) { sidebar.close(); $("nav-toggle").focus(); }
  });
  document.addEventListener("qa-language", () => { if (s.data) { renderProviders(); renderPanel(); } });
  window.addEventListener("hashchange", () => {
    const id = location.hash.slice(1);
    if (s.data && id !== s.selected && s.data.providers.some((p) => p.id === id)) select(id);
  });
  load();
})();
