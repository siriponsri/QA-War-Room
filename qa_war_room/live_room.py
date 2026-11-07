"""Bounded live multi-role workflow over real offline session transitions.

Agents are deterministic observation-only policies, never independent experts.
The background scheduler advances without browser polling; deadlines use monotonic
wall time, including pauses. Timed/stopped rooms do not force a verdict or read gold.
"""

from copy import deepcopy
import threading
import time
import uuid

from .engine import EngineError
from .policies import assess_visible, next_action
from .ui_language import thai_message

TERMINAL = {"completed", "time_limit", "stopped", "turn_limit", "error"}


class LiveRooms:
    def __init__(self, engine, *, clock=time.monotonic, threaded=True, max_rooms=50, max_running=4):
        self.engine, self.clock, self.threaded = engine, clock, threaded
        self.max_rooms, self.max_running = max_rooms, max_running
        self._rooms, self._lock = {}, threading.RLock()
        self._shutdown = threading.Event()

    def create(self, case_id, auditor_role="auditor-expert-01", time_limit=60, interval_ms=650):
        if type(time_limit) is not int or not 1 <= time_limit <= 300 or type(interval_ms) is not int or not 100 <= interval_ms <= 2000:
            raise EngineError("invalid_run_limits", "Use 1–300 seconds and 100–2000 milliseconds per turn.")
        with self._lock:
            if len(self._rooms) >= self.max_rooms or sum(r["status"] not in TERMINAL for r in self._rooms.values()) >= self.max_running:
                raise EngineError("room_limit", "Local room limit reached. Stop another room or restart the local server.", 429)
            session = self.engine.create(case_id, auditor_role)
            room_id = "room_" + uuid.uuid4().hex
            room = {"room_id": room_id, "session_id": session["session_id"], "status": "running",
                "time_limit": time_limit, "interval_ms": interval_ms, "started": self.clock(), "ended": None,
                "phase": "investigator", "turns": 0, "max_turns": 80, "pending": None, "messages": [], "notes": 0,
                "lead": auditor_role, "reviewer": "auditor-expert-02" if auditor_role != "auditor-expert-02" else "auditor-expert-01", "controls": 0}
            self._rooms[room_id] = room
            self._message(room, "coordinator", "started", "The room is open. The investigator will request evidence; record owners will respond; the checker will review the acquired facts. Offline scripted agents · synthetic case.")
            state = self._state(room)
            if self.threaded:
                threading.Thread(target=self._work, args=(room_id,), name="qa-live-room", daemon=True).start()
            return state

    def _get(self, room_id):
        if not isinstance(room_id, str) or room_id not in self._rooms:
            raise EngineError("unknown_room", "This room is not in the current local server process.", 404)
        return self._rooms[room_id]

    def _message(self, room, role, kind, text, citations=None):
        room["messages"].append({"seq": len(room["messages"]) + 1, "role": role, "kind": kind,
            "text": text, "text_th": thai_message(kind, text), "citations": list(citations or []), "elapsed_seconds": round(max(0, self.clock() - room["started"]), 3)})

    def _finish(self, room, status, text):
        room["status"], room["ended"] = status, self.clock()
        self._message(room, "coordinator", status, text)

    def _expire(self, room):
        if room["status"] not in TERMINAL and self.clock() - room["started"] >= room["time_limit"]:
            self._finish(room, "time_limit", "Time limit reached. The room stopped with its current evidence. No decision or reference debrief was forced.")

    def _state(self, room):
        self._expire(room)
        session = self.engine.state(room["session_id"])
        session.pop("session_id")
        elapsed = max(0, (room["ended"] if room["ended"] is not None else self.clock()) - room["started"])
        return deepcopy({"room_id": room["room_id"], "mode": "offline_scripted_live_workflow", "status": room["status"],
            "phase": room["phase"], "turns": room["turns"], "max_turns": room["max_turns"],
            "time_limit": room["time_limit"], "interval_ms": room["interval_ms"], "elapsed_seconds": round(elapsed, 3),
            "remaining_seconds": round(max(0, room["time_limit"] - elapsed), 3), "messages": room["messages"],
            "lead": room["lead"], "reviewer": room["reviewer"], "session": session,
            "next_role": next((row["owner"] for row in session["catalog"] if row["id"] == (room["pending"] or {}).get("evidence_id")), None),
            "llm_calls": 0, "cost_usd": "0", "notice": "Original synthetic demo; scripted agents, not LLMs or independent pharmaceutical reviewers."})

    def state(self, room_id):
        with self._lock:
            return self._state(self._get(room_id))

    def control(self, room_id, action):
        with self._lock:
            room = self._get(room_id)
            self._expire(room)
            if room["status"] in TERMINAL:
                raise EngineError("room_finished", "This room has ended. Start a new room to run again.", 409)
            if room["controls"] >= 40:
                raise EngineError("control_limit", "The room control limit was reached; its time/turn limit still applies.", 429)
            room["controls"] += 1
            if action == "pause" and room["status"] == "running":
                room["status"] = "paused"
                self._message(room, "operator", "paused", "Paused the agents. The wall-clock deadline continues.")
            elif action == "resume" and room["status"] == "paused":
                room["status"] = "running"
                self._message(room, "operator", "resumed", "Resumed the agent workflow.")
            elif action == "stop":
                self._finish(room, "stopped", "Stopped by the operator. Partial evidence and messages remain exportable; no decision was forced.")
            else:
                raise EngineError("invalid_room_control", "Pause a running room, resume a paused room, or stop an active room.", 409)
            return self._state(room)

    def note(self, room_id, text):
        with self._lock:
            room = self._get(room_id)
            self._expire(room)
            if room["status"] in TERMINAL:
                raise EngineError("room_finished", "The room has ended.", 409)
            if not isinstance(text, str) or not text.strip() or len(text) > 1000 or room["notes"] >= 20:
                raise EngineError("invalid_note", "Use a nonempty note of at most 1000 characters; at most 20 notes per room.")
            room["notes"] += 1
            self._message(room, "operator", "note", text.strip())
            return self._state(room)

    def request(self, room_id, evidence_id):
        with self._lock:
            room = self._get(room_id)
            self._expire(room)
            if room["status"] != "paused":
                raise EngineError("pause_to_request", "Pause the agents before requesting a record yourself.", 409)
            before = self.engine.state(room["session_id"])
            result = self.engine.request(room["session_id"], evidence_id)
            new_events = result["events"][len(before["events"]):]
            self._message(room, "operator", "request", f"Requested {evidence_id} from the evidence register.")
            self._record_response(room, result, evidence_id, new_events)
            room["pending"], room["phase"] = None, "reviewer"
            return self._state(room)

    def _record_response(self, room, state, evidence_id, events):
        delivered = next((record for record in state["evidence"] if record["id"] == evidence_id), None)
        owner = next((row["owner"] for row in state["catalog"] if row["id"] == evidence_id), "user-02")
        if delivered:
            self._message(room, owner, "record", f"Delivered {evidence_id}: {delivered['title']}. Revision {delivered['revision']} · {delivered['date']}. Open the attached record to inspect its content.", [evidence_id])
        else:
            note = next((event["message"] for event in events if event["type"] == "evidence_unavailable"), "The requested record was not delivered.")
            self._message(room, owner, "unavailable", f"{evidence_id}: {note}")

    def advance(self, room_id):
        """One auditable phase; production scheduler calls this in the background."""
        with self._lock:
            room = self._get(room_id)
            self._expire(room)
            if room["status"] != "running":
                return self._state(room)
            if room["turns"] >= room["max_turns"]:
                self._finish(room, "turn_limit", "Turn limit reached. No decision or reference feedback was forced.")
                return self._state(room)
            state = self.engine.state(room["session_id"])
            if state["status"] != "active":
                self._finish(room, "completed", "The underlying session has completed.")
                return self._state(room)
            # No feedback exists in active observations. Policies receive detached visible state.
            room["turns"] += 1
            if room["phase"] == "investigator":
                action = next_action(deepcopy(state))
                room["pending"] = action
                if action["type"] == "request":
                    record = next(r for r in state["catalog"] if r["id"] == action["evidence_id"])
                    self._message(room, room["lead"], "request", f"Please provide {record['id']} · {record['title']} ({record['cost']} credit). I will use the returned record in this claim review.")
                    room["phase"] = "custodian"
                else:
                    self._message(room, room["lead"], "proposal", f"Proposed decision: {action['verdict']}. {action['rationale']}", action["evidence_ids"])
                    room["phase"] = "final_review"
            elif room["phase"] == "custodian":
                evidence_id = room["pending"]["evidence_id"]
                result = self.engine.request(room["session_id"], evidence_id)
                self._record_response(room, result, evidence_id, result["events"][len(state["events"]):])
                room["phase"], room["pending"] = "reviewer", None
            elif room["phase"] == "reviewer":
                assessment = assess_visible(deepcopy(state))
                self._message(room, room["reviewer"], "review", f"Visible-evidence check: {assessment['verdict']}. {assessment['rationale']}", assessment["evidence_ids"])
                room["phase"] = "investigator"
            elif room["phase"] == "final_review":
                assessment = assess_visible(deepcopy(state))
                grounded = deepcopy(state)
                grounded["auditor_role"] = "auditor-expert-01"
                additional = next_action(grounded)
                if assessment["verdict"] == "insufficient" and additional["type"] == "request":
                    self._message(room, room["reviewer"], "challenge", f"I cannot accept closure yet. {assessment['rationale']} Requesting {additional['evidence_id']} before finalizing.", assessment["evidence_ids"])
                    room["pending"], room["phase"] = additional, "custodian"
                else:
                    self._message(room, room["reviewer"], "final_review", f"Checked conclusion: {assessment['verdict']}. {assessment['rationale']}", assessment["evidence_ids"])
                    room["pending"], room["phase"] = assessment, "closeout"
            elif room["phase"] == "closeout":
                action = room["pending"]
                self.engine.decide(room["session_id"], action["verdict"], action["evidence_ids"], action["rationale"])
                self._message(room, room["lead"], "decision", f"Final draft decision: {action['verdict']}. {action['rationale']}", action["evidence_ids"])
                self._finish(room, "completed", "Process completed. The authored reference debrief is now available separately. This is a synthetic rehearsal, not a GMP approval.")
            return self._state(room)

    def _work(self, room_id):
        while not self._shutdown.is_set():
            try:
                state = self.advance(room_id)
                if state["status"] in TERMINAL:
                    return
                self._shutdown.wait(state["interval_ms"] / 1000)
            except Exception:
                with self._lock:
                    room = self._get(room_id)
                    if room["status"] not in TERMINAL:
                        self._finish(room, "error", "The local workflow stopped after a processing error. Existing evidence and messages were preserved.")
                return

    def report(self, room_id):
        state = self.state(room_id)
        return {"schema": "qawr-live-room-v1", "evaluation_state": "TERMINAL_AUTHORED_DEBRIEF" if state["status"] == "completed" else "NOT_EVALUATED", **state}

    def overview(self):
        """Local process metadata only: no source text, labels or evaluator results."""
        with self._lock:
            summaries = []
            for room in self._rooms.values():
                state = self._state(room)
                summaries.append({"room_id": room["room_id"], "case": state["session"]["case"],
                    "status": state["status"], "message_count": len(state["messages"]),
                    "records_received": len(state["session"]["evidence"]), "elapsed_seconds": state["elapsed_seconds"]})
            return {"case_count": len(self.engine.list_cases()), "rooms": summaries, "mode": "local_synthetic_demo"}

    def close(self):
        self._shutdown.set()
        with self._lock:
            for room in self._rooms.values():
                if room["status"] not in TERMINAL:
                    self._finish(room, "stopped", "The local server closed. No decision was forced.")


