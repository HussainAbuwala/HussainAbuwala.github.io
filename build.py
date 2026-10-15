#!/usr/bin/env python3
"""Build the home page and the synonym table from content.json.

    python3 build.py

Writes index.html and assets/synonyms.js. Article pages are written by hand.
Standard library only.
"""
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def month(ym):
    """'2025-10' -> 'Oct 2025'; None -> 'present'."""
    if not ym:
        return "present"
    y, m = ym.split("-")
    return f"{MONTHS[int(m) - 1]} {y}"


def margin_note(note_id, body, cls=""):
    """A margin note for asides. 'fig' notes stay visible on phones."""
    return (f'<label for="mn-{note_id}" class="margin-toggle fig-toggle">&#8853;</label>'
            f'<input type="checkbox" id="mn-{note_id}" class="margin-toggle"/>'
            f'<span class="marginnote {cls}">{body}</span>')


# Figures and inline extras that only the website shows (the résumé ignores them).
MARGIN_FIGS = {
    "everything-has-a-price": '<img src="/assets/poster.jpg" alt="Everything Has a Price: a drawn figure tied to a price tag labelled TIME">',
}
INLINE_EXTRA = {}

# Icons from IBM Carbon (Apache-2.0), drawn in the text colour.
def _icon(paths):
    return f'<svg viewBox="0 0 32 32" width="24" height="24" fill="currentColor" aria-hidden="true">{paths}</svg>'

ICONS = {
    "email": _icon('<path d="M28,6H4A2,2,0,0,0,2,8V24a2,2,0,0,0,2,2H28a2,2,0,0,0,2-2V8A2,2,0,0,0,28,6ZM25.8,8,16,14.78,6.2,8ZM4,24V8.91l11.43,7.91a1,1,0,0,0,1.14,0L28,8.91V24Z"/>'),
    "github": _icon('<path fill-rule="evenodd" d="M16,2a14,14,0,0,0-4.43,27.28c.7.13,1-.3,1-.67s0-1.21,0-2.38c-3.89.84-4.71-1.88-4.71-1.88A3.71,3.71,0,0,0,6.24,22.3c-1.27-.86.1-.85.1-.85A2.94,2.94,0,0,1,8.48,22.9a3,3,0,0,0,4.08,1.16,2.93,2.93,0,0,1,.88-1.87c-3.1-.36-6.37-1.56-6.37-6.92a5.4,5.4,0,0,1,1.44-3.76,5,5,0,0,1,.14-3.7s1.17-.38,3.85,1.43a13.3,13.3,0,0,1,7,0c2.67-1.81,3.84-1.43,3.84-1.43a5,5,0,0,1,.14,3.7,5.4,5.4,0,0,1,1.44,3.76c0,5.38-3.27,6.56-6.39,6.91a3.33,3.33,0,0,1,.95,2.59c0,1.87,0,3.38,0,3.84s.25.81,1,.67A14,14,0,0,0,16,2Z"/>'),
    "youtube": _icon('<path d="M29.41,9.26a3.5,3.5,0,0,0-2.47-2.47C24.76,6.2,16,6.2,16,6.2s-8.76,0-10.94.59A3.5,3.5,0,0,0,2.59,9.26,36.13,36.13,0,0,0,2,16a36.13,36.13,0,0,0,.59,6.74,3.5,3.5,0,0,0,2.47,2.47C7.24,25.8,16,25.8,16,25.8s8.76,0,10.94-.59a3.5,3.5,0,0,0,2.47-2.47A36.13,36.13,0,0,0,30,16,36.13,36.13,0,0,0,29.41,9.26ZM13.2,20.2V11.8L20.47,16Z"/>'),
    "linkedin": _icon('<path d="M26.2,4H5.8C4.8,4,4,4.8,4,5.7v20.5c0,0.9,0.8,1.7,1.8,1.7h20.4c1,0,1.8-0.8,1.8-1.7V5.7C28,4.8,27.2,4,26.2,4z M11.1,24.4H7.6V13h3.5V24.4z M9.4,11.4c-1.1,0-2.1-0.9-2.1-2.1c0-1.2,0.9-2.1,2.1-2.1c1.1,0,2.1,0.9,2.1,2.1S10.5,11.4,9.4,11.4z M24.5,24.3H21v-5.6c0-1.3,0-3.1-1.9-3.1c-1.9,0-2.1,1.5-2.1,2.9v5.7h-3.5V13h3.3v1.5h0.1c0.5-0.9,1.7-1.9,3.4-1.9c3.6,0,4.3,2.4,4.3,5.5V24.3z"/>'),
    "resume": _icon('<path d="M25.7,9.3l-7-7C18.5,2.1,18.3,2,18,2H8C6.9,2,6,2.9,6,4v24c0,1.1,0.9,2,2,2h16c1.1,0,2-0.9,2-2V10C26,9.7,25.9,9.5,25.7,9.3z M18,4.4l5.6,5.6H18V4.4z M24,28H8V4h8v6c0,1.1,0.9,2,2,2h6V28z"/><path d="M10 22H22V24H10z"/><path d="M10 16H22V18H10z"/>'),
}


