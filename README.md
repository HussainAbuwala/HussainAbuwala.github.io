# hussainabuwala.github.io

Personal site. Plain HTML and CSS, no framework.

- `content.json` holds the work items, projects, skills and log. Edit it, then run `python3 build.py` to regenerate `index.html`.
- Article pages under `projects/`, `work/` and `thoughts/` are written by hand.
- `build.py` also stamps the shared CSS and JS links with a content hash, so browsers fetch new versions after a change.
- To preview locally: `python3 -m http.server 8000`, then open http://localhost:8000.

Fonts: ET Book (MIT licence, in `assets/fonts/`).