def transcript_markdown(report, language="th"):
    """Readable partial/terminal export; original requested evidence stays intact."""
    thai = language == "th"
    role_names = {"coordinator": "ผู้ประสานงาน", "operator": "คุณ", "user-01": "ฝ่ายผลิต", "user-02": "ฝ่ายคุณภาพ",
                  report["lead"]: "ผู้ทบทวน", report["reviewer"]: "ผู้ตรวจหลักฐาน"}
    session = report["session"]
    lines = ["# " + ("บทสนทนาทบทวนหลักฐาน CAPA" if thai else "CAPA evidence conversation"), "",
        "เคสและทีมจำลอง ไม่ใช่การอนุมัติ GMP หรือ CAPA จริง" if thai else "Synthetic case and scripted team; not an actual GMP or CAPA approval.", "",
        session["case"]["title"], "", ("สถานะ" if thai else "Status") + ": " + report["status"],
        ("เวลา" if thai else "Elapsed time") + f": {report['elapsed_seconds']} / {report['time_limit']} s", "",
        "## " + ("ข้อกล่าวอ้างต้นฉบับ" if thai else "Original claim"), "", session["case"]["claim"], "",
        "## " + ("บทสนทนา" if thai else "Conversation"), ""]
    for message in report["messages"]:
        name = role_names.get(message["role"], message["role"]) if thai else message["role"]
        lines.extend([f"**{name} · {message['elapsed_seconds']} s**", "", message["text_th"] if thai else message["text"], ""])
        if message["citations"]:
            lines.extend([("เอกสารอ้างอิง: " if thai else "Records: ") + ", ".join(message["citations"]), ""])
    lines.extend(["## " + ("เอกสารที่ได้รับ" if thai else "Received evidence"), ""])
    for record in session["evidence"]:
        lines.extend([f"### {record['id']} · {record['title']}", "", f"{record['date']} · revision {record['revision']}", "", record["content"], ""])
    if session["decision"]:
        lines.extend(["## " + ("ข้อสรุปฉบับร่าง" if thai else "Draft conclusion"), "", session["decision"]["verdict"], ""])
    else:
        lines.extend(["ยังไม่มีข้อสรุปสุดท้าย เก็บเป็นงานค้างโดยไม่บังคับคำตอบ" if thai else "No final decision. This remains a partial run without a forced answer.", ""])
    return "\n".join(lines)
