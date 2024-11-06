// scroll.js
document.addEventListener("DOMContentLoaded", function () {
    let currentIndex = 0;
    const slides = document.querySelectorAll(".slide");
    const dots = document.querySelectorAll(".dot");
    const delay = 5000;  // Auto-scroll every 5 seconds

    function showSlide(index) {
        slides[index].scrollIntoView({ behavior: "smooth" });
        dots.forEach(dot => dot.classList.remove("active"));
        dots[index].classList.add("active");
        currentIndex = index;
    }

    function autoScroll() {
        currentIndex = (currentIndex + 1) % slides.length;
        showSlide(currentIndex);
    }

    // Auto-scroll
    setInterval(autoScroll, delay);

    // Manual navigation
    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => showSlide(index));
    });

    // Set initial slide to active
    showSlide(0);
});
