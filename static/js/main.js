// WorkBee — main.js
// Scroll-triggered fade-in animations & active nav highlighting

document.addEventListener('DOMContentLoaded', () => {

    // ── Scroll Animations ──────────────────────────────
    // Elements with .animate-in fade in when they enter the viewport
    const animatedEls = document.querySelectorAll('.animate-in');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        animatedEls.forEach((el, index) => {
            // Set initial hidden state via JS so content is still
            // visible if JS is disabled
            el.style.opacity = '0';
            el.style.transform = 'translateY(24px)';
            el.style.transition = 'opacity 0.55s ease, transform 0.55s ease';
            el.style.transitionDelay = `${Math.min(index * 60, 300)}ms`;
            observer.observe(el);
        });
    }

    // ── Auto-dismiss alerts after 5 seconds ────────────
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // ── Active nav link highlighting ───────────────────
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const onScroll = () => {
            navbar.classList.toggle('navbar-scrolled', window.scrollY > 10);
        };
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    console.log('🐝 WorkBee loaded');
});
