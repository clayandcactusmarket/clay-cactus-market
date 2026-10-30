(function () {
    var grid = document.getElementById('ceramics-grid');
    var modal = document.getElementById('ceramics-modal');
    var dataScript = document.getElementById('ceramics-data');
    if (!grid || !modal || !dataScript) { return; }

    var modalImage = document.getElementById('ceramics-modal-image');
    var modalName = document.getElementById('ceramics-modal-name');
    var modalPrice = document.getElementById('ceramics-modal-price');
    var modalDesc = document.getElementById('ceramics-modal-description');
    var modalLink = document.getElementById('ceramics-modal-link');
    var modalSoldNote = document.getElementById('ceramics-modal-sold-note');
    var modalCustomLink = document.getElementById('ceramics-modal-custom-link');
    var lastFocus = null;

    var productsById = {};
    try {
        var data = JSON.parse(dataScript.textContent);
        ((data && data.products) || []).forEach(function (product) {
            productsById[product.id] = product;
        });
    } catch (e) {
        return;
    }

    function formatPrice(product) {
        try {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: product.currency || 'USD'
            }).format(product.price);
        } catch (e) {
            return '$' + Number(product.price).toFixed(2);
        }
    }

    function safeUrl(url) {
        return /^https:\/\//i.test(url || '') ? url : '#';
    }

    function openModal(product, trigger) {
        lastFocus = trigger;
        modalImage.src = product.image;
        modalImage.alt = product.imageAlt || product.name;
        modalName.textContent = product.name;
        modalPrice.textContent = formatPrice(product);
        modalDesc.textContent = product.description || '';
        modalDesc.hidden = !product.description;
        modalLink.href = safeUrl(product.etsyUrl);
        modalLink.hidden = product.available === false;
        modalSoldNote.hidden = product.available !== false;
        modalCustomLink.hidden = product.available !== false;
        modal.hidden = false;
        document.body.classList.add('modal-open');
        modal.querySelector('.ceramics-modal__close').focus();
    }

    function closeModal() {
        modal.hidden = true;
        document.body.classList.remove('modal-open');
        if (lastFocus) { lastFocus.focus(); }
    }

    grid.addEventListener('click', function (event) {
        var button = event.target.closest('button[data-product-id]');
        if (!button) { return; }
        var product = productsById[button.getAttribute('data-product-id')];
        if (product) { openModal(product, button); }
    });

    modal.addEventListener('click', function (event) {
        if (event.target.hasAttribute('data-close')) { closeModal(); }
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && !modal.hidden) { closeModal(); }
    });
})();
