/* ══════════════════════════════════════
   AJMAL ALI — MOBILE JS
══════════════════════════════════════ */

/* ── Page navigation ── */
function mGoPage(name) {
  document.querySelectorAll('.m-page').forEach(p => p.classList.remove('active'));
  document.getElementById('m-page-' + name).classList.add('active');
  document.querySelectorAll('[data-mpage]').forEach(el => {
    el.classList.toggle('active', el.dataset.mpage === name);
  });
  // close drawer
  document.getElementById('m-drawer').classList.remove('open');
  document.getElementById('m-menu-btn').classList.remove('open');
  window.scrollTo({ top: 0, behavior: 'instant' });
  setTimeout(() => { mInitReveal(); mInitBars(); }, 80);
}

/* ── Hamburger drawer ── */
function mToggleDrawer() {
  const d = document.getElementById('m-drawer');
  const b = document.getElementById('m-menu-btn');
  d.classList.toggle('open');
  b.classList.toggle('open');
}

/* Close drawer when tapping outside */
document.addEventListener('click', function(e) {
  const drawer = document.getElementById('m-drawer');
  const btn = document.getElementById('m-menu-btn');
  if (drawer.classList.contains('open') && !drawer.contains(e.target) && !btn.contains(e.target)) {
    drawer.classList.remove('open');
    btn.classList.remove('open');
  }
});

/* ── Reveal on scroll ── */
function mInitReveal() {
  const els = document.querySelectorAll('.m-page.active .m-reveal');
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('up'); io.unobserve(e.target); }
    });
  }, { threshold: .06 });
  els.forEach(el => { if (!el.classList.contains('up')) io.observe(el); });
}

/* ── Skill bars ── */
function mInitBars() {
  document.querySelectorAll('.m-page.active .m-sb-fill').forEach(b => {
    b.style.width = '0';
    setTimeout(() => { b.style.width = b.dataset.pct + '%'; }, 180);
  });
}

/* ── Toast ── */
function mShowToast(icon, msg, dur) {
  const t = document.getElementById('m-toast');
  t.innerHTML = `<span>${icon}</span><span>${msg}</span>`;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), dur || 2800);
}

/* ── Contact form ── */
function mSendMsg() {
  const n = document.getElementById('m-cf-name').value.trim();
  const e = document.getElementById('m-cf-email').value.trim();
  const s = document.getElementById('m-cf-subject').value.trim();
  const m = document.getElementById('m-cf-msg').value.trim();
  if (!n || !e || !m) { mShowToast('⚠️', 'Please fill in all required fields', 2500); return; }
  window.location.href = 'mailto:ajmalsworkshop@gmail.com?subject=' +
    encodeURIComponent(s || 'Portfolio Enquiry — ' + n) +
    '&body=' + encodeURIComponent('Name: ' + n + '\nEmail: ' + e + '\n\n' + m);
}

/* ══════════════════════
   EASTER EGGS
══════════════════════ */

// 1. Tap autumn stat
document.getElementById('m-egg-stat')?.addEventListener('click', () => {
  mShowToast('☕', 'Warm like milk tea on an October morning 🍂', 3200);
});

// 2. Triple-tap headline
let hc = 0, ht;
document.querySelector('.m-headline')?.addEventListener('click', function() {
  hc++;
  clearTimeout(ht);
  ht = setTimeout(() => { hc = 0; }, 700);
  if (hc >= 3) {
    hc = 0;
    this.style.animation = 'none';
    void this.offsetWidth;
    this.style.animation = 'mShake .6s ease';
    mShowToast('✨', 'Triple tap! Headline went wild 🤪', 2500);
  }
});

// 3. Long press logo
let logoTimer;
document.querySelector('.m-nav-logo')?.addEventListener('touchstart', () => {
  logoTimer = setTimeout(() => mShowToast('🌙', 'Long press unlocked! Secret finder 🔓', 2800), 800);
});
document.querySelector('.m-nav-logo')?.addEventListener('touchend', () => clearTimeout(logoTimer));

// 4. Shake device
if (window.DeviceMotionEvent) {
  let lastShake = 0;
  window.addEventListener('devicemotion', e => {
    const a = e.acceleration;
    if (!a) return;
    const force = Math.abs(a.x||0) + Math.abs(a.y||0) + Math.abs(a.z||0);
    if (force > 38 && Date.now() - lastShake > 3000) {
      lastShake = Date.now();
      mShowToast('📳', 'You shook your phone! Explorer unlocked 🎉', 3000);
    }
  });
}

// 5. Type "boba" (bluetooth keyboard)
let typed = '';
document.addEventListener('keypress', e => {
  typed = (typed + e.key).slice(-4);
  if (typed === 'boba') { mShowToast('🧋', 'BOBA! True connoisseur detected 🧋', 3000); typed = ''; }
});

/* Shake keyframe (injected) */
const style = document.createElement('style');
style.textContent = `
@keyframes mShake {
  0%,100% { transform: none; }
  20% { transform: rotate(-3deg) scale(1.02); }
  40% { transform: rotate(3deg); }
  60% { transform: rotate(-2deg) translateX(-3px); }
  80% { transform: rotate(2deg) translateX(3px); }
}`;
document.head.appendChild(style);

/* ── Init ── */
mInitReveal();
mInitBars();
