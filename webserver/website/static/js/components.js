// Components initialization
document.addEventListener('DOMContentLoaded', function() {
    // Load header
    fetch('/static/components/header.html')
        .then(response => response.text())
        .then(data => {
            document.querySelector('header').innerHTML = data;
            initializeMobileMenu(); // Initialize mobile menu after header is loaded
        });

    // Load footer
    fetch('/static/components/footer.html')
        .then(response => response.text())
        .then(data => {
            document.querySelector('footer').innerHTML = data;
        });
});

// Mobile menu functionality
function initializeMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent event from bubbling
            navLinks.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.main-nav')) {
                navLinks.classList.remove('active');
            }
        });

        // Close menu when clicking a link
        navLinks.addEventListener('click', function() {
            navLinks.classList.remove('active');
        });
    }
}
