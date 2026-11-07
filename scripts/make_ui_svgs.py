"""Generate the original character and document SVG assets for the live UI.

Writes qa_war_room/static/characters/*.svg and qa_war_room/static/docs/*.svg.
All artwork is original and illustrative: the characters depict the simulated, rule-based
roles in the demo, not real people, real experts or an AI model.

The server sends `style-src 'self'` on every response, so the SVGs use presentation
attributes only (no <style> or style=""). Blink/talk animation is applied from live.css
through the class names ch-eyes, ch-mouth and ch-mouth-open when the SVG is inlined.
Run from the project root:  py -3 scripts/make_ui_svgs.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "qa_war_room" / "static"


def face(skin, ink="#2a1d18", blush="#f19a8c", extra=""):
    """Ears, head, eyes, cheeks, per-character features and both mouth states centred at (48, 40)."""
    return f'''
  <ellipse cx="31.5" cy="42" rx="3.4" ry="4.4" fill="{skin}"/>
  <ellipse cx="64.5" cy="42" rx="3.4" ry="4.4" fill="{skin}"/>
  <ellipse cx="48" cy="40" rx="16.5" ry="18.5" fill="{skin}"/>
  <g class="ch-eyes">
    <ellipse cx="41.5" cy="41.5" rx="2.1" ry="2.5" fill="{ink}"/>
    <ellipse cx="54.5" cy="41.5" rx="2.1" ry="2.5" fill="{ink}"/>
    <circle cx="42.2" cy="40.6" r=".7" fill="#fff"/>
    <circle cx="55.2" cy="40.6" r=".7" fill="#fff"/>
  </g>
  <circle cx="37.5" cy="47.5" r="2.6" fill="{blush}" opacity=".45"/>
  <circle cx="58.5" cy="47.5" r="2.6" fill="{blush}" opacity=".45"/>{extra}
  <path class="ch-mouth" d="M44 49.5q4 3.2 8 0" fill="none" stroke="{ink}" stroke-width="1.9" stroke-linecap="round"/>
  <g class="ch-mouth-open" opacity="0">
    <ellipse cx="48" cy="50.6" rx="3.6" ry="2.9" fill="#7a2c22"/>
    <ellipse cx="48" cy="52" rx="2.2" ry="1.1" fill="#e77b6e"/>
  </g>'''


def svg(label, background, body):
    key = "".join(ch for ch in label.split(" ")[0].lower() if ch.isalnum())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" role="img" aria-label="{label}">
  <title>{label}</title>
  <defs><clipPath id="qawr-ch-{key}"><circle cx="48" cy="48" r="48"/></clipPath></defs>
  <g clip-path="url(#qawr-ch-{key})">
  <rect width="96" height="96" fill="{background}"/>{body}
  </g>
</svg>
'''


CHARACTERS = {
    # Investigator: green blazer, round glasses, magnifier pin.
    "investigator": svg("Phum, investigator (fictional character)", "#d6f0df", f'''
  <path d="M12 96c1.5-17 15.5-28 36-28s34.5 11 36 28z" fill="#0a7a43"/>
  <path d="M39 67.5l9 12.5 9-12.5-4-1.5-5 7-5-7z" fill="#ffffff"/>
  <path d="M39 67.5L48 80 37 96H26l2-20z" fill="#086637"/>
  <path d="M57 67.5L48 80l11 16h11l-2-20z" fill="#086637"/>
  <rect x="43.5" y="54" width="9" height="13" rx="4" fill="#e3a97f"/>
  {face("#f2c7a2", extra='<path d="M37 34.6q4.2-1.6 8.6-.2M50.4 34.4q4.4-1.4 8.6.2" fill="none" stroke="#24242c" stroke-width="2" stroke-linecap="round"/>')}
  <path d="M31 39c-1.5-13.5 7-22.5 18-22.5 10.5 0 18.5 8 17 21-3-5.5-8.5-8.5-15.5-8.5-8.5 0-15.5 3.5-19.5 10z" fill="#24242c"/>
  <circle cx="41.5" cy="41.5" r="5.6" fill="none" stroke="#173b2b" stroke-width="1.8"/>
  <circle cx="54.5" cy="41.5" r="5.6" fill="none" stroke="#173b2b" stroke-width="1.8"/>
  <path d="M47.1 41.2h1.8" stroke="#173b2b" stroke-width="1.8"/>
  <circle cx="66" cy="82" r="6" fill="#ffffff"/>
  <circle cx="65.2" cy="81.2" r="2.6" fill="none" stroke="#0a7a43" stroke-width="1.6"/>
  <path d="M67.2 83.2l2.2 2.2" stroke="#0a7a43" stroke-width="1.8" stroke-linecap="round"/>'''),

    # Evidence checker: purple cardigan, hair bun, checklist pin.
    "checker": svg("Mind, evidence checker (fictional character)", "#e9e3fb", f'''
  <path d="M12 96c1.5-17 15.5-28 36-28s34.5 11 36 28z" fill="#6b4fbb"/>
  <path d="M40 67.5c2 5 5 8 8 8s6-3 8-8l-3-1c-1.5 3-3 4.5-5 4.5s-3.5-1.5-5-4.5z" fill="#f6f3ff"/>
  <path d="M48 75.5V96" stroke="#563d9e" stroke-width="2"/>
  <circle cx="48" cy="82" r="1.3" fill="#f6f3ff"/><circle cx="48" cy="89" r="1.3" fill="#f6f3ff"/>
  <rect x="43.5" y="54" width="9" height="13" rx="4" fill="#d79e78"/>
  <circle cx="48" cy="18.5" r="7.5" fill="#4a2c22"/>
  {face("#e8b48e", extra='<path d="M37.6 36q3.8-3.4 7.8-1M50.6 35q4-2.4 7.8 1" fill="none" stroke="#4a2c22" stroke-width="1.6" stroke-linecap="round"/><circle cx="57.6" cy="50.4" r=".8" fill="#4a2c22"/>')}
  <path d="M31 41c0-13.5 7.5-21.5 17-21.5S65 27.5 65 41c-3.5-6.5-9.5-10.5-17-10.5S34.5 34.5 31 41z" fill="#4a2c22"/>
  <circle cx="31.5" cy="47.5" r="1.4" fill="#f3c44e"/>
  <rect x="60" y="76" width="12" height="14" rx="2.5" fill="#ffffff"/>
  <rect x="63" y="74.5" width="6" height="3" rx="1.2" fill="#b29cf2"/>
  <path d="M62.8 83.5l2.2 2.2 4.2-4.4" fill="none" stroke="#6b4fbb" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'''),

    # Manufacturing records: navy coverall, hi-vis stripe, cleanroom cap.
    "manufacturing": svg("Chai, manufacturing records (fictional character)", "#fde7cf", f'''
  <path d="M12 96c1.5-17 15.5-28 36-28s34.5 11 36 28z" fill="#2c4f78"/>
  <path d="M15.5 86h65l1.3 4.5H14.2z" fill="#f08a24"/>
  <path d="M15.5 86h65l.4 1.5H15.1z" fill="#ffd18f"/>
  <path d="M41 68l7 6 7-6" fill="none" stroke="#1d3a5c" stroke-width="2.2" stroke-linejoin="round"/>
  <rect x="58" y="73" width="10" height="7" rx="1.5" fill="#ffffff"/>
  <path d="M60 76.5h6" stroke="#2c4f78" stroke-width="1.4"/>
  <rect x="43.5" y="54" width="9" height="13" rx="4" fill="#c98d64"/>
  {face("#dca27a", ink="#2b1d16", extra='<path d="M36.8 35.4l8.4-.6M50.8 34.8l8.4.6" stroke="#8b9198" stroke-width="2.8" stroke-linecap="round"/><path d="M41 47.6c2.2-2.4 4.9-2.4 7-.7 2.1-1.7 4.8-1.7 7 .7-2.3 1-4.6 1-7-.1-2.4 1.1-4.7 1.1-7 .1z" fill="#8b9198"/><path d="M36.6 44.2q-1 2.4 0 4.6M59.4 44.2q1 2.4 0 4.6" fill="none" stroke="#b97f58" stroke-width="1.1" stroke-linecap="round"/><path d="M31.6 38.6v6.4M64.4 38.6v6.4" stroke="#aab0b6" stroke-width="2.6" stroke-linecap="round"/>')}
  <path d="M29.5 39.5C29.5 25 38 16.5 48 16.5S66.5 25 66.5 39.5c-2.5-2.6-5-3.5-7.5-3.5H37c-2.5 0-5 .9-7.5 3.5z" fill="#f4f8fb"/>
  <path d="M30.5 35.5c6-2.2 11.5-3 17.5-3s11.5.8 17.5 3" fill="none" stroke="#c7d3de" stroke-width="1.5"/>
  <circle cx="40" cy="25" r=".9" fill="#c7d3de"/><circle cx="48" cy="22.5" r=".9" fill="#c7d3de"/><circle cx="56" cy="25" r=".9" fill="#c7d3de"/>
  <circle cx="44" cy="29" r=".9" fill="#c7d3de"/><circle cx="52" cy="29" r=".9" fill="#c7d3de"/>'''),

    # Quality records: white lab coat, blue shirt, shield badge, long hair.
    "quality": svg("Fon, quality records (fictional character)", "#d9ebf8", f'''
  <path d="M29.5 44c-2.5-17 6-27.5 18.5-27.5S69 27 66.5 44l1.5 20H28z" fill="#5e3522"/>
  <path d="M12 96c1.5-17 15.5-28 36-28s34.5 11 36 28z" fill="#ffffff"/>
  <path d="M12 96c1.5-17 15.5-28 36-28s34.5 11 36 28" fill="none" stroke="#c8d8e4" stroke-width="1.4"/>
  <path d="M40.5 67.5L48 81l7.5-13.5z" fill="#1d6fa5"/>
  <path d="M40.5 67.5L48 81 41 96h-8l1-22zM55.5 67.5L48 81l7 15h8l-1-22z" fill="#eef4f9"/>
  <rect x="43.5" y="54" width="9" height="13" rx="4" fill="#e1a983"/>
  {face("#f1c4a0", extra='<path d="M37.8 35.6q3.8-1.8 7.6-.6M50.6 35q3.8-1.2 7.6.6" fill="none" stroke="#5e3522" stroke-width="1.5" stroke-linecap="round"/>')}
  <path d="M31.5 40c0-13 7-20.5 16.5-20.5 9.8 0 17 7.5 17 20.5-6.5-1.5-12-5-15-10-3 5.5-9.5 9-18.5 10z" fill="#5e3522"/>
  <rect x="55.5" y="26" width="8" height="3.4" rx="1.7" transform="rotate(-24 59.5 27.7)" fill="#f3c44e"/>
  <path d="M62 75.5l6 2.2v4.6c0 3.4-2.6 5.8-6 7-3.4-1.2-6-3.6-6-7v-4.6z" fill="#1d6fa5"/>
  <path d="M59.4 82.4l1.8 1.8 3.4-3.6" fill="none" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'''),

    # The person using the app: neutral silhouette, no face (not a simulated agent).
    "you": svg("You", "#cdebd8", '''
  <path d="M14 96c1.5-17 15.5-27 34-27s32.5 10 34 27z" fill="#0a7a43"/>
  <circle cx="48" cy="42" r="17" fill="#0a7a43"/>
  <circle cx="48" cy="42" r="17" fill="#ffffff" opacity=".14"/>'''),
}

# Document tiles: tinted rounded square, paper sheet, type glyph. 40x40.
PAPER = '<path d="M11 6.5h13l6 6V33a1.5 1.5 0 0 1-1.5 1.5h-17A1.5 1.5 0 0 1 10 33V8a1.5 1.5 0 0 1 1-1.5z" fill="#ffffff"/><path d="M24 6.5V12a.5.5 0 0 0 .5.5H30" fill="{fold}"/>'
DOCS = {
    "closure_summary": ("Closure cover sheet", "#d6f0df", "#9fdab7", "#0a7a43",
        '<path d="M14 15h9M14 19h12" stroke="{c}" stroke-width="1.6" stroke-linecap="round" opacity=".55"/>'
        '<circle cx="20" cy="27" r="4.6" fill="none" stroke="{c}" stroke-width="1.6"/><path d="M18 27l1.5 1.5 3-3" fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'),
    "closure_protocol": ("Closure criteria", "#d4f1ee", "#97dcd3", "#0b7d70",
        '<path d="M14 16l1.4 1.4 2.4-2.6M14 22l1.4 1.4 2.4-2.6M14 28l1.4 1.4 2.4-2.6" fill="none" stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M20 16.2h7M20 22.2h7M20 28.2h5" stroke="{c}" stroke-width="1.6" stroke-linecap="round" opacity=".6"/>'),
    "implementation_record": ("Implementation record", "#fde7cf", "#f6c690", "#b8620d",
        '<circle cx="20" cy="23" r="3" fill="none" stroke="{c}" stroke-width="1.6"/>'
        '<path d="M20 15.5v2.3M20 28.2v2.3M12.5 23h2.3M25.2 23h2.3M14.7 17.7l1.6 1.6M23.7 26.7l1.6 1.6M14.7 28.3l1.6-1.6M23.7 19.3l1.6-1.6" stroke="{c}" stroke-width="1.6" stroke-linecap="round"/>'),
    "effectiveness_report": ("Effectiveness report", "#d9ebf8", "#a5cdec", "#1d6fa5",
        '<path d="M14 29.5h13" stroke="{c}" stroke-width="1.5" stroke-linecap="round" opacity=".5"/>'
        '<rect x="14.5" y="22" width="3" height="6" rx="1" fill="{c}"/><rect x="19.5" y="18" width="3" height="10" rx="1" fill="{c}"/><rect x="24.5" y="14.5" width="3" height="13.5" rx="1" fill="{c}"/>'),
    "deviation_trend": ("Related deviations", "#fde3df", "#f4b2a8", "#b8321f",
        '<path d="M13.5 26l4-4.5 3.5 3 5.5-7" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M23.5 17.5h3v3" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M14 30.5h12" stroke="{c}" stroke-width="1.5" stroke-linecap="round" opacity=".5"/>'),
    "status_log": ("Current status register", "#ebe5fb", "#c6b6f1", "#6b4fbb",
        '<circle cx="15" cy="16.5" r="1.6" fill="{c}"/><circle cx="15" cy="22.5" r="1.6" fill="{c}" opacity=".7"/><circle cx="15" cy="28.5" r="1.6" fill="none" stroke="{c}" stroke-width="1.3"/>'
        '<path d="M19 16.5h8M19 22.5h8M19 28.5h6" stroke="{c}" stroke-width="1.6" stroke-linecap="round" opacity=".6"/>'),
    "training_record": ("Training record", "#e1e6fb", "#b3bff1", "#3f51b5",
        '<path d="M12.5 20.5l7.5-3.5 7.5 3.5-7.5 3.5z" fill="{c}"/><path d="M15.5 22.2v3.6c1.4 1.6 2.9 2.2 4.5 2.2s3.1-.6 4.5-2.2v-3.6" fill="none" stroke="{c}" stroke-width="1.6" stroke-linejoin="round"/>'
        '<path d="M27.5 20.5v5" stroke="{c}" stroke-width="1.4" stroke-linecap="round"/>'),
    "shift_log": ("Shift log", "#e4ebe7", "#bccbc3", "#4c6458",
        '<circle cx="20" cy="22.5" r="6.5" fill="none" stroke="{c}" stroke-width="1.6"/><path d="M20 19v3.7l2.6 1.6" fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'),
    "generic": ("Record", "#e4ebe7", "#bccbc3", "#4c6458",
        '<path d="M14 16h12M14 20.5h12M14 25h8" stroke="{c}" stroke-width="1.6" stroke-linecap="round" opacity=".6"/>'),
}


def doc_svg(label, tile, fold, colour, glyph):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" role="img" aria-label="{label}">
  <title>{label}</title>
  <rect width="40" height="40" rx="11" fill="{tile}"/>
  {PAPER.format(fold=fold)}
  {glyph.format(c=colour)}
</svg>
'''


def main():
    (ROOT / "characters").mkdir(exist_ok=True)
    (ROOT / "docs").mkdir(exist_ok=True)
    for name, text in CHARACTERS.items():
        (ROOT / "characters" / f"{name}.svg").write_text(text, encoding="utf-8")
    for name, spec in DOCS.items():
        (ROOT / "docs" / f"{name}.svg").write_text(doc_svg(*spec), encoding="utf-8")
    print(f"wrote {len(CHARACTERS)} characters and {len(DOCS)} document icons under {ROOT}")


if __name__ == "__main__":
    main()
