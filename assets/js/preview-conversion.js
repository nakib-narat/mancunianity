(function () {
  var audio = document.getElementById('river-audio-preview');
  var end = document.getElementById('preview-end');
  var bar = document.getElementById('sticky-book');
  if (!audio || !end || !bar) return;
  var shown = false;
  function showBar() {
    if (shown) return;
    shown = true;
    bar.hidden = false;
  }
  audio.addEventListener('play', function () { end.hidden = true; showBar(); });
  audio.addEventListener('ended', function () { end.hidden = false; });
  window.addEventListener('scroll', function () {
    if (window.scrollY > 600) showBar();
  }, { passive: true });
})();
