// Rotate the manually selected moments without accounts or remote services.
for (const grid of document.querySelectorAll('.manual-moments')) {
 const cards = [...grid.children];
 for (let i=cards.length-1;i>0;i--) { const j=Math.floor(Math.random()*(i+1)); [cards[i],cards[j]]=[cards[j],cards[i]]; }
 grid.append(...cards);
}
