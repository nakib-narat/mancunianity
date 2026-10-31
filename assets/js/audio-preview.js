document.querySelectorAll('audio[data-preview-seconds]').forEach((player) => {
  const previewSeconds = Number(player.dataset.previewSeconds);
  if (!Number.isFinite(previewSeconds) || previewSeconds <= 0) return;

  player.addEventListener('timeupdate', () => {
    if (player.currentTime >= previewSeconds) {
      player.pause();
      player.currentTime = 0;
    }
  });

  player.addEventListener('seeking', () => {
    if (player.currentTime >= previewSeconds) player.currentTime = 0;
  });

  player.addEventListener('error', () => {
    const note = document.getElementById(player.getAttribute('aria-describedby'));
    if (note) note.textContent = 'Audio is not available right now. You can still explore the photos and read about the experience.';
  });
});
