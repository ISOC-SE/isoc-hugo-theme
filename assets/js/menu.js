/* Header behaviour: mobile menu, compact layout for crowded menus, dropdowns,
   scrolled state and reveal-on-scroll.
   Progressive enhancement only; the page works without it. */
(function () {
  'use strict';

  var root = document.documentElement;
  var body = document.body;
  var OPEN = '[data-submenu-toggle][aria-expanded="true"], [data-dropdown-toggle][aria-expanded="true"]';
  var desktop = window.matchMedia('(min-width: 1180px)');

  // Mobile menu
  var menuToggle = document.querySelector('[data-menu-toggle]');
  var label = menuToggle && menuToggle.querySelector('.sr-only');

  function setMenu(open) {
    if (!menuToggle) return;
    menuToggle.setAttribute('aria-expanded', String(open));
    body.classList.toggle('menu-open', open);
    if (label) {
      label.textContent = label.getAttribute(open ? 'data-label-close' : 'data-label-open');
    }
  }

  if (menuToggle) {
    menuToggle.addEventListener('click', function () {
      setMenu(menuToggle.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && body.classList.contains('menu-open')) {
        setMenu(false);
        menuToggle.focus();
      }
    });
  }

  // Compact layout on desktop: when the menu, language switcher and Join do not
  // fit on one row (many items or long labels), switch to the hamburger layout
  // (html.nav-compact, styled by compact.css).
  var headerRow = document.querySelector('.site-header__inner');

  function fitMenu() {
    if (!headerRow) return;
    var wasCompact = root.classList.contains('nav-compact');
    root.classList.remove('nav-compact');
    var compact = desktop.matches && headerRow.scrollWidth > headerRow.clientWidth + 1;
    root.classList.toggle('nav-compact', compact);
    if (wasCompact && !compact && desktop.matches) setMenu(false);
  }

  fitMenu();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitMenu);
  var fitTimer;
  window.addEventListener('resize', function () {
    clearTimeout(fitTimer);
    fitTimer = setTimeout(fitMenu, 100);
  });
  desktop.addEventListener('change', function () {
    setMenu(false);
    fitMenu();
  });

  // Sub-menus and the language dropdown
  function closeOthers(keep) {
    document.querySelectorAll(OPEN).forEach(function (btn) {
      if (btn === keep) return;
      if (keep && btn.parentElement.contains(keep)) return; // keep ancestors of a nested toggle open
      btn.setAttribute('aria-expanded', 'false');
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-submenu-toggle], [data-dropdown-toggle]');
    if (btn) {
      var open = btn.getAttribute('aria-expanded') !== 'true';
      closeOthers(btn);
      btn.setAttribute('aria-expanded', String(open));
      return;
    }
    if (!e.target.closest('.menu-item.has-children, [data-dropdown]')) closeOthers(null);
  });

  // Desktop dropdowns also open on hover and keyboard focus (CSS). Escape hides
  // them until the pointer and focus have left the item (WCAG 1.4.13).
  var dropdownItems = document.querySelectorAll('.nav-primary .menu-item.has-children');

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = document.querySelector(OPEN);
    if (open) {
      closeOthers(null);
      open.focus();
      return;
    }
    dropdownItems.forEach(function (item) {
      if (!item.matches(':hover') && !item.contains(document.activeElement)) return;
      item.classList.add('is-dismissed');
      if (item.contains(document.activeElement)) item.querySelector('a').focus();
    });
  });

  dropdownItems.forEach(function (item) {
    item.addEventListener('mouseleave', function () {
      if (!item.contains(document.activeElement)) item.classList.remove('is-dismissed');
    });
    item.addEventListener('focusout', function (e) {
      if (!item.contains(e.relatedTarget) && !item.matches(':hover')) item.classList.remove('is-dismissed');
    });
  });

  // Header shadow once the page scrolls
  var header = document.querySelector('[data-header]');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 10);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Reveal blocks as they scroll into view
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var revealEls = document.querySelectorAll('.reveal');
    if (revealEls.length) {
      document.documentElement.classList.add('can-reveal');
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -10% 0px' });
      revealEls.forEach(function (node) { observer.observe(node); });
    }
  }
})();
