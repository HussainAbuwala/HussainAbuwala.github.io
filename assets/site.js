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
    b.style.backgroundImage = 'url(https://i.ytimg.com/vi/' + b.dataset.yt + '/hqdefault.jpg)';
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

  /* ---------- doodles: sketch themselves in when they come into view, and again on hover ---------- */
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function sketch(svg) {
    if (still) return;
    svg.querySelectorAll('path, circle, rect, ellipse, line').forEach(function (el, i) {
      var len = el.getTotalLength ? el.getTotalLength() : 0;
      if (!len) return;
      el.style.transition = 'none';
      el.style.strokeDasharray = len;
      el.style.strokeDashoffset = len;
      el.getBoundingClientRect();
      el.style.transition = 'stroke-dashoffset .7s ease ' + (i * 0.08) + 's';
      el.style.strokeDashoffset = 0;
    });
  }
  var doodles = document.querySelectorAll('.doodle svg');
  if (doodles.length && 'IntersectionObserver' in window) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { sketch(e.target); seen.unobserve(e.target); }
      });
    }, { threshold: 0.6 });
    doodles.forEach(function (svg) {
      seen.observe(svg);
      svg.parentNode.addEventListener('mouseenter', function () { sketch(svg); });
    });
  }

  /* ---------- tailoring ---------- */
  var params = new URLSearchParams(location.search);

  var clean = function (s, max) { return (s || '').replace(/[\u0000-\u001f<>]/g, '').trim().slice(0, max); };
  var list = function (s) { return clean(s, 400).split(',').map(function (t) { return t.trim(); }).filter(Boolean); };
  var show = list(params.get('show')).slice(0, 6);
  var match = list(params.get('match')).slice(0, 25);
  var company = clean(params.get('company'), 60);
  var role = clean(params.get('role'), 80);
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
      box.appendChild(p); box.appendChild(ol); box.appendChild(cv);
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
})();
