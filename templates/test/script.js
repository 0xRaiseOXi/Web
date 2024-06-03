// script.js
document.addEventListener("DOMContentLoaded", () => {
    const progressBar = document.getElementById('progress-bar');
    let percentage = 75; // Укажите процент заполнения здесь (например, 75%)

    setProgress(percentage);

    function setProgress(percentage) {
        if (percentage < 0) percentage = 0;
        if (percentage > 100) percentage = 100;
        progressBar.style.height = percentage + '%';
    }
});