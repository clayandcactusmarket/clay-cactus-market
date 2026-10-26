(function () {
    var DATA_URL = 'data/ceramics.json';
    var grid = document.getElementById('ceramics-grid');
    var status = document.getElementById('ceramics-status');
    var modal = document.getElementById('ceramics-modal');
    if (!grid || !modal) { return; }

    var modalImage = document.getElementById('ceramics-modal-image');
    var modalName = document.getElementById('ceramics-modal-name');
    var modalPrice = document.getElementById('ceramics-modal-price');
    var modalDesc = document.getElementById('ceramics-modal-description');
    var modalLink = document.getElementById('ceramics-modal-link');
    var lastFocus = null;

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

    function el(tag, className, text) {
        var node = document.createElement(tag);
        if (className) { node.className = className; }
        if (text !== undefined) { node.textContent = text; }
        return node;
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
        modal.hidden = false;
        document.body.classList.add('modal-open');
        modal.querySelector('.ceramics-modal__close').focus();
    }

    function closeModal() {
        modal.hidden = true;
        document.body.classList.remove('modal-open');
        if (lastFocus) { lastFocus.focus(); }
    }

    function buildCard(product) {
        var card = el('li', 'ceramics-card');
        var button = el('button', 'ceramics-card__button');
        button.type = 'button';
        button.setAttribute('aria-label', 'View details for ' + product.name);

        var media = el('span', 'ceramics-card__media');
        var img = el('img');
        img.src = product.image;
        img.alt = product.imageAlt || product.name;
        img.loading = 'lazy';
        media.appendChild(img);
        if (product.available === false) {
            media.appendChild(el('span', 'ceramics-card__badge', 'Sold'));
        }

        var body = el('span', 'ceramics-card__body');
        body.appendChild(el('span', 'ceramics-card__name', product.name));
        body.appendChild(el('span', 'ceramics-card__price', formatPrice(product)));

        button.appendChild(media);
        button.appendChild(body);
        button.addEventListener('click', function () { openModal(product, button); });
        card.appendChild(button);
        return card;
    }

    function injectStructuredData(data, products) {
        if (!products.length) { return; }
        var availabilityMap = {
            true: 'https://schema.org/InStock',
            false: 'https://schema.org/SoldOut'
        };
        var itemList = {
            '@context': 'https://schema.org',
            '@type': 'ItemList',
            name: 'Ceramics by Jaymi',
            itemListElement: products.map(function (product, index) {
                return {
                    '@type': 'ListItem',
                    position: index + 1,
                    url: safeUrl(product.etsyUrl),
                    item: {
                        '@type': 'Product',
                        name: product.name,
                        image: 'https://clayandcactusmarket.com/' + product.image.replace(/^\//, ''),
                        description: product.seoDescription || product.description || product.name,
                        brand: {
                            '@type': 'Brand',
                            name: 'Ceramics by Jaymi'
                        },
                        creator: {
                            '@type': 'Person',
                            name: 'Jaymi'
                        },
                        offers: {
                            '@type': 'Offer',
                            priceCurrency: product.currency || 'USD',
                            price: Number(product.price),
                            availability: availabilityMap[String(product.available !== false)],
                            url: safeUrl(product.etsyUrl)
                        }
                    }
                };
            })
        };

        var collectionPage = {
            '@context': 'https://schema.org',
            '@type': 'CollectionPage',
            name: 'Ceramics by Jaymi',
            url: 'https://clayandcactusmarket.com/ceramics.html',
            description: 'Handmade ceramics by Jaymi, sold through the Clay & Cactus Market Etsy shop.',
            isPartOf: {
                '@type': 'WebSite',
                name: 'Clay & Cactus Market',
                url: 'https://clayandcactusmarket.com/'
            },
            about: {
                '@type': 'Person',
                name: 'Jaymi'
            },
            mainEntity: itemList
        };

        var script = document.createElement('script');
        script.type = 'application/ld+json';
        script.text = JSON.stringify(collectionPage);
        document.head.appendChild(script);
    }

    function render(data) {
        var products = (data && data.products) || [];
        grid.innerHTML = '';
        if (!products.length) {
            status.textContent = 'New pieces are on the way. Check back soon!';
            status.hidden = false;
            return;
        }
        status.hidden = true;
        products.forEach(function (product) { grid.appendChild(buildCard(product)); });
        injectStructuredData(data, products);
    }

    modal.addEventListener('click', function (event) {
        if (event.target.hasAttribute('data-close')) { closeModal(); }
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && !modal.hidden) { closeModal(); }
    });

    fetch(DATA_URL)
        .then(function (response) {
            if (!response.ok) { throw new Error('Request failed'); }
            return response.json();
        })
        .then(render)
        .catch(function () {
            status.textContent = 'We couldn\u2019t load the collection right now. Please visit our Etsy shop instead.';
            status.hidden = false;
        });
})();
