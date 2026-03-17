var hamburger = document.getElementById('hamburger');
var nav = document.getElementById('nav-links');

if (hamburger && nav) {
    hamburger.addEventListener('click', function () {
        nav.classList.toggle('show');
    });
}
