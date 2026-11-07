# QA War Room — Starter Package และแผน Product + Pharmaceutical Research

**เวอร์ชัน 0.1 · 7 พฤศจิกายน 2026**  
**ขอบเขตที่เลือกแล้ว: Manufacturing GMP · Solo project · ใช้ open benchmark ที่มี paper ก่อน**

## 1. ข้อเสนอหลัก

ให้ใช้ชื่อโครงการ **QA War Room** ต่อไป และเรียกโมดูลแรกว่า **CAPA Evidence Review**: ระบบซ้อม audit และช่วยทบทวนหลักฐานว่า ข้อกล่าวอ้างเกี่ยวกับการดำเนินการและประสิทธิผลของ CAPA มีหลักฐานรองรับเพียงพอหรือยัง

คำถามหลักสำหรับ paper คือ:

> ภายใต้งบการขอหลักฐานที่กำหนด ระบบที่เลือกขอเอกสารทีละขั้นและตรวจความเพียงพอ/ความเกี่ยวข้องของหลักฐาน ช่วยลดข้อสรุปว่า CAPA มีหลักฐานรองรับทั้งที่จริงยังไม่รองรับได้หรือไม่ โดยยังตัดสินเคสที่มีหลักฐานครบได้ดี?

นี่เป็นสมมติฐานที่จะทดสอบ ยังไม่มีผลยืนยันว่าหลาย agent, RL หรือวิธีที่เสนอเหนือกว่าวิธีง่ายกว่า

