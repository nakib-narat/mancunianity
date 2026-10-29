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
    music.setStep(index);
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
    musicBtn.setAttribute('aria-pressed', String(on));
    musicBtn.innerHTML = on ? '&#9835; Music on' : '&#9835; Music off';
    if (on) music.setStep(index);
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

  /* Music: plays audio/walk-theme.mp3 if that file exists, otherwise a gentle
     generated soundtrack whose key and mood change from stop to stop. */
  const music = (function () {
    const MOODS = [
      { root: 50, scale: [0, 2, 4, 7, 9] },
      { root: 55, scale: [0, 2, 4, 7, 9] },
      { root: 52, scale: [0, 3, 5, 7, 10] },
      { root: 57, scale: [0, 2, 4, 7, 9] },
      { root: 50, scale: [0, 3, 5, 7, 10] },
      { root: 48, scale: [0, 2, 4, 7, 9] },
      { root: 55, scale: [0, 2, 4, 7, 9] },
      { root: 52, scale: [0, 2, 4, 7, 9] },
      { root: 55, scale: [0, 2, 4, 7, 9] },
      { root: 50, scale: [0, 2, 4, 7, 9] }
    ];
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    let ctx = null;
    let master = null;
    let send = null;
    let pad = null;
    let arpTimer = null;
    let mood = MOODS[0];
    let theme = null;
    let themeState = 'unknown';
    let wanted = false;

    const hz = m => 440 * Math.pow(2, (m - 69) / 12);

    function setup() {
      if (ctx || !AudioCtx) return;
      ctx = new AudioCtx();
      master = ctx.createGain();
      master.gain.value = 0;
      master.connect(ctx.destination);
      const delay = ctx.createDelay(1);
      delay.delayTime.value = 0.42;
      const feedback = ctx.createGain();
      feedback.gain.value = 0.38;
      send = ctx.createGain();
      send.gain.value = 0.5;
      send.connect(delay);
      delay.connect(feedback);
      feedback.connect(delay);
      delay.connect(master);
    }

    function startPad(m) {
      const t = ctx.currentTime;
      const bus = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 900;
      bus.gain.setValueAtTime(0, t);
      bus.gain.linearRampToValueAtTime(0.16, t + 3);
      bus.connect(filter);
      filter.connect(master);
      const oscs = [0, 7, 12, 16].map((semi, i) => {
        const o = ctx.createOscillator();
        o.type = i === 0 ? 'sine' : 'triangle';
        o.frequency.value = hz(m.root + semi - (i === 0 ? 12 : 0));
        o.detune.value = (i - 1.5) * 4;
        o.connect(bus);
        o.start(t);
        return o;
      });
      return { bus, oscs };
    }

    function stopPad(p) {
      if (!p) return;
      const t = ctx.currentTime;
      p.bus.gain.cancelScheduledValues(t);
      p.bus.gain.setValueAtTime(p.bus.gain.value, t);
      p.bus.gain.linearRampToValueAtTime(0, t + 2.5);
      p.oscs.forEach(o => o.stop(t + 2.6));
    }

    function pluck(freq) {
      const t = ctx.currentTime;
      const g = ctx.createGain();
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(0.2, t + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0008, t + 2.2);
      g.connect(master);
      g.connect(send);
      [[1, 'sine', 1], [2, 'triangle', 0.25]].forEach(([mult, type, amp]) => {
        const o = ctx.createOscillator();
        const og = ctx.createGain();
        o.type = type;
        o.frequency.value = freq * mult;
        og.gain.value = amp;
        o.connect(og);
        og.connect(g);
        o.start(t);
        o.stop(t + 2.3);
      });
    }

    let pos = 2;
    function arp() {
      if (Math.random() < 0.3) return;
      pos = Math.max(0, Math.min(mood.scale.length * 2 - 1, pos + [-2, -1, 1, 2][Math.floor(Math.random() * 4)]));
      const octave = Math.floor(pos / mood.scale.length);
      const degree = mood.scale[pos % mood.scale.length];
      pluck(hz(mood.root + 24 + degree + octave * 12));
    }

    function startSynth() {
      setup();
      if (!ctx) return;
      ctx.resume();
      master.gain.cancelScheduledValues(ctx.currentTime);
      master.gain.linearRampToValueAtTime(0.7, ctx.currentTime + 2);
      if (!pad) pad = startPad(mood);
      if (!arpTimer) arpTimer = setInterval(arp, 560);
    }

    function stopSynth() {
      if (!ctx) return;
      master.gain.cancelScheduledValues(ctx.currentTime);
      master.gain.linearRampToValueAtTime(0, ctx.currentTime + 1);
      clearInterval(arpTimer);
      arpTimer = null;
      const old = pad;
      pad = null;
      setTimeout(() => stopPad(old), 1100);
    }

    function startTheme() {
      if (!theme) {
        theme = new Audio('audio/walk-theme.mp3');
        theme.loop = true;
        theme.volume = 0.7;
        theme.addEventListener('error', () => {
          themeState = 'none';
          if (wanted) startSynth();
        });
        theme.addEventListener('playing', () => { themeState = 'ok'; });
      }
      const p = theme.play();
      if (p && p.catch) p.catch(() => {});
      setTimeout(() => {
        if (wanted && themeState === 'unknown') { theme.pause(); themeState = 'none'; startSynth(); }
      }, 2500);
    }

    return {
      enabled: false,
      toggle(on) {
        this.enabled = on;
        wanted = on;
        if (on) {
          if (themeState === 'none') startSynth(); else startTheme();
        } else {
          if (theme) theme.pause();
          stopSynth();
        }
      },
      setStep(i) {
        mood = MOODS[Math.min(i, MOODS.length - 1)];
        if (!wanted || !ctx || !pad) return;
        const old = pad;
        pad = startPad(mood);
        stopPad(old);
      }
    };
  })();

  map.style.transition = 'none';
  render();
  void map.offsetWidth;
  map.style.transition = '';
})();
