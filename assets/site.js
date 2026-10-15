/* Sparklines, click-to-load videos, and link-based tailoring.
 *
 * Tailoring reads the page URL:
 *   ?show=llm-pipeline,url-shortener   items to list first and mark as relevant (home page)
 *   &match=typescript,k8s,llm          words to highlight wherever they already appear
 *   &company=Stripe&role=Backend+Engineer   shown in the note, never stored
 * It only reorders and highlights what is already on the page.
 */
(function () {
  'use strict';

  /* ---------- sparklines: <svg class="spark" data-spark="1,2,3" data-hot="1" data-step> ---------- */
  document.querySelectorAll('svg[data-spark]').forEach(function (el) {
    var vals = el.dataset.spark.split(',').map(Number);
    var hot = (el.dataset.hot || '').split(',').filter(Boolean).map(Number);
    var step = el.hasAttribute('data-step');
    var W = 66, H = 13, n = vals.length;
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    var x = function (i) { return i / (n - 1) * W; };
    var y = function (v) { return H - (v - lo) / (hi - lo || 1) * H; };
    var d = 'M' + x(0) + ' ' + y(vals[0]);
    for (var i = 1; i < n; i++) d += step ? ' H' + x(i) + ' V' + y(vals[i]) : ' L' + x(i) + ' ' + y(vals[i]);
    el.setAttribute('viewBox', '-2 -2 ' + (W + 4) + ' ' + (H + 4));
    el.innerHTML = '<path d="' + d + '" fill="none" stroke="#111" stroke-width=".9"/>' +
      hot.map(function (k) { return '<circle class="hot" cx="' + x(k) + '" cy="' + y(vals[k]) + '" r="1.8"/>'; }).join('') +
      '<circle cx="' + x(n - 1) + '" cy="' + y(vals[n - 1]) + '" r="1.6" fill="#111"/>';
  });

  /* ---------- videos: YouTube loads only after a click ---------- */
  document.querySelectorAll('button.video[data-yt]').forEach(function (b) {
    // full-HD thumbnail when the video has one; YouTube serves a 120px placeholder when it doesn't
    var thumb = 'https://i.ytimg.com/vi/' + b.dataset.yt + '/';
    b.style.backgroundImage = 'url(' + thumb + 'hqdefault.jpg)';
    var hd = new Image();
    hd.onload = function () { if (hd.naturalWidth > 120) b.style.backgroundImage = 'url(' + hd.src + ')'; };
    hd.src = thumb + 'maxresdefault.jpg';
    b.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + b.dataset.yt + '?autoplay=1&rel=0';
      f.title = b.getAttribute('aria-label') || 'Video';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      var box = document.createElement('div');
      box.className = 'video';
      box.appendChild(f);
      b.replaceWith(box);
    }, { once: true });
  });

  /* ---------- tables: on phones, text tables with 3+ columns become stacked rows ---------- */
  document.querySelectorAll('table.booktabs').forEach(function (t) {
    var heads = Array.prototype.map.call(t.querySelectorAll('thead th'), function (th) { return th.textContent.trim(); });
    var cells = t.querySelectorAll('tbody td');
    var chars = 0;
    cells.forEach(function (td) { chars += td.textContent.trim().length; });
    // short numeric tables still fit as a grid; only long text gets squeezed
    if (t.classList.contains('numbers') || heads.length < 3 || chars / (cells.length || 1) < 12) return;
    t.classList.add('stacked');
    t.querySelectorAll('tbody tr').forEach(function (tr) {
      Array.prototype.forEach.call(tr.children, function (td, i) { if (heads[i]) td.setAttribute('data-label', heads[i]); });
    });
  });

  /* ---------- tailoring ---------- */
  var params = new URLSearchParams(location.search);

  var clean = function (s, max) { return (s || '').replace(/[\u0000-\u001f<>]/g, '').trim().slice(0, max); };
  var list = function (s) { return clean(s, 400).split(',').map(function (t) { return t.trim(); }).filter(Boolean); };
  var show = list(params.get('show')).slice(0, 6);
  var match = list(params.get('match')).slice(0, 25);
  var company = clean(params.get('company'), 60);
  var role = clean(params.get('role'), 80);
  var fit = (params.get('fit') || '').match(/^(\d{1,3})-(\d{1,3})$/);
  var gaps = list(params.get('gaps')).slice(0, 10);
  var tailored = show.length || match.length || company || role;
  if (match.length) document.documentElement.classList.add('has-match');

  // carry the tailoring to other pages of this site
  if (tailored) {
    document.querySelectorAll('a[href^="/"]:not([href^="//"])').forEach(function (a) {
      var u = new URL(a.getAttribute('href'), location.origin);
      if (u.search || /\.(pdf|jpg|png)$/i.test(u.pathname)) return;
      a.setAttribute('href', u.pathname + location.search + u.hash);
    });
  }

  // the note at the top of the home page
  var slot = document.getElementById('tailor-slot');
  if (slot && show.length) {
    var items = show.map(function (id) { return document.getElementById(id); })
      .filter(function (el) { return el && el.hasAttribute('data-item') && el.dataset.tailorable !== 'false'; });
    if (items.length) {
      var box = document.createElement('div');
      box.className = 'tailor';
      var p = document.createElement('p');
      p.className = 'for';
      p.textContent = role && company ? 'For the ' + role + ' role at ' + company + ', the most relevant work:'
        : role ? 'For the ' + role + ' role, the most relevant work:'
        : company ? 'For ' + company + ', the most relevant work:'
        : 'The most relevant work:';
      var ol = document.createElement('ol');
      items.forEach(function (el) {
        el.classList.add('relevant');
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.className = 't';
        a.href = el.dataset.href || '#' + el.id;
        a.textContent = el.dataset.title;
        li.appendChild(a);
        li.appendChild(document.createTextNode('. ' + el.dataset.summary));
        ol.appendChild(li);
      });
      var cv = document.createElement('p');
      cv.className = 'cv';
      cv.innerHTML = '<a href="/cv.pdf">Résumé (PDF)</a>';
      box.appendChild(p);
      if (fit) {
        var f = document.createElement('p');
        f.className = 'fit';
        f.textContent = fit[1] + ' of ' + fit[2] + ' skills in this posting appear in my work.' +
          (gaps.length ? ' Not on this site: ' + gaps.join(', ') + '.' : '');
        box.appendChild(f);
      }
      box.appendChild(ol); box.appendChild(cv);
      slot.appendChild(box);
    }
  }

  // highlight matched words, including synonyms, wherever they already appear
  if (match.length) {
    var syn = window.SYNONYMS || {};
    var terms = {};
    match.forEach(function (m) {
      var low = m.toLowerCase();
      terms[low] = 1;
      Object.keys(syn).forEach(function (canon) {
        var group = [canon.toLowerCase()].concat(syn[canon].map(function (s) { return s.toLowerCase(); }));
        if (group.indexOf(low) !== -1) group.forEach(function (g) { terms[g] = 1; });
      });
    });
    var esc = function (s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); };
    var words = Object.keys(terms).filter(function (t) { return t.length > 1; })
      .sort(function (a, b) { return b.length - a.length; }).map(esc);
    if (words.length) {
      var re = new RegExp('(^|[^\\w.+#-])(' + words.join('|') + ')(?![\\w+#])', 'gi');
      var root = document.querySelector('article') || document.body;
      var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode: function (n) {
          return n.parentElement.closest('script,style,svg,.tailor,.katex,label,mark.match,button,pre')
            ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
        }
      });
      var nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(function (n) {
        var text = n.nodeValue;
        re.lastIndex = 0;
        if (!re.test(text)) return;
        re.lastIndex = 0;
        var frag = document.createDocumentFragment(), last = 0, m;
        while ((m = re.exec(text))) {
          var start = m.index + m[1].length;
          frag.appendChild(document.createTextNode(text.slice(last, start)));
          var mk = document.createElement('mark');
          mk.className = 'match';
          mk.textContent = m[2];
          frag.appendChild(mk);
          last = start + m[2].length;
        }
        frag.appendChild(document.createTextNode(text.slice(last)));
        n.parentNode.replaceChild(frag, n);
      });
    }
  }

  /* ---------- match this page to a pasted job description (runs only in the browser) ---------- */
  var jdGo = document.getElementById('jd-go');
  if (jdGo && window.PROFILE) {
    // common technologies, so the summary can say honestly what is NOT on this site
    var COMMON = ['Go', 'Golang', 'Rust', 'C++', 'C#', 'Ruby', 'Rails', 'Scala', 'Kotlin', 'Swift', 'PHP', 'Elixir',
      'JavaScript', 'TypeScript', 'Java', 'Python', 'SQL', 'Bash', 'React', 'Angular', 'Vue', 'Next.js', 'Svelte',
      'Node.js', 'Django', 'Flask', 'FastAPI', 'Spring', 'Express', 'GraphQL', 'gRPC', 'REST',
      'PostgreSQL', 'Postgres', 'MySQL', 'MongoDB', 'Redis', 'Cassandra', 'DynamoDB', 'Elasticsearch', 'SQLite',
      'Snowflake', 'BigQuery', 'Kafka', 'RabbitMQ', 'Spark', 'Airflow', 'dbt', 'Flink', 'Hadoop',
      'AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Helm', 'Linux', 'nginx',
      'Prometheus', 'Grafana', 'Datadog', 'Jenkins', 'GitHub Actions', 'CI/CD', 'Git',
      'PyTorch', 'TensorFlow', 'scikit-learn', 'pandas', 'NumPy', 'LangChain', 'LlamaIndex', 'RAG',
      'LLMs', 'Embeddings', 'Agents', 'Prompt engineering', 'k6'];
    // words that are also ordinary English: only count them when capitalised as a name
    var CASED = { 'Go': 1, 'Rust': 1, 'Swift': 1, 'Spark': 1, 'Spring': 1, 'Express': 1, 'Helm': 1, 'Agents': 1, 'Flink': 1, 'Ruby': 1 };

    var syn = window.SYNONYMS || {};
    var lower = function (x) { return x.toLowerCase(); };
    var esc = function (x) { return x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); };
    var has = function (text, term, cased) {
      return new RegExp('(^|[^\\w.+#-])' + esc(term) + '(?![\\w+#])', cased ? '' : 'i').test(text);
    };
    // every name a skill goes by: itself plus its synonyms
    var namesOf = function (skill) {
      var names = [skill];
      Object.keys(syn).forEach(function (canon) {
        var group = [canon].concat(syn[canon]).map(lower);
        if (group.indexOf(lower(skill)) !== -1) names = names.concat([canon], syn[canon]);
      });
      return names;
    };

    // everything this site claims, by canonical name
    var mine = {};
    window.PROFILE.skills.forEach(function (x) { mine[lower(x)] = x; });
    window.PROFILE.items.forEach(function (it) { it.stack.concat(it.tags).forEach(function (x) { mine[lower(x)] = x; }); });
    var mineNames = {};
    Object.keys(mine).forEach(function (k) { namesOf(mine[k]).forEach(function (n) { mineNames[lower(n)] = mine[k]; }); });

    jdGo.addEventListener('click', function () {
      var text = document.getElementById('jd-text').value;
      var msg = document.getElementById('jd-msg');
      if (text.trim().length < 40) { msg.textContent = 'Paste the full posting first.'; return; }

      // skills of mine that the posting asks for
      var asked = {};
      Object.keys(mine).forEach(function (k) {
        if (namesOf(mine[k]).some(function (n) { return n.length > 1 && has(text, n, CASED[n]); })) asked[lower(mine[k])] = mine[k];
      });
      // common technologies the posting asks for that are not on this site
      var gapList = [];
      COMMON.forEach(function (t) {
        if (!has(text, t, CASED[t])) return;
        if (mineNames[lower(t)]) return;
        if (t === 'Golang' && gapList.indexOf('Go') !== -1) return;
        var name = t === 'Golang' ? 'Go' : t === 'Postgres' ? 'PostgreSQL' : t;
        if (gapList.indexOf(name) === -1) gapList.push(name);
      });

      // skills that are names for the same thing (k6 and load testing, LLMs and language models) count once
      var seenGroup = {};
      Object.keys(asked).forEach(function (k) {
        var key = namesOf(asked[k]).map(lower).sort()[0];
        if (seenGroup[key]) delete asked[k]; else seenGroup[key] = 1;
      });
      var matched = Object.keys(asked).map(function (k) { return asked[k]; });
      if (!matched.length) {
        msg.textContent = 'None of the skills on this site appear in that posting.' + (gapList.length ? ' It asks for: ' + gapList.join(', ') + '.' : '');
        return;
      }
      // rank items by how much of what was asked they use
      var ranked = window.PROFILE.items.map(function (it, i) {
        var uses = it.stack.concat(it.tags).map(lower);
        var score = 0;
        matched.forEach(function (m) {
          if (uses.indexOf(lower(m)) !== -1) score += 1;
          else if (has(it.text, m)) score += 0.5;
        });
        return { id: it.id, score: score, i: i };
      }).filter(function (r) { return r.score > 0; })
        .sort(function (a, b) { return b.score - a.score || a.i - b.i; })
        .slice(0, 3);

      var q = new URLSearchParams();
      q.set('show', ranked.map(function (r) { return r.id; }).join(','));
      q.set('match', matched.slice(0, 25).join(','));
      q.set('fit', matched.length + '-' + (matched.length + gapList.length));
      if (gapList.length) q.set('gaps', gapList.slice(0, 10).join(','));
      location.search = q.toString();
    });
  }
})();
