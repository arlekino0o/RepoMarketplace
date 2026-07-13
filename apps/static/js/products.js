async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) return null;

    try {
        const response = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('accessToken', data.access);
            return data.access;
        }
    } catch (err) {
        console.error('Не удалось обновить JWT токен:', err);
    }

    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    return null;
}

async function fetchWithAuth(url, options = {}) {
    let token = localStorage.getItem('accessToken');
    options.headers = options.headers || {};

    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    let response = await fetch(url, options);

    if (response.status === 401 && localStorage.getItem('refreshToken')) {
        token = await refreshAccessToken();
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
            response = await fetch(url, options);
        }
    }
    return response;
}

function debounce(func, delay) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

function getActionHtml(productId, inCart, isCatalog = false) {
    const style = isCatalog
        ? 'width: auto; height: 38px; padding: 8px 16px; font-size: 14px;'
        : 'width: 100%; height: 50px; font-size: 16px; font-weight: 600;';

    const containerStyle = isCatalog ? 'width: auto;' : 'width: 100%;';

    if (inCart) {
        return `
            <div class="cart-management-panel" style="${containerStyle}">
                <a href="/orders/cart/" class="btn-in-cart" style="${style} display: flex; flex-direction: column; align-items: center; justify-content: center; text-decoration: none;">
                    В корзине
                    <small class="btn-remove-cart" data-id="${productId}" style="cursor: pointer; display: block; margin-top: 2px; font-size: 11px;">
                        (удалить)
                    </small>
                </a>
            </div>
        `;
    } else {
        return `
            <button class="btn btn-primary add-to-cart-btn" data-id="${productId}" style="${style}">
                Купить код
            </button>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const metaElement = document.getElementById('product-seller-meta');
    const purchaseBlock = document.getElementById('sidebar-purchase-block');
    const tabsList = document.getElementById('versions-tabs-list');
    const changelogTitle = document.getElementById('selected-version-title');
    const changelogText = document.getElementById('selected-version-text');

    const productHolder = document.getElementById('product-holder');
    const searchInput = document.getElementById('product-search-input');

    if (metaElement && purchaseBlock) {
        loadProductDetailData();
    }

    async function loadProductDetailData() {
        const sellerId = parseInt(metaElement.dataset.sellerId, 10);
        const productSlug = metaElement.dataset.productSlug;
        const token = localStorage.getItem('accessToken');

        try {
            const response = await fetchWithAuth(`/api/products/${productSlug}/`, { method: 'GET' });

            if (response.ok) {
                const productData = await response.json();

                let currentUserId = null;
                if (token) {
                    try {
                        const userRes = await fetchWithAuth('/api/users/me/', { method: 'GET' });
                        if (userRes.ok) {
                            const userData = await userRes.json();
                            currentUserId = userData.id;
                        } else {
                            console.warn(`Профиль /api/users/me/ вернул статус ${userRes.status}.`);
                        }
                    } catch (userErr) {
                        console.error('Ошибка при запросе /api/users/me/:', userErr);
                    }
                }

                const isSeller = currentUserId === sellerId;
                const isPurchased = productData.has_purchased || productData.price == 0;
                const versions = productData.versions || [];
                const latestVersion = versions.length > 0 ? versions[0].version_number : '1.0.0';

                if (isSeller) {
                    purchaseBlock.innerHTML = `
                        <div class="card" style="padding: 24px; display: flex; flex-direction: column; align-items: center; border-color: #bbf7d0; background-color: #f0fdf4;">
                            <span style="font-size: 15px; font-weight: 500; color: #16a34a; margin-bottom: 12px; text-align: center;">Вы автор этого кода</span>
                            <a href="/products/${productSlug}/add-version/" class="btn" style="display: inline-flex; align-items: center; justify-content: center; width: 100%; height: 50px; font-size: 16px; font-weight: 600; text-decoration: none; border-radius: 8px; background-color: #22c55e; color: #fff !important;">
                                Выпустить обновление
                            </a>
                        </div>
                    `;
                } else if (isPurchased && token) {
                    if (versions.length > 0) {
                        const latestVersion = versions[0].version_number;

                        let optionsHtml = '';
                        versions.forEach(ver => {
                            optionsHtml += `<option value="${ver.version_number}">Версия v${ver.version_number}</option>`;
                        });

                        purchaseBlock.innerHTML = `
                            <div class="card" style="padding: 24px; display: flex; flex-direction: column; gap: 14px; border-color: #bae6fd; background-color: #f0f9ff;">
                                <span style="font-size: 15px; font-weight: 500; color: #0284c7; text-align: center; display: block;">
                                    Продукт успешно приобретен
                                </span>

                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <label style="font-size: 13px; font-weight: 500; color: #0369a1;">Выберите версию для скачивания:</label>
                                    <select id="download-version-select" class="form-select" style="height: 40px; padding: 0 12px; font-size: 14px; border-color: #bae6fd;">
                                        ${optionsHtml}
                                    </select>
                                </div>

                                <!-- Кнопка скачивания: теперь в ней гарантированно реальный номер версии -->
                                <a id="download-code-btn" href="/api/products/${productSlug}/download/?version=${latestVersion}" class="btn" style="display: inline-flex; align-items: center; justify-content: center; width: 100%; height: 50px; font-size: 16px; font-weight: 600; text-decoration: none; border-radius: 8px; background-color: #0284c7; color: #fff !important; transition: background-color 0.2s;">
                                    Скачать архив v${latestVersion}
                                </a>
                            </div>
                        `;

                        const versionSelect = document.getElementById('download-version-select');
                        const downloadBtn = document.getElementById('download-code-btn');

                        if (versionSelect && downloadBtn) {
                            versionSelect.addEventListener('change', (e) => {
                                const selectedVer = e.target.value;
                                downloadBtn.innerHTML = `Скачать архив v${selectedVer}`;
                                downloadBtn.setAttribute('href', `/api/products/${productSlug}/download/?version=${selectedVer}`);
                            });
                        }
                    } else {
                        purchaseBlock.innerHTML = `
                            <div class="card" style="padding: 24px; display: flex; flex-direction: column; align-items: center; border-color: #e2e8f0; background-color: #f8fafc;">
                                <span style="font-size: 15px; font-weight: 500; color: var(--text); text-align: center; margin-bottom: 4px;">
                                    Продукт успешно приобретен 🎉
                                </span>
                                <span style="font-size: 13px; color: var(--muted); text-align: center;">
                                    Файлы исходного кода ещё не загружены продавцом. Пожалуйста, зайдите позже.
                                </span>
                            </div>
                        `;
                    }
                }

                if (tabsList && versions.length > 0) {
                    tabsList.innerHTML = '';

                    versions.forEach((ver, index) => {
                        const tabBtn = document.createElement('button');
                        tabBtn.innerText = `Версия v${ver.version_number}`;
                        tabBtn.style = `
                            width: 100%; padding: 10px 12px; text-align: left; background: none;
                            border: none; border-radius: 6px; font-size: 14px; font-weight: 500;
                            cursor: pointer; transition: all 0.2s; color: var(--text);
                        `;

                        if (index === 0) {
                            tabBtn.style.backgroundColor = 'var(--bg-page)';
                            tabBtn.style.color = 'var(--primary)';
                            if (changelogTitle) changelogTitle.innerText = `Что нового в версии v${ver.version_number}`;
                            if (changelogText) changelogText.innerText = ver.changelog || 'Описание изменений отсутствует.';
                        }

                        tabBtn.addEventListener('click', () => {
                            Array.from(tabsList.children).forEach(b => {
                                b.style.backgroundColor = 'transparent';
                                b.style.color = 'var(--text)';
                            });
                            tabBtn.style.backgroundColor = 'var(--bg-page)';
                            tabBtn.style.color = 'var(--primary)';

                            if (changelogTitle) changelogTitle.innerText = `Что нового в версии v${ver.version_number}`;
                            if (changelogText) changelogText.innerText = ver.changelog || 'Описание изменений отсутствует.';
                        });

                        tabsList.appendChild(tabBtn);
                    });
                } else if (tabsList) {
                    tabsList.innerHTML = '<p style="color: var(--muted); font-size: 14px;">Версии не найдены</p>';
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки данных детальной страницы:', error);
        }
    }

    if (productHolder) {
        productHolder.className = 'products-grid';

                function renderProducts(products) {
            productHolder.innerHTML = '';

            if (products.length === 0) {
                productHolder.innerHTML = '<div class="alert alert-info" style="grid-column: 1/-1; text-align: center;">Ничего не найдено</div>';
                return;
            }

            products.forEach(product => {
                const productCard = document.createElement('article');
                productCard.className = 'product-card card';

                const previewHtml = product.preview_image
                    ? `<img src="${product.preview_image}" alt="${product.title}">`
                    : `<div class="code-placeholder">&lt;Code /&gt;</div>`;

                const licenseText = product.license_type === 'mit' ? 'MIT License' : 'Commercial';

                productCard.innerHTML = `
                    <div class="product-card-image">
                        ${previewHtml}
                    </div>

                    <div class="product-meta" style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">
                        <span class="tech-tag">${product.tech_stack || 'Script'}</span>
                        <span class="license-tag">${licenseText}</span>
                    </div>

                    <h3><a href="/${product.slug}/">${product.title}</a></h3>

                    <div class="product-rating-line" style="margin-bottom: 14px; margin-top: -4px; display: flex; gap: 12px; font-size: 14px; align-items: center;">
                        <div class="rating-stars-value" style="display: flex; align-items: center; gap: 4px; font-weight: 700;">
                            <span class="icon-star-gold" style="color: #f59e0b; display: inline-flex;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                            </span>
                            <span>${product.average_rating ? product.average_rating.toFixed(1) : '0.0'}</span>
                        </div>
                        <div class="rating-reviews-count" style="display: flex; align-items: center; gap: 6px; color: #64748b;">
                            <span class="icon-comment-gray" style="color: #94a3b8; display: inline-flex;">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                            </span>
                            <span>${product.reviews_count || 0} отзывов</span>
                        </div>
                    </div>

                    <p class="product-description">
                        ${product.short_description || product.description || 'Описание отсутствует.'}
                    </p>

                    <div class="product-card-footer">
                        <span class="product-price">
                            ${product.price == 0 ? 'Free' : parseFloat(product.price).toLocaleString() + ' ₽'}
                        </span>
                        <div id="action-holder-${product.id}" style="flex: 1; display: flex; justify-content: flex-end;">
                            ${getActionHtml(product.id, product.in_cart, true)}
                        </div>
                    </div>
                `;
                productHolder.appendChild(productCard);
            });
        }

        async function fetchProducts(searchQuery = '') {
            try {
                let url = '/api/products/';
                if (searchQuery) {
                    url += `?search=${encodeURIComponent(searchQuery)}`;
                }

                const response = await fetchWithAuth(url, { method: 'GET' });
                if (!response.ok) throw new Error('Ошибка сети');
                const data = await response.json();
                renderProducts(data.results || data);
            } catch (error) {
                console.error('Не удалось загрузить товары:', error);
                productHolder.innerHTML = '<p style="color: #dc3545; padding: 20px; text-align: center; grid-column: 1/-1;">Ошибка загрузки ленты товаров.</p>';
            }
        }

        if (searchInput) {
            searchInput.addEventListener('input', debounce((e) => {
                const query = e.target.value.trim();
                fetchProducts(query);
            }, 350));
        }
        fetchProducts();
    }

    document.body.addEventListener('click', async (event) => {
        const target = event.target;
        const addBtn = target.closest('.add-to-cart-btn');

        if (addBtn) {
            const productId = addBtn.dataset.id;
            const actionHolder = document.getElementById(`action-holder-${productId}`);
            const isCatalogView = !!productHolder && !!actionHolder;

            addBtn.disabled = true;

            try {
                const response = await fetchWithAuth('/api/cart/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': typeof getCookie === 'function' ? getCookie('csrftoken') : ''
                    },
                    body: JSON.stringify({ product_id: parseInt(productId, 10), quantity: 1 })
                });

                if (response.status === 201 || response.ok) {
                    if (actionHolder) {
                        actionHolder.innerHTML = getActionHtml(productId, true, isCatalogView);
                    } else {
                        const detailPriceBox = addBtn.parentElement;
                        if (detailPriceBox) detailPriceBox.innerHTML = getActionHtml(productId, true, false);
                    }
                }
            } catch (err) {
                console.error('Ошибка при добавлении в корзину:', err);
            } finally {
                addBtn.disabled = false;
            }
        }
    });
});