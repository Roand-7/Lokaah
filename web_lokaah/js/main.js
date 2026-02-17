/**
 * LOKAAH - Main JavaScript
 * Interactivity and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true,
            offset: 100
        });
    }

    // Navigation scroll effect
    initNavbar();
    
    // Mobile menu
    initMobileMenu();
    
    // FAQ accordion
    initFAQ();
    
    // Pricing toggle
    initPricingToggle();
    
    // Smooth scroll for anchor links
    initSmoothScroll();
    
    // Typing effect for hero chat
    initTypingEffect();
});

/**
 * Navbar scroll effect
 */
function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;
    
    let lastScroll = 0;
    
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        // Add/remove scrolled class
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Hide/show on scroll direction
        if (currentScroll > lastScroll && currentScroll > 100) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;
    }, { passive: true });
}

/**
 * Mobile menu toggle
 */
function initMobileMenu() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    
    if (!menuBtn || !navLinks) return;
    
    menuBtn.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        
        // Toggle icon
        const icon = menuBtn.querySelector('i');
        if (navLinks.classList.contains('active')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        } else {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        }
    });
    
    // Close menu when clicking a link
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            const icon = menuBtn.querySelector('i');
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        });
    });
}

/**
 * FAQ accordion
 */
function initFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', function() {
            const isActive = item.classList.contains('active');
            
            // Close all other items
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle current item
            item.classList.toggle('active');
        });
    });
}

/**
 * Pricing toggle (monthly/yearly)
 */
function initPricingToggle() {
    const toggle = document.getElementById('pricingToggle');
    const prices = document.querySelectorAll('.pricing-price .amount');
    const labels = document.querySelectorAll('.toggle-label');
    
    if (!toggle) return;
    
    toggle.addEventListener('change', function() {
        const isYearly = this.checked;
        
        // Update labels
        labels.forEach((label, index) => {
            if (index === 1) { // Yearly label
                label.classList.toggle('active', isYearly);
            } else {
                label.classList.toggle('active', !isYearly);
            }
        });
        
        // Update prices with animation
        prices.forEach(price => {
            const monthly = price.dataset.monthly;
            const yearly = price.dataset.yearly;
            
            if (monthly && yearly) {
                // Fade out
                price.style.opacity = '0';
                price.style.transform = 'translateY(-10px)';
                
                setTimeout(() => {
                    price.textContent = isYearly ? yearly : monthly;
                    // Fade in
                    price.style.opacity = '1';
                    price.style.transform = 'translateY(0)';
                }, 200);
            }
        });
    });
}

/**
 * Smooth scroll for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                
                const offsetTop = target.offsetTop - 80; // Account for navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Typing effect for hero chat
 */
function initTypingEffect() {
    const chatMessages = document.querySelector('.chat-messages');
    if (!chatMessages) return;
    
    const messages = [
        { type: 'bot', text: 'Hi Rahul! Ready to tackle Quadratic Equations today? 🎯' },
        { type: 'user', text: 'Yes! But I always get confused with the discriminant' },
        { type: 'bot', text: 'No worries! Think of D = b² - 4ac as a "checker"...\n\nD > 0 → 2 different roots\nD = 0 → 1 repeated root\nD < 0 → No real roots' }
    ];
    
    let currentMessage = 0;
    
    function typeNextMessage() {
        if (currentMessage >= messages.length) {
            // Show typing indicator
            const typing = document.querySelector('.typing');
            if (typing) typing.style.display = 'flex';
            return;
        }
        
        const msg = messages[currentMessage];
        const messageEl = chatMessages.children[currentMessage];
        
        if (messageEl) {
            const bubble = messageEl.querySelector('.message-bubble');
            if (bubble) {
                bubble.textContent = '';
                
                let charIndex = 0;
                const text = msg.text;
                
                const typeChar = () => {
                    if (charIndex < text.length) {
                        bubble.textContent += text[charIndex];
                        charIndex++;
                        setTimeout(typeChar, 30);
                    } else {
                        currentMessage++;
                        setTimeout(typeNextMessage, 800);
                    }
                };
                
                setTimeout(typeChar, 500);
            }
        }
    }
    
    // Start typing effect when hero is visible
    const heroObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                setTimeout(typeNextMessage, 1000);
                heroObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    const hero = document.querySelector('.hero');
    if (hero) heroObserver.observe(hero);
}

/**
 * Parallax effect for orbs
 */
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const orbs = document.querySelectorAll('.gradient-orb');
    
    orbs.forEach((orb, index) => {
        const speed = 0.5 + (index * 0.1);
        orb.style.transform = `translateY(${scrolled * speed}px)`;
    });
}, { passive: true });

/**
 * Form validation helper
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Debounce helper
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle helper
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Lazy load images
 */
function initLazyLoad() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy load
initLazyLoad();

/**
 * Copy to clipboard helper
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!');
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}

/**
 * Show toast notification
 */
function showToast(message, duration = 3000) {
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) existingToast.remove();
    
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%) translateY(100px);
        background: #0F172A;
        color: #FFFFFF;
        padding: 12px 24px;
        border-radius: 10px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
        z-index: 9999;
        font-size: 14px;
        font-family: 'Inter', sans-serif;
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(-50%) translateY(0)';
    });
    
    // Remove after duration
    setTimeout(() => {
        toast.style.transform = 'translateX(-50%) translateY(100px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Expose utilities globally
window.LOKAAH = {
    validateEmail,
    debounce,
    throttle,
    copyToClipboard,
    showToast
};
