// Highlight selected radio choice visually
document.addEventListener('DOMContentLoaded', function () {
  const choiceLabels = document.querySelectorAll('.choice-label');
  choiceLabels.forEach(function (label) {
    const radio = label.querySelector('input[type="radio"]');
    if (!radio) return;
    radio.addEventListener('change', function () {
      choiceLabels.forEach(function (l) { l.classList.remove('choice-selected'); });
      label.classList.add('choice-selected');
    });
  });
});
