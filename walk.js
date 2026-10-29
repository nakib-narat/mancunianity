(function () {
  const walk = document.getElementById('walk');
  if (!walk) return;

  const stage = document.getElementById('stage');
  const map = document.getElementById('map');
  const badge = document.getElementById('badge');
  const kicker = document.getElementById('kicker');
  const copy = document.getElementById('copy');
  const dots = document.getElementById('dots');
  const prevBtn = document.getElementById('prev');
  const nextBtn = document.getElementById('next');
  const playBtn = document.getElementById('play');
  const musicBtn = document.getElementById('music');
  const musicStatus = document.getElementById('music-status');
  const textBox = document.getElementById('walktext');
  const items = [...document.querySelectorAll('#stops > li')];
  const ratio = parseFloat(walk.dataset.imageRatio) || 16 / 9;
  const totalStops = items.filter(li => li.dataset.stop).length;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const steps = items.map(li => ({
    el: li,
    x: parseFloat(li.dataset.x),
    y: parseFloat(li.dataset.y),
    z: parseFloat(li.dataset.z),
    stop: li.dataset.stop ? parseInt(li.dataset.stop, 10) : null,
    kind: li.dataset.kind || 'stop',
    label: li.dataset.label || li.dataset.stop,
    title: li.querySelector('h3').textContent,
    chars: li.textContent.length
  }));

  let index = 0;
  let playing = false;
  let timer = null;

  function updateMusicButton(on, message = '') {
    musicBtn.setAttribute('aria-pressed', String(on));
    musicBtn.textContent = on ? '\u266b Music on' : '\u266b Music off';
    musicStatus.textContent = message;
  }

  textBox.removeAttribute('open');
  walk.classList.add('wk-ready');

  function frame(step) {
    const W = stage.clientWidth;
    const H = stage.clientHeight;
    const baseW = Math.min(W, H * ratio);
    const w = baseW * step.z;
    const h = w / ratio;
    const place = (focus, size, view) => {
      if (size <= view) return (view - size) / 2;
      return Math.min(0, Math.max(view - size, view / 2 - focus * size));
    };
    const tx = place(step.x, w, W);
    const ty = place(step.y, h, H);
    map.style.width = baseW + 'px';
    map.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + step.z + ')';
  }

  function render() {
    const step = steps[index];
    frame(step);

    if (step.stop) {
      kicker.textContent = 'Stop ' + step.stop + ' of ' + totalStops;
      badge.hidden = false;
      badge.textContent = step.stop;
      badge.classList.remove('wk-pop');
      void badge.offsetWidth;
      badge.classList.add('wk-pop');
    } else {
      kicker.textContent = step.kind === 'intro' ? 'Welcome' : 'The end of the walk';
      badge.hidden = true;
    }

    copy.innerHTML = step.el.innerHTML;
    copy.classList.remove('wk-in');
    void copy.offsetWidth;
    copy.classList.add('wk-in');

    [...dots.children].forEach((d, i) => {
      if (i === index) d.setAttribute('aria-current', 'step');
      else d.removeAttribute('aria-current');
    });
    prevBtn.disabled = index === 0;
    nextBtn.disabled = index === steps.length - 1;
  }

  function dwell(step) {
    return Math.min(20000, Math.max(9000, 7000 + step.chars * 40));
  }

  function schedule() {
    clearTimeout(timer);
    if (!playing) return;
    timer = setTimeout(() => {
      if (index < steps.length - 1) {
        index += 1;
        render();
        schedule();
      } else {
        setPlaying(false);
      }
    }, dwell(steps[index]));
  }

  function setPlaying(on) {
    playing = on;
    playBtn.setAttribute('aria-pressed', String(on));
    playBtn.innerHTML = on ? '&#10074;&#10074; Pause' : '&#9654; Play the walk';
    if (on && index === steps.length - 1) {
      index = 0;
      render();
    }
    schedule();
  }

  function go(i) {
    index = Math.max(0, Math.min(steps.length - 1, i));
    render();
    schedule();
  }

  steps.forEach((step, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'wk-dot';
    b.textContent = step.label;
    b.setAttribute('aria-label', step.stop ? 'Stop ' + step.stop + ': ' + step.title : step.title);
    b.addEventListener('click', () => go(i));
    dots.appendChild(b);
  });

  prevBtn.addEventListener('click', () => go(index - 1));
  nextBtn.addEventListener('click', () => go(index + 1));
  playBtn.addEventListener('click', () => setPlaying(!playing));
  musicBtn.addEventListener('click', () => {
    const on = !music.enabled;
    music.toggle(on);
    updateMusicButton(music.enabled);
  });

  walk.addEventListener('keydown', e => {
    if (e.target.closest('input,textarea,select')) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1); }
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden && playing) setPlaying(false);
    if (document.hidden && music.enabled) musicBtn.click();
  });

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      map.style.transition = 'none';
      frame(steps[index]);
      void map.offsetWidth;
      map.style.transition = '';
    }, 120);
  });

  /* The soundtrack is user-initiated and fades gently in and out. */
  const music = (function () {
    const player = new Audio('audio/summer-adventures-115949.mp3');
    player.loop = true;
    player.preload = 'none';
    let enabled = false;
    let fadeTimer = null;

    function fadeTo(target, afterFade) {
      clearInterval(fadeTimer);
      const startVolume = player.volume;
      const startTime = performance.now();
      fadeTimer = setInterval(() => {
        const progress = Math.min(1, (performance.now() - startTime) / 900);
        player.volume = startVolume + (target - startVolume) * progress;
        if (progress === 1) {
          clearInterval(fadeTimer);
          fadeTimer = null;
          if (afterFade) afterFade();
        }
      }, 30);
    }

    function playbackFailed() {
      if (!enabled) return;
      enabled = false;
      clearInterval(fadeTimer);
      fadeTimer = null;
      player.pause();
      player.volume = 0.65;
      updateMusicButton(false, 'Music could not be played. Please try again or check your device audio settings.');
    }

    player.addEventListener('error', playbackFailed);

    return {
      get enabled() {
        return enabled;
      },
      toggle(on) {
        enabled = on;
        if (on) {
          player.volume = 0;
          player.play().then(() => {
            if (enabled) fadeTo(0.65);
          }).catch(playbackFailed);
        } else {
          fadeTo(0, () => player.pause());
        }
      }
    };
  })();

  map.style.transition = 'none';
  render();
  void map.offsetWidth;
  map.style.transition = '';
})();
