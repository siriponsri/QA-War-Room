"""Authored Thai presentation of public offline workflow messages, not an LLM."""

import re

PHRASES = {
    "All explicit local-protocol prerequisites are documented in the retrieved records, within the specified scope and cutoff. This conclusion applies only to this fictional protocol and case.": "เอกสารที่ได้รับแสดงว่าครบเงื่อนไขของเกณฑ์จำลอง ทั้งขอบเขตและวันตัดข้อมูล ข้อสรุปนี้ใช้กับเคสและเกณฑ์จำลองนี้เท่านั้น",
    "The closure criteria have not been retrieved; I cannot establish the claim.": "ยังไม่ได้รับเกณฑ์การปิด CAPA จึงยังยืนยันข้อกล่าวอ้างไม่ได้",
    "Implementation evidence is missing.": "ยังขาดหลักฐานการดำเนินการ",
    "Training evidence is missing.": "ยังขาดหลักฐานการฝึกอบรม",
    "A completed effectiveness report has not been obtained.": "ยังไม่ได้รับรายงานตรวจประสิทธิผลที่เสร็จสมบูรณ์",
    "A current related-deviation review is missing.": "ยังขาดการทบทวน deviation ที่เกี่ยวข้องฉบับปัจจุบัน",
    "A current complete status register is missing.": "ยังขาดทะเบียนสถานะที่ครบถ้วน ณ วันตัดข้อมูล",
    "The shortcut policy could not retrieve a closure cover sheet.": "การอ่านแบบสรุปยังไม่ได้รับใบสรุปปิด CAPA",
    "Implementation documentation falls after the review cutoff.": "หลักฐานการดำเนินการอยู่หลังวันตัดข้อมูล",
    "The training register is not a complete snapshot available at the review cutoff.": "ทะเบียนฝึกอบรมยังไม่ใช่ข้อมูลครบถ้วนที่มีอยู่ ณ วันตัดข้อมูล",
    "The effectiveness report was not completed within the review cutoff.": "รายงานประสิทธิผลเสร็จหลังวันตัดข้อมูล",
    "The related-deviation review is not a complete current in-scope review.": "การทบทวน deviation ยังไม่ครบ เป็นปัจจุบัน หรือตรงขอบเขตที่กำหนด",
    "The status register does not establish current status at the cutoff.": "ทะเบียนสถานะยังยืนยันสถานะ ณ วันตัดข้อมูลไม่ได้",
    "Missing or out-of-scope evidence does not by itself establish manufacturing failure.": "การขาดหลักฐานหรือหลักฐานผิดขอบเขต ไม่ได้แปลว่าการผลิตผิดข้อกำหนดโดยอัตโนมัติ",
    "Shortcut baseline: the cover sheet marks this CAPA closed and effective. This policy intentionally does not verify the underlying evidence.": "ใบสรุประบุว่า CAPA ปิดและมีประสิทธิผล การอ่านแบบสรุปนี้ยังไม่ได้ตรวจหลักฐานประกอบ จึงต้องส่งให้ผู้ตรวจหลักฐานทบทวน",
    "The implementation record concerns a different line or CAPA.": "เอกสารดำเนินการอ้างถึงสายการผลิตหรือ CAPA คนละรายการ",
    "The effectiveness report does not cover the required protocol revision, line, batches and observation window.": "รายงานประสิทธิผลไม่ครอบคลุมฉบับเกณฑ์ สายการผลิต รุ่นผลิต หรือช่วงติดตามที่กำหนด",
    "The current related-deviation review exceeds the unresolved-deviation limit in the protocol.": "พบ deviation ที่ยังไม่ปิดเกินจำนวนที่เกณฑ์กำหนด",
    "The complete current register records an open or reopened CAPA at the review cutoff; the protocol requires closed status.": "ทะเบียน ณ วันตัดข้อมูลระบุว่า CAPA ยังเปิดหรือถูกเปิดใหม่ แต่เกณฑ์กำหนดให้ปิดแล้ว",
    "The implementation record explicitly fails the protocol's completion/procedure prerequisite.": "หลักฐานการดำเนินการไม่ผ่านเงื่อนไขการทำให้เสร็จหรือวิธีปฏิบัติที่กำหนด",
    "The complete training register does not meet the required procedure revision, operator coverage, or pre-cohort timing specified by the protocol.": "ทะเบียนฝึกอบรมไม่ครบตามฉบับวิธีปฏิบัติ รายชื่อผู้ปฏิบัติงาน หรือช่วงเวลาที่เกณฑ์กำหนด",
    "The in-scope effectiveness report records failed acceptance against the protocol's explicit criteria.": "รายงานประสิทธิผลที่ตรงขอบเขตระบุผลไม่ผ่านเกณฑ์ยอมรับ",
    "Too few batches were reviewed to demonstrate the required effectiveness criterion.": "จำนวนรุ่นผลิตที่ทบทวนยังน้อยกว่าที่เกณฑ์ประสิทธิผลกำหนด",
    "Proposed decision:": "เสนอข้อสรุป:", "Visible-evidence check:": "ตรวจจากหลักฐานที่ได้รับ:",
    "Checked conclusion:": "ผลทบทวนข้อสรุป:", "Final draft decision:": "สรุปผลฉบับร่าง:",
    "I cannot accept closure yet.": "ยังยอมรับการปิดเคสไม่ได้", "before finalizing.": "ก่อนสรุปผล",
    "Requesting ": "ขอเอกสาร ", "supported": "มีหลักฐานสนับสนุน", "contradicted": "หลักฐานขัดแย้ง", "insufficient": "หลักฐานยังไม่เพียงพอ",
    "The requested record was not delivered.": "ไม่ได้รับเอกสารที่ขอ", "Requested ": "ขอเอกสาร ",
    "from the evidence register.": "จากรายการหลักฐาน",
}
FIXED = {
    "started": "เปิดห้องสนทนาแล้ว ผู้ทบทวนจะขอหลักฐาน เจ้าของเอกสารจะส่งข้อมูล และผู้ตรวจหลักฐานจะทบทวนต่อกัน เป็นทีมจำลองที่ทำงานตามกติกาในเคสสมมติ",
    "time_limit": "ครบเวลาที่ตั้งไว้แล้ว ระบบหยุดพร้อมเก็บหลักฐานปัจจุบัน โดยไม่บังคับข้อสรุปและไม่เปิดเฉลย",
    "completed": "กระบวนการเสร็จแล้ว เปิดดูผลเทียบกับคำตอบอ้างอิงของเคสจำลองได้ ข้อสรุปนี้ไม่ใช่การอนุมัติ GMP หรือ CAPA จริง",
    "stopped": "หยุดการทำงานแล้ว เก็บข้อความและหลักฐานที่ได้รับไว้ โดยไม่บังคับข้อสรุป",
    "turn_limit": "ครบจำนวนรอบสูงสุดแล้ว หยุดพร้อมเก็บงานค้างไว้ โดยไม่บังคับข้อสรุป",
    "error": "หยุดเนื่องจากปัญหาในการประมวลผล ข้อความและหลักฐานเดิมยังถูกเก็บไว้",
    "paused": "พักทีมแล้ว เวลาที่กำหนดยังคงเดินต่อ", "resumed": "ให้ทีมทำงานต่อแล้ว",
}


def thai_message(kind, text):
    if kind in FIXED:
        return FIXED[kind]
    if kind == "note":
        return text
    if kind == "request" and text.startswith("Please provide "):
        matched = re.match(r"Please provide (.+?) · (.+?) \((\d+) credit\)", text)
        if matched:
            return f"ขอเอกสาร {matched[1]} — {matched[2]} ใช้งบหลักฐาน {matched[3]} หน่วย เพื่อนำมาทบทวนข้อกล่าวอ้างนี้"
    if kind == "record":
        matched = re.match(r"Delivered (.+?): (.+?)\. Revision (.+?) · (.+?)\.", text)
        if matched:
            return f"ส่งเอกสาร {matched[1]} แล้ว — {matched[2]} ฉบับ {matched[3]} วันที่ {matched[4]} เปิดเอกสารแนบเพื่อตรวจข้อมูลได้"
    value = text
    for source in sorted(PHRASES, key=len, reverse=True):
        value = value.replace(source, PHRASES[source])
    return value
