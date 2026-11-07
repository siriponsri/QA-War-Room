# Prompt สำหรับส่งกลับให้ ChatGPT / Codex ทำวิจัยต่อ

คัดลอกข้อความในกรอบด้านล่างไปวางได้เลย ก่อนส่งให้กรอกบรรทัด **งบ API รอบนี้** ถ้าไม่กรอก ให้ถือว่าห้ามเรียกโมเดลที่เสียเงิน

---

```text
ทำงานใน C:\Users\User\Desktop\myProject\qa-war-room

ผมให้คุณกลับมารับช่วง QA War Room ต่อ โดยเน้นงานวิจัย หลังจาก Claude ทำ frontend และหน้าตั้งค่า AI เสร็จแล้ว ใช้ workspace ปัจจุบันเป็นหลัก ไม่เอา source จาก archive เก่ามาทับ

อ่านตามลำดับก่อนเริ่ม:
1. AGENTS.md (กติกาหลัก ใช้ทุกข้อ) และกฎ shell ในเครื่อง C:\Users\User\.codex\RTK.md
2. HANDOFF_BACK_TO_CODEX.md (สิ่งที่ Claude ทำ ไฟล์ที่แก้ ผลทดสอบ สถานะ runtime และข้อเสนอ)
3. STATUS.md ส่วนบนสุด แล้วต่อด้วย "Next session" และ handoff G4/G5/G6 เดิม
4. docs/DECISIONS.md (โดยเฉพาะ D07, D19–D21), GOAL.md, PLAN.md, docs/RESEARCH_PROTOCOL.md, docs/EVALUATION_SPEC.md, docs/G5_EVALUATION_PLAN.md, docs/G6_REPRODUCIBILITY.md, docs/AGENT_PERSONAS.md

ขั้นแรก ตรวจ baseline ให้ตรงกับ handoff ก่อนแก้อะไร:
- รัน full suite ด้วย ResourceWarning เป็น error (ล่าสุด Claude รายงานไว้ 195 tests) และ node --check ไฟล์ static
- server ที่ port 8765 เปิดไว้ก่อนมี route /api/settings ให้รีสตาร์ตก่อนใช้งาน ส่วน port 8766 เป็นตัวทดสอบของ Claude ปิดได้
- ถ้าผลไม่ตรงกับ handoff ให้บันทึกความต่างตามจริงก่อนทำงานต่อ

ขอบเขตงานวิจัยรอบนี้ (เรียงตามความสำคัญ):
1. วางและทำ model adapter แบบ offline-first สำหรับ sequential evidence acquisition ใช้ provider/model ที่ตั้งไว้ใน ProviderSettings (qa_war_room/provider_settings.py) ต้องมี hard cap จำนวนครั้งและค่าใช้จ่ายต่อ run แบบจองก่อนเรียก (แนวเดียวกับ native_runner.py) บันทึก provider, model ID, prompt version/hash, token usage และ cost ทุกครั้ง ถ้าไม่มีงบหรือเกิน cap ต้องปฏิเสธ ไม่เรียกต่อ
2. รักษาการแยก observation/gold อย่างเคร่งครัด: โมเดลเห็นเฉพาะ public case metadata และเอกสารที่ขอแล้วเท่านั้น ห้ามให้ gold, reference rationale, เอกสารที่ไม่ได้ขอ หรือ evaluator output เข้า prompt, retrieval หรือ few-shot ห้ามใช้ข้อมูล evaluation/test มาจูน prompt
3. ถ้ามีงบ ให้รันได้เฉพาะ pilot เล็กบน dev split ที่กำหนดไว้แล้ว เพื่อเป็น engineering check ห้ามเรียกผลนี้ว่าผลวิทยาศาสตร์ และห้ามรัน confirmatory หรือ test split
4. เตรียมงาน independent review G4 ต่อได้ (packet, instruction, intake format) แต่ห้ามกรอกคะแนนผู้ตรวจสมมติ ห้ามใช้ความเห็นของโมเดลเป็น gold และห้ามเปลี่ยนสถานะ NOT_PERFORMED / NOT_LOCKED / NOT_RUN จนกว่าจะมีผู้ตรวจจริงพร้อม provenance
5. ระบุสิ่งที่ยังต้องให้ผมตัดสินใจก่อน Stage B lock (jurisdiction/intended use, sample size, margins, primary methods, multiplicity) โดยเขียนเป็นคำถามสั้นที่ตอบได้ อย่าตัดสินใจแทน

งบ API รอบนี้: ____ USD รวม (ถ้าว่างหรือเป็น 0 = ห้ามเรียกโมเดลที่เสียเงินทุกกรณี)
ผู้ให้บริการที่อนุญาต: Typhoon และ OpenRouter (key อยู่ใน .qawr/provider-settings.json แล้ว)
จำนวนครั้งสูงสุดต่อ run: ____ ครั้ง

ข้อห้ามสำคัญ:
- ห้ามพิมพ์ คัดลอก อัปโหลด หรือใส่ .qawr/provider-settings.json ลงใน archive, log, รายงาน หรือ reproducibility bundle อ่าน key ผ่าน ProviderSettings เท่านั้น และห้ามแสดง key ใน output
- ห้ามแก้ dataset, gold, budget เดิมของ benchmark, evaluator, frozen lock หรือ archive เดิม (reports/g6-reproducibility-v1/ และ runs เก่า) ให้สร้าง path ใหม่เสมอ
- ห้าม push, deploy, publish, ส่งข้อความภายนอก หรือ assign license
- ห้องสนทนา (live room) ยังเป็น rule-based ถ้าจะให้ agent ในห้องใช้โมเดลจริง ให้เสนอแผนและถามผมก่อน
- สำนวนตัวละครใน personas.js เป็นแค่ display layer ถ้าจะใช้เป็นตัวแปรวิจัยต้องมี protocol ชัดเจนก่อน
- อย่าอ้างว่าทดสอบ, รัน experiment หรือได้ผลใดๆ ถ้ายังไม่ได้ทำจริง รายงานผลลบและความไม่แน่นอนตามจริง

ส่งมอบเมื่อจบรอบ:
- ตอบผมเป็นภาษาไทย โค้ดและเอกสารเทคนิคเป็นภาษาอังกฤษ
- อัปเดต STATUS.md (สิ่งที่ทำได้จริง, คำสั่งที่รัน, ผลทดสอบ, ค่าใช้จ่ายจริงเป็น USD, ข้อจำกัด, งานถัดไป) และ docs/DECISIONS.md ถ้ามีการตัดสินใจใหม่
- แยกให้ชัดระหว่าง implemented / tested / proposed / blocked
- ทุก experimental claim ต้องมี dataset version, split, baseline, evaluator และ run record
```

---

หมายเหตุสำหรับเจ้าของงาน:
- ถ้าต้องการให้ทำเฉพาะงานที่ไม่เสียเงิน ปล่อยบรรทัดงบว่างไว้ Codex จะทำ adapter, การทดสอบแบบ offline และงานเตรียม review ได้
- ถ้าจะให้รัน pilot ด้วยโมเดลจริง ใส่งบรวมและจำนวนครั้งสูงสุด เช่น 2 USD และ 200 ครั้ง (ตัวเลขนี้เป็นแค่ตัวอย่าง ไม่ใช่คำแนะนำด้านงบ)
- ก่อนส่ง prompt ให้รีสตาร์ต server ที่ port 8765 ถ้ายังไม่ได้ทำ
