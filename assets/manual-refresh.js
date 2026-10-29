// Feed cards use the same approved local records as the wall. Source failure keeps static cards.
function initializeMoments(){
// Local content carousel: shuffled on each visit, with native touch scrolling.
for (const track of document.querySelectorAll('.manual-moments')) {
  if (track.dataset.carouselReady) continue;
  track.dataset.carouselReady = 'true';
  const cards = [...track.children];

  track.append(...cards);
  track.id ||= 'khyber-moments-' + [...document.querySelectorAll('.manual-moments')].indexOf(track);
  track.tabIndex = 0;
  track.setAttribute('role', 'region');
  track.setAttribute('aria-roledescription', 'carousel');
  track.setAttribute('aria-label', 'A little more Khyber. Use arrow keys or swipe to browse.');
  cards.forEach((card, i) => {
    card.setAttribute('role', 'group');
    card.setAttribute('aria-roledescription', 'slide');
    card.setAttribute('aria-label', `${i + 1} of ${cards.length}`);
  });

  const controls = document.createElement('div');
  controls.className = 'moments-controls';
  const previous = document.createElement('button');
  const next = document.createElement('button');
  const status = document.createElement('span');
  status.className = 'moments-status';
  status.setAttribute('aria-live', 'polite');
  status.setAttribute('aria-atomic', 'true');
  for (const [button, label, symbol] of [[previous, 'Previous Khyber moment', '←'], [next, 'Next Khyber moment', '→']]) {
    button.type = 'button';
    button.className = 'moments-arrow';
    button.setAttribute('aria-label', label);
    button.setAttribute('aria-controls', track.id);
    button.textContent = symbol;
  }
  controls.append(previous, status, next);
  track.before(controls);

  function positions() {
    const origin = track.getBoundingClientRect().left;
    return cards.map(card => card.getBoundingClientRect().left - origin + track.scrollLeft);
  }
  function update() {
    const max = Math.max(0, track.scrollWidth - track.clientWidth);
    previous.disabled = track.scrollLeft <= 2;
    next.disabled = track.scrollLeft >= max - 2;
    const origin = track.getBoundingClientRect().left;
    const visible = cards.map((card, i) => ({i, rect: card.getBoundingClientRect()}))
      .filter(({rect}) => rect.right > origin + 8 && rect.left < origin + track.clientWidth - 8);
    const text = visible.length ? `${visible[0].i + 1}–${visible.at(-1).i + 1} of ${cards.length}` : `${cards.length} moments`;
    if (status.textContent !== text) status.textContent = text;
  }
  function move(direction) {
    const targets = positions();
    const current = track.scrollLeft;
    const target = direction > 0 ? targets.find(x => x > current + 4) : targets.reverse().find(x => x < current - 4);
    track.scrollTo({left: target ?? (direction > 0 ? track.scrollWidth : 0), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
  }
  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  track.addEventListener('keydown', event => {
    if (event.target !== track) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      move(event.key === 'ArrowRight' ? 1 : -1);
    }
  });
  let timer;
  track.addEventListener('scroll', () => { clearTimeout(timer); timer = setTimeout(update, 120); }, {passive: true});
  if ('ResizeObserver' in window) new ResizeObserver(update).observe(track);
  else window.addEventListener('resize', update);
  update();
}

}
fetch('/assets/community-content.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('Feed unavailable');return r.json()}).then(data=>{
 const isSurrey=location.pathname.startsWith('/grill');
 const now=new Date().toISOString().slice(0,10);
 const photos=(data.photos||[]).filter(p=>p.approved===true&&p.title&&p.image&&p.url&&(!p.expires||p.expires>=now)&&(!isSurrey||!p.location_key||p.location_key==='surrey')).slice().sort((a,b)=>(b.published||'').localeCompare(a.published||'')).slice(0,12);
 document.querySelectorAll('.manual-moments').forEach(track=>{
 const cards=[];
 for(const p of photos){
  let url;try{url=new URL(p.url);if(url.protocol!=='https:')continue}catch{continue}
  const imageUrl=new URL(p.image,new URL('/assets/',location.origin));if(imageUrl.origin!==location.origin||!imageUrl.pathname.startsWith('/assets/'))continue;
  const card=document.createElement('article');card.className='manual-moment';
  const link=document.createElement('a');link.href=url.href;link.target='_blank';link.rel='noopener';
  const image=document.createElement('img');image.src=imageUrl.href;image.alt=p.alt||p.title;image.width=600;image.height=600;image.loading='lazy';link.append(image);
  const body=document.createElement('div');body.className='manual-moment-body';const title=document.createElement('h3');title.textContent=p.title;
  const source=document.createElement('a');source.className='text-link';source.href=url.href;source.target='_blank';source.rel='noopener';source.textContent='@'+p.handle+' · Instagram ↗';
  if(p.published){const date=document.createElement('p');date.className='eyebrow';date.textContent=p.published.slice(0,10);body.append(date)}
  body.append(title,source);card.append(link,body);cards.push(card);
 }
 if(cards.length)track.replaceChildren(...cards);
 });initializeMoments();
}).catch(()=>initializeMoments());