def item_html(it, title_html, meta="", tailorable=True, href=None):
    """One entry: title line, description, then the tools used, each on its own line."""
    attrs = (f'id="{it["id"]}" data-item data-title="{escape(it["title"])}" '
             f'data-summary="{escape(it["summary"])}"')
    if href:
        attrs += f' data-href="{href}"'
    if not tailorable:
        attrs += ' data-tailorable="false"'
    fig = margin_note(it["id"] + "-fig", MARGIN_FIGS[it["id"]], "fig") if it["id"] in MARGIN_FIGS else ""
    meta = f'<span class="when">{meta}</span>' if meta else ""
    tools = f'<p class="tools">{" · ".join(escape(t) for t in it["stack"])}</p>' if it.get("stack") else ""
    return (f'<div class="item" {attrs}><p class="ititle">{title_html}{meta}{fig}</p>'
            f'<p>{summary_html(it)}{INLINE_EXTRA.get(it["id"], "")}</p>{tools}</div>')


def mark_key(text, key):
    """Escape text and highlight the key phrase if it is this text."""
    text = escape(text)
    return f'<mark class="hl">{text}</mark>' if key and escape(key) == text else text


def summary_html(it):
    """The summary, with the item's headline result (its "key" phrase) highlighted."""
    text = escape(it["summary"])
    key = it.get("key")
    if key:
        k = escape(key)
        assert k in text, f'key phrase not in summary of {it["id"]}: {key}'
        text = text.replace(k, f'<mark class="hl">{k}</mark>', 1)
    return text


def build():
    c = json.loads((ROOT / "content.json").read_text())
    p = c["person"]
    L = p["links"]

    contact = " ".join([
        f'<a class="addr" href="mailto:{p["email"]}">{ICONS["email"]}{p["email"]}</a>',
        f'<a class="icon gh" href="{L["github"]}" aria-label="GitHub" title="GitHub">{ICONS["github"]}</a>',
        f'<a class="icon yt" href="{L["youtube"]}" aria-label="YouTube" title="YouTube">{ICONS["youtube"]}</a>',
        f'<a class="icon li" href="{L["linkedin"]}" aria-label="LinkedIn" title="LinkedIn">{ICONS["linkedin"]}</a>',
        '<a class="cv" href="/cv.pdf">' + ICONS["resume"] + 'Résumé</a>',
    ])

    work = []
    for job in c["work"]:
        for r_i, role in enumerate(job["roles"]):
            work.append(f'<h3 class="role">{escape(role["title"])}, {escape(job["company"])}'
                        f'<span class="when">{month(role["start"])} – {month(role["end"])}</span></h3>')
            work += [item_html(it, f'<a href="{it["page"]}">{escape(it["title"])}</a>' if it.get("page") else escape(it["title"]),
                               href=it.get("page"))
                     for it in job["items"] if it["role"] == r_i]

    skills = "".join(f'<dt>{escape(g)}</dt><dd>{escape(", ".join(v))}</dd>' for g, v in c["skills"].items())

    edu = "".join(
        f'<div class="item"><p class="ititle">{escape(e["school"])}'
        f'<span class="when">{e["start"][:4]} – {e["end"][:4]}</span></p>'
        f'<p>{escape(e["degree"])}<br><span class="detail">{" · ".join(mark_key(d.strip(), e.get("key")) for d in e["detail"].split(";"))}</span></p></div>'
        for e in c["education"])

    projects = [item_html(pr, f'<a href="{pr["page"]}">{escape(pr["title"])}</a>', month(pr["date"]), href=pr["page"])
                for pr in c["projects"]]
    thoughts = [item_html(t, f'<a href="{t["page"]}">{escape(t["title"])}</a>', month(t["date"]),
                          tailorable=False, href=t["page"])
                for t in c["thoughts"]]

    log = "".join(f'<dt class="num">{l["date"]}</dt><dd><a href="{l["link"]}">{l["text"]}</a></dd>' for l in c["log"])

    # the channel link gets a small YouTube mark before its name
    yt_mark = ICONS["youtube"].replace('width="24" height="24"', 'class="inline-yt" width="20" height="20"')
    intro = p["intro"].replace('">The Unplanned Stack</a>', '">' + yt_mark + 'The Unplanned Stack</a>')

    title_line = f'{p["title"]} at IBM, {p["location"].split(",")[0]}. {p["experience"]} building AI/LLM and backend systems.'

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(p["name"])}</title>
<meta name="description" content="{escape(title_line)}">
<link rel="canonical" href="{p["site"]}/">
<link rel="stylesheet" href="/assets/tufte.css">
<style>
  dl.log {{ display: grid; grid-template-columns: 6rem 1fr; gap: .4rem 1rem; }}
  dl.log dt {{ color: var(--soft); }}
  dl.log dd {{ margin: 0; }}
  dl.log a:link, dl.log a:visited {{ background: none; }}
