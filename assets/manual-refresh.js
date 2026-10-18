// Local content carousel: shuffled on each visit, with native touch scrolling.
for (const track of document.querySelectorAll('.manual-moments')) {
  if (track.dataset.carouselReady) continue;
  track.dataset.carouselReady = 'true';
  const cards = [...track.children];
  for (let i = cards.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [cards[i], cards[j]] = [cards[j], cards[i]];
  }
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
