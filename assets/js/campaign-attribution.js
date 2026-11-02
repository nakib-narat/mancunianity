(() => {
  const utmKeys = [
    'utm_source',
    'utm_medium',
    'utm_campaign',
    'utm_content',
    'utm_term',
  ];
  const values = {};
  const searchParams = new URLSearchParams(window.location.search);

  utmKeys.forEach((key) => {
    const rawValue = searchParams.get(key);
    if (!rawValue) return;

    const value = rawValue
      .toLowerCase()
      .replace(/[^a-z0-9_-]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 24);
    if (value) values[key] = value;
  });

  if (Object.keys(values).length === 0) return;

  document.querySelectorAll('a[href]').forEach((link) => {
    let url;
    try {
      url = new URL(link.href, window.location.href);
    } catch {
      return;
    }

    if (url.origin === window.location.origin) {
      utmKeys.forEach((key) => {
        if (values[key] && !url.searchParams.has(key)) {
          url.searchParams.set(key, values[key]);
        }
      });
      link.href = url.href;
      return;
    }

    if (url.hostname !== 'www.trybooking.com' || url.searchParams.has('track')) return;

    const trackingParts = [
      values.utm_source || 'website',
      values.utm_medium || 'referral',
      values.utm_campaign || 'unspecified',
      values.utm_content,
      link.dataset.session ? `session-${link.dataset.session}` : '',
    ].filter(Boolean);

    url.searchParams.set('track', trackingParts.join('-'));
    link.href = url.href;
  });
})();
