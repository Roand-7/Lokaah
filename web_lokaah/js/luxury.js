/**
 * LOKAAH — Luxury Landing Page JavaScript
 * Scroll-triggered reveals, smooth interactions, premium feel
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initMobileMenu();
    initScrollReveal();
    initHeroWordReveal();
    initFAQ();
    initSmoothScroll();
});

/* ---- Navbar ---- */
function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    let lastY = 0;

    window.addEventListener('scroll', () => {
        const y = window.pageYOffset;

        if (y > 60) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Hide on scroll down, show on scroll up
        if (y > lastY && y > 120) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }

        lastY = y;
    }, { passive: true });
}

/* ---- Mobile Menu ---- */
function initMobileMenu() {
    const toggle = document.getElementById('mobileToggle');
    const links = document.getElementById('navLinks');
    if (!toggle || !links) return;

    toggle.addEventListener('click', () => {
        links.classList.toggle('open');
        const spans = toggle.querySelectorAll('span');
        if (links.classList.contains('open')) {
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
        } else {
            spans[0].style.transform = '';
            spans[1].style.opacity = '';
            spans[2].style.transform = '';
        }
    });

    links.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            links.classList.remove('open');
            const spans = toggle.querySelectorAll('span');
            spans[0].style.transform = '';
            spans[1].style.opacity = '';
            spans[2].style.transform = '';
        });
    });
}

/* ---- Scroll Reveal (IntersectionObserver) ---- */
function initScrollReveal() {
    const reveals = document.querySelectorAll('.reveal, .stagger-children');
    if (!reveals.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -60px 0px'
    });

    reveals.forEach(el => observer.observe(el));
}

/* ---- Hero Word-by-Word Reveal ---- */
function initHeroWordReveal() {
    const title = document.getElementById('heroTitle');
    if (!title) return;

    // Split text into words and wrap each
    const lines = title.querySelectorAll('.line');
    lines.forEach(line => {
        const html = line.innerHTML;
        // Check for accent span
        if (line.querySelector('.accent')) {
            const accent = line.querySelector('.accent');
            const words = accent.textContent.trim().split(/\s+/);
            accent.innerHTML = words.map((w, i) =>
                `<span class="word" style="transition-delay: ${(i + 2) * 0.08}s">${w}</span>`
            ).join(' ');
        } else {
            const text = line.textContent.trim();
            const words = text.split(/\s+/);
            line.innerHTML = words.map((w, i) =>
                `<span class="word" style="transition-delay: ${i * 0.08}s">${w}</span>`
            ).join(' ');
        }
    });

    // Trigger animation after a short delay
    setTimeout(() => {
        title.classList.add('animate');
    }, 300);
}

/* ---- FAQ Accordion ---- */
function initFAQ() {
    const items = document.querySelectorAll('.faq-item');
    items.forEach(item => {
        const btn = item.querySelector('.faq-q');
        btn.addEventListener('click', () => {
            const isOpen = item.classList.contains('open');
            // Close all
            items.forEach(i => i.classList.remove('open'));
            // Toggle current
            if (!isOpen) item.classList.add('open');
        });
    });
}

/* ---- Smooth Scroll ---- */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const href = anchor.getAttribute('href');
            if (href === '#') return;
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
}
