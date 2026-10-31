(() => {
  const status = document.getElementById('availability-status');
  const buttons = [...document.querySelectorAll('.slot-choices [data-session]')];
  if (!status || buttons.length === 0) return;

  const staleMessage = 'Availability figures need updating. Please check TryBooking for current availability.';
  const unavailableMessage = 'Availability could not be checked. Please check TryBooking for current availability.';
  const maxAge = 24 * 60 * 60 * 1000;

  fetch('/availability.json', { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Availability request failed: ${response.status}`);
      return response.json();
    })
    .then((data) => {
      const updatedAt = Date.parse(data.updatedAt);
      const age = Date.now() - updatedAt;
      const sessionIds = buttons.map((button) => button.dataset.session);
      const hasAllCounts = sessionIds.every((id) => {
        const remaining = data.sessions?.[id]?.remaining;
        return remaining === null || (Number.isInteger(remaining) && remaining >= 0 && remaining <= 35);
      });

      if (!Number.isFinite(updatedAt) || age < 0 || age > maxAge || !hasAllCounts) {
        status.textContent = staleMessage;
        return;
      }

      buttons.forEach((button) => {
        const remaining = data.sessions[button.dataset.session].remaining;
        if (remaining === null || remaining > 15) return;

        const badge = document.createElement('span');
        badge.className = 'availability-badge';
        badge.textContent = remaining === 0
          ? 'Fully booked'
          : `Only ${remaining} headset${remaining === 1 ? '' : 's'} remaining`;
        button.append(' ', badge);
      });

      const timestamp = new Intl.DateTimeFormat('en-GB', {
        dateStyle: 'medium',
        timeStyle: 'short',
        timeZone: 'UTC',
      }).format(updatedAt);
      status.textContent = `Availability last updated ${timestamp} UTC. Confirm your place on TryBooking.`;
    })
    .catch(() => {
      status.textContent = unavailableMessage;
    });
})();
