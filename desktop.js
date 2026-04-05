/* ══════════════════════════════════════
   AJMAL ALI — DESKTOP JS
══════════════════════════════════════ */

/* ── Falling leaves ── */
const emojis = ['🍂','🍁','🍃','🌿'];
const lc = document.getElementById('lc');
for (let i = 0; i < 20; i++) {
  const l = document.createElement('div');
  l.className = 'leaf';
  l.textContent = emojis[Math.floor(Math.random() * emojis.length)];
  l.style.cssText = `left:${Math.random()*100}%;font-size:${1+Math.random()*1.2}rem;animation-duration:${12+Math.random()*18}s;animation-delay:${-Math.random()*28}s;`;
  lc.appendChild(l);
}

/* ── Page system ── */
function goPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  document.querySelectorAll('.nav-links a').forEach(a => a.classList.toggle('active', a.dataset.page === name));
  window.scrollTo({ top: 0, behavior: 'instant' });
  setTimeout(() => { initReveal(); initBars(); }, 100);
}

/* ── Reveal on scroll ── */
function initReveal() {
  const els = document.querySelectorAll('.page.active .reveal,.page.active .reveal-l,.page.active .reveal-r');
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('up'); io.unobserve(e.target); } });
  }, { threshold: .1 });
  els.forEach(el => { if (!el.classList.contains('up')) io.observe(el); });
}

/* ── Skill bars ── */
function initBars() {
  document.querySelectorAll('.page.active .sb-fill').forEach(b => {
    b.style.width = '0';
    setTimeout(() => { b.style.width = b.dataset.pct + '%'; }, 250);
  });
}

/* ── Contact form ── */
function sendMsg() {
  const n = document.getElementById('cf-name').value.trim();
  const e = document.getElementById('cf-email').value.trim();
  const s = document.getElementById('cf-subject').value.trim();
  const m = document.getElementById('cf-msg').value.trim();
  if (!n || !e || !m) { showToast('Please fill in all required fields.'); return; }
  window.location.href = 'mailto:ajmalsworkshop@gmail.com?subject=' + encodeURIComponent(s || 'Portfolio Enquiry — ' + n) + '&body=' + encodeURIComponent('Name: ' + n + '\nEmail: ' + e + '\n\n' + m);
  showToast('Opening your email client…');
}
function showToast(msg) {
  const t = document.getElementById('toast');
  document.getElementById('toast-msg').textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3200);
}

/* ═══════════════════════
   EASTER EGGS
═══════════════════════ */
function showEgg(icon, msg, dur) {
  dur = dur || 3000;
  const et = document.getElementById('egg-toast');
  document.getElementById('egg-icon').textContent = icon;
  document.getElementById('egg-msg').textContent = msg;
  et.classList.add('show');
  setTimeout(() => et.classList.remove('show'), dur);
}

// 1. Konami Code
const konami = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
let kIdx = 0;
document.addEventListener('keydown', function(e) {
  if (e.key === konami[kIdx]) { kIdx++; } else { kIdx = 0; }
  if (kIdx === konami.length) {
    kIdx = 0;
    showEgg('🎮','Konami Code! You clearly know your classics.', 4000);
    for (let i = 0; i < 30; i++) {
      const m = document.createElement('div');
      m.textContent = emojis[Math.floor(Math.random() * emojis.length)];
      m.style.cssText = 'position:fixed;z-index:9997;pointer-events:none;font-size:'+(1.5+Math.random()*2)+'rem;left:'+(Math.random()*100)+'%;top:'+(Math.random()*60)+'vh;animation:matrixFall '+(0.5+Math.random()*0.8)+'s ease-out forwards;animation-delay:'+(Math.random()*0.5)+'s;opacity:1;';
      document.body.appendChild(m);
      setTimeout(() => m.remove(), 1400);
    }
  }
});

// 2. Autumn vibes cell
const eggCell = document.getElementById('egg-cell');
if (eggCell) eggCell.addEventListener('click', () => showEgg('☕','Warm like milk tea on an October morning.', 3500));

// 3. Triple-click headline
let hClicks = 0, hTimer;
const hl = document.getElementById('home-headline');
if (hl) hl.addEventListener('click', function() {
  hClicks++;
  clearTimeout(hTimer);
  hTimer = setTimeout(() => { hClicks = 0; }, 700);
  if (hClicks >= 3) {
    hClicks = 0;
    hl.classList.add('shake');
    setTimeout(() => hl.classList.remove('shake'), 800);
    showEgg('✨','Triple click! The headline shook with excitement.', 2800);
  }
});

// 4. Type "boba"
let typed = '';
document.addEventListener('keypress', function(e) {
  typed = (typed + e.key).slice(-4);
  if (typed === 'boba') { showEgg('🧋','You typed BOBA — a true connoisseur!', 3200); typed = ''; }
});

// 5. Alt+click nav logo
document.querySelector('.nav-logo').addEventListener('click', function(e) {
  if (e.altKey) {
    document.body.style.transition = 'filter .3s';
    document.body.style.filter = 'invert(1) hue-rotate(180deg)';
    showEgg('🌙','Alt-click: spooky mode for 1 second!', 1800);
    setTimeout(() => { document.body.style.filter = 'none'; }, 1000);
  }
});

// 6. Gold cursor trail (home only)
const trail = [];
for (let i = 0; i < 8; i++) {
  const d = document.createElement('div');
  const sz = 7 - i * 0.6;
  d.className = 'cursor-dot';
  d.style.cssText = `width:${sz}px;height:${sz}px;`;
  document.body.appendChild(d);
  trail.push({ el: d, x: 0, y: 0 });
}
let mx = 0, my = 0;
document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });
(function animate() {
  const onHome = document.getElementById('page-home').classList.contains('active');
  trail.forEach((t, i) => {
    const prev = i === 0 ? { x: mx, y: my } : trail[i-1];
    t.x += (prev.x - t.x) * 0.35;
    t.y += (prev.y - t.y) * 0.35;
    t.el.style.left = t.x + 'px';
    t.el.style.top = t.y + 'px';
    t.el.style.opacity = onHome ? (0.5 - i * 0.055).toFixed(2) : '0';
  });
  requestAnimationFrame(animate);
})();

// 7. 7 bento cards fast
let bClicks = 0, bTimer;
document.querySelectorAll('.bc').forEach(bc => {
  bc.addEventListener('click', () => {
    bClicks++;
    clearTimeout(bTimer);
    bTimer = setTimeout(() => { bClicks = 0; }, 2000);
    if (bClicks === 7) { bClicks = 0; showEgg('🤯','7 cards in 2s — you are a speed-clicker!', 3000); }
  });
});

/* ── Init ── */
initReveal();
initBars();
