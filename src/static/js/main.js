/**
 * production-grade-devops-platform — Main Application JavaScript
 * Author  : Shivam Gadilkar
 * Version : 1.0.0
 *
 * Modules:
 *  1. Scroll-reveal (IntersectionObserver)
 *  2. Animated counters
 *  3. Architecture diagram pulse animation
 *  4. Tech card tilt micro-interaction
 *  5. Live status polling (/health)
 *  6. API endpoint link copy
 *  7. Navigation active-link tracker
 */

'use strict';

/* ============================================================================
   1. Scroll-reveal
   ========================================================================== */
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
);

document.querySelectorAll('.reveal').forEach((el) => revealObserver.observe(el));

/* ============================================================================
   2. Animated Counters
   ========================================================================== */

/**
 * Animate a numeric counter from 0 to its target value.
 *
 * @param {HTMLElement} el     - The element whose text content is updated.
 * @param {number}      target - Final numeric value.
 * @param {number}      [duration=1800] - Animation duration in ms.
 */
function animateCounter(el, target, duration = 1800) {
  const start = performance.now();
  const easeOut = (t) => 1 - Math.pow(1 - t, 3); // cubic ease-out

  const tick = (now) => {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const current = Math.round(easeOut(progress) * target);
    el.textContent = current.toLocaleString();
    if (progress < 1) requestAnimationFrame(tick);
  };

  requestAnimationFrame(tick);
}

const counterObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.dataset.target, 10);
      if (!isNaN(target)) animateCounter(el, target);
      counterObserver.unobserve(el);
    });
  },
  { threshold: 0.5 }
);

document.querySelectorAll('[data-counter]').forEach((el) => counterObserver.observe(el));

/* ============================================================================
   3. Architecture Diagram — cascading pulse animation
   ========================================================================== */
(function initArchAnimation() {
  const nodes = document.querySelectorAll('.arch-node');
  if (!nodes.length) return;

  let activeIndex = 0;
  const INTERVAL = 900; // ms between each node lighting up

  function pulse() {
    nodes.forEach((n) => n.classList.remove('arch-node--active'));
    nodes[activeIndex].classList.add('arch-node--active');
    activeIndex = (activeIndex + 1) % nodes.length;
  }

  // Inject active style dynamically so it doesn't override theme colours
  const style = document.createElement('style');
  style.textContent = `
    .arch-node--active {
      border-color: rgba(59,130,246,0.8) !important;
      box-shadow: 0 0 24px rgba(59,130,246,0.35) !important;
    }
  `;
  document.head.appendChild(style);

  pulse();
  setInterval(pulse, INTERVAL);
})();

/* ============================================================================
   4. Tech-card 3-D tilt micro-interaction
   ========================================================================== */
(function initTilt() {
  const MAX_TILT = 8; // degrees

  document.querySelectorAll('.tech-card').forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = (e.clientX - cx) / (rect.width / 2);
      const dy = (e.clientY - cy) / (rect.height / 2);
      const rotX = (-dy * MAX_TILT).toFixed(2);
      const rotY = (dx * MAX_TILT).toFixed(2);
      card.style.transform = `translateY(-4px) rotateX(${rotX}deg) rotateY(${rotY}deg)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });
})();

/* ============================================================================
   5. Live status polling — fetch /health every 30 s
   ========================================================================== */
(function initStatusPoller() {
  const statusMap = {
    'status-backend':  (d) => d.status === 'healthy' ? 'Running' : 'Degraded',
    'status-env':      (d) => d.environment,
    'status-uptime':   (d) => `${d.uptime_seconds}s`,
    'status-python':   (d) => d.python_version,
  };

  async function poll() {
    try {
      const res = await fetch('/health', { cache: 'no-store' });
      if (!res.ok) return;
      const data = await res.json();

      Object.entries(statusMap).forEach(([id, fn]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = fn(data);
      });

      // Light up the "live" badge
      const liveDot = document.querySelector('.badge__dot');
      if (liveDot) liveDot.style.background = '#10b981';
    } catch (_) {
      // Silently ignore network errors in demo environments
    }
  }

  poll();
  setInterval(poll, 30_000);
})();

/* ============================================================================
   6. API row — click to open in new tab + copy feedback
   ========================================================================== */
(function initApiRows() {
  document.querySelectorAll('.api-row[data-href]').forEach((row) => {
    row.addEventListener('click', (e) => {
      e.preventDefault();
      const href = row.dataset.href;
      window.open(href, '_blank', 'noopener,noreferrer');
    });

    // Keyboard accessibility
    row.setAttribute('role', 'link');
    row.setAttribute('tabindex', '0');
    row.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        window.open(row.dataset.href, '_blank', 'noopener,noreferrer');
      }
    });
  });
})();

/* ============================================================================
   7. Navigation — highlight active section on scroll
   ========================================================================== */
(function initNavHighlight() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.topnav__link[href^="#"]');
  if (!sections.length || !navLinks.length) return;

  const sectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const id = entry.target.id;
        navLinks.forEach((link) => {
          link.classList.toggle(
            'topnav__link--active',
            link.getAttribute('href') === `#${id}`
          );
        });
      });
    },
    { threshold: 0.4 }
  );

  sections.forEach((s) => sectionObserver.observe(s));

  // Inject active style
  const style = document.createElement('style');
  style.textContent = `.topnav__link--active { color: var(--text-primary) !important; }`;
  document.head.appendChild(style);
})();

/* ============================================================================
   8. Smooth scroll for anchor links
   ========================================================================== */
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

/* ============================================================================
   9. "Copy endpoint" on API path click
   ========================================================================== */
(function initCopyPath() {
  document.querySelectorAll('.api-path').forEach((el) => {
    el.style.cursor = 'pointer';
    el.title = 'Click to copy';

    el.addEventListener('click', async (e) => {
      e.stopPropagation();
      const path = el.textContent.trim();
      const full = `${location.origin}${path}`;
      try {
        await navigator.clipboard.writeText(full);
        const original = el.textContent;
        el.textContent = '✓ Copied!';
        el.style.color = 'var(--color-success)';
        setTimeout(() => {
          el.textContent = original;
          el.style.color = '';
        }, 1500);
      } catch (_) {
        // clipboard not available (non-https / browser policy)
      }
    });
  });
})();

/* ============================================================================
   10. Console branding (Easter egg for devs who open DevTools)
   ========================================================================== */
(function consoleBrand() {
  const styles = [
    'color: #3b82f6; font-size: 18px; font-weight: 800;',
    'color: #94a3b8; font-size: 12px;',
    'color: #10b981; font-size: 12px; font-weight: 600;',
  ];
  /* eslint-disable no-console */
  console.log('%c☁ production-grade-devops-platform', styles[0]);
  console.log('%cMulti-Environment CI/CD Platform with Kubernetes, GitOps & Cloud Automation', styles[1]);
  console.log('%c✦ Built by Shivam Gadilkar — DevSecOps Engineer', styles[2]);
  console.log('%cAPI Endpoints: /health  /info  /version  /metrics  /tech-stack  /developer', styles[1]);
  /* eslint-enable no-console */
})();
