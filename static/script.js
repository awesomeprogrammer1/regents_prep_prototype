document.addEventListener('DOMContentLoaded', function () {
  // Highlight selected radio choice visually
  const choiceLabels = document.querySelectorAll('.choice-label');
  choiceLabels.forEach(function (label) {
    const radio = label.querySelector('input[type="radio"]');
    if (!radio) return;
    radio.addEventListener('change', function () {
      choiceLabels.forEach(function (l) { l.classList.remove('choice-selected'); });
      label.classList.add('choice-selected');
    });
  });

  // Apply bar widths from data-width attributes
  document.querySelectorAll('[data-width]').forEach(function (el) {
    el.style.width = el.dataset.width + '%';
  });
});


