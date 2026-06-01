/* Road Map — shared behavior for all study guide pages */

function switchPillar(index) {
  document.querySelectorAll('.pillar-tab').forEach((tab, i) => {
    tab.classList.toggle('active', i === index);
  });
  document.querySelectorAll('.pillar-panel').forEach((panel, i) => {
    panel.classList.toggle('active', i === index);
  });
}

function toggleCode(btn) {
  const el = btn.nextElementSibling;
  if (!el) return;
  el.classList.toggle('open');
  btn.textContent = el.classList.contains('open') ? 'إخفاء الكود ↑' : 'عرض الكود ↓';
}

function toggleNav() {
  document.getElementById('sidenav')?.classList.toggle('open');
  document.getElementById('navBackdrop')?.classList.toggle('open');
}

function closeNav() {
  document.getElementById('sidenav')?.classList.remove('open');
  document.getElementById('navBackdrop')?.classList.remove('open');
}

function updateReadingProgress() {
  const bar = document.getElementById('progress') || document.getElementById('reading-progress');
  if (!bar) return;
  const max = document.documentElement.scrollHeight - window.innerHeight;
  const scrolled = max > 0 ? window.scrollY / max : 0;
  bar.style.transform = `scaleX(${scrolled})`;
}

function initScrollProgress() {
  window.addEventListener('scroll', updateReadingProgress, { passive: true });
  updateReadingProgress();
}

function initActiveNav() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');
  if (!sections.length || !navLinks.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((link) => {
          link.classList.toggle('active', link.getAttribute('href') === '#' + entry.target.id);
        });
      });
    },
    { rootMargin: '-30% 0px -60% 0px' }
  );

  sections.forEach((section) => observer.observe(section));
}

function initMobileNav() {
  document.querySelectorAll('.nav-link').forEach((link) => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 900) closeNav();
    });
  });
}

function initSmoothAnchors() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const href = anchor.getAttribute('href');
      if (!href || href === '#') return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initScrollProgress();
  initActiveNav();
  initMobileNav();
  initSmoothAnchors();
});
