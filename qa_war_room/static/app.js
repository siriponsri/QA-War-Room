"use strict";

// This client never creates a reference verdict. It displays only server-returned
// evidence, and it renders all case content as text rather than executable HTML.
const state = { cases: [], personas: [], session: null, selectedEvidence: null, busy: false };
const $ = (id) => document.getElementById(id);
const element = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
};

function message(text, error = false) {
  $("message").textContent = text;
  $("message").classList.toggle("is-error", error);
  $("message").hidden = !text;
}

async function api(path, body) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(path, {
      method: body === undefined ? "GET" : "POST",
      headers: body === undefined ? { Accept: "application/json" } : { Accept: "application/json", "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: "same-origin",
      signal: controller.signal,
    });
    let data;
    try { data = await response.json(); }
    catch { throw new Error("The server returned an unreadable response. Check that the local QA War Room server is running."); }
    if (!response.ok) throw new Error(data?.error?.message || `Request failed (${response.status}).`);
    return data;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("The local server did not respond in time. Your current form has been kept; try again.");
    if (error instanceof TypeError) throw new Error("Cannot reach the local server. Start it, then reload this page.");
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

function setBusy(value) {
  state.busy = value;
  document.body.classList.toggle("is-busy", value);
  $("start-button").disabled = value || !state.cases.length;
  $("case-select").disabled = value;
  $("role-select").disabled = value;
  const active = state.session?.status === "active";
  $("decision-fields").disabled = value || !active;
  $("step-button").disabled = value || !active;
  document.querySelectorAll(".record-action").forEach((button) => {
    button.disabled = value || button.dataset.unavailable === "true";
  });
}

async function task(action) {
  if (state.busy) return;
  message("");
  setBusy(true);
  try { await action(); }
  catch (error) { message(error.message || "The action could not be completed.", true); }
  finally { setBusy(false); }
}

function selectedCase() {
  return state.cases.find((item) => item.id === $("case-select").value);
}

function renderPreview() {
  const item = selectedCase();
  $("case-brief").textContent = item?.brief || "Choose a manufacturing scenario.";
  if (!state.session) $("case-claim").textContent = item?.claim || "Choose a scenario and start a session to inspect its evidence.";
  if (state.session && state.session.case.id !== item?.id) {
    $("case-brief").textContent = `${item?.brief || ""} Start a new session to open this case; the current investigation stays visible until then.`;
  }
  renderRoles();
}

function renderRoles() {
  const container = $("role-list");
  container.replaceChildren();
  const current = state.session?.auditor_role || $("role-select").value;
  state.personas.forEach((persona, index) => {
    const row = element("div", "role-item");
    row.dataset.kind = persona.kind || (persona.id.startsWith("user-") ? "auditee" : "auditor");
    row.classList.toggle("is-selected", persona.id === current);
    row.title = persona.description || persona.label || persona.id;
    const avatar = element("span", "role-avatar", persona.id.startsWith("user-") ? `U${index + 1}` : persona.id.includes("expert") ? "EX" : "JR");
    avatar.setAttribute("aria-hidden", "true");
    const text = element("span");
    text.append(element("strong", "", persona.id), element("small", "", persona.label || (persona.id.startsWith("user-") ? "Records owner" : "Scripted auditor")));
    row.append(avatar, text);
    container.append(row);
  });
}

function renderHeader() {
  const session = state.session;
  if (!session) return;
  const complete = session.status === "completed";
  const budget = session.budget;
  $("case-claim").textContent = session.case.claim;
  $("budget-remaining").textContent = budget.remaining;
  $("budget-total").textContent = budget.total;
  const spentPercent = Math.min(100, Math.max(0, 100 * budget.spent / Math.max(1, budget.total)));
  $("budget-fill").style.width = `${spentPercent}%`;
  $("budget-meter").setAttribute("aria-valuenow", String(Math.round(spentPercent)));
  $("budget-meter").setAttribute("aria-valuetext", `${budget.spent} of ${budget.total} units spent`);
  $("budget-meter").classList.toggle("is-low", budget.remaining <= budget.total * 0.25);
  $("budget-description").textContent = `${budget.spent} units spent. Reopening an already requested record is free.`;
  $("session-status").textContent = complete ? "COMPLETED" : "IN PROGRESS";
  $("session-status").className = `badge ${complete ? "badge-completed" : "badge-active"}`;
  $("session-short-id").textContent = session.session_id.slice(0, 12);
  $("session-short-id").title = session.session_id;
  $("session-as-of").textContent = `Assess records as of ${session.case.as_of || "the case date"}.`;
  $("session-doc-count").replaceChildren(element("strong", "", session.evidence.length), document.createTextNode(" records returned"));
  $("catalog-count").textContent = session.catalog.length;
  const requested = session.catalog.filter((record) => record.requested).length;
  $("requested-count").textContent = `${requested} / ${session.catalog.length} requested`;
  $("start-button").replaceChildren(document.createTextNode("New session "), element("span", "", "↗"));
  $("phase-brief").className = "phase is-done";
  $("phase-evidence").className = `phase ${complete ? "is-done" : "is-active"}`;
  $("phase-decision").className = `phase ${complete ? "is-done" : ""}`;
  $("phase-debrief").className = `phase ${complete ? "is-active" : ""}`;
}

function renderCatalog() {
  const container = $("evidence-catalog");
  container.replaceChildren();
  const session = state.session;
  if (!session) return;
  session.catalog.forEach((record) => {
    const retrieved = session.evidence.find((item) => item.id === record.id);
    const missing = record.requested && !retrieved;
    const row = element("article", "evidence-row");
    row.classList.toggle("is-retrieved", Boolean(retrieved));
    row.classList.toggle("is-missing", missing);
    row.classList.toggle("is-selected", state.selectedEvidence === record.id);
    row.append(element("span", "document-symbol", "▤"));
    const info = element("div", "evidence-info");
    info.append(element("h3", "evidence-title", record.title));
    info.append(element("p", "evidence-meta", [record.id, record.revision ? `rev ${record.revision}` : null, record.date].filter(Boolean).join(" · ")));
    info.append(element("p", `evidence-state ${missing ? "is-missing" : ""}`, retrieved ? `Retrieved · ${record.owner}` : missing ? "Requested · No record returned" : `${record.document_type} · ${record.owner}`));
    row.append(info);
    const button = element("button", `record-action ${retrieved ? "has-record" : missing ? "no-record" : ""}`);
    button.type = "button";
    const unavailable = !record.requested && (session.status !== "active" || record.cost > session.budget.remaining);
    button.dataset.unavailable = String(unavailable);
    button.disabled = state.busy || unavailable;
    button.setAttribute("aria-label", record.requested ? `Read response for ${record.title}` : `Request ${record.title}; cost ${record.cost} budget units`);
    if (record.requested) {
      button.textContent = retrieved ? "Read ↗" : "Response";
      button.addEventListener("click", () => { state.selectedEvidence = record.id; renderCatalog(); renderReader(); });
    } else {
      button.append(document.createTextNode("Request"), element("span", "cost", `${record.cost} ${record.cost === 1 ? "unit" : "units"}`));
      if (unavailable) button.title = session.status === "completed" ? "This session has ended." : "This request exceeds the remaining budget.";
      button.addEventListener("click", () => task(async () => {
        const updated = await api(`/api/sessions/${encodeURIComponent(session.session_id)}/request`, { evidence_id: record.id });
        state.selectedEvidence = record.id;
        acceptSession(updated);
        message(updated.evidence.some((item) => item.id === record.id) ? `Retrieved ${record.id}. Read the record, then decide whether it supports your reasoning.` : `${record.id} was requested, but no record was returned. This alone does not establish a GMP violation.`);
      }));
    }
    row.append(button);
    container.append(row);
  });
}

function renderReader() {
  const session = state.session;
  const metadata = $("reader-metadata");
  const catalogItem = session?.catalog.find((item) => item.id === state.selectedEvidence);
  const record = session?.evidence.find((item) => item.id === state.selectedEvidence);
  metadata.replaceChildren();
  metadata.hidden = !catalogItem;
  $("reader-content").hidden = !record;
  $("reader-empty").hidden = Boolean(record);
  if (!catalogItem) {
    $("reader-code").textContent = "DOCUMENT VIEWER";
    $("reader-title").textContent = "No record selected";
    $("reader-badge").textContent = "EVIDENCE";
    $("reader-empty").textContent = "Request a record, then read its contents here. A document title alone is not evidence for a verdict.";
    $("reader-content").textContent = "";
    return;
  }
  $("reader-code").textContent = `RECORD ${catalogItem.id}`;
  $("reader-title").textContent = catalogItem.title;
  $("reader-badge").textContent = record ? "RETRIEVED" : "NO RECORD";
  for (const [label, value] of [["Owner", catalogItem.owner], ["Revision", catalogItem.revision], ["Date", catalogItem.date]]) {
    if (value) metadata.append(element("span", "", `${label}: ${value}`));
  }
  if (record) $("reader-content").textContent = record.content;
  else {
    $("reader-content").textContent = "";
    $("reader-empty").textContent = "The records owner did not return this artifact in the authored scenario. Its request cost was consumed. Consider what can and cannot be concluded from the remaining records.";
  }
}

function currentCitations() {
  return Array.from(document.querySelectorAll("#citation-list input:checked"), (input) => input.value);
}

function renderCitations() {
  const session = state.session;
  const selected = new Set(session.decision?.evidence_ids || currentCitations());
  const container = $("citation-list");
  container.replaceChildren();
  if (!session.evidence.length) {
    container.append(element("p", "citation-empty", "No records retrieved yet."));
    return;
  }
  session.evidence.forEach((record) => {
    const label = element("label", "citation-item");
    const input = element("input");
    input.type = "checkbox";
    input.name = "evidence_id";
    input.value = record.id;
    input.checked = selected.has(record.id);
    const title = element("span");
    title.append(element("strong", "", record.id), document.createTextNode(` · ${record.title}`));
    label.append(input, title);
    container.append(label);
  });
}

function renderEvents() {
  const events = state.session?.events || [];
  const list = $("event-list");
  list.replaceChildren();
  $("event-count").textContent = `${events.length} ${events.length === 1 ? "event" : "events"}`;
  if (!events.length) { list.append(element("li", "empty-log", "Evidence requests and decisions will appear here.")); return; }
  events.forEach((event) => {
    const row = element("li", "event-item");
    row.append(element("span", "event-seq", String(event.seq).padStart(2, "0")), element("span", "event-role", event.role || "system"), element("span", "event-message", event.message));
    list.append(row);
  });
}

function addDebriefList(container, title, values) {
  if (!Array.isArray(values) || !values.length) return;
  container.append(element("h3", "", title));
  const list = element("ul");
  values.forEach((value) => list.append(element("li", "", typeof value === "string" ? value : JSON.stringify(value))));
  container.append(list);
}

function renderDebrief() {
  const session = state.session;
  const feedback = session?.status === "completed" ? session.feedback : null;
  $("debrief-panel").hidden = !feedback;
  if (!feedback) return;
  const metrics = $("debrief-metrics");
  metrics.replaceChildren();
  for (const [label, pass, positive, negative] of [
    ["Reference verdict", feedback.verdict_correct, "Matches", "Does not match"],
    ["Reference-set coverage", feedback.evidence_support_complete, "Complete", "Incomplete"],
  ]) {
    const metric = element("div", `debrief-metric ${pass ? "" : "is-fail"}`);
    metric.append(element("span", "", label), element("strong", "", pass ? positive : negative));
    metrics.append(metric);
  }
  const details = $("debrief-details");
  details.replaceChildren();
  details.append(element("h3", "", `Authored reference: ${feedback.expected_verdict}`), element("p", "", feedback.explanation));
  addDebriefList(details, "Reference records missing from submitted citations", feedback.missing_support);
  addDebriefList(details, "Citations rejected by the evaluator", feedback.unsupported_citations);
  addDebriefList(details, "Citations outside the reference set (may still be relevant)", feedback.citations_not_in_reference);
  addDebriefList(details, "Requested records not returned", feedback.requested_unavailable);
  addDebriefList(details, "Required availability checks not made", feedback.missing_unavailability_checks);
  const limits = Array.isArray(feedback.limitations) ? feedback.limitations.join(" ") : feedback.limitations;
  if (limits) details.append(element("h3", "", "Interpretation limits"), element("p", "", limits));
  details.append(element("p", "", "Reference-set coverage checks record IDs against authored answer sets. It does not assess semantic entailment. This demo is not a competency score, an independent assessment of expertise, or evidence of real-world GMP performance."));
  $("report-markdown").href = `/api/sessions/${encodeURIComponent(session.session_id)}/report?format=markdown`;
  $("report-json").href = `/api/sessions/${encodeURIComponent(session.session_id)}/report?format=json`;
}

function acceptSession(session) {
  state.session = session;
  renderHeader();
  renderRoles();
  renderCatalog();
  renderReader();
  renderCitations();
  renderEvents();
  renderDebrief();
  if (session.decision) {
    document.querySelectorAll('input[name="verdict"]').forEach((radio) => { radio.checked = radio.value === session.decision.verdict; });
    $("rationale").value = session.decision.rationale || "";
  }
  setBusy(state.busy);
}

$("case-select").addEventListener("change", renderPreview);
$("role-select").addEventListener("change", () => {
  renderRoles();
  if (state.session && state.session.auditor_role !== $("role-select").value) {
    message(`Policy changes apply to a new session. This investigation still uses ${state.session.auditor_role} for scripted steps.`);
  }
});
$("case-setup").addEventListener("submit", (event) => {
  event.preventDefault();
  task(async () => {
    const session = await api("/api/sessions", { case_id: $("case-select").value, auditor_role: $("role-select").value });
    state.selectedEvidence = null;
    $("decision-form").reset();
    $("citation-list").replaceChildren();
    acceptSession(session);
    renderPreview();
    message("Session opened. Start with the claim and choose which record to request first.");
  });
});

$("decision-form").addEventListener("submit", (event) => {
  event.preventDefault();
  task(async () => {
    const session = state.session;
    if (!session || session.status !== "active") return;
    const verdict = document.querySelector('input[name="verdict"]:checked')?.value;
    const rationale = $("rationale").value.trim();
    const evidence_ids = currentCitations();
    if (!verdict || !rationale) throw new Error("Choose a verdict and write a short reasoning note before finalizing.");
    if (verdict !== "insufficient" && !evidence_ids.length) throw new Error("Cite at least one retrieved record to support a supported or contradicted verdict.");
    const updated = await api(`/api/sessions/${encodeURIComponent(session.session_id)}/decide`, { verdict, evidence_ids, rationale });
    acceptSession(updated);
    message("Session finalized. The debrief compares your decision with this demo case’s authored reference.");
    $("debrief-panel").scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "nearest" });
  });
});

