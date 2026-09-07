"""Render docs/paper/PAPER.md to a single self-contained HTML page (figures inlined).

Usage:
    python backend/scripts/build_paper_html.py [--out /path/to/paper.html]

Needs the `markdown` package (`pip install markdown`); it is a documentation tool,
not a runtime dependency, so it is not in pyproject.
"""

from __future__ import annotations

import argparse
import base64
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "docs" / "paper"

CSS = """
:root {
  color-scheme: light;
  --plane: #f5f4f0; --surface: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --rule: #e1e0d9; --accent: #c98500; --accent-ink: #7a5000; --naive: #2a78d6; --mono-bg: #f0efe9;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --plane: #111110; --surface: #1a1a19; --ink: #f4f3ee; --ink-2: #c3c2b7; --muted: #898781;
    --rule: #2c2c2a; --accent: #eda100; --accent-ink: #f0b73a; --naive: #3987e5; --mono-bg: #232321;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --plane: #111110; --surface: #1a1a19; --ink: #f4f3ee; --ink-2: #c3c2b7; --muted: #898781;
  --rule: #2c2c2a; --accent: #eda100; --accent-ink: #f0b73a; --naive: #3987e5; --mono-bg: #232321;
}
html { background: var(--plane); }
body { margin: 0; background: var(--plane); color: var(--ink);
  font-family: "Source Serif 4", Georgia, "Times New Roman", serif; font-size: 17px; line-height: 1.55; }
.page { max-width: 1120px; margin: 0 auto; padding: 0 24px 96px; }
.masthead { padding: 56px 0 28px; border-bottom: 1px solid var(--rule); }
.eyebrow { font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace; font-size: 12px; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted); margin: 0 0 18px; }
h1 { font-family: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif; font-weight: 600;
  font-size: clamp(30px, 4.2vw, 44px); line-height: 1.12; letter-spacing: -.015em; margin: 0 0 18px; max-width: 22ch; text-wrap: balance; }
.byline { color: var(--ink-2); font-size: 15px; margin: 0; }
.byline a { color: var(--accent-ink); text-decoration: none; border-bottom: 1px solid var(--rule); }
.cueline { margin: 26px 0 0; font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace; font-size: 12.5px;
  color: var(--ink-2); background: var(--mono-bg); border-left: 3px solid var(--accent); padding: 10px 14px;
  white-space: pre-wrap; max-width: 78ch; }
.cueline b { color: var(--ink); font-weight: 600; }
article { max-width: 66ch; }
article h2 { font-family: "IBM Plex Sans", system-ui, sans-serif; font-weight: 600; font-size: 24px; line-height: 1.2;
  letter-spacing: -.01em; margin: 56px 0 14px; text-wrap: balance; }
article h2 + p, article h2 + table { margin-top: 0; }
article p { margin: 0 0 1em; }
article ul, article ol { padding-left: 1.3em; }
article li { margin: 0 0 .45em; }
article strong { font-weight: 650; }
article em { font-style: italic; }
article a { color: var(--accent-ink); text-decoration: none; border-bottom: 1px solid var(--rule); }
article hr { border: 0; border-top: 1px solid var(--rule); margin: 40px 0 0; }
article blockquote { margin: 0 0 1.4em; padding: 12px 18px; border-left: 3px solid var(--accent);
  background: var(--surface); color: var(--ink-2); font-size: 15.5px; }
article blockquote p { margin: 0; }
article code { font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace; font-size: .86em; background: var(--mono-bg);
  padding: .1em .35em; border-radius: 3px; }
article pre { font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace; font-size: 13px; line-height: 1.5;
  background: var(--mono-bg); padding: 14px 16px; overflow-x: auto; border-radius: 4px; }
article pre code { background: none; padding: 0; font-size: inherit; }
.abstract { font-size: 18.5px; line-height: 1.5; }
.abstract p:first-child::first-letter { font-family: "IBM Plex Sans", system-ui, sans-serif; font-weight: 600; }
/* figures and wide tables break out of the prose column */
.figure { margin: 26px 0 30px; width: min(100%, 1072px); }
.figure img { display: block; width: 100%; height: auto; background: #fcfcfb; border: 1px solid var(--rule); }
.figure figcaption { font-family: "IBM Plex Sans", system-ui, sans-serif; font-size: 13.5px; line-height: 1.45;
  color: var(--ink-2); margin: 10px 0 0; max-width: 78ch; }
.figure figcaption .fn { font-weight: 600; color: var(--ink); }
.tablewrap { overflow-x: auto; margin: 14px 0 26px; width: min(100%, 1072px); }
table { border-collapse: collapse; font-family: "IBM Plex Sans", system-ui, sans-serif; font-size: 13.5px; line-height: 1.35;
  font-variant-numeric: tabular-nums; min-width: 100%; }
th, td { text-align: left; padding: 7px 12px 7px 0; border-bottom: 1px solid var(--rule); vertical-align: top; }
th { font-weight: 600; color: var(--ink-2); font-size: 12.5px; letter-spacing: .02em; }
td:not(:first-child), th:not(:first-child) { text-align: right; white-space: nowrap; }
td:first-child { white-space: nowrap; }
tr:last-child td { border-bottom: 1px solid var(--ink-2); }
table strong { color: var(--accent-ink); }
.arms { display: flex; gap: 18px; flex-wrap: wrap; margin: 18px 0 0; font-family: "IBM Plex Sans", system-ui, sans-serif; font-size: 13px; color: var(--ink-2); }
.arms span::before { content: ""; display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 7px; vertical-align: -1px; }
.arms .a1::before { background: #2a78d6; } .arms .a2::before { background: #eb6834; }
.arms .a3::before { background: #1baf7a; } .arms .a4::before { background: #eda100; }
footer { margin-top: 64px; padding-top: 18px; border-top: 1px solid var(--rule); color: var(--muted);
  font-family: "IBM Plex Sans", system-ui, sans-serif; font-size: 13px; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
@media (max-width: 720px) { body { font-size: 16px; } .masthead { padding-top: 36px; } article h2 { margin-top: 44px; } }
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&'
    'family=IBM+Plex+Mono:wght@400;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap">'
)


def data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def render(md_text: str) -> str:
    # Pull the title, byline and scope note out of the markdown; the template sets them.
    lines = md_text.splitlines()
    title = lines[0].lstrip("# ").strip()
    byline = next(ln for ln in lines if ln.startswith("**Aaron Lu**"))
    body_md = "\n".join(ln for ln in lines[1:] if ln != byline)
    html = markdown.markdown(body_md, extensions=["tables", "fenced_code", "sane_lists"])

    # Inline figures and turn "![Figure N](path)" + following italic caption into <figure>.
    def fig(m):
        src = PAPER / m.group(2)
        cap = re.sub(r"^<em>(.*)</em>$", r"\1", m.group(3).strip())
        cap = re.sub(r"^(Figure \d+\.)", r'<span class="fn">\1</span>', cap)
        return f'<figure class="figure"><img src="{data_uri(src)}" alt="{m.group(1)}"><figcaption>{cap}</figcaption></figure>'

    html = re.sub(
        r'<p><img alt="([^"]*)" src="([^"]+)" /></p>\s*<p>(<em>.*?</em>)</p>', fig, html, flags=re.S
    )
    html = html.replace("<table>", '<div class="tablewrap"><table>').replace(
        "</table>", "</table></div>"
    )
    # Abstract: the first h2 is "Abstract"; give its paragraph the larger setting.
    html = re.sub(r"(<h2>Abstract</h2>\s*)<p>", r'\1<div class="abstract"><p>', html, count=1)
    html = html.replace("<hr />", "</div><hr />", 1) if '<div class="abstract">' in html else html
    byline_html = markdown.markdown(byline).replace("<p>", "").replace("</p>", "")
    return f"""<title>Engineered Context for Low-Vision Guidance</title>
{FONTS}
<style>{CSS}</style>
<div class="page">
<header class="masthead">
  <p class="eyebrow">Research summary · egocentric video benchmark · September 2026</p>
  <h1>{title}</h1>
  <p class="byline">{byline_html}</p>
  <div class="cueline"><b>What the model hears each second</b>
Free space: left=partly blocked, centre=partly blocked, right=blocked.
Obstacles: person (right, near); motorcycle (centre, mid); person (centre, far).
→  <b>"STOP. There's a motorcycle in the way."</b>   (context-v2, no echo, 4.8 s, 13 tokens)</div>
  <div class="arms"><span class="a1">naive</span><span class="a2">context-v1</span><span class="a3">context-v1, no echo</span><span class="a4">context-v2, no echo</span></div>
</header>
<article>
{html}
</article>
<footer>Built from <code>docs/paper/PAPER.md</code> and <code>docs/paper/figures/</code> by <code>backend/scripts/build_paper_html.py</code>. Footage: YouTube V8_Iaqmj3nk and omcY89kce2A, Creative Commons Attribution.</footer>
</div>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=PAPER / "paper.html")
    args = ap.parse_args()
    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render((PAPER / "PAPER.md").read_text()))
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
