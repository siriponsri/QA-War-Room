"use strict";
/*
 * Shared presentation layer for the live chat and dashboard pages.
 * - Loaded synchronously in <head> so the saved theme/language apply before first paint.
 * - Holds interface copy only. Evidence text, notes and policy decisions are never rewritten here.
 * - All dynamic text is inserted with textContent; icons are static, trusted SVG constants.
 */
window.UI = (() => {
  const LANG_KEY = "qawr-language-v1";
  const THEME_KEY = "qawr-theme-v1";

  const read = (key, fallback) => { try { return localStorage.getItem(key) || fallback; } catch (_) { return fallback; } };
  const write = (key, value) => { try { localStorage.setItem(key, value); } catch (_) { /* storage blocked: keep in-memory */ } };

  // [English, Thai]
  const copy = {
    appName: ["QA War Room", "QA War Room"],
    tagline: ["CAPA evidence rehearsal", "ซ้อมทบทวนหลักฐาน CAPA"],
    navChat: ["Chat room", "ห้องสนทนา"],
    navDashboard: ["Dashboard", "ภาพรวม"],
    navManual: ["Manual evidence desk", "หน้าทบทวนด้วยตนเอง"],
    newRoom: ["New conversation", "เริ่มห้องใหม่"],
    yourRooms: ["Your conversations", "ห้องสนทนาของคุณ"],
    emptyHistory: ["Rooms you start in this browser appear here.", "ห้องที่คุณเริ่มจากเบราว์เซอร์นี้จะแสดงที่นี่"],
    localOnly: ["Runs on this computer · no paid API", "ทำงานบนเครื่องนี้ · ไม่ใช้ API แบบเสียเงิน"],
    menu: ["Open menu", "เปิดเมนู"],
    closeMenu: ["Close menu", "ปิดเมนู"],
    switchLang: ["Switch to English", "เปลี่ยนเป็นภาษาไทย"],
    themeToLight: ["Switch to light theme", "เปลี่ยนเป็นธีมสว่าง"],
    themeToDark: ["Switch to dark theme", "เปลี่ยนเป็นธีมมืด"],
    display: ["Language and theme", "ภาษาและธีม"],
    skipChat: ["Skip to conversation", "ข้ามไปยังห้องสนทนา"],
    skipDashboard: ["Skip to dashboard", "ข้ามไปยังภาพรวม"],
    demoBadge: ["Simulated team · fictional records", "ทีมจำลอง · เอกสารสมมติ"],

    // Setup
    setupEyebrow: ["Start a review in three steps", "เริ่มทบทวนได้ใน 3 ขั้นตอน"],
    setupTitle: ["Pick a CAPA case for the team", "เลือกเคส CAPA ให้ทีมตรวจ"],
    setupIntro: ["Pick a sample case and a time limit. The team requests records, reviews the evidence and reports back in the chat.", "เลือกเคสตัวอย่างและเวลา ทีมจะขอเอกสาร ทบทวนหลักฐาน และรายงานผลให้คุณเห็นในแชต"],
    stepCase: ["Choose a case", "เลือกเคส"],
    stepTime: ["Set a time limit", "ตั้งเวลา"],
    stepStart: ["Start", "เริ่ม"],
    casesLoading: ["Loading sample cases…", "กำลังโหลดเคสตัวอย่าง…"],
    casesError: ["Sample cases could not be loaded from the local server.", "โหลดเคสตัวอย่างจากระบบบนเครื่องไม่ได้"],
    retry: ["Try again", "ลองอีกครั้ง"],
    claimLabel: ["Claim to review", "ข้อกล่าวอ้างที่จะทบทวน"],
    asOf: ["As of", "ณ วันที่"],
    minute1: ["1 min", "1 นาที"], minute2: ["2 min", "2 นาที"], minute5: ["5 min", "5 นาที"], custom: ["Custom", "กำหนดเอง"],
    timeHint: ["The team stops when it concludes or when time runs out. Unfinished work is kept, never forced into a verdict.", "ทีมจะหยุดเมื่อได้ข้อสรุปหรือครบเวลา งานที่ยังไม่จบจะเก็บเป็นงานค้าง ไม่บังคับคำตัดสิน"],
    advanced: ["More options", "ตัวเลือกเพิ่มเติม"],
    advancedHint: ["Optional. The defaults suit most reviews.", "ไม่จำเป็นต้องปรับ ค่าเริ่มต้นเหมาะกับการใช้งานส่วนใหญ่"],
    strategy: ["Review approach", "แนวทางของผู้ทบทวน"],
    careful: ["Criteria first (recommended)", "ตรวจตามเกณฑ์ก่อน (แนะนำ)"],
    risks: ["Look for counter-evidence first", "หาหลักฐานแย้งก่อน"],
    order: ["Read in catalog order", "อ่านตามลำดับรายการ"],
    shortcut: ["Start from the cover sheet", "เริ่มจากใบสรุป"],
    pace: ["Message pace", "จังหวะข้อความ"],
    normal: ["Normal", "ปกติ"], relaxed: ["Relaxed", "ช้าลง อ่านทัน"], fast: ["Fast", "เร็ว"],
    customSeconds: ["Custom time (1–300 seconds)", "กำหนดเวลาเอง (1–300 วินาที)"],
    seconds: ["seconds", "วินาที"],
    invalidTime: ["Enter a whole number of seconds from 1 to 300.", "กรอกจำนวนวินาทีเป็นเลขจำนวนเต็ม 1–300"],
    chooseCaseFirst: ["Choose a case first.", "กรุณาเลือกเคสก่อน"],
    start: ["Start conversation", "เริ่มสนทนา"],
    starting: ["Starting…", "กำลังเริ่ม…"],
    setupFoot: ["A rule-based simulated team, not an AI model or professional auditors. Results are rehearsal only, not GMP or CAPA approval.", "ทีมจำลองที่ทำงานตามกติกา ไม่ใช่โมเดล AI หรือผู้ตรวจประเมินจริง ผลลัพธ์ใช้ซ้อมเท่านั้น ไม่ใช่การอนุมัติ GMP หรือ CAPA"],

    // Room
    roomDetails: ["Room details", "รายละเอียดห้อง"],
    closeDetails: ["Close room details", "ปิดรายละเอียดห้อง"],
    showClaim: ["Show claim", "ดูข้อกล่าวอ้าง"],
    hideClaim: ["Hide claim", "ซ่อนข้อกล่าวอ้าง"],
    timeLeft: ["Time left", "เวลาที่เหลือ"],
    pause: ["Pause", "พัก"], resume: ["Resume", "ทำต่อ"], stop: ["Stop", "หยุด"],
    notePlaceholder: ["Write a note for the record…", "เขียนบันทึกถึงทีม…"],
    noteLabel: ["Note to this room", "บันทึกถึงห้องนี้"],
    sendNote: ["Send note", "ส่งบันทึก"],
    noteHelp: ["Notes are saved word for word in the report. They do not change the team's rules.", "บันทึกจะถูกเก็บตามที่พิมพ์ไว้ในรายงาน และไม่เปลี่ยนกติกาการทำงานของทีม"],
    pausedHint: ["Paused. The clock keeps running. You can now request a record yourself.", "พักทีมอยู่ เวลายังเดินต่อ ตอนนี้คุณขอเอกสารเองได้"],
    openEvidence: ["Request a record", "ขอเอกสาร"],
    latest: ["New messages", "ข้อความใหม่"],
    timeUp: ["Time is up · saving…", "ครบเวลา · กำลังบันทึก…"],
    roomEnded: ["This room has ended.", "ห้องนี้จบแล้ว"],
    turns: ["rounds", "รอบ"],
    stopTitle: ["Stop this conversation?", "หยุดการสนทนานี้หรือไม่"],
    stopBody: ["The team stops now. Messages and received records are kept as unfinished work. No verdict is forced, and the room cannot be restarted.", "ทีมจะหยุดทันที ข้อความและเอกสารที่ได้รับจะเก็บเป็นงานค้าง ไม่มีการบังคับคำตัดสิน และเริ่มห้องนี้ต่อไม่ได้"],
    cancel: ["Keep going", "ทำต่อไป"],
    confirmStop: ["Stop conversation", "หยุดการสนทนา"],
    original: ["Original (English)", "ต้นฉบับ (อังกฤษ)"],
    staleRoom: ["This room is no longer on the local server (the server may have restarted). It was removed from your list.", "ไม่พบห้องนี้ในระบบบนเครื่องแล้ว (อาจมีการรีสตาร์ตระบบ) จึงนำออกจากรายการของคุณ"],
    connectionLost: ["Connection to the local server was interrupted. Retrying…", "การเชื่อมต่อกับระบบบนเครื่องขัดข้อง กำลังลองใหม่…"],
    reconnected: ["Connection restored.", "เชื่อมต่อได้แล้ว"],
    dismiss: ["Dismiss", "ปิด"],

    // Typing / next step
    nextInvestigator: ["choosing the next record to request", "กำลังเลือกเอกสารที่จะขอ"],
    nextCustodian: ["preparing the requested record", "กำลังเตรียมเอกสาร"],
    nextReviewer: ["reviewing the evidence received", "กำลังทบทวนหลักฐาน"],
    nextFinal: ["checking the proposed conclusion", "กำลังทบทวนข้อสรุป"],
    nextCloseout: ["writing the draft conclusion", "กำลังสรุปผล"],
    pausedWaiting: ["Team paused", "ทีมพักอยู่"],

    // Roles
    investigator: ["Investigator", "ผู้ทบทวน"],
    checker: ["Evidence checker", "ผู้ตรวจหลักฐาน"],
    manufacturing: ["Manufacturing records", "ฝ่ายผลิต"],
    quality: ["Quality records", "ฝ่ายคุณภาพ"],
    you: ["You", "คุณ"],
    system: ["Room", "ระบบ"],
    roleInvestigator: ["Requests the records the claim depends on", "ขอเอกสารที่ข้อกล่าวอ้างต้องใช้"],
    roleChecker: ["Checks received facts before any conclusion", "ตรวจข้อมูลที่ได้รับก่อนสรุป"],
    roleOwner: ["Sends only the records that are requested", "ส่งเฉพาะเอกสารที่ถูกขอ"],
    teamNote: ["Illustrated, rule-based simulated roles, not AI models or real experts.", "ตัวละครประกอบของบทบาทจำลองที่ทำงานตามกติกา ไม่ใช่โมเดล AI หรือผู้เชี่ยวชาญจริง"],
    speaking: ["speaking…", "กำลังพูด…"],
    spoke: ["just spoke", "เพิ่งพูด"],
    waiting: ["waiting", "รอคิว"],
    stageLabel: ["Who is talking", "ใครกำลังพูด"],
    systemText: ["System wording", "ข้อความระบบเดิม"],
    showPrompt: ["Response style (system prompt)", "สไตล์การตอบ (system prompt)"],
    voiceNote: ["Each character's voice is a display template over the backend's rule-based messages; facts are unchanged and downloaded reports keep the system wording.", "สำนวนของตัวละครเป็นแม่แบบการแสดงผลบนข้อความของระบบที่ทำงานตามกติกา ข้อเท็จจริงไม่เปลี่ยน และรายงานที่ดาวน์โหลดใช้ข้อความระบบเดิม"],
    castNote: ["Names and faces are fictional characters for the simulated roles, not real people or experts.", "ชื่อและหน้าตาเป็นตัวละครสมมติของบทบาทจำลอง ไม่ใช่บุคคลจริงหรือผู้เชี่ยวชาญ"],
    heroBadge: ["4 simulated roles · fictional records", "ทีมจำลอง 4 บทบาท · เอกสารสมมติ"],
    stateNext: ["Up next", "คิวถัดไป"],
    stateIdle: ["In room", "อยู่ในห้อง"],
    stateDone: ["Finished", "เสร็จแล้ว"],

    // Message kinds
    k_request: ["Request", "ขอเอกสาร"], k_record: ["Record sent", "ส่งเอกสาร"], k_unavailable: ["Not available", "ไม่มีเอกสาร"],
    k_review: ["Evidence check", "ทบทวนหลักฐาน"], k_challenge: ["Needs more", "ขอหลักฐานเพิ่ม"], k_proposal: ["Proposal", "เสนอข้อสรุป"],
    k_final_review: ["Conclusion check", "ทบทวนข้อสรุป"], k_decision: ["Draft conclusion", "ร่างข้อสรุป"], k_note: ["Note", "บันทึก"],
    youPaused: ["You paused the team", "คุณพักทีม"], youResumed: ["You resumed the team", "คุณให้ทีมทำงานต่อ"],

    // Panel sections
    team: ["Team", "ทีมในห้อง"],
    progress: ["Progress", "ความคืบหน้า"],
    stageClaim: ["Read the claim", "อ่านข้อกล่าวอ้าง"],
    stageGather: ["Gather records", "รวบรวมเอกสาร"],
    stageCheck: ["Check the facts", "ทบทวนข้อมูล"],
    stageDone: ["Conclude", "สรุปผล"],
    elapsed: ["Elapsed", "ใช้ไป"],
    clockNote: ["The time limit keeps running while paused.", "เวลาสูงสุดยังเดินต่อแม้ขณะพัก"],
    evidence: ["Evidence", "หลักฐาน"],
    budget: ["Evidence budget", "งบขอเอกสาร"],
    used: ["used", "ใช้แล้ว"],
    received: ["Received", "ได้รับแล้ว"],
    notRequested: ["Not requested", "ยังไม่ได้ขอ"],
    unavailable: ["No record available", "ไม่มีเอกสารให้ส่ง"],
    read: ["Read", "เปิดอ่าน"],
    request: ["Request", "ขอ"],
    requestNeedsPause: ["Pause the team to request records yourself.", "พักทีมก่อน จึงจะขอเอกสารเองได้"],
    credit: ["credit", "หน่วย"],
    evidenceEmpty: ["Only records the team requests are opened. Unrequested records stay closed.", "ระบบเปิดเฉพาะเอกสารที่ถูกขอ เอกสารที่ไม่ได้ขอจะไม่ถูกเปิด"],
    downloads: ["Report", "รายงาน"],
    downloadTh: ["Download report (Thai)", "ดาวน์โหลดรายงาน (ไทย)"],
    downloadEn: ["Download report (English)", "ดาวน์โหลดรายงาน (อังกฤษ)"],
    downloadJson: ["Developer JSON", "ไฟล์ JSON สำหรับนักพัฒนา"],
    downloadNote: ["Available at any time. Unfinished rooms are exported as unfinished.", "ดาวน์โหลดได้ทุกเมื่อ ห้องที่ยังไม่จบจะระบุว่าเป็นงานค้าง"],
    download: ["Download report", "ดาวน์โหลดรายงาน"],
    viewEvidence: ["View evidence", "ดูหลักฐาน"],
    startAnother: ["Start a new room", "เริ่มห้องใหม่"],

    // Statuses
    s_running: ["In progress", "กำลังทำงาน"], s_paused: ["Paused", "พักอยู่"], s_completed: ["Completed", "เสร็จสมบูรณ์"],
    s_time_limit: ["Time limit reached", "ครบเวลา"], s_stopped: ["Stopped", "หยุดแล้ว"], s_turn_limit: ["Round limit reached", "ครบรอบสูงสุด"],
    s_error: ["Interrupted", "ขัดข้อง"], s_stale: ["Not on server", "ไม่พบในระบบ"],
    unfinished: ["Unfinished", "งานค้าง"],

    // Outcome
    outcomeCompleted: ["The team finished its review", "ทีมทบทวนครบกระบวนการแล้ว"],
    outcomeCompletedText: ["This is the simulated team's draft conclusion from the records it received. It is a rehearsal result, not a GMP or CAPA approval.", "นี่คือร่างข้อสรุปของทีมจำลองจากเอกสารที่ได้รับ เป็นผลการซ้อม ไม่ใช่การอนุมัติ GMP หรือ CAPA"],
    outcomePartial: ["Saved as unfinished work", "เก็บเป็นงานค้างแล้ว"],
    outcome_time_limit: ["Time ran out before the team concluded. No verdict was forced and the case reference stays closed. Running out of time does not mean the claim passed or failed.", "หมดเวลาก่อนทีมได้ข้อสรุป ระบบไม่บังคับคำตัดสินและไม่เปิดคำตอบอ้างอิง การหมดเวลาไม่ได้แปลว่าข้อกล่าวอ้างผ่านหรือไม่ผ่าน"],
    outcome_stopped: ["You stopped the room. No verdict was forced and the case reference stays closed.", "คุณหยุดห้องนี้แล้ว ระบบไม่บังคับคำตัดสินและไม่เปิดคำตอบอ้างอิง"],
    outcome_turn_limit: ["The room reached its round limit. No verdict was forced.", "ห้องครบจำนวนรอบสูงสุด ระบบไม่บังคับคำตัดสิน"],
    outcome_error: ["The local workflow stopped after a processing problem. Existing messages and records were kept.", "ระบบบนเครื่องหยุดทำงานเพราะเกิดปัญหาในการประมวลผล ข้อความและเอกสารเดิมยังถูกเก็บไว้"],
    keptCounts: ["Kept", "เก็บไว้"],
    messagesN: ["messages", "ข้อความ"],
    recordsN: ["records", "เอกสาร"],
    draftVerdict: ["Team's draft conclusion", "ร่างข้อสรุปของทีม"],
    compareTitle: ["Compare with the case author's reference", "เทียบกับคำตอบอ้างอิงของผู้สร้างเคส"],
    compareNote: ["Written by the case author for this fictional scenario. It is not an independent expert review.", "เขียนโดยผู้สร้างเคสสมมตินี้ ไม่ใช่การทบทวนโดยผู้เชี่ยวชาญอิสระ"],
    referenceVerdict: ["Reference answer", "คำตอบอ้างอิง"],
    matches: ["Matches the team's draft", "ตรงกับร่างข้อสรุปของทีม"],
    differs: ["Differs from the team's draft", "ต่างจากร่างข้อสรุปของทีม"],
    v_supported: ["Supported by evidence", "มีหลักฐานสนับสนุน"],
    v_contradicted: ["Contradicted by evidence", "หลักฐานขัดแย้ง"],
    v_insufficient: ["Not enough evidence", "หลักฐานยังไม่เพียงพอ"],

    // Record dialog
    receivedRecord: ["Received record", "เอกสารที่ได้รับ"],
    closeRecord: ["Close record", "ปิดเอกสาร"],
    revision: ["Revision", "ฉบับ"],
    dated: ["Dated", "วันที่"],
    from: ["From", "จาก"],
    facts: ["Key facts", "ข้อมูลสำคัญ"],
    yes: ["Yes", "ใช่"], no: ["No", "ไม่ใช่"],
    recordNote: ["Facts are shown as recorded. Thai labels translate field names only; values stay as in the original.", "แสดงข้อมูลตามที่บันทึกไว้ ป้ายภาษาไทยแปลเฉพาะชื่อหัวข้อ ค่าข้อมูลคงตามต้นฉบับ"],

    // Dashboard
    dashEyebrow: ["Local workspace overview", "ภาพรวมพื้นที่ทำงานบนเครื่องนี้"],
    dashTitle: ["All rooms at a glance", "ห้องสนทนาทั้งหมด"],
    dashIntro: ["Live counts from the local server since it last started. Nothing here is a quality score or a real approval.", "ตัวเลขจริงจากระบบบนเครื่องนับตั้งแต่เริ่มระบบครั้งล่าสุด ไม่ใช่คะแนนคุณภาพหรือการอนุมัติจริง"],
    kpiCases: ["Sample cases", "เคสตัวอย่าง"],
    kpiRooms: ["Rooms this session", "ห้องในรอบนี้"],
    kpiActive: ["Running or paused", "กำลังทำงาน/พัก"],
    kpiCompleted: ["Completed", "เสร็จสมบูรณ์"],
    kpiUnfinished: ["Unfinished", "งานค้าง"],
    kpiCasesHint: ["Fictional manufacturing CAPA cases", "เคส CAPA การผลิตแบบสมมติ"],
    kpiRoomsHint: ["Resets when the server restarts", "เริ่มนับใหม่เมื่อรีสตาร์ตระบบ"],
    kpiActiveHint: ["Up to 4 unfinished rooms at once", "ทำงานพร้อมกันได้สูงสุด 4 ห้อง"],
    kpiCompletedHint: ["Reached a draft conclusion", "ทีมได้ร่างข้อสรุป"],
    kpiUnfinishedHint: ["Time limit, stopped, round limit or interrupted", "ครบเวลา หยุด ครบรอบ หรือขัดข้อง"],
    statusMix: ["Room status", "สถานะของห้อง"],
    statusMixEmpty: ["Status counts appear after the first room starts.", "สัดส่วนสถานะจะแสดงหลังเริ่มห้องแรก"],
    recentRooms: ["Rooms", "ห้องสนทนา"],
    filterAll: ["All", "ทั้งหมด"], filterActive: ["Active", "กำลังทำงาน"], filterDone: ["Completed", "เสร็จแล้ว"], filterUnfinished: ["Unfinished", "งานค้าง"],
    noRoomsTitle: ["No rooms yet", "ยังไม่มีห้องสนทนา"],
    noRoomsText: ["Start a conversation and it will appear here with its live status.", "เริ่มห้องสนทนาแล้วห้องจะแสดงที่นี่พร้อมสถานะล่าสุด"],
    noMatch: ["No rooms with this status.", "ไม่มีห้องในสถานะนี้"],
    openRoom: ["Open", "เปิดห้อง"],
    casesTitle: ["Sample cases", "เคสตัวอย่าง"],
    casesIntro: ["Rooms started per case in this server session.", "จำนวนห้องที่เริ่มในแต่ละเคสในรอบนี้"],
    roomsUsed: ["rooms", "ห้อง"],
    useCase: ["Start with this case", "เริ่มด้วยเคสนี้"],
    refresh: ["Refresh", "อัปเดต"],
    updatedAt: ["Updated", "อัปเดตล่าสุด"],
    autoRefresh: ["Auto-refresh every 5 seconds", "อัปเดตอัตโนมัติทุก 5 วินาที"],
    staleData: ["Showing the last data received.", "กำลังแสดงข้อมูลชุดล่าสุดที่ได้รับ"],
    dashError: ["Cannot reach the local server. Is it still running?", "ติดต่อระบบบนเครื่องไม่ได้ ระบบยังทำงานอยู่หรือไม่"],
    dataNote: ["About this data: counts come from GET /api/rooms on this computer. Rooms live in memory and disappear when the server restarts. There are no model scores, accuracy figures or real company records on this page.", "เกี่ยวกับข้อมูล: ตัวเลขมาจากระบบบนเครื่องนี้โดยตรง ห้องสนทนาเก็บในหน่วยความจำและจะหายเมื่อรีสตาร์ตระบบ หน้านี้ไม่มีคะแนนโมเดล ความแม่นยำ หรือข้อมูลบริษัทจริง"],
    duration: ["Duration", "ระยะเวลา"],

    // Settings page
    navSettings: ["AI settings", "ตั้งค่า AI"],
    skipSettings: ["Skip to settings", "ข้ามไปยังการตั้งค่า"],
    setTitle: ["AI model settings", "ตั้งค่าโมเดล AI"],
    setIntro: ["Choose a provider, paste its API key and pick a model. Keys stay on this computer.", "เลือกผู้ให้บริการ ใส่ API key และเลือกโมเดล key จะเก็บไว้บนเครื่องนี้เท่านั้น"],
    setNotice: ["Not used by chat rooms yet: the agents still follow fixed rules and cost nothing. Saving or testing a key never runs a paid model.", "ยังไม่ได้ใช้ในห้องสนทนา agent ยังทำงานตามกติกาและไม่มีค่าใช้จ่าย การบันทึกหรือทดสอบ key ไม่ได้เรียกใช้โมเดลที่เสียเงิน"],
    setLoadError: ["Settings could not be loaded from the local server. Restart it if it predates this page.", "โหลดการตั้งค่าจากระบบบนเครื่องไม่ได้ ถ้าเปิดระบบไว้ก่อนมีหน้านี้ ให้รีสตาร์ตระบบ"],
    providers: ["Providers", "ผู้ให้บริการ"],
    active: ["Default", "ค่าหลัก"], ready: ["Ready", "พร้อมใช้"], keySaved: ["Key saved", "มี key แล้ว"], notSet: ["Not set up", "ยังไม่ตั้งค่า"],
    noKeyNeeded: ["No key needed", "ไม่ต้องใช้ key"], thaiFocus: ["Thai-focused", "เน้นภาษาไทย"],
    getKey: ["Get an API key ↗", "ขอ API key ↗"], priceSource: ["Price source ↗", "ที่มาของราคา ↗"],
    apiKey: ["API key", "API key"], noKeyYet: ["No key saved yet.", "ยังไม่ได้บันทึก key"],
    keyPlaceholder: ["Paste a new key to save or replace", "วาง key ใหม่เพื่อบันทึกหรือเปลี่ยน"],
    show: ["Show", "แสดง"], hide: ["Hide", "ซ่อน"],
    keyStorage: ["Saved in .qawr/provider-settings.json on this computer (git-ignored). This page only ever sees the last 4 characters.", "เก็บในไฟล์ .qawr/provider-settings.json บนเครื่องนี้ (git ไม่เก็บ) หน้าเว็บเห็นแค่ 4 ตัวท้าย"],
    baseUrl: ["Ollama address", "ที่อยู่ Ollama"], baseUrlHint: ["Must be on this computer, e.g. http://127.0.0.1:11434", "ต้องอยู่บนเครื่องนี้ เช่น http://127.0.0.1:11434"],
    model: ["Model", "โมเดล"],
    tier_budget: ["Budget · cheap and fast", "ประหยัด · ถูกและเร็ว"], tier_balanced: ["Balanced · good value", "สมดุล · คุ้มค่า"], tier_best: ["Best quality", "คุณภาพสูงสุด"],
    recommended: ["Recommended", "แนะนำ"],
    perM: ["USD per 1M tokens, input / output", "USD ต่อ 1 ล้าน token (ขาเข้า / ขาออก)"],
    priceChecked: ["prices checked {date}, may change", "ตรวจราคาเมื่อ {date} อาจเปลี่ยนได้"],
    free: ["Free", "ฟรี"], priceUnknown: ["See provider", "ดูที่ผู้ให้บริการ"], contextLbl: ["context", "context"],
    customModel: ["Other model ID", "ระบุรุ่นอื่นเอง"], customHint: ["Type or pick from the last test", "พิมพ์หรือเลือกจากผลทดสอบล่าสุด"],
    makeDefault: ["Use as the default provider", "ตั้งเป็นผู้ให้บริการหลัก"],
    save: ["Save", "บันทึก"], test: ["Test connection", "ทดสอบการเชื่อมต่อ"], testing: ["Testing…", "กำลังทดสอบ…"],
    removeKey: ["Remove settings", "ลบการตั้งค่า"], confirmRemove: ["Click again to remove", "กดอีกครั้งเพื่อยืนยันการลบ"],
    saved: ["Saved on this computer.", "บันทึกบนเครื่องนี้แล้ว"], removed: ["Settings removed.", "ลบการตั้งค่าแล้ว"],
    chooseModel: ["Choose a model or type a model ID.", "เลือกโมเดล หรือพิมพ์ชื่อรุ่น"],
    testOk: ["Connected. {n} models available.", "เชื่อมต่อได้ พบโมเดล {n} รายการ"],
    modelFound: ["The selected model is in the list.", "พบโมเดลที่เลือกในรายการ"],
    modelMissing: ["The selected model is not in the list. Check the ID.", "ไม่พบโมเดลที่เลือกในรายการ ตรวจชื่อรุ่นอีกครั้ง"],
    liveHint: ["The full list is now offered under “Other model ID”.", "รายชื่อทั้งหมดเลือกได้ในช่อง “ระบุรุ่นอื่นเอง”"],
    err_key_rejected: ["The provider rejected this key.", "ผู้ให้บริการไม่รับ key นี้"],
    err_key_forbidden: ["This key is not allowed to list models.", "key นี้ไม่มีสิทธิ์ดูรายการโมเดล"],
    err_endpoint_not_found: ["The provider endpoint was not found.", "ไม่พบ endpoint ของผู้ให้บริการ"],
    err_rate_limited: ["Too many requests. Try again shortly.", "เรียกถี่เกินไป ลองใหม่อีกสักครู่"],
    err_provider_error: ["The provider returned an error.", "ผู้ให้บริการตอบกลับเป็นข้อผิดพลาด"],
    err_unreachable: ["Could not reach the provider. Check the internet connection (or that Ollama is running).", "ติดต่อผู้ให้บริการไม่ได้ ตรวจอินเทอร์เน็ต (หรือว่าเปิด Ollama อยู่หรือไม่)"],
    err_unexpected_response: ["The provider sent an unexpected response.", "ผู้ให้บริการตอบกลับในรูปแบบที่ไม่คาดไว้"],
  };

  const errorCopy = {
    room_limit: ["Room limit reached: up to 4 rooms can run at once (50 per server session). Stop a running room or wait for one to finish.", "ห้องเต็มแล้ว: ทำงานพร้อมกันได้สูงสุด 4 ห้อง (รวม 50 ห้องต่อรอบระบบ) หยุดห้องที่กำลังทำงานหรือรอให้ห้องใดห้องหนึ่งจบก่อน"],
    room_finished: ["This room has already ended.", "ห้องนี้จบแล้ว"],
    unknown_room: ["This room is not on the local server any more.", "ไม่พบห้องนี้ในระบบบนเครื่องแล้ว"],
    pause_to_request: ["Pause the team before requesting a record yourself.", "พักทีมก่อนจึงจะขอเอกสารเองได้"],
    invalid_note: ["Notes must be 1–1000 characters, up to 20 per room.", "บันทึกต้องยาว 1–1000 ตัวอักษร และส่งได้ไม่เกิน 20 ครั้งต่อห้อง"],
    control_limit: ["This room has reached its limit of 40 pause/resume/stop actions. The time limit still applies.", "ห้องนี้ใช้ปุ่มพัก/ทำต่อ/หยุดครบ 40 ครั้งแล้ว เวลาสูงสุดยังมีผลตามเดิม"],
    invalid_room_control: ["That action is not available in the room's current state.", "ทำรายการนี้ไม่ได้ในสถานะปัจจุบันของห้อง"],
    invalid_run_limits: ["Use 1–300 seconds.", "ใช้เวลา 1–300 วินาที"],
    budget_exceeded: ["Not enough evidence budget left for this record.", "งบขอเอกสารเหลือไม่พอสำหรับเอกสารนี้"],
    session_completed: ["The review has already concluded.", "การทบทวนสรุปผลไปแล้ว"],
    unknown_case: ["That case is not available.", "ไม่พบเคสนี้"],
    network: ["Cannot reach the local server.", "ติดต่อระบบบนเครื่องไม่ได้"],
    unknown_provider: ["Choose one of the listed providers.", "เลือกผู้ให้บริการจากรายการ"],
    invalid_api_key: ["Paste the API key as one line without spaces (8–400 characters).", "วาง API key เป็นบรรทัดเดียว ไม่มีช่องว่าง (8–400 ตัวอักษร)"],
    invalid_model: ["Model IDs use letters, digits and . _ : / @ + - only.", "ชื่อรุ่นใช้ได้เฉพาะตัวอักษร ตัวเลข และ . _ : / @ + -"],
    invalid_base_url: ["Ollama must run on this computer, e.g. http://127.0.0.1:11434.", "Ollama ต้องอยู่บนเครื่องนี้ เช่น http://127.0.0.1:11434"],
    key_not_used: ["This provider does not use an API key.", "ผู้ให้บริการนี้ไม่ใช้ API key"],
    missing_api_key: ["Save an API key before testing.", "บันทึก API key ก่อนทดสอบ"],
    settings_unreadable: ["The local settings file could not be read.", "อ่านไฟล์การตั้งค่าบนเครื่องไม่ได้"],
  };

  const recordNames = {
    closure_summary: ["Closure cover sheet", "ใบสรุปปิด CAPA"],
    closure_protocol: ["Closure criteria", "เกณฑ์ปิดและตรวจประสิทธิผล"],
    implementation_record: ["Implementation record", "หลักฐานการดำเนินการ"],
    effectiveness_report: ["Effectiveness report", "รายงานตรวจประสิทธิผล"],
    deviation_trend: ["Related deviations", "การทบทวน deviation ที่เกี่ยวข้อง"],
    status_log: ["Current status register", "ทะเบียนสถานะปัจจุบัน"],
    training_record: ["Training record", "ทะเบียนฝึกอบรม"],
    shift_log: ["Shift log", "บันทึกประจำกะ"],
  };

  // Thai names for record field keys only; field values are always shown as recorded.
  const factLabels = {
    acceptance_pass: "ผ่านเกณฑ์ยอมรับ", as_of: "วันที่ข้อมูล", batch_ids: "รุ่นผลิต", batches_reviewed: "รุ่นผลิตที่ทบทวน",
    capa_id: "CAPA", claimed_effective: "ระบุว่ามีประสิทธิผล", closure_date: "วันที่ปิด", closure_requires: "เงื่อนไขการปิด",
    completed_on: "วันที่ดำเนินการเสร็จ", date: "วันที่", effective_date: "วันที่มีผล", failed_acceptance_batches: "รุ่นผลิตที่ไม่ผ่านเกณฑ์",
    id: "รหัส", line: "สายการผลิต", maximum_failed_batches: "รุ่นผลิตไม่ผ่านได้สูงสุด",
    maximum_unresolved_related_deviations: "deviation ค้างได้สูงสุด", minimum_batches: "จำนวนรุ่นผลิตขั้นต่ำ", notes: "หมายเหตุ",
    operator_ids: "ผู้ปฏิบัติงาน", procedure: "วิธีปฏิบัติ", protocol_id: "เกณฑ์อ้างอิง", protocol_revision: "ฉบับของเกณฑ์",
    record_type: "ประเภทเอกสาร", register_complete: "ทะเบียนครบถ้วน", required_operator_ids: "ผู้ปฏิบัติงานที่ต้องผ่านการอบรม",
    required_procedure: "วิธีปฏิบัติที่กำหนด", review_complete: "ทบทวนครบถ้วน", review_completed_on: "วันที่ทบทวนเสร็จ",
    revision: "ฉบับ", scope: "ขอบเขต", shift: "กะ", status: "สถานะ", unresolved_related_deviations: "deviation ที่ยังไม่ปิด",
    window_end: "สิ้นสุดช่วงติดตาม", window_start: "เริ่มช่วงติดตาม",
  };

  // Static, trusted SVG icons (no user data is ever interpolated here).
  const icons = {
    chat: '<path d="M4 5h16v11H8l-4 4z"/>',
    grid: '<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>',
    desk: '<path d="M5 4h10l4 4v12H5z"/><path d="M14 4v5h5M8 13h8M8 17h6"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
    close: '<path d="M6 6l12 12M18 6L6 18"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    moon: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
    pause: '<path d="M9 6v12M15 6v12"/>',
    play: '<path d="M8 5.5v13l10-6.5z"/>',
    stop: '<rect x="6.5" y="6.5" width="11" height="11" rx="2"/>',
    send: '<path d="M5 12l14-7-5 15-3-6z"/>',
    file: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/>',
    download: '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
    clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    search: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    factory: '<path d="M3 20V10l6 3V10l6 3V6h6v14z"/><path d="M7 17h2M12 17h2M17 17h1"/>',
    shield: '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
    check: '<path d="M8 4h8v3H8z"/><path d="M6 6h2M16 6h2v15H6V6"/><path d="M9 14l2 2 4-4"/>',
    user: '<circle cx="12" cy="8.5" r="3.5"/><path d="M5 20c1.2-3.5 4-5 7-5s5.8 1.5 7 5"/>',
    spark: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M6 18l2.5-2.5M15.5 8.5L18 6"/>',
    alert: '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17v.01"/>',
    refresh: '<path d="M20 11a8 8 0 0 0-14-4.5L4 9M4 4v5h5M4 13a8 8 0 0 0 14 4.5l2-2.5M20 20v-5h-5"/>',
    arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    down: '<path d="M12 5v14M6 13l6 6 6-6"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M12 2.5v3M12 18.5v3M4.2 6.5l2.6 1.5M17.2 16l2.6 1.5M4.2 17.5l2.6-1.5M17.2 8l2.6-1.5"/><circle cx="12" cy="12" r="7"/>',
    down: '<path d="M12 5v14M6 13l6 6 6-6"/>',
    flag: '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
    hourglass: '<path d="M7 3h10M7 21h10M8 3c0 5 8 5 8 9s-8 4-8 9M16 3c0 5-8 5-8 9"/>',
  };

  // ---- Illustrated characters (original artwork of the simulated roles, not real people) ----
  // Loaded once and inlined so live.css can animate blinking and talking (class hooks
  // ch-eyes / ch-mouth / ch-mouth-open). Falls back to <img> if a fetch fails.
  const CHARACTERS = ["investigator", "checker", "manufacturing", "quality", "you"];
  const characterSvg = {};
  const charactersReady = Promise.allSettled(CHARACTERS.map(async (key) => {
    const response = await fetch(`/characters/${key}.svg`);
    if (!response.ok) throw new Error(key);
    const doc = new DOMParser().parseFromString(await response.text(), "image/svg+xml");
    const svg = doc.documentElement;
    if (svg.nodeName !== "svg" || svg.querySelector("script, foreignObject, [onload], [onclick]")) throw new Error(key);
    svg.querySelectorAll("title").forEach((n) => n.remove());
    svg.removeAttribute("role");
    svg.removeAttribute("aria-label");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("focusable", "false");
    characterSvg[key] = svg;
  }));
  // Fictional characters and their style "system prompts" live in personas.js (loaded first).
  const PERSONAS = window.QAWR_PERSONAS || {};
  const DOC_TYPES = new Set(["closure_summary", "closure_protocol", "implementation_record", "effectiveness_report", "deviation_trend", "status_log", "training_record", "shift_log"]);

  let lang = read(LANG_KEY, "th") === "en" ? "en" : "th";
  const savedTheme = read(THEME_KEY, "");
  let theme = savedTheme === "dark" || savedTheme === "light" ? savedTheme
    : (window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document.documentElement.lang = lang;
  document.documentElement.dataset.theme = theme;

  const idx = () => (lang === "th" ? 1 : 0);
  const t = (key) => copy[key]?.[idx()] ?? key;

  function icon(name, className = "icon") {
    const span = document.createElement("span");
    span.className = className;
    span.setAttribute("aria-hidden", "true");
    span.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${icons[name] || ""}</svg>`;
    return span;
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function character(key, className = "avatar") {
    const span = el("span", `${className} ch ch-${key}`);
    span.setAttribute("aria-hidden", "true");
    if (characterSvg[key]) span.append(document.importNode(characterSvg[key], true));
    else if (CHARACTERS.includes(key)) { const img = el("img"); img.src = `/characters/${key}.svg`; img.alt = ""; span.append(img); }
    else span.append(icon("spark"));
    return span;
  }

  function docIcon(type, className = "doc-icon") {
    const img = el("img", className);
    img.src = `/docs/${DOC_TYPES.has(type) ? type : "generic"}.svg`;
    img.alt = "";
    img.decoding = "async";
    return img;
  }

  /** Overlapping team illustration used on the setup and dashboard heroes. */
  function lineup(className = "lineup") {
    const wrap = el("div", className);
    wrap.setAttribute("aria-hidden", "true");
    ["investigator", "manufacturing", "quality", "checker"].forEach((key, i) => {
      const item = el("span", `lineup-item lineup-${i}`);
      item.append(character(key, "lineup-avatar"), el("span", "lineup-name", PERSONAS[key]?.name[idx()] || ""));
      wrap.append(item);
    });
    return wrap;
  }

  function apply(root = document) {
    document.documentElement.lang = lang;
    root.querySelectorAll("[data-ui]").forEach((n) => { n.textContent = t(n.dataset.ui); });
    root.querySelectorAll("[data-ui-placeholder]").forEach((n) => { n.placeholder = t(n.dataset.uiPlaceholder); });
    root.querySelectorAll("[data-ui-label]").forEach((n) => { n.setAttribute("aria-label", t(n.dataset.uiLabel)); });
    root.querySelectorAll("[data-ui-title]").forEach((n) => { n.title = t(n.dataset.uiTitle); });
    root.querySelectorAll("[data-icon]").forEach((n) => { if (!n.firstChild) n.append(icon(n.dataset.icon)); });
    document.querySelectorAll(".js-lang").forEach((button) => {
      button.textContent = lang === "th" ? "EN" : "ไทย";
      button.setAttribute("aria-label", t("switchLang"));
      button.title = t("switchLang");
    });
    syncThemeButton();
  }

  function syncThemeButton() {
    const label = t(theme === "dark" ? "themeToLight" : "themeToDark");
    document.querySelectorAll(".js-theme").forEach((button) => {
      button.replaceChildren(icon(theme === "dark" ? "sun" : "moon"));
      button.setAttribute("aria-label", label);
      button.title = label;
    });
  }

  function setLang(value) {
    lang = value === "en" ? "en" : "th";
    write(LANG_KEY, lang);
    apply();
    document.dispatchEvent(new Event("qa-language"));
  }

  function setTheme(value) {
    theme = value === "dark" ? "dark" : "light";
    document.documentElement.dataset.theme = theme;
    write(THEME_KEY, theme);
    syncThemeButton();
  }

  /** Called once by each page script after the DOM is ready. */
  function mount() {
    document.querySelectorAll(".js-lang").forEach((b) => b.addEventListener("click", () => setLang(lang === "th" ? "en" : "th")));
    document.querySelectorAll(".js-theme").forEach((b) => b.addEventListener("click", () => setTheme(theme === "dark" ? "light" : "dark")));
    apply();
  }

  // ---- Case and record presentation (public metadata only) ----
  const isPackaging = (c) => /packag/i.test(c?.process || c?.title || "");
  const caseNumber = (c) => (c?.id || "").split("-").pop() || "";
  function caseTitle(c) {
    if (!c) return "";
    if (lang === "en") return c.title;
    return `ทบทวน CAPA ${isPackaging(c) ? "งานบรรจุ" : "งานผสม"} · ${caseNumber(c)}`;
  }
  function caseProcess(c) {
    if (!c) return "";
    if (lang === "en") return c.process || "";
    return isPackaging(c) ? "ยาเม็ด · บรรจุและกระทบยอดฉลาก" : "ยาเม็ด · ขั้นตอนผสม";
  }
  function caseClaim(c) {
    if (!c) return "";
    if (lang === "en") return c.claim;
    const m = c.claim?.match(/^As of (.*?), (.*?) meets every closure criterion explicitly specified in (.*?) revision (\d+) for line (.*?) and batches (.*?)\.$/);
    return m ? `ณ วันที่ ${m[1]} ${m[2]} ผ่านเกณฑ์การปิดทุกข้อใน ${m[3]} ฉบับ ${m[4]} สำหรับสายการผลิต ${m[5]} และรุ่นผลิต ${m[6]}` : c.claim;
  }
  const recordTitle = (r) => recordNames[r?.document_type]?.[idx()] || r?.title || "";
  const factLabel = (key) => (lang === "th" ? factLabels[key] : null) || key.replaceAll("_", " ");
  const message = (m) => (lang === "th" ? (m.text_th || m.text) : m.text);
  const verdict = (v) => (copy[`v_${v}`] ? t(`v_${v}`) : v);
  const status = (s) => (copy[`s_${s}`] ? t(`s_${s}`) : s);
  const STATUS_TONE = { running: "live", paused: "warn", completed: "done", time_limit: "partial", stopped: "partial", turn_limit: "partial", error: "danger", stale: "muted" };
  const tone = (s) => STATUS_TONE[s] || "muted";

  function errorText(error) {
    const entry = errorCopy[error?.code];
    if (entry) return entry[idx()];
    return error?.message || t("connectionLost");
  }

  function clock(seconds) {
    const v = Math.max(0, Math.ceil(Number(seconds) || 0));
    return `${String(Math.floor(v / 60)).padStart(2, "0")}:${String(v % 60).padStart(2, "0")}`;
  }

  function timeOfDay(date) {
    return date.toLocaleTimeString(lang === "th" ? "th-TH" : "en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  /** Mobile/off-canvas sidebar shared by both pages. */
  function bindSidebar(app) {
    const toggle = document.getElementById("nav-toggle");
    const scrim = document.getElementById("scrim");
    const sidebar = document.getElementById("sidebar");
    if (!toggle || !sidebar) return { close() {} };
    const set = (open) => {
      app.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      if (open) sidebar.querySelector("a,button")?.focus();
    };
    toggle.addEventListener("click", () => set(!app.classList.contains("nav-open")));
    scrim?.addEventListener("click", () => set(false));
    return { close: () => set(false), open: () => set(true) };
  }

  return {
    persona: (key) => (PERSONAS[key]?.name[idx()] || ""),
    trait: (key) => (PERSONAS[key]?.trait[idx()] || ""),
    systemPrompt: (key) => (PERSONAS[key]?.systemPrompt?.[lang] || ""),
    voiceFor: (key) => PERSONAS[key]?.voice?.[lang] || null,
    t, el, icon, character, docIcon, lineup, charactersReady, apply, mount, setLang, setTheme, errorText, clock, timeOfDay, bindSidebar,
    get lang() { return lang; },
    get theme() { return theme; },
    caseTitle, caseClaim, caseProcess, recordTitle, factLabel, message, verdict, status, tone,
  };
})();
