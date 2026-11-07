"use strict";
/*
 * Dashboard: renders only what GET /api/rooms and GET /api/cases return for this local
 * server process. No scores, charts or activity are invented; every number is a count of
 * actual room records. Data resets when the server restarts.
 */
(() => {
  const { t, el, icon } = UI;
  const $ = (id) => document.getElementById(id);
  const app = $("app");
  const REFRESH_MS = 5000;
  const STATUS_ORDER = ["running", "paused", "completed", "time_limit", "stopped", "turn_limit", "error"];
  const UNFINISHED = new Set(["time_limit", "stopped", "turn_limit", "error"]);
  const FILTERS = {
    all: () => true,
    active: (r) => r.status === "running" || r.status === "paused",
    done: (r) => r.status === "completed",
    unfinished: (r) => UNFINISHED.has(r.status),
  };
  const FILTER_LABEL = { all: "filterAll", active: "filterActive", done: "filterDone", unfinished: "filterUnfinished" };

  const s = { overview: null, cases: null, filter: "all", updated: null, failed: false, loading: false, timer: null };

  async function getJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  function setKpi(id, value) {
    const node = $(id);
    node.classList.toggle("is-loading", value === null);
    node.textContent = value === null ? "—" : String(value);
  }

  function counts(rooms) {
    const c = Object.fromEntries(STATUS_ORDER.map((k) => [k, 0]));
    rooms.forEach((r) => { c[r.status] = (c[r.status] || 0) + 1; });
    return c;
  }

  function renderKpis() {
    const o = s.overview;
    if (!o) { ["kpi-cases", "kpi-rooms", "kpi-active", "kpi-completed", "kpi-unfinished"].forEach((id) => setKpi(id, null)); return; }
    const c = counts(o.rooms);
    setKpi("kpi-cases", o.case_count);
    setKpi("kpi-rooms", o.rooms.length);
    setKpi("kpi-active", c.running + c.paused);
    setKpi("kpi-completed", c.completed);
    setKpi("kpi-unfinished", c.time_limit + c.stopped + c.turn_limit + c.error);
  }

  function renderMix() {
    const bar = $("status-bar");
    const legend = $("legend");
    bar.replaceChildren();
    legend.replaceChildren();
    const rooms = s.overview?.rooms || [];
    $("mix-empty").hidden = rooms.length > 0 || !s.overview;
    bar.hidden = rooms.length === 0;
    legend.hidden = rooms.length === 0;
    if (!rooms.length) return;
    const c = counts(rooms);
    const parts = [];
    STATUS_ORDER.forEach((status) => {
      if (!c[status]) return;
      const seg = el("span", `seg-${status}`);
      seg.style.flexGrow = String(c[status]);
      seg.title = `${UI.status(status)}: ${c[status]}`;
      bar.append(seg);
      const li = el("li");
      const swatch = el("i", `seg-${status}`);
      swatch.setAttribute("aria-hidden", "true");
      li.append(swatch, el("span", "", UI.status(status)), el("strong", "", String(c[status])));
      legend.append(li);
      parts.push(`${UI.status(status)} ${c[status]}`);
    });
    bar.setAttribute("aria-label", parts.join(", "));
  }

  function renderFilters() {
    const box = $("filters");
    box.replaceChildren();
    const rooms = s.overview?.rooms || [];
    Object.keys(FILTERS).forEach((key) => {
      const button = el("button", "filter");
      button.type = "button";
      button.setAttribute("aria-pressed", String(s.filter === key));
      button.append(document.createTextNode(t(FILTER_LABEL[key])), el("span", "count", String(rooms.filter(FILTERS[key]).length)));
      button.addEventListener("click", () => { s.filter = key; renderFilters(); renderRooms(); });
      box.append(button);
    });
  }

  function renderRooms() {
    const box = $("rooms");
    if (!s.overview) return; // keep skeleton while loading
    box.replaceChildren();
    const rooms = s.overview.rooms.slice().reverse(); // newest first (server keeps insertion order)
    if (!rooms.length) {
      const empty = el("div", "empty");
      const ic = el("span", "empty-icon");
      ic.append(icon("chat"));
      const link = el("a", "btn btn-primary");
      link.href = "/";
      link.append(icon("plus"), el("span", "", t("newRoom")));
      empty.append(ic, el("h3", "", t("noRoomsTitle")), el("p", "", t("noRoomsText")), link);
      box.append(empty);
      return;
    }
    const visible = rooms.filter(FILTERS[s.filter]);
    if (!visible.length) { box.append(el("p", "empty hint", t("noMatch"))); return; }
    const list = el("ul", "room-list");
    visible.forEach((room) => {
      const li = el("li", "room-row");
      const main = el("div", "room-row-main");
      main.append(
        el("strong", "", UI.caseTitle(room.case)),
        el("small", "", `${room.records_received} ${t("recordsN")} · ${room.message_count} ${t("messagesN")} · ${t("duration")} ${UI.clock(room.elapsed_seconds)}`),
      );
      const badge = el("span", `badge badge-${UI.tone(room.status)}`);
      badge.append(el("span", "dot"), document.createTextNode(UI.status(room.status)));
      const open = el("a", "btn btn-small btn-soft");
      open.href = `/?room=${encodeURIComponent(room.room_id)}`;
      open.append(el("span", "", t("openRoom")), icon("arrow"));
      open.setAttribute("aria-label", `${t("openRoom")}: ${UI.caseTitle(room.case)} (${UI.status(room.status)})`);
      li.append(main, badge, open);
      list.append(li);
    });
    box.append(list);
  }

  function renderCases() {
    const list = $("case-usage");
    if (!s.cases) return;
    list.replaceChildren();
    const rooms = s.overview?.rooms || [];
    s.cases.forEach((c) => {
      const used = rooms.filter((r) => r.case.id === c.id).length;
      const li = el("li");
      const num = el("span", "case-num", c.id.split("-").pop());
      num.setAttribute("aria-hidden", "true");
      const main = el("div", "case-usage-main");
      main.append(el("strong", "", UI.caseTitle(c)), el("small", "", `${UI.caseProcess(c)} · ${used} ${t("roomsUsed")}`));
      const link = el("a", "", t("useCase"));
      link.href = `/?case=${encodeURIComponent(c.id)}`;
      link.setAttribute("aria-label", `${t("useCase")}: ${UI.caseTitle(c)}`);
      li.append(num, main, link);
      list.append(li);
    });
  }

  function renderUpdated() {
    const text = $("updated-text");
    const dot = $("updated-dot");
    if (s.failed) { dot.className = "dot dot-danger"; text.textContent = s.updated ? `${t("staleData")} ${t("updatedAt")} ${UI.timeOfDay(s.updated)}` : t("dashError"); return; }
    dot.className = s.updated ? "dot dot-live" : "dot dot-muted";
    text.textContent = s.updated ? `${t("updatedAt")} ${UI.timeOfDay(s.updated)} · ${t("autoRefresh")}` : "";
  }

  function renderAll() {
    renderKpis();
    renderMix();
    renderFilters();
    renderRooms();
    renderCases();
    renderUpdated();
  }

  async function refresh() {
    if (s.loading) return;
    s.loading = true;
    $("refresh").disabled = true;
    try {
      const [overview, cases] = await Promise.all([getJson("/api/rooms"), s.cases ? Promise.resolve(null) : getJson("/api/cases")]);
      s.overview = overview;
      if (cases) s.cases = cases.cases || [];
      s.updated = new Date();
      s.failed = false;
      $("banner").hidden = true;
    } catch (_) {
      s.failed = true;
      $("banner-text").textContent = s.overview ? `${t("dashError")} ${t("staleData")}` : t("dashError");
      $("banner").hidden = false;
      if (!s.overview) {
        $("rooms").replaceChildren(el("p", "empty hint", t("dashError")));
      }
    } finally {
      s.loading = false;
      $("refresh").disabled = false;
      renderAll();
      schedule();
    }
  }

  function schedule() {
    clearTimeout(s.timer);
    if (!document.hidden) s.timer = setTimeout(refresh, s.failed ? REFRESH_MS * 2 : REFRESH_MS);
  }

  UI.mount();
  const sidebar = UI.bindSidebar(app);
  $("refresh").addEventListener("click", refresh);
  $("banner-retry").addEventListener("click", refresh);
  document.addEventListener("qa-language", renderAll);
  document.addEventListener("visibilitychange", () => { if (document.hidden) clearTimeout(s.timer); else refresh(); });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && app.classList.contains("nav-open")) { sidebar.close(); $("nav-toggle").focus(); }
  });
  renderAll();
  refresh();
  UI.charactersReady.then(() => $("hero-lineup").replaceChildren(UI.lineup()));
})();
