document.addEventListener('DOMContentLoaded', () => {
    const animatedBorder = document.querySelector('.animated-border');

    animatedBorder.addEventListener('mouseenter', () => {
        animatedBorder.classList.add('animate');
    });

    animatedBorder.addEventListener('mouseleave', () => {
        animatedBorder.classList.remove('animate');
    });
});