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

    var controls = document.getElementById('ceramics-controls');
    var categories = document.getElementById('ceramics-categories');
    var sortSelect = document.getElementById('ceramics-sort');
    var count = document.getElementById('ceramics-count');
    var empty = document.getElementById('ceramics-empty');
    var selectedCategory = '';
    var cards = Array.from(grid.querySelectorAll('.ceramics-card')).map(function (element, index) {
        return { element: element, index: index,
            product: productsById[element.querySelector('[data-product-id]').getAttribute('data-product-id')] };
    });

    function updateCollection() {
        var visible = 0;
        var sold = 0;
        cards.slice().sort(function (a, b) {
            var delta;
            if (sortSelect.value === 'price-asc') { delta = a.product.price - b.product.price; }
            else if (sortSelect.value === 'price-desc') { delta = b.product.price - a.product.price; }
            else { delta = Number(b.product.listedAt || 0) - Number(a.product.listedAt || 0); }
            return delta || a.index - b.index;
        }).forEach(function (card) {
            var matches = !selectedCategory || String(card.product.sectionId || '') === selectedCategory;
            card.element.hidden = !matches;
            if (matches) {
                visible++;
                if (card.product.available === false) { sold++; }
            }
            grid.appendChild(card.element);
        });
        count.textContent = visible + (visible === 1 ? ' piece' : ' pieces') +
            (sold ? ' · ' + sold + ' sold' : '');
        empty.hidden = visible !== 0;
        categories.querySelectorAll('button').forEach(function (button) {
            button.setAttribute('aria-pressed', String(button.dataset.category === selectedCategory));
        });
    }

    if (controls && categories && sortSelect && count && empty) {
        [{id: '', name: 'All pieces'}].concat((data.sections || []).filter(Boolean)).forEach(function (section) {
            var button = document.createElement('button');
            button.type = 'button';
            button.dataset.category = String(section.id);
            var total = cards.filter(function (card) {
                return !section.id || String(card.product.sectionId || '') === String(section.id);
            }).length;
            button.textContent = section.name + ' (' + total + ')';
            button.setAttribute('aria-controls', 'ceramics-grid');
            button.addEventListener('click', function () {
                selectedCategory = String(section.id);
                updateCollection();
            });
            categories.appendChild(button);
        });
        sortSelect.addEventListener('change', updateCollection);
        controls.hidden = false;
        updateCollection();
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
