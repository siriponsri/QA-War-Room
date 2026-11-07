# เริ่ม QA War Room ใน Codex

## โฟลเดอร์ที่ใช้

เปิด workspace นี้:

```text
C:\Users\User\Desktop\myProject\qa-war-room
```

เมื่อแตก ZIP ถูกตำแหน่ง ไฟล์ AGENTS.md, README.md, GOAL.md, PLAN.md และโฟลเดอร์ qa_war_room, docs, reading-pack, benchmark-data จะอยู่ภายในโฟลเดอร์นี้ทันที ไม่มีโฟลเดอร์ repository ซ้อนอีกชั้น

ZIP นี้รวมโค้ด เอกสาร แผนวิจัย บทความที่ดาวน์โหลดได้ และข้อมูล benchmark แล้ว ใช้ไฟล์นี้เพียงไฟล์เดียวสำหรับเริ่ม session

## Prompt สำหรับวางใน Codex

```text
ทำงานใน C:\Users\User\Desktop\myProject\qa-war-room

นี่คือโครงการ QA War Room ของผม เป็น solo project ที่พัฒนา product และงานวิจัย pharmaceutical ควบคู่กัน ขอบเขตแรกคือ Manufacturing GMP โดยเน้นหลักฐานสำหรับ deviation/CAPA effectiveness และ closure claims

อ่าน AGENTS.md, GOAL.md, PLAN.md, STATUS.md, HANDOFF_TO_CODEX.md และ docs/DECISIONS.md ก่อน จากนั้นตรวจโครงสร้างจริงใน workspace และรักษางานที่มีอยู่

ชุดนี้มีโค้ดที่ root แล้ว มี reading-pack/ และ benchmark-data/ อยู่ภายใน root และถูก Git ignore อย่าย้ายกลับไปสร้างโฟลเดอร์ repository/ หรือเผยแพร่ไฟล์เหล่านี้โดยไม่ตั้งใจ

เริ่มด้วยการตรวจ Python และรัน tests, engineering smoke runner, benchmark preparation แล้วเปิด localhost เพื่อทดสอบ UI จริง แก้ปัญหาที่พบให้ใช้งานได้ก่อนดำเนิน milestone ต่อไป

เมื่อ starter ผ่าน ให้ทำงานต่อที่ native benchmark runner พร้อม model interface, deterministic offline adapter, metrics ตามต้นฉบับ, การแยก input/gold, resumable logs และการจำกัดงบ ตาม HANDOFF_TO_CODEX.md

ทำงาน local ที่อยู่ในขอบเขตนี้ต่อเนื่องและอัปเดต STATUS.md ไม่หยุดหลังเสนอแผน หากยังไม่มี API key หรืองบ ให้ทำส่วน offline ให้เสร็จ และรายงานเฉพาะสิ่งที่ขาดก่อนเริ่ม paid inference อย่าสร้างผลทดลองหรืออ้าง pharmaceutical validation ที่ยังไม่ได้ทำ

ตอบผมเป็นภาษาไทย เอกสารเทคนิคและโค้ดใช้ภาษาอังกฤษ รักษาคู่มือภาษาไทยไว้
```

## คำสั่งตรวจเบื้องต้น

เปิด PowerShell ที่โฟลเดอร์หลัก แล้วรัน:

```powershell
Set-Location "C:\Users\User\Desktop\myProject\qa-war-room"
py -3 -m unittest discover -s tests -v
py -3 scripts/prepare_benchmarks.py
py -3 -m qa_war_room --port 8765
```

เปิด http://127.0.0.1:8765 ใน browser และใช้ Ctrl+C เพื่อหยุดเซิร์ฟเวอร์ หากเครื่องใช้คำสั่ง python แทน py ให้เปลี่ยน py -3 เป็น python

Codex สามารถตรวจและรันคำสั่งเหล่านี้ให้ได้ ไม่จำเป็นต้องทำเองก่อนเริ่ม session

## สถานะที่ต้องเข้าใจ

ตัวเว็บปัจจุบันเป็น offline scripted demo ที่มี 8 เคสจาก 2 template families ยังไม่ได้เรียก LLM หรือฝึก RL มี benchmark ต้นฉบับสำหรับเตรียมการทดลอง แต่ยังไม่มีผล LLM benchmark หรือ independent pharmaceutical validation

การตรวจจากสภาพแวดล้อมที่จัดแพ็กเกจไม่แทนการทดสอบบน Windows เครื่องนี้ ให้ Codex ตรวจ UI และคำสั่งบนเครื่องจริงเป็นงานแรก

ใช้ START_HERE_TH.md สำหรับอ่านภาพรวมงานวิจัยและสินค้าโดยละเอียด
