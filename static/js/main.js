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

        animatedEls.forEach(el => {
            // Set initial hidden state via JS so content is still
            // visible if JS is disabled
            el.style.opacity = '0';
            el.style.transform = 'translateY(24px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
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

    console.log('🐝 WorkBee loaded');
});