จุดที่มีความหมายทาง pharmaceutical คือการแยก **ทำ action แล้ว / มีเอกสารแล้ว / ประเมิน effectiveness แล้ว / หลักฐานรองรับ claim นี้จริง** ออกจากกัน ICH Q10§3.2.2 และตารางการใช้ CAPA ในช่วง commercial manufacturing ให้เหตุผลเชิงโดเมนสำหรับการประเมิน effectiveness แต่จำนวน batch หรือช่วงเวลาที่เหมาะสมต้องกำหนดตามบริบท ไม่ควรแต่งขึ้นว่าเป็นเกณฑ์ GMP สากล [ICH Q10](https://database.ich.org/sites/default/files/Q10_Guideline.pdf)

## 2. สิ่งที่ส่งมอบ

| ส่วน | ใช้ทำอะไร |
|---|---|
| โฟลเดอร์หลัก qa-war-room/ | โค้ดเว็บ/เซิร์ฟเวอร์ ตัวอย่างเคส tests และเอกสารที่จะนำเข้า repo |
| reading-pack/ | PDF บทความ 21 เรื่อง, full-text XML อีก 1 เรื่อง, เอกสารอ้างอิงทางการ 6PDF และสถานะดาวน์โหลด |
| benchmark-data/ | ข้อมูล ContractNLI และ Sino-US-DrugQA ฉบับเปิดที่ตรึงเวอร์ชัน พร้อม license/checksum |
| START_HERE_TH.md | คู่มือเจ้าของโครงการฉบับนี้ |

PDF และข้อมูลวิจัยอยู่แยกจากโค้ดที่จะนำขึ้น GitHub เพราะสิทธิ์ของ code, paper, dataset และเอกสารต้นทางต่างกัน

แพ็กเกจนี้มีทั้งของที่รันได้จริงและแผนต่อยอด ส่วนที่ยังเป็นแผนติดป้ายไว้อย่างชัดเจน

## 3. ตัวอย่างที่รันได้ตอนนี้

เว็บทำวงจรหนึ่งเคสได้ครบ: เลือกเคส → ดู claim และวันที่ประเมิน → ขอเอกสารตาม budget → อ่านหลักฐาน → เลือก citation → ส่งข้อสรุป → ดู debrief → ดาวน์โหลดรายงาน Markdown/JSON

มี 8 เคสจำลองจาก 2 ตระกูล template ได้แก่ blending และ packaging ครอบคลุมหลักฐานครบ, effectiveness ไม่ผ่านเกณฑ์, เอกสารสำคัญหาไม่ได้, เอกสารผิด line/batch, revision ไม่ตรง, CAPA ถูกเปิดใหม่ และหลักฐานเกิดหลังวันประเมิน

ชื่อบทบาทครบตามแนวคิดเดิม:

- user-01: ผู้ดูแลบันทึกฝั่ง manufacturing
- user-02: ผู้ดูแลบันทึกฝั่ง quality
- auditor-newbie-01 และ 02
- auditor-expert-01 และ 02

**ในรุ่นนี้เป็น scripted policies** เพื่อทดสอบ environment และ workflow โดยไม่ต้องเสียค่า API ชื่อ newbie/expert ยังไม่ได้พิสูจน์ว่าแทนระดับความสามารถของคนจริง และไม่ได้มีโมเดล AI6 ตัวที่ฝึกแล้ว

ผลประเมินปัจจุบันตรวจ reference verdict และชุด ID ของหลักฐานที่ผู้สร้างเคสกำหนดไว้ จึงยังไม่ใช่ตัวประเมินว่า rationale ภาษาธรรมชาติถูกต้องทาง semantic หรือผ่านการรับรองด้าน pharmaceutical

## 4. เริ่มรันและส่งต่อให้ Codex

แตก ZIP ลงโฟลเดอร์ qa-war-room แล้วเปิด terminal ในโฟลเดอร์หลักนี้ ใช้ Python 3.10 ขึ้นไป:

```bash
python -m qa_war_room --port 8765
```

เปิด http://127.0.0.1:8765 ใน browser ไม่ต้องติดตั้งแพ็กเกจ Python เพิ่มและไม่ต้องใส่ API key หาก Windows ใช้คำสั่ง python ไม่ได้แต่มี Python launcher ให้ใช้ py -3 แทน

ตรวจระบบ:

```bash
python -m unittest discover -s tests -v
python -m qa_war_room benchmark --output runs/engineering-smoke.json
python scripts/prepare_benchmarks.py --source benchmark-data
```

คำสั่ง benchmark ในตอนนี้เป็น **engineering smoke run** ไม่ใช่ผลการทดลองสำหรับ paper

เปิดโฟลเดอร์ qa-war-room นี้เป็น workspace ของ Codex ได้เลย โค้ดอยู่ที่ root แล้ว ใช้ START_CODEX_TH.md เป็นจุดเริ่มต้น และให้ Codex อ่าน AGENTS.md, GOAL.md, STATUS.md, PLAN.md และ HANDOFF_TO_CODEX.md ส่วน reading-pack/ และ benchmark-data/ อยู่ภายในโฟลเดอร์เดียวกันและกำหนดให้ Git ไม่ติดตาม

ตรวจ repo พบว่าเป็น repo สาธารณะที่ยังว่างขณะตรวจ แพ็กเกจนี้ยังไม่ได้ push หรือเผยแพร่ไฟล์ให้ หากมีงานใหม่ใน repo หลังจากนั้นให้ Codex ตรวจและรักษางานเดิมก่อนนำเข้า

## 5. Contribution ที่ตั้งใจพิสูจน์ และสิ่งที่จะใช้ใน product

| Contribution ที่เสนอ | ทดลองอย่างไร | ฟังก์ชันที่ต่อยอด |
|---|---|---|
| ความเพียงพอของหลักฐาน | วัดข้อสรุปเชิงบวกที่ไม่รองรับ พร้อม sensitivity/coverage | เตือนว่าเหตุผลปิด CAPA ยังขาดหลักฐานอะไร |
| การเลือกเอกสารชิ้นถัดไป | เทียบกับ fixed checklist, retrieval และ single-agent ด้วย budget เท่ากัน | แนะนำ next evidence request |
| ความเกี่ยวข้องตาม scope/time/version | เปลี่ยน batch, line, cutoff หรือ revision อย่างควบคุม | ตรวจเอกสารผิดขอบเขตหรือผิดช่วงเวลา |
| การตอบสนองต่อหลักฐานที่เปลี่ยน | เคสคู่ที่ต่างเพียงข้อเท็จจริงสำคัญ + การเปลี่ยนที่ไม่สำคัญ | Replay/debrief ว่าเหตุใดข้อสรุปจึงเปลี่ยน |
| การทำผลซ้ำและตรวจย้อนกลับ | ตรึง case, rule, source, split, prompt และ run | รายงานพร้อมหลักฐานและ regression tests |

ภาพ demo ที่ควรทำให้น่าสนใจคือ ผู้ใช้เห็นแฟ้มที่ดูครบและ cover sheet ระบุปิดแล้ว แต่เมื่อขอข้อมูล effectiveness พบว่าเป็นคนละ batch หรือมี recurrence ก่อนวันประเมิน ระบบชี้จุดขัดแย้งและอธิบายว่าต้องขออะไรเพิ่มได้

สิ่งนี้เป็น **product behavior ที่ออกแบบไว้** ประโยชน์ต่อผู้ใช้จริงยังต้องวัดด้วย pilot การเปลี่ยนคำตอบถูกต้องในโลกจำลองไม่ได้พิสูจน์ว่าลดความเสี่ยงของโรงงานจริงแล้ว

## 6. สิ่งที่ literature ทำให้ต้องปรับ positioning

มี prior art ที่ใกล้แล้ว:

- Salami และคณะ 2024 ทดลอง LLM กับรายงาน manufacturing deviations จริง เพื่อดึงข้อมูลและหาเหตุการณ์ที่คล้ายกัน: [paper](https://arxiv.org/abs/2404.15578)
- WinAI2026 เป็นระบบ audit โรงงาน oral solid dosage ที่มี NLP, rule-based scoring และติดตามการเกิดซ้ำ: [publisher](https://journals.innovareacademics.in/index.php/ijap/article/view/57414)
- IntelliAudit2026 มีการตรวจหลักฐานด้วยบทบาท auditor/defender/judge ใน IT audit: [preprint](https://arxiv.org/abs/2608.07688)
- Waikar และคณะ 2026 ตีพิมพ์การใช้ RAG ประเมิน regulatory compliance ของข้อมูลยาและ clinical protocol ในวารสารสายยา: [DOI](https://doi.org/10.1002/psp4.70201)

จึงควรใช้คำถามและการทดลองที่แคบและเข้มแข็งกว่า “เอา AI มาทำ audit” จุดขายทางวิจัยจะอยู่ที่ **หลักฐานแบบไหนพอสำหรับข้อสรุปใด ระบบหาหลักฐานอย่างไร และผิดแบบไหนเมื่อ scope หรือข้อมูลเปลี่ยน**

Literature review ในแพ็กเกจเป็น targeted narrative review22 รายการ มีตารางวิจารณ์ prior art และข้อจำกัด ยังไม่ใช่ systematic review ที่อ้างค้นครบทุกฐานข้อมูล

## 7. Dataset ที่เตรียมไว้ และข้อจำกัดที่ต้องรักษา

### ContractNLI

มี 607 เอกสาร แบ่ง 423train/61dev/123test ตามต้นฉบับ เหมาะสำหรับทดสอบ entailment, contradiction, NotMentioned และตำแหน่งหลักฐานในเอกสาร ใช้เป็นฐาน method ได้ แต่ไม่ใช่ข้อมูล pharmaceutical [paper](https://aclanthology.org/2021.findings-emnlp.164/)

หากซ่อนเอกสารบางส่วนให้ agent ขอทีละชิ้น จะเป็น **derived interactive task ใหม่** ต้องรายงานแยกจากคะแนน official benchmark ที่ให้เอกสารครบ

### Sino-US-DrugQA

มี 11,444 คำถามตาม authoritative bilingual release และ 4,571 ข้อใน categoryDrugs จากการตรวจไฟล์จริง ใช้ทดสอบความรู้กฎระเบียบประกอบได้ [paper](https://doi.org/10.1371/journal.pone.0343858)

แต่ public JSONL ไม่มี field functional_subdomain แม้ dataset card จะรายงานยอดรวมหมวด Manufacturing & Quality จึงกรอง “Drugs∩GMP”จาก official tag ตรงๆไม่ได้ และไม่ควรเรียกชุดนี้ว่า CAPA audit benchmark ไม่มี official train split; แผนนี้กันไว้สำหรับ evaluation ไม่ใช้เฉลยฝึก RL หรือใส่เข้า RAG

### Pharmaceutical case pack

เริ่มจากเคสเดโมเพื่อพัฒนาระบบ จากนั้นสร้าง research cases ตาม specification แยกต่างหาก มี case rules, decisive facts, counterfactual families และการทบทวนด้านโดเมน ก่อนใช้สนับสนุนข้ออ้างด้าน pharmaceutical

ไม่ควรขยาย 8 เคสเป็นหลักพันเพียงด้วยการ paraphrase แล้วนับว่าเป็นตัวอย่างอิสระหลายพันเคส

## 8. Roadmap ที่ให้ Codex เดินต่อ

| ช่วง | งาน product | งาน research | เงื่อนไขผ่าน |
|---|---|---|---|
| G0 | เว็บ offline และ report | นิยามโจทย์/ขอบเขต | Starter tests และตรวจ UI ด้วยคน |
| G1 | ตัวอ่านข้อมูลและ source register | Native open benchmarks | checksum/schema/splits ถูกต้อง |
| G2 | Model adapter +retrieval | Baselines และ cost ledger | ไม่มี gold รั่วและมี budget จริง |
| G3 | ขอหลักฐานทีละขั้น | Sequential task +counterfactual | แยก task ใหม่และแบ่ง source families |
| G4 | CAPA workflow และ evidence gaps | Manufacturing cases และ domain review | reference labels ตรวจสอบได้ |
| G5 | Report ที่ใช้งานง่าย | Freeze แล้วรันการทดลองหลัก | primary endpoint+guardrails ตามแผน |
| G6 | Pilot/demo สำหรับผู้ใช้ | Manuscript+reproducibility archive | ข้ออ้างตรงกับหลักฐาน |
| G7 | RL/process twin เมื่อจำเป็น | งานต่อยอดตามผลที่พบ | มีเหตุผลจากข้อมูลให้เพิ่มความซับซ้อน |

งบเวลา 12–20 สัปดาห์ของงานเข้มข้นเป็นเพียงกรอบสำหรับวางแผน solo ต้องปรับหลังวัดภาระ annotation และค่า inference จริง ไม่รวมเวลารอผู้ทบทวนหรือวารสาร

## 9. การทดลองที่ทำให้ paper น่าเชื่อถือ

การเปรียบเทียบต้องมี fixed checklist/rules, retrieval, single-agent แบบ sequential, single-agent ที่ได้จำนวน call เทียบเท่า และ multi-agent ที่เสนอ พร้อมแยก oracle/full-context เป็น diagnostic

Primary outcome ที่เสนอคือ false-support rate หรืออัตราแนะนำเชิงบวกทั้งที่ reference ไม่รองรับ ต้องดูคู่กับ sensitivity ต่อเคสที่รองรับจริง, coverage, คะแนน label ทั้งหมด และค่าใช้จ่าย ระบบที่ปฏิเสธทุกเคสหรือ abstain ทุกเคสไม่ถือว่าชนะ

ต้องแยกต้นทางเดียวกัน/เคสคู่/template เดียวกันไว้ใน split เดียว วิเคราะห์ความไม่แน่นอนตามกลุ่มอิสระ และตรึง protocol ก่อนดู test ผลสุดท้าย จำนวนตัวอย่างขึ้นกับ pilot และ precision/power ที่ต้องการ ไม่กำหนดจำนวนสวยๆแล้วอ้างว่าเพียงพอ

กำหนดสองช่วงการตรึงแผน:

1. **Stage A:** benchmark เปิดสำหรับ method development และ feasibility
2. **Stage B:** หากมุ่ง pharmaceutical journal ต้องให้ผล Manufacturing GMP ที่ผ่านการทบทวนเป็น primary หรือ key confirmatory endpoint ก่อน unblinding; native benchmark เป็นหลักฐานประกอบ

หากยังไม่มี domain validation ให้รายงานผลเป็นวิธีเชิงเทคนิคและ constructed-environment evaluation ตามจริง การเป็น solo developer ยังทำได้ แต่อย่าแทนผู้เชี่ยวชาญจริงด้วย prompt ที่ตั้งชื่อว่า expert

## 10. Journal route และความหมายของ impact

เป้าหมายแรกที่เหมาะกับกรอบนี้คือ **Journal of Pharmaceutical Innovation** เมื่อผลด้าน manufacturing quality เป็นสาระหลัก เพราะ scope ครอบคลุม quality management, information management และ process automation [official scope](https://link.springer.com/journal/12247/aims-and-scope)

**PDA Journal of Pharmaceutical Science and Technology** เป็นทางเลือกสำหรับงาน manufacturing/quality ที่มีน้ำหนักทางปฏิบัติ และ **AAPS Open**อาจเหมาะกับนวัตกรรมเชิง pharmaceutical science ที่ชัด [PDA](https://www.pda.org/pda-letter-portal/home/full-article/the-role-of-peer-review-in-the-success-of-the-pda-journal-of-pharmaceutical-science-and-technology), [AAPS Open](https://link.springer.com/journal/41120/aims-and-scope)

ยังประเมิน acceptance หรือรับประกัน impact factor ไม่ได้ การตั้งเป้าควรอยู่ที่ผลที่คนอื่นใช้ซ้ำได้, การพิสูจน์ failure mode ที่สำคัญ และการแปลงผลเป็นฟังก์ชันที่ช่วยผู้ใช้ได้ มีแผน negative results ไว้ด้วย หากหลาย agent ไม่ดีกว่าวิธีง่าย เราได้ทั้งข้อค้นพบและ product ที่ต้นทุนต่ำกว่า

## 11. ขายอะไร

ข้อเสนอเริ่มต้นสำหรับทดสอบตลาดคือ **ชุดซ้อมทบทวนหลักฐาน Manufacturing GMP พร้อม debrief และ report** สำหรับผู้เรียน/ผู้ฝึกอบรมหรือทีม QA ไม่จำเป็นต้องขายระบบตัดสิน compliance อัตโนมัติ

เมื่อได้หลักฐานเพิ่ม จึงพัฒนาเป็นเครื่องมือช่วยตรวจความพร้อมของแฟ้ม CAPA: แสดง missing evidence, contradiction, wrong scope/time และรายการคำถามที่ควรถามต่อ ผู้ซื้อจะจ่ายเพราะงานทบทวนมีประโยชน์และตรวจสอบได้ ต้องทดสอบด้วย pilot ไม่ใช่เพราะมี agent หลายตัว

แผนธุรกิจในแพ็กเกจเป็นสมมติฐานสำหรับสัมภาษณ์และทดลอง ยังไม่มีการยืนยันตลาด ราคา willingness-to-pay หรือ ROI

## 12. สิ่งที่ตรวจแล้วและยังไม่ตรวจ

ตรวจแล้ว: 35 automated tests ครอบคลุม engine/API/การแยก gold/งบ/รายงาน/adapter, JavaScript syntax, ความสอดคล้องของ DOM และ API, checksum/count ของ benchmark, PDF parser และชื่อ/ฉบับของ 21 ไฟล์

ยังไม่ตรวจ: หน้าจอผ่าน browser จริงในสภาพแวดล้อมนี้ เพราะ browser เปิดเชื่อมเซิร์ฟเวอร์ท้องถิ่นไม่ได้ แม้ HTTP tests ทำงานผ่านแล้ว ต้องให้ Codex ตรวจ UI บนเครื่องที่จะใช้จริง

ยังไม่มี: LLM benchmark ผลจริง, RL, independent domain review, learning study, site pilot, operational digital twin หรือ validated GMP system

## 13. ไฟล์ที่ขอให้ช่วยหา

| รายการ | สถานะ | ลิงก์ |
|---|---|---|
| P02 Waikar etal.,2026 | มี full-text XML แล้ว แต่ดาวน์โหลด publisher/PMC PDF ไม่ได้ | https://doi.org/10.1002/psp4.70201 |
| R07 NIST IR 8356 | technicalreport เสริมเรื่อง digitaltwin; PDF ตอบ 403 | https://csrc.nist.gov/pubs/ir/8356/final |

ถ้าสะดวกโหลด PDF สองรายการแล้วแนบกลับมาได้ โดย P02 มีประโยชน์ก่อน ส่วน R07 ไม่จำเป็นต่อการเริ่มงาน CAPA ข้อจำกัดการดาวน์โหลดไม่ขวางการพัฒนา starter หรือการวางแผนนี้

## 14. คำถามที่ควรตัดสินใจก่อนรอบจริง

1. การใช้จริงครั้งแรกมุ่ง Thai/PIC/S, US FDA หรือ EU?
2. สามารถให้ผู้เชี่ยวชาญ Manufacturing QA/CAPA ทบทวนเคสบางส่วนแบบไม่เห็นชื่อวิธีได้หรือไม่?
3. งบ API/compute สูงสุดต่อ pilot และต่อการทดลองหลักเท่าไร?
4. ลูกค้าแรกที่อยากทดสอบคือผู้เรียน/ผู้สอนหรือทีม QA โรงงาน?
5. ต้องการ license แบบใดสำหรับโค้ดต้นฉบับ?

ตอบภายหลังได้ Codex ยังทำงาน offline และ native runner ต่อได้ตามขอบเขตนี้ เมื่อได้คำตอบให้บันทึกใน DECISIONS.md เพื่อไม่ถามซ้ำ

## 15. ลำดับเอกสารสำหรับอ่านต่อ

เริ่มที่ GOAL.md และ PLAN.md จากนั้น RESEARCH_PROTOCOL.md/EVALUATION_SPEC.md สำหรับแผนวิทยาศาสตร์, PHARMACEUTICAL_CASE_SPEC.md สำหรับ case, DATASET_PLAN.md สำหรับข้อมูล, LITERATURE_REVIEW.md สำหรับ prior art, PRODUCT_SPEC.md/BUSINESS_PRODUCT_MAP.md สำหรับสินค้า และ JOURNAL_STRATEGY.md/MANUSCRIPT_OUTLINE.md สำหรับการตีพิมพ์

เอกสารเทคนิคเป็นภาษาอังกฤษเพื่อใช้ต่อกับ Codex และ manuscript ส่วนคู่มือฉบับนี้อธิบายการตัดสินใจหลักเป็นภาษาไทย
