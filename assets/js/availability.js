(() => {
  const status = document.getElementById('availability-status');
  const buttons = [...document.querySelectorAll('.slot-choices [data-session]')];
  if (!status || buttons.length === 0) return;

  const staleMessage = 'Availability figures need updating. Please check TryBooking for current availability.';
  const unavailableMessage = 'Availability could not be checked. Please check TryBooking for current availability.';
  const maxAge = 24 * 60 * 60 * 1000;
  const performanceStatuses = {
    available: 'Available',
    sold_out: 'Sold out',
    cancelled: 'Cancelled',
    rescheduled: 'Rescheduled',
    completed: 'Completed',
  };
  const noticeTypes = new Set([
    'severe_weather',
    'meeting_point_change',
    'delayed_start',
    'cancelled_performance',
  ]);
  const notice = document.getElementById('event-urgent-notice');

  function showUrgentNotice(value) {
    if (!notice || !value || !noticeTypes.has(value.type)) return;
    if (
      typeof value.performance !== 'string' ||
      typeof value.message !== 'string' ||
      typeof value.actionText !== 'string' ||
      typeof value.actionUrl !== 'string' ||
      !value.performance.trim() ||
      !value.message.trim() ||
      !value.actionText.trim()
    ) return;

    const updatedAt = Date.parse(value.updatedAt);
    const actionUrl = new URL(value.actionUrl, location.origin);
    if (!Number.isFinite(updatedAt) || updatedAt > Date.now()) return;
    if (actionUrl.origin !== location.origin && actionUrl.href !== 'https://www.trybooking.com/uk/HEFF') return;

    const updated = notice.querySelector('[data-updated]');
    updated.dateTime = new Date(updatedAt).toISOString();
    updated.textContent = new Intl.DateTimeFormat('en-GB', {
      dateStyle: 'medium',
      timeStyle: 'short',
      timeZone: 'Europe/London',
    }).format(updatedAt);
    notice.querySelector('[data-performance]').textContent = value.performance;
    notice.querySelector('[data-message]').textContent = value.message;
    const action = notice.querySelector('[data-action]');
    action.href = actionUrl.href;
    action.textContent = value.actionText;
    notice.hidden = false;
  }

  fetch('/availability.json', { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Availability request failed: ${response.status}`);
      return response.json();
    })
    .then((data) => {
      showUrgentNotice(data.urgentNotice);
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
        const session = data.sessions[button.dataset.session];
        const hasSessionStatus = Object.prototype.hasOwnProperty.call(performanceStatuses, session.status);
        if (hasSessionStatus) {
          const badge = document.createElement('span');
          badge.className = 'session-status-badge';
          badge.textContent = `Performance status: ${performanceStatuses[session.status]}`;
          button.append(' ', badge);
          return;
        }

        const remaining = session.remaining;
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
      const hasAvailabilityCounts = sessionIds.some((id) => data.sessions[id].remaining !== null);
      status.textContent = hasAvailabilityCounts
        ? `Availability last updated ${timestamp} UTC. Confirm your place on TryBooking.`
        : `Performance statuses last updated ${timestamp} UTC. Confirm ticket availability on TryBooking.`;
    })
    .catch(() => {
      status.textContent = unavailableMessage;
    });
})();
