document.addEventListener('DOMContentLoaded', function () {

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
