#!/usr/bin/env python3
"""Build the home page and the synonym table from content.json.

    python3 build.py

Writes index.html and assets/synonyms.js. Article pages are written by hand.
Standard library only.
"""
import json
from html import escape
from pathlib import Path

from doodles import DOODLES

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

    contact = ' <span class="sep">·</span> '.join([
        f'<a class="addr" href="mailto:{p["email"]}">{p["email"]}</a>',
        f'<a href="{L["github"]}">github</a>',
        f'<a href="{L["youtube"]}">youtube</a>',
        f'<a href="{L["linkedin"]}">linkedin</a>',
        '<a href="/cv.pdf">résumé</a>',
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

    outside = "".join(
        f'<figure class="doodle"><svg viewBox="0 0 80 64" width="104" height="83" fill="none" stroke="#111" '
        f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{DOODLES[o["id"]]}</svg>'
        f'<figcaption>{escape(o["caption"])}</figcaption></figure>'
        for o in c.get("outside", []))

    log = "".join(f'<dt class="num">{l["date"]}</dt><dd><a href="{l["link"]}">{l["text"]}</a></dd>' for l in c["log"])

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
    <p>{p["intro"]}</p>
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

  <section id="outside">
    <h2>Outside work</h2>
    <div class="doodles">{outside}</div>
  </section>

  <section id="log">
    <h2>Log</h2>
    <dl class="log">{log}</dl>
  </section>

  <footer class="colophon"><p class="contact" style="margin:0">{contact}</p></footer>
</article>
<script src="/assets/synonyms.js"></script>
<script src="/assets/site.js"></script>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page)
    (ROOT / "assets" / "synonyms.js").write_text(
        "window.SYNONYMS = " + json.dumps(c["synonyms"], ensure_ascii=False, indent=1) + ";\n")
    stamp_assets()
    print("wrote index.html and assets/synonyms.js; stamped asset links")


def stamp_assets():
    """Add ?v=<content hash> to the shared CSS and JS links in every page, so a changed
    file gets a new URL and browsers never keep using a stale cached copy."""
    import hashlib
    import re
    for name in ("tufte.css", "site.js", "synonyms.js"):
        digest = hashlib.sha1((ROOT / "assets" / name).read_bytes()).hexdigest()[:8]
        pattern = re.compile(r'(/assets/' + re.escape(name) + r')(\?v=[0-9a-f]+)?"')
        for page in ROOT.rglob("*.html"):
            text = page.read_text()
            new = pattern.sub(r'\1?v=' + digest + '"', text)
            if new != text:
                page.write_text(new)


if __name__ == "__main__":
    build()
