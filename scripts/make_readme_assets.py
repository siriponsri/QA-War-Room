"""Generate the README logo and diagrams (original artwork, no external fonts or images).

Writes docs/assets/logo.svg and light/dark variants of:
  architecture-{light,dark}.svg  - components, trust boundaries and who talks to whom
  room-flow-{light,dark}.svg     - the state a live room moves through, incl. unfinished endings
The README picks the variant with <picture> + prefers-color-scheme. SVGs use presentation
attributes only (no <style>/<script>) so they render as plain images on GitHub.
Run from the project root:  py -3 scripts/make_readme_assets.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parents[1] / "docs" / "assets"
FONT = "Segoe UI, -apple-system, Helvetica, Arial, sans-serif"
MONO = "SFMono-Regular, Consolas, Menlo, monospace"
THEMES = {
    "light": {"text": "#13241b", "muted": "#4d6357", "line": "#5b6f63", "box": "#f1f6f2", "edge": "#c3d3c9",
              "group": "#fafcfb", "accent": "#0a7a43", "accent_box": "#dcf1e4", "warn": "#8a5a00", "warn_box": "#fff1cf", "warn_edge": "#d7a43a"},
    "dark": {"text": "#e4eee8", "muted": "#a9bcb1", "line": "#93a79b", "box": "#18231d", "edge": "#34463b",
             "group": "#111915", "accent": "#3fc982", "accent_box": "#16352a", "warn": "#f1c467", "warn_box": "#34290f", "warn_edge": "#8a6a22"},
}


class Svg:
    def __init__(self, w, h, label, t):
        self.w, self.h, self.t = w, h, t
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(label)}">',
            f"<title>{escape(label)}</title>",
            "<defs>"
            + "".join(
                f'<marker id="a-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0 0L10 5L0 10z" fill="{color}"/></marker>'
                for name, color in (("line", t["line"]), ("accent", t["accent"]), ("warn", t["warn"]))
            )
            + "</defs>",
        ]

    def text(self, x, y, s, size=12.5, weight=400, fill=None, anchor="start", mono=False):
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{MONO if mono else FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill or self.t["text"]}" text-anchor="{anchor}">{escape(s)}</text>'
        )

    def box(self, x, y, w, h, title, sub="", fill=None, edge=None, title_fill=None, dashed=False, rx=10):
        dash = ' stroke-dasharray="6 5"' if dashed else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill or self.t["box"]}" stroke="{edge or self.t["edge"]}" stroke-width="1.4"{dash}/>')
        cx = x + w / 2
        if sub:
            self.text(cx, y + h / 2 - 3, title, 13.5, 650, title_fill, "middle")
            self.text(cx, y + h / 2 + 15, sub, 11.5, 400, self.t["muted"], "middle")
        else:
            self.text(cx, y + h / 2 + 5, title, 13.5, 650, title_fill, "middle")

    def group(self, x, y, w, h, label, dashed=False, edge=None, fill=None, label_fill=None):
        dash = ' stroke-dasharray="7 6"' if dashed else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill or self.t["group"]}" stroke="{edge or self.t["edge"]}" stroke-width="1.4"{dash}/>')
        self.text(x + 16, y + 24, label, 12, 700, label_fill or self.t["muted"])

    def arrow(self, d, kind="line", dashed=False, both=False):
        color = self.t["accent" if kind == "accent" else "warn" if kind == "warn" else "line"]
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        start = f' marker-start="url(#a-{kind})"' if both else ""
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6"{dash}{start} marker-end="url(#a-{kind})"/>')

    def label(self, x, y, s, kind="muted", anchor="middle", size=11.5):
        fill = {"muted": self.t["muted"], "accent": self.t["accent"], "warn": self.t["warn"]}[kind]
        self.text(x, y, s, size, 600 if kind != "muted" else 500, fill, anchor)

    def render(self):
        return "\n".join(self.parts + ["</svg>"]) + "\n"


def architecture(t):
    s = Svg(980, 560, "QA War Room architecture: browser pages talk only to a localhost server; records are released only on request; gold and the evaluator sit behind a boundary reached only after completion; live rooms make no model calls; API keys stay in a local git-ignored file.", t)
    # Browser
    s.group(20, 40, 214, 316, "BROWSER · THIS COMPUTER")
    pages = [("Live chat  /", "LINE-style room"), ("Dashboard", "real room counts"), ("Manual desk", "review by hand"), ("AI settings", "provider · key · model")]
    for i, (title, sub) in enumerate(pages):
        s.box(36, 76 + i * 66, 182, 52, title, sub)
    # Server
    s.group(300, 40, 340, 420, "LOCAL SERVER · 127.0.0.1 ONLY")
    s.box(350, 76, 270, 58, "HTTP API", "strict JSON · host / origin checks")
    s.box(350, 190, 270, 58, "LiveRooms scheduler", "rule-based roles · 0 model calls", fill=t["accent_box"], edge=t["accent"])
    s.box(350, 300, 270, 58, "SessionEngine", "evidence budget · requests · decision")
    s.box(350, 392, 270, 52, "ProviderSettings", "key saved locally · never returned")
    # Right side
    s.box(706, 300, 254, 58, "Evidence register", "a record is released only when requested")
    s.group(690, 150, 286, 110, "EVALUATOR-ONLY BOUNDARY", dashed=True, edge=t["warn_edge"], fill=t["warn_box"], label_fill=t["warn"])
    s.box(706, 184, 254, 58, "Gold + evaluator", "never in active observations")
    s.box(706, 392, 254, 52, ".qawr/provider-settings.json", "git-ignored · masked in the UI")
    s.box(706, 478, 254, 52, "Provider endpoints", "Typhoon · OpenRouter · Claude · GPT · Gemini")
    # Browser -> server
    s.arrow("M218 102 L350 96", both=True); s.label(284, 91, "polls · controls")
    s.arrow("M218 168 L350 112"); s.label(270, 147, "reads counts")
    s.arrow("M218 234 L350 126"); s.label(272, 200, "manual session")
    s.arrow("M218 300 C 290 300, 290 418, 350 418"); s.label(264, 372, "/api/settings")
    # Inside server
    s.arrow("M485 134 L485 190"); s.label(476, 166, "pause · resume · stop · note", anchor="end")
    s.arrow("M485 248 L485 300"); s.label(476, 278, "request · review · decide", anchor="end")
    # Engine -> evidence / evaluator
    s.arrow("M620 329 L706 329"); s.label(663, 320, "release")
    s.arrow("M620 312 C 660 312, 666 226, 706 222", kind="warn"); s.label(640, 276, "completed only", kind="warn", anchor="start")
    s.arrow("M706 200 C 660 196, 660 118, 620 112", kind="warn", dashed=True); s.label(668, 138, "debrief", kind="warn", anchor="start")
    # Settings -> file / providers
    s.arrow("M620 412 L706 412"); s.label(663, 404, "writes key")
    s.arrow("M620 430 C 660 430, 666 504, 706 504", dashed=True); s.label(650, 482, "Test only", anchor="end")
    s.label(833, 548, "free model-list / key check · no prompts sent")
    return s.render()


def room_flow(t):
    s = Svg(980, 330, "Live room flow: the investigator requests a record, an owner delivers it, the checker reviews; more evidence loops back; a proposal gets a final review that can challenge for a specific record; completion unlocks the authored debrief; time limit, stop or round limit at any point saves unfinished work with no verdict and no reference answer.", t)
    steps = [("Phum requests", "one record"), ("Chai / Fon deliver", "the requested record"), ("Mind checks", "received facts only"),
             ("Phum proposes", "a conclusion"), ("Mind final review", "accept or challenge"), ("Completed", "debrief unlocked")]
    xs = [20, 182, 344, 506, 668, 830]
    for i, ((title, sub), x) in enumerate(zip(steps, xs)):
        last = i == len(steps) - 1
        s.box(x, 70, 130, 58, title, sub, fill=t["accent_box"] if last else None, edge=t["accent"] if last else None, title_fill=t["accent"] if last else None)
    for i in range(5):
        x1, x2 = xs[i] + 130, xs[i + 1]
        kind = "accent" if i == 4 else "line"
        s.arrow(f"M{x1} 99 L{x2} 99", kind=kind)
    # Loop: more evidence
    s.arrow("M409 128 L409 158 L85 158 L85 128")
    s.label(247, 175, "not enough yet → request the next record")
    # Challenge back to custodian
    s.arrow("M733 70 L733 40 L247 40 L247 70", kind="warn")
    s.label(490, 32, "challenge → a specific record is requested", kind="warn")
    # Interruptions
    s.parts.append(f'<path d="M85 210 L895 210" stroke="{t["warn_edge"]}" stroke-width="1.4" stroke-dasharray="5 4" fill="none"/>')
    for x in (85, 247, 409, 571, 733):
        s.parts.append(f'<path d="M{x} {158 if x in (85, 409) else 128} L{x} 210" stroke="{t["warn_edge"]}" stroke-width="1.2" stroke-dasharray="3 4" fill="none"/>')
    s.arrow("M490 210 L490 244", kind="warn")
    s.label(498, 232, "any time", kind="warn", anchor="start")
    s.box(250, 244, 480, 62, "Time limit · Stop · Round limit", "saved as unfinished: no forced verdict, no reference answer", fill=t["warn_box"], edge=t["warn_edge"], title_fill=t["warn"])
    return s.render()


LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120" role="img" aria-label="QA War Room logo: a speech bubble holding a checked evidence mark">
<title>QA War Room</title>
<rect width="120" height="120" rx="30" fill="#0a7a43"/>
<path d="M30 34a12 12 0 0 1 12-12h36a12 12 0 0 1 12 12v26a12 12 0 0 1-12 12H52l-14 12v-12h-2a6 6 0 0 1-6-6z" fill="#ffffff"/>
<path d="M45 47l9 9 17-18" fill="none" stroke="#0a7a43" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="82" cy="82" r="13" fill="#0a7a43" stroke="#c5e8d2" stroke-width="6"/>
<path d="M91.5 91.5l9 9" stroke="#c5e8d2" stroke-width="7" stroke-linecap="round"/>
</svg>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "logo.svg").write_text(LOGO, encoding="utf-8")
    for name, theme in THEMES.items():
        (OUT / f"architecture-{name}.svg").write_text(architecture(theme), encoding="utf-8")
        (OUT / f"room-flow-{name}.svg").write_text(room_flow(theme), encoding="utf-8")
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
