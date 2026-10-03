/* Client-side search with Fuse.js over the index Hugo builds per language.
   Fuse.js and the index are downloaded on first use only. */
(function () {
  'use strict';

  var cfgEl = document.getElementById('search-config');
  if (!cfgEl) return;
  var cfg = JSON.parse(cfgEl.textContent);
  var fusePromise = null;

  function loadScript(src, integrity) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = src;
      if (integrity) s.integrity = integrity;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function getFuse() {
    if (!fusePromise) {
      fusePromise = Promise.all([
        window.Fuse ? Promise.resolve() : loadScript(cfg.fuse, cfg.fuseIntegrity),
        fetch(cfg.index).then(function (r) {
          if (!r.ok) throw new Error('search index: HTTP ' + r.status);
          return r.json();
        })
      ]).then(function (res) {
        return new window.Fuse(res[1], {
          keys: [
            { name: 'title', weight: 3 },
            { name: 'tags', weight: 2 },
            { name: 'categories', weight: 2 },
            { name: 'summary', weight: 1.5 },
            { name: 'content', weight: 1 }
          ],
          threshold: 0.35,
          ignoreLocation: true,
          minMatchCharLength: 2
        });
      });
      fusePromise.catch(function () { fusePromise = null; }); // allow a retry later
    }
    return fusePromise;
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function render(container, query, results, limit) {
    container.textContent = '';
    if (!query) return;
    if (!results.length) {
      container.appendChild(el('p', 'search-results__empty', cfg.i18n.noResults.replace('{query}', query)));
      return;
    }
    container.appendChild(el('p', 'search-results__count', cfg.i18n.results.replace('{count}', String(results.length))));
    var list = el('ul', 'search-results__list');
    results.slice(0, limit || results.length).forEach(function (r) {
      var item = r.item;
      var li = el('li', 'search-result');
      var a = el('a', 'search-result__title', item.title);
      a.href = item.url;
      li.appendChild(a);
      if (item.date) li.appendChild(el('span', 'search-result__meta', item.date));
      if (item.summary) li.appendChild(el('p', 'search-result__summary', item.summary));
      list.appendChild(li);
    });
    container.appendChild(list);
    if (limit && results.length > limit && cfg.page) {
      var all = el('a', 'search-results__all', cfg.i18n.seeAll);
      all.href = cfg.page + '?q=' + encodeURIComponent(query);
      container.appendChild(all);
    }
  }

  function search(container, query, limit) {
    if (query.length < 2) {
      render(container, '', [], limit);
      return;
    }
    getFuse().then(function (fuse) {
      render(container, query, fuse.search(query), limit);
    }).catch(function () {
      container.textContent = '';
      container.appendChild(el('p', 'search-results__empty', cfg.i18n.error));
    });
  }

  function bindInput(input, container, limit) {
    var timer;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { search(container, input.value.trim(), limit); }, 150);
    });
  }

  // Header search panel
  var toggle = document.querySelector('[data-search-toggle]');
  var panel = document.getElementById('search-panel');
  if (toggle && panel) {
    var input = panel.querySelector('[data-search-input]');
    var results = panel.querySelector('[data-search-results]');
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      panel.hidden = !open;
      if (open) {
        input.focus();
        getFuse().catch(function () {});
      }
    };
    toggle.addEventListener('click', function () { setOpen(panel.hidden); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !panel.hidden) {
        setOpen(false);
        toggle.focus();
      }
    });
    bindInput(input, results, 8);
    panel.querySelector('form').addEventListener('submit', function (e) {
      if (!cfg.page) e.preventDefault(); // no search page: keep results in the panel
    });
  }

  // Search page
  var pageForm = document.querySelector('[data-search-page]');
  if (pageForm) {
    var pageInput = pageForm.querySelector('input[name="q"]');
    var pageResults = document.querySelector('[data-search-page-results]');
    var initial = (new URLSearchParams(window.location.search).get('q') || '').trim();
    pageInput.value = initial;
    bindInput(pageInput, pageResults, 0);
    pageForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var query = pageInput.value.trim();
      history.replaceState(null, '', '?q=' + encodeURIComponent(query));
      search(pageResults, query, 0);
    });
    if (initial) search(pageResults, initial, 0);
  }
})();
