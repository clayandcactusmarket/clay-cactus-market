var hamburger = document.getElementById('hamburger');
var nav = document.getElementById('nav-links');

if (hamburger && nav) {
    var navLinks = nav.querySelectorAll('a');

    hamburger.addEventListener('click', function () {
        var isOpen = nav.classList.toggle('show');
        hamburger.setAttribute('aria-expanded', String(isOpen));
    });

    navLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            nav.classList.remove('show');
            hamburger.setAttribute('aria-expanded', 'false');
        });
    });
}
