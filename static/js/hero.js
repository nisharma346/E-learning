document.addEventListener('DOMContentLoaded', function () {
    const heroBlocks = document.querySelectorAll('.hero-animate');

    heroBlocks.forEach(function (element) {
        element.classList.add('is-ready');
    });
});
