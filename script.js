document.querySelectorAll('[data-year]').forEach(e=>e.textContent=new Date().getFullYear());
(function(){
  const nav=document.querySelector('.menu');
  if(!nav || nav.querySelector('a[href="stories-learning.html"]')) return;
  const link=document.createElement('a');
  link.href='stories-learning.html'; link.textContent='Stories & Learning';
  if(location.pathname.endsWith('/stories-learning.html') || location.pathname.endsWith('/resource-standards.html') || location.pathname.includes('/learning-pack-')) link.setAttribute('aria-current','page');
  const walks=[...nav.querySelectorAll('a')].find(a=>a.getAttribute('href')==='walks.html');
  if(walks) walks.insertAdjacentElement('afterend',link); else nav.appendChild(link);
})();

(function(){
  const walks=document.querySelector('.header a[href="walks.html"]');
  if(!walks || document.querySelector('.header a[href="walk.html"]')) return;
  const link=document.createElement('a');
  link.href='walk.html'; link.textContent='Virtual Walk';
  walks.insertAdjacentElement('afterend',link);
})();


// Cloudflare Web Analytics: aggregate website usage.
(function(){
  if (document.querySelector('script[data-cf-beacon]')) return;
  const beacon=document.createElement('script');
  beacon.type='module';
  beacon.src='https://static.cloudflareinsights.com/beacon.min.js';
  beacon.setAttribute('data-cf-beacon', '{"token":"df1b1ab518564dd49638f7cf85120946"}');
  document.head.appendChild(beacon);
})();
