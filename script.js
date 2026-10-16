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
