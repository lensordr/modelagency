// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form submissions
document.addEventListener('DOMContentLoaded', function() {
    // Trial form - let Formspree handle it naturally
    // No JavaScript intervention needed
    
    // Contact form - let Formspree handle it naturally
    // No JavaScript intervention needed
});

// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.backdropFilter = 'blur(10px)';
    } else {
        navbar.style.background = '#fff';
        navbar.style.backdropFilter = 'none';
    }
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.addEventListener('DOMContentLoaded', function() {
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });
});

// Add loading animation for placeholders
document.addEventListener('DOMContentLoaded', function() {
    const placeholders = document.querySelectorAll('.hero-placeholder, .video-placeholder, .screenshot-placeholder');
    
    placeholders.forEach(placeholder => {
        placeholder.addEventListener('click', function() {
            alert('This is where you can upload your screenshots and demo video. The placeholders will be replaced with your actual media.');
        });
        
        // Add hover effect
        placeholder.style.cursor = 'pointer';
        placeholder.addEventListener('mouseenter', function() {
            this.style.borderColor = '#2563eb';
            this.style.backgroundColor = 'rgba(37, 99, 235, 0.05)';
        });
        
        placeholder.addEventListener('mouseleave', function() {
            this.style.borderColor = '';
            this.style.backgroundColor = '';
        });
    });
});