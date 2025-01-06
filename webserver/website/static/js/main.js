document.addEventListener('DOMContentLoaded', () => {
    const connectWalletBtn = document.getElementById('connectWallet');
    const contactForm = document.getElementById('contactForm');
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    const prevButton = document.querySelector('.prev-slide');
    const nextButton = document.querySelector('.next-slide');
    let currentSlide = 0;

    // Web3 wallet connection
    async function connectWallet() {
        if (typeof window.ethereum !== 'undefined') {
            try {
                // Request account access
                const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                console.log('Connected account:', accounts[0]);
                connectWalletBtn.textContent = 'Connected';
                // Add your Web3 logic here
            } catch (error) {
                console.error('Error connecting wallet:', error);
            }
        } else {
            alert('Please install MetaMask or another Web3 wallet to continue.');
        }
    }

    // Contact form submission
    function handleContactSubmit(e) {
        e.preventDefault();
        // Add your form submission logic here
        console.log('Form submitted');
    }

    function showSlide(n) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        currentSlide = (n + slides.length) % slides.length;
        slides[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
    }

    function nextSlide() {
        showSlide(currentSlide + 1);
    }

    function prevSlide() {
        showSlide(currentSlide - 1);
    }

    // Event listeners
    connectWalletBtn.addEventListener('click', connectWallet);
    contactForm.addEventListener('submit', handleContactSubmit);
    prevButton.addEventListener('click', prevSlide);
    nextButton.addEventListener('click', nextSlide);
    
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => showSlide(index));
    });

    // Show first slide
    showSlide(0);

    // Optional: Auto-advance slides
    setInterval(nextSlide, 5000);
});

// Mobile menu functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
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
}); 