</style>
</head>
<body>
<article>
  <h1>{escape(p["name"])}</h1>
  <p class="subtitle">{escape(title_line)}</p>
  <p class="contact">{contact}</p>

  <section id="tailor-slot"></section>

  <section>
    <p>{intro}</p>
  </section>

  <section id="work">
    <h2>Work</h2>
    {"".join(work)}
    <h3 class="role">Skills</h3>
    <dl class="skills">{skills}</dl>
    <h3 class="role">Education</h3>
    {edu}
  </section>

  <section id="projects">
    <h2>Projects</h2>
    {"".join(projects)}
  </section>

  <section id="thoughts">
    <h2>Thoughts</h2>
    {"".join(thoughts)}
  </section>

  <section id="log">
    <h2>Log</h2>
    <dl class="log">{log}</dl>
  </section>

  <footer class="colophon"><p class="contact" style="margin:0">{contact}</p></footer>
</article>
<script src="/assets/synonyms.js"></script>
<script src="/assets/profile.js"></script>
<script src="/assets/site.js"></script>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page)
    profile = {
        "items": [{"id": it["id"], "stack": it.get("stack", []), "tags": it.get("tags", []), "text": it["summary"]}
                  for it in [i for job in c["work"] for i in job["items"]] + c["projects"]],
        "skills": [s for group in c["skills"].values() for s in group],
    }
    (ROOT / "assets" / "profile.js").write_text(
        "window.PROFILE = " + json.dumps(profile, ensure_ascii=False, indent=1) + ";\n")
    (ROOT / "assets" / "synonyms.js").write_text(
        "window.SYNONYMS = " + json.dumps(c["synonyms"], ensure_ascii=False, indent=1) + ";\n")
    stamp_assets()
    print("wrote index.html and assets/synonyms.js; stamped asset links")


def stamp_assets():
    """Add ?v=<content hash> to the shared CSS and JS links in every page, so a changed
    file gets a new URL and browsers never keep using a stale cached copy."""
    import hashlib
    import re
    for name in ("tufte.css", "site.js", "synonyms.js", "profile.js"):
        digest = hashlib.sha1((ROOT / "assets" / name).read_bytes()).hexdigest()[:8]
        pattern = re.compile(r'(/assets/' + re.escape(name) + r')(\?v=[0-9a-f]+)?"')
        for page in ROOT.rglob("*.html"):
            text = page.read_text()
            new = pattern.sub(r'\1?v=' + digest + '"', text)
            if new != text:
                page.write_text(new)


if __name__ == "__main__":
    build()