$("step-button").addEventListener("click", () => task(async () => {
  const session = state.session;
  if (!session || session.status !== "active") return;
  const oldIds = new Set(session.evidence.map((item) => item.id));
  const updated = await api(`/api/sessions/${encodeURIComponent(session.session_id)}/step`, {});
  const newRecord = updated.evidence.find((item) => !oldIds.has(item.id));
  if (newRecord) state.selectedEvidence = newRecord.id;
  acceptSession(updated);
  message(updated.status === "completed" ? "The scripted policy has finalized its decision. Review the reference comparison below." : "One scripted step completed. You can request evidence or assess the claim yourself at any point.");
}));

async function initialize() {
  setBusy(true);
  try {
    const [casesResult, personasResult] = await Promise.allSettled([api("/api/cases"), api("/api/personas")]);
    if (casesResult.status === "rejected") throw casesResult.reason;
    state.cases = casesResult.value.cases || [];
    const select = $("case-select");
    select.replaceChildren();
    state.cases.forEach((item) => { const option = element("option", "", item.title); option.value = item.id; select.append(option); });
    if (!state.cases.length) throw new Error("No demo cases are available. Check that the server can read its packaged data files.");
    if (personasResult.status === "fulfilled") state.personas = personasResult.value.personas || [];
    else {
      state.personas = ["user-01", "user-02", "auditor-newbie-01", "auditor-newbie-02", "auditor-expert-01", "auditor-expert-02"].map((id) => ({ id, label: id.startsWith("user-") ? "Records owner" : "Scripted auditor", kind: id.startsWith("user-") ? "auditee" : "auditor" }));
      message("Cases loaded. Role descriptions are temporarily unavailable; the local policy identifiers are shown instead.");
    }
    renderPreview();
  } catch (error) {
    message(error.message || "The workspace could not be initialized.", true);
    $("case-select").replaceChildren(element("option", "", "Cases unavailable"));
  } finally {
    setBusy(false);
  }
}

initialize();
