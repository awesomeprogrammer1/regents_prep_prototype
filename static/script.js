// ------------------------------------------------------------------
// Page transition — card scales up to fill screen, then slides off top.
// ------------------------------------------------------------------
(function () {
  var overlay = document.getElementById('page-transition');
  if (!overlay) return;

  var SPIN_DELAY = 400; // ms  spinner runs before expansion begins
  var EXPAND     = 1200; // ms  card → fullscreen
  var REVEAL     = 2000; // ms  fullscreen → slides off top (on next page)
  var EASE     = 'cubic-bezier(.22,1,.36,1)';

  // ── On arrival at new page: overlay is covering screen, slide it off the top ──
  if (sessionStorage.getItem('page-transition') === '1') {
    sessionStorage.removeItem('page-transition');
    overlay.style.transition = 'none';
    overlay.style.transform  = 'translateY(0)';
    overlay.style.borderRadius = '0';
    overlay.getBoundingClientRect(); // force reflow
    overlay.style.transition = 'transform ' + REVEAL + 'ms ' + EASE;
    overlay.style.transform  = 'translateY(-100%)';
  }

  // ── On card click: size the overlay up from the card, then navigate ──
  document.addEventListener('click', function (e) {
    var card = e.target.closest('.subject-card-active');
    if (!card || !card.href) return;
    e.preventDefault();
    var dest = card.href;

    var rect = card.getBoundingClientRect();
    var vw = window.innerWidth;
    var vh = window.innerHeight;

    // Scale factors so the fullscreen overlay appears card-sized
    var sx = rect.width  / vw;
    var sy = rect.height / vh;

    // Translation so the overlay is centred on the card
    var tx = (rect.left + rect.width  / 2) - vw / 2;
    var ty = (rect.top  + rect.height / 2) - vh / 2;

    // Border-radius that looks like 16px after scaling
    var startRadius = Math.round(16 / Math.min(sx, sy)) + 'px';

    // Start spinner on the play circle
    var playEl = card.querySelector('.subject-card-play');
    if (playEl) playEl.classList.add('spinning');

    // After spin delay, snap overlay to card then expand to fill screen
    setTimeout(function () {
      overlay.style.transition   = 'none';
      overlay.style.transform    = 'translate(' + tx + 'px,' + ty + 'px) scale(' + sx + ',' + sy + ')';
      overlay.style.borderRadius = startRadius;
      overlay.getBoundingClientRect(); // force reflow

      overlay.style.transition   = 'transform ' + EXPAND + 'ms ' + EASE + ', border-radius ' + EXPAND + 'ms ease';
      overlay.style.transform    = 'translate(0,0) scale(1)';
      overlay.style.borderRadius = '0px';

      sessionStorage.setItem('page-transition', '1');
      setTimeout(function () { window.location.href = dest; }, EXPAND);
    }, SPIN_DELAY);
  });
})();

document.addEventListener('DOMContentLoaded', function () {

  // ------------------------------------------------------------------
  // Guest mid-session navigation warning
  // ------------------------------------------------------------------
  if (document.body.dataset.guestWarn) {
    var navLinks = document.querySelectorAll('.nav-brand, .nav-links a');
    navLinks.forEach(function (link) {
      link.addEventListener('click', function (e) {
        if (!confirm('Are you sure you want to leave? You\'ll lose your current practice session.')) {
          e.preventDefault();
          e.stopImmediatePropagation();
        }
      });
    });
  }

  // ------------------------------------------------------------------
  // Dark mode — persist preference in localStorage
  // ------------------------------------------------------------------
  var darkToggle = document.getElementById('dark-toggle');
  if (localStorage.getItem('dark') === '1') {
    document.body.classList.add('dark');
    if (darkToggle) darkToggle.textContent = '\u2600'; // sun icon when dark
  }
  if (darkToggle) {
    darkToggle.addEventListener('click', function () {
      var isDark = document.body.classList.toggle('dark');
      localStorage.setItem('dark', isDark ? '1' : '0');
      darkToggle.textContent = isDark ? '\u2600' : '\u263E'; // sun / moon
    });
  }

  // ------------------------------------------------------------------
  // Highlight selected radio choice visually
  // ------------------------------------------------------------------
  var choiceLabels = document.querySelectorAll('.choice-label');
  choiceLabels.forEach(function (label) {
    var radio = label.querySelector('input[type="radio"]');
    if (!radio) return;
    radio.addEventListener('change', function () {
      choiceLabels.forEach(function (l) { l.classList.remove('choice-selected'); });
      label.classList.add('choice-selected');
    });
  });

  // ------------------------------------------------------------------
  // Apply bar widths from data-width attributes (progress bars, accuracy, sidebar stats)
  // ------------------------------------------------------------------
  document.querySelectorAll('[data-width]').forEach(function (el) {
    el.style.width = el.dataset.width + '%';
  });
  document.querySelectorAll('[data-pct]').forEach(function (el) {
    el.style.width = el.dataset.pct + '%';
  });

  // ------------------------------------------------------------------
  // Stagger-on-scroll: when a .stagger-section enters viewport, reveal
  // its .stagger-item children one by one with 70ms between each.
  // Also triggers renderMap() when the map screen becomes visible.
  // ------------------------------------------------------------------
  var staggerSections = document.querySelectorAll('.stagger-section');
  if (staggerSections.length) {
    var STAGGER_MS = 70;
    var staggerObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var items = entry.target.querySelectorAll('.stagger-item');
          items.forEach(function (item, i) {
            item.style.transitionDelay = (i * STAGGER_MS) + 'ms';
            item.classList.add('is-visible');
          });
          if (entry.target.classList.contains('home-screen-3') &&
              typeof renderMap === 'function') {
            // Delay map render until canvas is visible
            var canvasDelay = items.length * STAGGER_MS;
            setTimeout(renderMap, canvasDelay);
          }
          staggerObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    staggerSections.forEach(function (el) { staggerObserver.observe(el); });
  }

  // ------------------------------------------------------------------
  // "Why is my subject not available?" toggle
  // ------------------------------------------------------------------
  var faqToggle = document.getElementById('subjects-faq-toggle');
  var faqBody   = document.getElementById('subjects-faq-body');
  if (faqToggle && faqBody) {
    faqToggle.addEventListener('click', function () {
      var expanded = faqToggle.getAttribute('aria-expanded') === 'true';
      faqToggle.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      faqBody.hidden = expanded;
    });
  }

  // ------------------------------------------------------------------
  // "Explain why" toggle
  // ------------------------------------------------------------------
  var explainToggle = document.getElementById('explain-toggle');
  var explainBody   = document.getElementById('explain-body');
  if (explainToggle && explainBody) {
    explainToggle.addEventListener('click', function () {
      var expanded = explainToggle.getAttribute('aria-expanded') === 'true';
      explainToggle.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      explainBody.hidden = expanded;
    });
  }

  // ------------------------------------------------------------------
  // Grid-in help modal
  // ------------------------------------------------------------------
  var modal   = document.getElementById('grid-help-modal');
  var openBtn = document.getElementById('open-grid-help');
  var closeBtn = document.getElementById('close-grid-help');

  if (openBtn && modal) {
    openBtn.addEventListener('click', function () {
      modal.hidden = false;
    });
  }
  if (closeBtn && modal) {
    closeBtn.addEventListener('click', function () {
      modal.hidden = true;
    });
  }
  // Close on backdrop click
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) { modal.hidden = true; }
    });
    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !modal.hidden) { modal.hidden = true; }
    });
  }

});
