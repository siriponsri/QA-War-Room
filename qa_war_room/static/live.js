"use strict";
/*
 * Live conversation page.
 * The server's background scheduler drives the room; this page only polls GET /api/rooms/{id}
 * to display state and sends the existing strict control actions. It never retries POSTs, never
 * invents messages, and only resolves attachments against records actually received
 * (session.evidence). All untrusted text is rendered with textContent.
 */
(() => {
  const { t, el, icon } = UI;
  const $ = (id) => document.getElementById(id);
  const app = $("app");

  const TERMINAL = new Set(["completed", "time_limit", "stopped", "turn_limit", "error"]);
  const ROOM_ID = /^room_[a-f0-9]{32}$/;
  const CASE_ID = /^[A-Za-z0-9_-]{1,40}$/;
  const HISTORY_KEY = "qawr-rooms-v1";
  const POLL_MS = 700;
  const wide = window.matchMedia("(min-width: 1200px)");

  const s = {
    cases: [], casesState: "loading", selected: null,
    room: null, receivedAt: 0, stale: false, busy: false,
    pollTimer: null, failures: 0,
    rendered: 0, viewed: null, lastRole: null, outcomeKey: null,
    history: loadHistory(), detailsPref: null, claimOpen: false, opener: null,
  };

  // ---------- storage ----------
  function loadHistory() {
    try {
      const parsed = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
      if (!Array.isArray(parsed)) return [];
      return parsed
        .filter((r) => r && typeof r.id === "string" && ROOM_ID.test(r.id) && typeof r.title === "string")
        .map((r) => ({ id: r.id, title: r.title, caseId: typeof r.caseId === "string" ? r.caseId : "", status: typeof r.status === "string" ? r.status : "" }))
        .slice(0, 12);
    } catch (_) { return []; }
  }
  function saveHistory() {
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(s.history.slice(0, 12))); } catch (_) { /* ignore */ }
  }
  function rememberRoom(room) {
    const entry = { id: room.room_id, title: room.session.case.title, caseId: room.session.case.id, status: room.status };
    const index = s.history.findIndex((r) => r.id === room.room_id);
    if (index === -1) s.history.unshift(entry);
    else if (s.history[index].status !== room.status) s.history[index] = entry;
    else return;
    saveHistory();
    renderHistory();
  }
  function forgetRoom(id) {
    s.history = s.history.filter((r) => r.id !== id);
    saveHistory();
    renderHistory();
  }

  // ---------- network ----------
  async function api(path, body) {
    let response;
    try {
      response = await fetch(path, body === undefined
        ? { cache: "no-store" }
        : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    } catch (_) {
      throw Object.assign(new Error("network"), { code: "network", status: 0 });
    }
    let value = null;
    try { value = await response.json(); } catch (_) { /* non-JSON error */ }
    if (!response.ok) {
      throw Object.assign(new Error(value?.error?.message || `HTTP ${response.status}`), { code: value?.error?.code || "http", status: response.status });
    }
    return value;
  }

  // ---------- banner ----------
  let bannerTimer = null;
  function showBanner(text, tone = "info", retry = false) {
    clearTimeout(bannerTimer);
    const banner = $("banner");
    banner.hidden = false;
    banner.className = `banner banner-${tone}`;
    $("banner-icon").replaceChildren(icon(tone === "ok" ? "check" : tone === "info" ? "info" : "alert"));
    $("banner-text").textContent = text;
    $("banner-retry").hidden = !retry;
    if (tone === "ok" || tone === "info") bannerTimer = setTimeout(hideBanner, 6000);
  }
  function hideBanner() { clearTimeout(bannerTimer); $("banner").hidden = true; }

  // ---------- helpers ----------
  const isActive = () => Boolean(s.room) && !TERMINAL.has(s.room.status) && !s.stale;
  const evidence = () => s.room?.session?.evidence || [];
  function roleKey(role) {
    if (!s.room) return "investigator";
    if (role === s.room.lead) return "investigator";
    if (role === s.room.reviewer) return "checker";
    return { "user-01": "manufacturing", "user-02": "quality", operator: "you", coordinator: "system" }[role] || "investigator";
  }
  const roleName = (role) => t(roleKey(role));
  const personaName = (role) => UI.persona(roleKey(role));
  /** "ภูมิ · ผู้ทบทวน" for agents; plain "คุณ"/"ระบบ" otherwise. */
  const fullName = (role) => (["you", "system"].includes(roleKey(role)) ? roleName(role) : `${personaName(role)} · ${roleName(role)}`);
  function avatar(role, extra = "") {
    const key = roleKey(role);
    return UI.character(key, `avatar role-${key} ${extra}`.trim());
  }
  /** Briefly animate a character's mouth when its message arrives. */
  function talk(node, ms = 1600) {
    if (!node) return;
    node.classList.add("is-talking");
    setTimeout(() => node.classList.remove("is-talking"), ms);
  }
  function liveRemaining() {
    if (!s.room) return 0;
    if (!isActive()) return s.room.remaining_seconds;
    return Math.max(0, s.room.remaining_seconds - (performance.now() - s.receivedAt) / 1000);
  }
  function liveElapsed() {
    if (!s.room) return 0;
    if (!isActive()) return s.room.elapsed_seconds;
    return Math.min(s.room.time_limit, s.room.elapsed_seconds + (performance.now() - s.receivedAt) / 1000);
  }
  function reportUrl(format, lang) {
    const base = `/api/rooms/${s.room.room_id}/report?format=${format}`;
    return format === "json" ? base : `${base}&lang=${lang}`;
  }

  // ---------- setup view ----------
  function renderCases() {
    const list = $("case-list");
    list.replaceChildren();
    list.setAttribute("aria-busy", String(s.casesState === "loading"));
    if (s.casesState === "loading") {
      for (let i = 0; i < 4; i += 1) list.append(el("div", "case-card skeleton"));
      const live = el("p", "sr-only", t("casesLoading"));
      list.append(live);
    } else if (s.casesState === "error") {
      const box = el("div", "inline-error");
      box.append(icon("alert"), el("span", "", t("casesError")));
      const retry = el("button", "btn btn-small", t("retry"));
      retry.type = "button";
      retry.addEventListener("click", loadCases);
      box.append(retry);
      list.append(box);
    } else {
      s.cases.forEach((c) => {
        const label = el("label", "case-card");
        const input = el("input");
        input.type = "radio";
        input.name = "case";
        input.value = c.id;
        input.checked = c.id === s.selected;
        input.addEventListener("change", () => { s.selected = c.id; renderClaimPreview(); updateStartButton(); });
        const num = el("span", "case-num", c.id.split("-").pop());
        num.setAttribute("aria-hidden", "true");
        const text = el("span", "case-text");
        text.append(el("strong", "", UI.caseTitle(c)), el("small", "", UI.caseProcess(c)));
        label.append(input, num, text);
        list.append(label);
      });
    }
    renderClaimPreview();
    updateStartButton();
  }
  function renderClaimPreview() {
    const c = s.cases.find((x) => x.id === s.selected);
    $("case-claim").hidden = !c;
    if (c) $("case-claim-text").textContent = UI.caseClaim(c);
  }
  function readTime() {
    const choice = document.querySelector('input[name="time"]:checked')?.value || "60";
    if (choice !== "custom") return Number(choice);
    const raw = $("custom-time").value.trim();
    if (!/^\d{1,3}$/.test(raw)) return null;
    const value = Number(raw);
    return value >= 1 && value <= 300 ? value : null;
  }
  function setupError(text) {
    $("setup-error").hidden = !text;
    $("setup-error").textContent = text || "";
  }
  function updateStartButton() {
    const button = $("start-button");
    button.disabled = s.busy || s.casesState !== "ready" || !s.selected;
    $("start-label").textContent = t(s.busy && !s.room ? "starting" : "start");
    const c = s.cases.find((x) => x.id === s.selected);
    const time = readTime();
    const timeText = time === null ? t("custom") : time % 60 === 0 ? `${time / 60} ${UI.lang === "th" ? "นาที" : "min"}` : `${time} ${t("seconds")}`;
    $("start-summary").textContent = c ? `${UI.caseTitle(c)} · ${timeText}` : "";
  }
  async function loadCases() {
    s.casesState = "loading";
    renderCases();
    try {
      s.cases = (await api("/api/cases")).cases || [];
      s.casesState = "ready";
      const wanted = new URLSearchParams(location.search).get("case");
      if (wanted && CASE_ID.test(wanted) && s.cases.some((c) => c.id === wanted)) s.selected = wanted;
      if (!s.cases.some((c) => c.id === s.selected)) s.selected = s.cases[0]?.id || null;
    } catch (_) {
      s.casesState = "error";
    }
    renderCases();
  }

  async function startRoom(event) {
    event.preventDefault();
    if (s.busy) return;
    if (!s.selected) { setupError(t("chooseCaseFirst")); return; }
    const time = readTime();
    if (time === null) { setupError(t("invalidTime")); $("custom-time").focus(); return; }
    setupError("");
    s.busy = true;
    updateStartButton();
    try {
      const room = await api("/api/rooms", {
        case_id: s.selected,
        auditor_role: $("role-select").value,
        time_limit: time,
        interval_ms: Number($("pace").value),
      });
      rememberRoom(room);
      showRoom(room);
    } catch (error) {
      setupError(UI.errorText(error));
    } finally {
      s.busy = false;
      updateStartButton();
      renderControls();
    }
  }

  function goSetup() {
    clearTimeout(s.pollTimer);
    s.room = null; s.viewed = null; s.rendered = 0; s.stale = false; s.outcomeKey = null;
    $("message-list").replaceChildren();
    $("room-view").hidden = true;
    $("setup-view").hidden = false;
    $("timer").hidden = true;
    $("details-toggle").hidden = true;
    $("stage").hidden = true;
    $("stage").dataset.key = "";
    $("room-avatar").hidden = false;
    app.classList.remove("has-room", "details-open");
    history.replaceState(null, "", "/");
    renderHeader();
    renderHistory();
    sidebar.close();
    refreshHistoryStatuses();
    const checked = document.querySelector('input[name="case"]:checked') || document.querySelector('input[name="case"]');
    checked?.focus({ preventScroll: true });
  }

  // ---------- room view ----------
  function showRoom(room) {
    $("setup-view").hidden = true;
    $("room-view").hidden = false;
    $("details-toggle").hidden = false;
    app.classList.add("has-room");
    if (s.detailsPref === null) setDetails(false, false);
    history.replaceState(null, "", `/?room=${room.room_id}`);
    s.claimOpen = false;
    accept(room, true);
    sidebar.close();
    startPolling();
    $("chat-scroll").focus({ preventScroll: true });
  }

  function accept(room, force = false) {
    const same = s.room?.room_id === room.room_id;
    if (!force && same && room.messages.length < s.room.messages.length) return; // out-of-order response
    s.room = room;
    s.receivedAt = performance.now();
    s.stale = false;
    rememberRoom(room);
    render();
    if (!isActive()) clearTimeout(s.pollTimer);
  }

  function render(full = false) {
    if (!s.room) return;
    renderHeader();
    renderClaim();
    const scroller = $("chat-scroll");
    const nearBottom = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 160;
    const first = s.viewed !== s.room.room_id;
    const added = renderMessages(full);
    renderTyping();
    renderStage();
    const outcomeBefore = s.outcomeKey;
    renderOutcome(full);
    const outcomeNew = !first && !full && s.outcomeKey && s.outcomeKey !== outcomeBefore;
    renderControls();
    renderDetails();
    renderHistory();
    tick();
    if (first || outcomeNew || ((added || full) && nearBottom)) {
      scroller.scrollTop = scroller.scrollHeight;
      $("latest-button").hidden = true;
    } else if (added) {
      $("latest-button").hidden = false;
    }
  }

  function renderHeader() {
    const room = s.room;
    const title = $("room-title");
    const sub = $("room-subtitle");
    sub.replaceChildren();
    if (!room) {
      title.textContent = t("navChat");
      sub.append(el("span", "badge badge-muted", t("demoBadge")));
      document.title = `QA War Room · ${t("navChat")}`;
      return;
    }
    const c = room.session.case;
    title.textContent = UI.caseTitle(c);
    const statusKey = s.stale ? "stale" : room.status;
    const badge = el("span", `badge badge-${UI.tone(statusKey)}`);
    badge.append(el("span", "dot", ""), document.createTextNode(UI.status(statusKey)));
    sub.append(badge, el("span", "room-sub-text", `${room.turns} ${t("turns")} · ${evidence().length} ${t("recordsN")}`));
    document.title = `${UI.caseTitle(c)} · QA War Room`;
    $("timer").hidden = false;
  }

  function renderClaim() {
    const claim = UI.caseClaim(s.room.session.case);
    $("claim-short").textContent = claim;
    $("claim-full").textContent = claim;
    $("claim-full").hidden = !s.claimOpen;
    $("claim-toggle").setAttribute("aria-expanded", String(s.claimOpen));
    $("claim-toggle").classList.toggle("is-open", s.claimOpen);
  }

  function kindTag(m) {
    const key = `k_${m.kind}`;
    const label = t(key);
    return label === key ? null : el("span", `kind kind-${m.kind}`, label);
  }

  function attachments(m) {
    if (!m.citations?.length) return null;
    const wrap = el("div", "attachments");
    m.citations.forEach((id) => {
      const record = evidence().find((r) => r.id === id);
      if (!record) { wrap.append(el("span", "attach is-missing", id)); return; }
      const button = el("button", "attach");
      button.type = "button";
      button.append(UI.docIcon(record.document_type, "doc-icon attach-icon"));
      const text = el("span", "attach-text");
      text.append(el("strong", "", UI.recordTitle(record)), el("small", "", `${id} · ${t("revision")} ${record.revision}`));
      button.append(text);
      button.setAttribute("aria-label", `${t("read")}: ${UI.recordTitle(record)} (${id})`);
      button.addEventListener("click", () => openRecord(id, button));
      wrap.append(button);
    });
    return wrap;
  }

  // ---------- persona voice (display only; facts come from backend fields verbatim) ----------
  const VERDICT_EN = /^(?:Visible-evidence check|Proposed decision|Checked conclusion|Final draft decision): (supported|contradicted|insufficient)\. ([\s\S]*)$/;
  function afterLabelTh(text) {
    const m = /^[^:]+:\s*[^.]+\.\s*([\s\S]*)$/.exec(text || "");
    return m ? m[1] : null;
  }
  function catalogTitle(id, fallback) {
    const row = s.room?.session?.catalog?.find((r) => r.id === id);
    return UI.lang === "th" && row ? UI.recordTitle(row) : (row?.title || fallback);
  }
  function ownerOf(id) {
    const row = s.room?.session?.catalog?.find((r) => r.id === id);
    return row ? UI.persona(roleKey(row.owner)) : "";
  }
  function requesterBefore(m) {
    const prior = s.room.messages.filter((x) => x.seq < m.seq && x.kind === "request").pop();
    return prior?.role === "operator" ? UI.persona("you") : UI.persona("investigator");
  }
  /** Returns persona-voiced text, or null to show the system wording unchanged. */
  function voiced(m) {
    if (!s.room || m.role === "operator" || m.role === "coordinator") return null;
    const voice = UI.voiceFor(roleKey(m.role));
    const tpl = voice?.[m.kind];
    if (!tpl) return null;
    const th = UI.lang === "th";
    const base = { lead: UI.persona("investigator"), checker: UI.persona("checker") };
    let f = null;
    let r;
    if (m.kind === "request" && (r = /^Please provide (\S+) · (.+?) \((\d+) credit\)/.exec(m.text))) {
      f = { id: r[1], title: catalogTitle(r[1], r[2]), cost: r[3], owner: ownerOf(r[1]) };
    } else if (m.kind === "record" && (r = /^Delivered (\S+): (.+?)\. Revision (.+?) · (.+?)\. /.exec(m.text))) {
      f = { id: r[1], title: catalogTitle(r[1], r[2]), revision: r[3], date: r[4], requester: requesterBefore(m) };
    } else if (m.kind === "unavailable" && (r = /^(\S+): ([\s\S]+)$/.exec(m.text))) {
      const note = th ? (/^\S+:\s*([\s\S]+)$/.exec(m.text_th || "")?.[1] || r[2]) : r[2];
      f = { id: r[1], note };
    } else if (m.kind === "challenge" && (r = /^I cannot accept closure yet\. ([\s\S]*?) Requesting (\S+) before finalizing\.$/.exec(m.text))) {
      const rth = /^ยังยอมรับการปิดเคสไม่ได้\s*([\s\S]*?)\s*ขอเอกสาร \S+ ก่อนสรุปผล$/.exec(m.text_th || "");
      f = { id: r[2], title: catalogTitle(r[2], r[2]), owner: ownerOf(r[2]), rationale: th ? (rth ? rth[1] : null) : r[1] };
    } else if (["review", "proposal", "final_review", "decision"].includes(m.kind) && (r = VERDICT_EN.exec(m.text))) {
      f = { verdict: UI.verdict(r[1]), rationale: th ? afterLabelTh(m.text_th) : r[2] };
    }
    if (!f || Object.values(f).some((v) => v === null || v === undefined || v === "")) return null;
    return tpl({ ...base, ...f });
  }

  function originalToggle(m, bubble, shown) {
    const system = UI.message(m);
    const hasEnglish = UI.lang === "th" && m.text_th && m.text_th !== m.text;
    if (m.role === "operator" || (shown === system && !hasEnglish)) return null;
    const button = el("button", "orig-btn", t("systemText"));
    button.type = "button";
    button.setAttribute("aria-expanded", "false");
    const original = el("div", "orig");
    if (shown !== system) original.append(el("p", "", system));
    if (hasEnglish) {
      const en = el("p", "", m.text);
      en.lang = "en";
      original.append(en);
    }
    original.hidden = true;
    bubble.append(original);
    button.addEventListener("click", () => {
      original.hidden = !original.hidden;
      button.setAttribute("aria-expanded", String(!original.hidden));
    });
    return button;
  }

  function renderMessage(m) {
    const isSystem = m.role === "coordinator" || (m.role === "operator" && (m.kind === "paused" || m.kind === "resumed"));
    if (isSystem) {
      s.lastRole = null;
      const li = el("li", `msg msg-system tone-${m.role === "coordinator" ? UI.tone(m.kind === "started" ? "running" : m.kind) : "muted"}`);
      li.dataset.seq = m.seq;
      const pill = el("div", "system-pill");
      if (m.role === "operator") pill.append(el("strong", "", `${t(m.kind === "paused" ? "youPaused" : "youResumed")} · `));
      pill.append(document.createTextNode(UI.message(m)), el("time", "msg-time", UI.clock(m.elapsed_seconds)));
      li.append(pill);
      return li;
    }
    const own = m.role === "operator";
    const continued = s.lastRole === m.role;
    s.lastRole = m.role;
    const li = el("li", `msg ${own ? "msg-own" : "msg-agent"} ${continued ? "is-continued" : ""} ${m.kind === "decision" ? "msg-decision" : ""}`);
    li.dataset.seq = m.seq;
    if (!own) li.append(continued ? el("span", "avatar-spacer") : avatar(m.role));
    const body = el("div", "msg-body");
    if (!continued || own) {
      const meta = el("div", "msg-meta");
      meta.append(el("strong", "msg-name", own ? roleName(m.role) : personaName(m.role)));
      if (!own) meta.append(el("span", "msg-role", roleName(m.role)));
      const tag = kindTag(m);
      if (tag) meta.append(tag);
      body.append(meta);
    } else {
      const tag = kindTag(m);
      if (tag) { const meta = el("div", "msg-meta"); meta.append(tag); body.append(meta); }
    }
    const row = el("div", "bubble-row");
    const bubble = el("div", "bubble");
    const shown = voiced(m) || UI.message(m);
    const text = el("p", "bubble-text", shown);
    if (m.kind === "note") text.lang = "";
    bubble.append(text);
    const files = attachments(m);
    if (files) bubble.append(files);
    const orig = originalToggle(m, bubble, shown);
    if (orig) bubble.append(orig);
    row.append(bubble, el("time", "msg-time", UI.clock(m.elapsed_seconds)));
    body.append(row);
    li.append(body);
    return li;
  }

  function renderMessages(full) {
    const list = $("message-list");
    if (full || s.viewed !== s.room.room_id) {
      list.replaceChildren();
      s.rendered = 0; s.lastRole = null; s.viewed = s.room.room_id;
    }
    const incremental = s.rendered > 0;
    const fresh = s.room.messages.slice(s.rendered);
    const fragment = document.createDocumentFragment();
    const nodes = fresh.map((m) => renderMessage(m));
    nodes.forEach((n) => fragment.append(n));
    list.append(fragment);
    s.rendered = s.room.messages.length;
    if (incremental && isActive()) {
      // The newest speaker "talks"; continued messages animate the avatar above them.
      const last = [...list.querySelectorAll(".msg-agent")].pop();
      const speaker = last?.querySelector(".avatar") || (last && [...list.querySelectorAll(".msg-agent .avatar")].pop());
      if (nodes.includes(last)) talk(speaker);
    }
    return fresh.length;
  }

  function nextActor() {
    const r = s.room;
    if (!r || r.status !== "running" || s.stale) return null;
    const map = {
      investigator: [r.lead, "nextInvestigator"],
      custodian: [r.next_role || "user-02", "nextCustodian"],
      reviewer: [r.reviewer, "nextReviewer"],
      final_review: [r.reviewer, "nextFinal"],
      closeout: [r.lead, "nextCloseout"],
    };
    return map[r.phase] || null;
  }

  function renderTyping() {
    const next = nextActor();
    const typing = $("typing");
    if (!next || liveRemaining() <= 0) { typing.hidden = true; return; }
    const [role, key] = next;
    if (typing.dataset.role !== role) {
      const node = avatar(role, "is-talking");
      node.id = "typing-avatar";
      $("typing-avatar").replaceWith(node);
      typing.dataset.role = role;
    }
    $("typing-text").textContent = `${personaName(role)} (${roleName(role)}) ${t(key)}`;
    typing.hidden = false;
  }

  /** Team strip: who is speaking now (server's next phase) and who spoke last. */
  function renderStage() {
    const room = s.room;
    const stage = $("stage");
    const next = liveRemaining() > 0 ? nextActor()?.[0] : null;
    const lastMsg = [...room.messages].reverse().find((m) => m.role !== "coordinator" && m.role !== "operator");
    const last = lastMsg?.role;
    const key = `${room.room_id}|${next}|${last}|${room.status}|${UI.lang}|${s.stale}`;
    if (stage.dataset.key === key) return;
    stage.dataset.key = key;
    stage.replaceChildren();
    [room.lead, "user-01", "user-02", room.reviewer].forEach((role) => {
      const state = role === next ? "speaking" : "waiting";
      const label = isActive() ? `${fullName(role)} · ${t(state)}` : fullName(role);
      const member = el("span", `stack-member is-${state}`);
      member.setAttribute("role", "img");
      member.setAttribute("aria-label", label);
      member.title = label;
      member.append(avatar(role, `stack-avatar ${state === "speaking" ? "is-talking" : ""}`));
      stage.append(member);
    });
    stage.hidden = false;
    $("room-avatar").hidden = true;
  }

  function renderOutcome(full) {
    const box = $("outcome");
    const room = s.room;
    if (!TERMINAL.has(room.status) && !s.stale) { box.hidden = true; box.replaceChildren(); s.outcomeKey = null; return; }
    const key = `${room.room_id}:${s.stale ? "stale" : room.status}:${UI.lang}`;
    if (!full && key === s.outcomeKey) return;
    s.outcomeKey = key;
    box.replaceChildren();
    const status = s.stale ? "stale" : room.status;
    const completed = status === "completed";
    const card = el("div", `outcome-card tone-${UI.tone(status)}`);
    const iconName = completed ? "flag" : status === "time_limit" ? "hourglass" : status === "error" || status === "stale" ? "alert" : "stop";
    card.append(el("span", "outcome-icon"));
    card.lastChild.append(icon(iconName));
    const head = el("div", "outcome-head");
    const title = el("h3", "outcome-title", t(completed ? "outcomeCompleted" : "outcomePartial"));
    title.id = "outcome-title";
    const badge = el("span", `badge badge-${UI.tone(status)}`);
    badge.append(el("span", "dot"), document.createTextNode(UI.status(status)));
    head.append(title, badge);
    card.append(head);
    const body = completed ? t("outcomeCompletedText") : s.stale ? t("staleRoom") : t(`outcome_${status}`);
    card.append(el("p", "outcome-text", body));

    const decision = room.session.decision;
    if (completed && decision) {
      const verdict = el("div", "verdict-row");
      verdict.append(el("span", "", t("draftVerdict")), el("strong", `verdict verdict-${decision.verdict}`, UI.verdict(decision.verdict)));
      card.append(verdict);
    }
    card.append(el("p", "hint", `${t("keptCounts")} ${room.messages.length} ${t("messagesN")} · ${evidence().length} ${t("recordsN")}`));

    const feedback = room.session.feedback;
    if (completed && feedback) {
      const details = el("details", "compare");
      details.append(el("summary", "", t("compareTitle")));
      const line = el("p", "compare-line");
      line.append(el("span", "", `${t("referenceVerdict")}: `), el("strong", "", UI.verdict(feedback.expected_verdict)));
      if (decision) line.append(el("span", `compare-match ${feedback.expected_verdict === decision.verdict ? "is-match" : "is-diff"}`, t(feedback.expected_verdict === decision.verdict ? "matches" : "differs")));
      details.append(line);
      if (feedback.explanation) {
        const exp = el("p", "compare-exp", feedback.explanation);
        exp.lang = "en";
        details.append(exp);
      }
      details.append(el("p", "hint", t("compareNote")));
      card.append(details);
    }

    const actions = el("div", "outcome-actions");
    if (!s.stale) {
      const view = el("button", "btn btn-soft");
      view.type = "button";
      view.append(icon("file"), el("span", "", t("viewEvidence")));
      view.addEventListener("click", () => openEvidencePanel());
      actions.append(view);
      card.append(actions);
    }
    box.append(card);
    box.hidden = false;
  }

  function renderControls() {
    const room = s.room;
    const active = isActive();
    const paused = room?.status === "paused";
    $("pause-button").disabled = s.busy || !active;
    $("stop-button").disabled = s.busy || !active;
    $("note-input").disabled = s.busy || !active;
    $("send-note").disabled = s.busy || !active;
    $("pause-icon").replaceChildren(icon(paused ? "play" : "pause"));
    $("pause-label").textContent = t(paused ? "resume" : "pause");
    $("pause-button").classList.toggle("btn-primary", paused);
    $("pause-button").classList.toggle("btn-soft", !paused);
    $("paused-hint").hidden = !(active && paused);
    document.querySelector(".dock-row").hidden = Boolean(room) && !active;
    $("note-help").hidden = Boolean(room) && !active;
    $("ended-row").hidden = !room || active;
    $("ended-download").hidden = s.stale;
    if (room && !s.stale) $("ended-download").href = reportUrl("markdown", UI.lang);
    $("new-room").disabled = false;
    updateStartButton();
  }

  // ---------- details panel ----------
  function renderDetails() {
    const room = s.room;
    if (!room) return;
    // Progress stages
    const completed = room.status === "completed";
    const checking = ["final_review", "closeout"].includes(room.phase);
    const stage = completed ? 4 : checking ? 2 : 1;
    const halted = TERMINAL.has(room.status) && !completed;
    document.querySelectorAll("#stages li").forEach((li, i) => {
      li.classList.toggle("is-done", i < stage);
      li.classList.toggle("is-active", i === stage && !halted);
      li.classList.toggle("is-halted", i === stage && halted);
    });

    // Evidence and budget
    const session = room.session;
    const budget = session.budget;
    $("budget-text").textContent = `${t("used")} ${budget.spent}/${budget.total} ${t("credit")}`;
    $("budget-bar").style.width = `${budget.total ? Math.min(100, (budget.spent / budget.total) * 100) : 0}%`;
    const paused = room.status === "paused" && !s.stale;
    $("evidence-hint").textContent = isActive() ? (paused ? t("pausedHint") : t("requestNeedsPause")) : t("evidenceEmpty");
    renderEvidence();

    // Team
    const next = nextActor()?.[0];
    const list = $("participants");
    list.replaceChildren();
    [[room.lead, "roleInvestigator"], ["user-01", "roleOwner"], ["user-02", "roleOwner"], [room.reviewer, "roleChecker"]].forEach(([role, desc]) => {
      const li = el("li", `participant ${role === next ? "is-next" : ""}`);
      const info = el("div", "participant-info");
      info.append(el("strong", "", fullName(role)), el("small", "", `${UI.trait(roleKey(role))} · ${t(desc)}`));
      const state = role === next ? "stateNext" : TERMINAL.has(room.status) ? "stateDone" : "stateIdle";
      li.append(avatar(role), info, el("span", `participant-state state-${state}`, t(state)));
      const prompt = UI.systemPrompt(roleKey(role));
      if (prompt) {
        const details = el("details", "persona-prompt");
        details.append(el("summary", "", t("showPrompt")), el("p", "", prompt));
        li.append(details);
      }
      list.append(li);
    });

    // Downloads
    const canDownload = !s.stale;
    ["download-th", "download-en", "download-json"].forEach((id) => { $(id).hidden = !canDownload; });
    if (canDownload) {
      $("download-th").href = reportUrl("markdown", "th");
      $("download-en").href = reportUrl("markdown", "en");
      $("download-json").href = reportUrl("json");
    }
  }

  function renderEvidence() {
    const room = s.room;
    if (!room) return;
    const session = room.session;
    const list = $("evidence-list");
    list.replaceChildren();
    const paused = room.status === "paused" && !s.stale;
    session.catalog.forEach((record) => {
      const delivered = evidence().some((r) => r.id === record.id);
      const li = el("li", `evidence-row ${delivered ? "is-received" : record.requested ? "is-unavailable" : ""}`);
      li.append(UI.docIcon(record.document_type, "doc-icon evidence-icon"));
      const info = el("div", "evidence-info");
      const state = delivered ? t("received") : record.requested ? t("unavailable") : `${t("notRequested")} · ${record.cost} ${t("credit")}`;
      info.append(el("strong", "", UI.recordTitle(record)), el("small", "", `${record.id} · ${state}`));
      li.append(info);
      if (delivered) {
        const button = el("button", "btn btn-small btn-soft", t("read"));
        button.type = "button";
        button.setAttribute("aria-label", `${t("read")}: ${UI.recordTitle(record)} (${record.id})`);
        button.addEventListener("click", () => openRecord(record.id, button));
        li.append(button);
      } else if (!record.requested && isActive()) {
        const button = el("button", "btn btn-small btn-outline", t("request"));
        button.type = "button";
        button.disabled = s.busy || !paused || record.cost > session.budget.remaining;
        button.title = paused ? "" : t("requestNeedsPause");
        button.setAttribute("aria-label", `${t("request")}: ${UI.recordTitle(record)} (${record.id})`);
        button.addEventListener("click", () => action(async () => {
          accept(await api(`/api/rooms/${room.room_id}/request`, { evidence_id: record.id }));
        }));
        li.append(button);
      }
      list.append(li);
    });
  }

  function setDetails(open, remember = true) {
    app.classList.toggle("details-open", open);
    $("details-toggle").setAttribute("aria-expanded", String(open));
    if (remember) s.detailsPref = open;
  }
  function openEvidencePanel() {
    setDetails(true);
    const section = $("evidence-section");
    section.scrollIntoView({ block: "start", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    const target = section.querySelector("button:not(:disabled)") || $("details-close");
    target.focus({ preventScroll: true });
  }

  // ---------- record viewer ----------
  function openRecord(id, opener) {
    const record = evidence().find((r) => r.id === id); // received records only
    if (!record) return;
    s.opener = opener || document.activeElement;
    $("record-title").textContent = `${UI.recordTitle(record)} · ${record.id}`;
    $("record-icon").replaceChildren(UI.docIcon(record.document_type, "doc-icon"));
    $("record-meta").textContent = `${t("revision")} ${record.revision} · ${t("dated")} ${record.date} · ${t("from")} ${fullName(record.owner)}`;
    const facts = $("record-facts");
    facts.replaceChildren();
    const add = (label, value) => {
      const row = el("div", "fact");
      const text = typeof value === "boolean" ? t(value ? "yes" : "no") : Array.isArray(value) ? value.join(", ") : String(value);
      row.append(el("dt", "", label), el("dd", "", text));
      facts.append(row);
    };
    const walk = (obj, prefix) => Object.entries(obj || {}).forEach(([key, value]) => {
      const label = prefix ? `${prefix} · ${UI.factLabel(key)}` : UI.factLabel(key);
      if (value && typeof value === "object" && !Array.isArray(value)) walk(value, label);
      else add(label, value);
    });
    walk(record.facts, "");
    $("record-content").textContent = record.content;
    $("record-dialog").querySelector("details").open = false;
    $("record-dialog").showModal();
  }

  // ---------- history ----------
  function renderHistory() {
    const box = $("room-history");
    box.replaceChildren();
    if (!s.history.length) { box.append(el("p", "history-empty", t("emptyHistory"))); return; }
    const list = el("ul", "history-list");
    s.history.forEach((entry) => {
      const c = s.cases.find((x) => x.id === entry.caseId) || s.cases.find((x) => x.title === entry.title);
      const li = el("li");
      const button = el("button", `history-item ${entry.id === s.room?.room_id ? "is-current" : ""}`);
      button.type = "button";
      if (entry.id === s.room?.room_id) button.setAttribute("aria-current", "true");
      const text = el("span", "history-text");
      text.append(el("strong", "", c ? UI.caseTitle(c) : entry.title));
      const status = el("small", "");
      status.append(el("span", `dot dot-${UI.tone(entry.status)}`), document.createTextNode(entry.status ? UI.status(entry.status) : ""));
      text.append(status);
      button.append(text);
      button.addEventListener("click", () => openRoomById(entry.id));
      li.append(button);
      list.append(li);
    });
    box.append(list);
  }

  async function refreshHistoryStatuses() {
    if (!s.history.length) return;
    try {
      const overview = await api("/api/rooms");
      const live = new Map(overview.rooms.map((r) => [r.room_id, r.status]));
      const before = s.history.length;
      s.history = s.history.filter((h) => live.has(h.id)).map((h) => ({ ...h, status: live.get(h.id) }));
      saveHistory();
      renderHistory();
      if (s.history.length < before) showBanner(t("staleRoom"), "info");
    } catch (_) { /* the banner for connectivity comes from other requests */ }
  }

  async function openRoomById(id) {
    if (s.busy) return;
    s.busy = true;
    try {
      const room = await api(`/api/rooms/${id}`);
      hideBanner();
      showRoom(room);
    } catch (error) {
      if (error.code === "unknown_room" || error.status === 404) {
        forgetRoom(id);
        showBanner(t("staleRoom"), "warn");
        if (s.room?.room_id === id || !s.room) goSetup();
      } else {
        showBanner(UI.errorText(error), "danger", true);
      }
    } finally {
      s.busy = false;
      renderControls();
    }
  }

  function markStale() {
    s.stale = true;
    clearTimeout(s.pollTimer);
    if (s.room) forgetRoom(s.room.room_id);
    showBanner(t("staleRoom"), "warn");
    render(true);
  }

  // ---------- polling and actions ----------
  function startPolling() {
    clearTimeout(s.pollTimer);
    if (isActive()) s.pollTimer = setTimeout(poll, POLL_MS);
  }
  async function poll() {
    const id = s.room?.room_id;
    if (!id || !isActive()) return;
    try {
      const room = await api(`/api/rooms/${id}`);
      if (s.room?.room_id !== id) return;
      if (s.failures) { s.failures = 0; showBanner(t("reconnected"), "ok"); }
      accept(room);
    } catch (error) {
      if (s.room?.room_id !== id) return;
      if (error.code === "unknown_room") { markStale(); return; }
      s.failures += 1;
      showBanner(t("connectionLost"), "warn", true);
    }
    if (s.room?.room_id === id && isActive()) {
      s.pollTimer = setTimeout(poll, s.failures ? Math.min(5000, 1000 * s.failures) : POLL_MS);
    }
  }

  async function action(work) {
    if (s.busy) return;
    s.busy = true;
    renderControls();
    renderEvidence();
    try {
      await work();
    } catch (error) {
      if (error.code === "unknown_room") { markStale(); }
      else {
        showBanner(UI.errorText(error), "danger");
        if (error.status === 409 && s.room) {
          try { accept(await api(`/api/rooms/${s.room.room_id}`)); } catch (_) { /* polling will retry */ }
        }
      }
    } finally {
      s.busy = false;
      renderControls();
      renderEvidence();
      startPolling();
    }
  }

  // Smooth countdown between polls; the server remains the source of truth.
  function tick() {
    if (!s.room) return;
    const remaining = liveRemaining();
    const elapsed = liveElapsed();
    const timer = $("timer");
    const terminal = !isActive();
    // Active: time left. Ended: time actually used (a finished room has no meaningful countdown).
    $("countdown").textContent = UI.clock(terminal ? elapsed : remaining);
    timer.classList.toggle("is-low", !terminal && remaining <= 10);
    timer.classList.toggle("is-paused", s.room.status === "paused" && !s.stale);
    timer.classList.toggle("is-ended", terminal);
    const mode = terminal ? "flag" : "clock";
    if (timer.dataset.mode !== mode) {
      timer.replaceChild(icon(mode), timer.firstElementChild);
      timer.dataset.mode = mode;
    }
    $("elapsed-text").textContent = `${UI.clock(elapsed)} / ${UI.clock(s.room.time_limit)}`;
    $("time-bar").style.width = `${Math.min(100, (elapsed / s.room.time_limit) * 100)}%`;
    let label = t(terminal ? "elapsed" : "timeLeft");
    if (!terminal && remaining <= 0) {
      $("typing").hidden = true;
      label = t("timeUp");
    }
    timer.title = label;
    timer.querySelector(".sr-only").textContent = label;
  }

  // ---------- events ----------
  const sidebar = UI.bindSidebar(app);
  $("setup-form").addEventListener("submit", startRoom);
  document.querySelectorAll('input[name="time"]').forEach((input) => input.addEventListener("change", () => {
    const custom = input.value === "custom" && input.checked;
    $("custom-time-row").hidden = !custom;
    if (custom) $("custom-time").focus();
    setupError("");
    updateStartButton();
  }));
  $("custom-time").addEventListener("input", () => { setupError(""); updateStartButton(); });
  $("new-room").addEventListener("click", goSetup);
  $("ended-new").addEventListener("click", goSetup);
  $("pause-button").addEventListener("click", () => {
    if (!isActive()) return;
    const verb = s.room.status === "paused" ? "resume" : "pause";
    action(async () => accept(await api(`/api/rooms/${s.room.room_id}/${verb}`, {})));
  });
  $("stop-button").addEventListener("click", () => { if (isActive()) $("stop-dialog").showModal(); });
  $("stop-dialog").addEventListener("close", () => {
    if ($("stop-dialog").returnValue === "stop" && isActive()) {
      action(async () => accept(await api(`/api/rooms/${s.room.room_id}/stop`, {})));
    }
    $("stop-button").focus();
  });
  $("composer").addEventListener("submit", (event) => {
    event.preventDefault();
    const input = $("note-input");
    const text = input.value.trim();
    if (!text || !isActive()) return;
    action(async () => {
      accept(await api(`/api/rooms/${s.room.room_id}/note`, { text }));
      input.value = "";
    });
  });
  $("paused-evidence").addEventListener("click", openEvidencePanel);
  $("claim-toggle").addEventListener("click", () => { s.claimOpen = !s.claimOpen; renderClaim(); });
  $("details-toggle").addEventListener("click", () => setDetails(!app.classList.contains("details-open")));
  $("details-close").addEventListener("click", () => { setDetails(false); $("details-toggle").focus(); });
  $("record-close").addEventListener("click", () => $("record-dialog").close());
  $("record-dialog").addEventListener("click", (event) => { if (event.target === $("record-dialog")) $("record-dialog").close(); });
  $("record-dialog").addEventListener("close", () => { s.opener?.focus?.(); s.opener = null; });
  $("banner-close").addEventListener("click", hideBanner);
  $("banner-retry").addEventListener("click", async () => {
    if (s.room) {
      try { accept(await api(`/api/rooms/${s.room.room_id}`)); s.failures = 0; hideBanner(); startPolling(); }
      catch (error) { if (error.code === "unknown_room") markStale(); else showBanner(t("connectionLost"), "warn", true); }
    } else {
      hideBanner();
      loadCases();
    }
  });
  $("latest-button").addEventListener("click", () => {
    const scroller = $("chat-scroll");
    scroller.scrollTop = scroller.scrollHeight;
    $("latest-button").hidden = true;
  });
  $("chat-scroll").addEventListener("scroll", () => {
    const scroller = $("chat-scroll");
    if (scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 90) $("latest-button").hidden = true;
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || document.querySelector("dialog[open]")) return;
    if (app.classList.contains("nav-open")) { sidebar.close(); $("nav-toggle").focus(); }
    else if (app.classList.contains("details-open") && !wide.matches) { setDetails(false); $("details-toggle").focus(); }
  });
  $("scrim").addEventListener("click", () => { if (!wide.matches) setDetails(false); });
  document.addEventListener("visibilitychange", () => { if (!document.hidden && isActive()) { clearTimeout(s.pollTimer); poll(); } });
  document.addEventListener("qa-language", () => {
    renderCases();
    renderHistory();
    if (s.room) render(true); else renderHeader();
    renderControls();
  });

  // ---------- start ----------
  UI.mount();
  renderHeader();
  renderHistory();
  renderControls();
  setInterval(tick, 250);
  (async () => {
    await Promise.all([loadCases(), UI.charactersReady]);
    $("setup-lineup").replaceChildren(UI.lineup());
    renderHistory();
    const roomParam = new URLSearchParams(location.search).get("room");
    if (roomParam && ROOM_ID.test(roomParam)) await openRoomById(roomParam);
    else refreshHistoryStatuses();
  })();
})();
