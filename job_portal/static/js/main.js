// Job Portal — Main JavaScript
'use strict';

// ── Dark Mode Toggle ───────────────────────────────────────────────────────
const themeToggle = document.getElementById('themeToggle');
const themeIcon   = document.getElementById('themeIcon');
const savedTheme  = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
if (savedTheme === 'dark' && themeIcon) themeIcon.className = 'bi bi-sun-fill';

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next    = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    if (themeIcon) themeIcon.className = next === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
  });
}

// ── Navbar scroll effect ──────────────────────────────────────────────────
const nav = document.getElementById('mainNav');
if (nav) {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 20);
  });
}

// ── Auto-dismiss alerts ───────────────────────────────────────────────────
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
    if (bsAlert) bsAlert.close();
  }, 5000);
});

// ── OTP input: only digits ────────────────────────────────────────────────
document.querySelectorAll('.otp-input').forEach(input => {
  input.addEventListener('input', e => {
    e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
  });
});

// ── CSRF helper for fetch ─────────────────────────────────────────────────
function getCookie(name) {
  const c = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return c ? decodeURIComponent(c[1]) : null;
}
window.csrfToken = getCookie('csrftoken');


window.addEventListener('load', () => {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('d-none');
    }
});