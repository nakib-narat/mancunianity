const button=document.querySelector('.menu-button');
const nav=document.querySelector('#site-nav');
if(button&&nav){
  const closeMenu=(returnFocus=false)=>{button.setAttribute('aria-expanded','false');button.textContent='Menu';nav.classList.remove('open');if(returnFocus)button.focus();};
  button.addEventListener('click',()=>{const opening=button.getAttribute('aria-expanded')!=='true';button.setAttribute('aria-expanded',String(opening));button.textContent=opening?'Close menu':'Menu';nav.classList.toggle('open',opening);});
  nav.addEventListener('click',event=>{if(event.target.closest('a'))closeMenu(false);});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&button.getAttribute('aria-expanded')==='true')closeMenu(true);});
  window.matchMedia('(min-width: 66.001rem)').addEventListener('change',event=>{if(event.matches)closeMenu(false);});
}
