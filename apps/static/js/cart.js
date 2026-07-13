document.addEventListener('DOMContentLoaded', () => {
    const cartContent = document.getElementById('product-holder');
    let cartItems = [], isProcessing = false;

    const getOrCreateGuestUUID = () =>
        localStorage.getItem('guestUUID') ||
        (() => {
            const id = crypto.randomUUID();
            localStorage.setItem('guestUUID', id);
            return id;
        })();

    async function fetchWithAuth(url, options = {}) {
        options.headers = {
            ...options.headers,
            'Content-Type': 'application/json'
        };

        const token = localStorage.getItem('accessToken');

        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        } else {
            options.headers['X-Guest-UUID'] = getOrCreateGuestUUID();
        }

        let response = await fetch(url, options);

        if (response.status === 401 && localStorage.getItem('refreshToken')) {
            const refreshRes = await fetch('/api/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    refresh: localStorage.getItem('refreshToken')
                })
            });

            if (refreshRes.ok) {
                const data = await refreshRes.json();
                localStorage.setItem('accessToken', data.access);
                return fetchWithAuth(url, options);
            }
        }

        return response;
    }

    const recalculateTotals = () => {
        const checkedBoxes = [...cartContent.querySelectorAll('.item-select-checkbox:checked')];
        const totalPrice = checkedBoxes.reduce((sum, cb) => sum + parseFloat(cb.dataset.price), 0);

        const countElem = document.getElementById('summary-count');
        const subtotalElem = document.getElementById('summary-subtotal');
        const totalElem = document.getElementById('summary-total');
        const checkoutBtn = document.getElementById('checkout-btn');

        if (countElem) countElem.textContent = checkedBoxes.length;
        if (subtotalElem) subtotalElem.textContent = `${totalPrice.toLocaleString()} ₽`;
        if (totalElem) totalElem.textContent = `${totalPrice.toLocaleString()} ₽`;
        if (checkoutBtn) checkoutBtn.disabled = isProcessing || !checkedBoxes.length;
    };

    function renderEmptyCart() {
        cartContent.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #64748b;">
                <h2>Ваша корзина пуста</h2>
                <p style="margin-bottom: 20px;">Вы еще не добавили ни одного программного продукта.</p>
                <a href="/" class="btn-main-checkout" style="display: inline-flex; align-items: center; justify-content: center; text-decoration: none; width: auto; padding: 0 32px;">
                    Перейти в каталог
                </a>
            </div>
        `;
    }

    function renderCart() {
        if (!cartItems.length) {
            renderEmptyCart();
            return;
        }

        const isGuest = !localStorage.getItem('accessToken');

        const sidebarContactHtml = isGuest
            ? `
            <div class="card sidebar-contact-card" style="padding: 24px; box-sizing: border-box; background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; margin-top: 16px;">
                <h4>Контактные данные</h4>
                <div class="form-group" style="margin-bottom: 0; display: flex; flex-direction: column; gap: 8px;">
                    <label for="checkout-email" style="font-size: 14px; font-weight: 600; color: #475569;">Email для получения кода</label>
                    <input type="email" id="checkout-email" class="cart-input" placeholder="example@mail.ru" required>
                </div>
            </div>
        `
            : '';

        const tableRows = cartItems.map(item => {
            const p = item.product;
            const itemTotal = parseFloat(p.price) * parseInt(item.quantity || 1);

            return `
                <tr data-item-id="${item.id}">
                    <td>
                        <input type="checkbox" class="cart-checkbox item-select-checkbox" data-id="${item.id}" data-price="${itemTotal}" checked>
                    </td>
                    <td>
                        <div class="cart-item-title">${p.title}</div>
                        <small style="color: #64748b;">${p.tech_stack || 'Исходный код'}</small>
                    </td>
                    <td style="font-weight: 500;">${parseFloat(p.price).toLocaleString()} ₽</td>
                    <td style="font-weight: 600;">${itemTotal.toLocaleString()} ₽</td>
                    <td style="text-align: right;">
                        <button class="btn-delete-item" data-id="${item.id}">Удалить</button>
                    </td>
                </tr>
            `;
        }).join('');

        cartContent.innerHTML = `
            <div class="cart-main-layout">
                <div class="cart-left-column">
                    <div class="cart-management-bar">
                        <label class="checkbox-label">
                            <input type="checkbox" class="cart-checkbox" id="select-all-checkbox" checked>
                            Выбрать все
                        </label>
                        <button class="btn-text-delete" id="clear-cart-btn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                            Очистить корзину
                        </button>
                    </div>

                    <div class="cart-table-wrapper">
                        <table class="cart-table">
                            <thead>
                                <tr>
                                    <th></th>
                                    <th>Товар (Исходный код)</th>
                                    <th>Цена за шт.</th>
                                    <th>Итого</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRows}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="cart-right-sidebar">
                    <button class="btn-main-checkout" id="checkout-btn">Перейти к оформлению</button>

                    <div class="card summary-card" style="padding: 24px;">
                        <h3>Ваша корзина</h3>

                        <div class="summary-row">
                            <span>Товары (<span id="summary-count">0</span>)</span>
                            <span id="summary-subtotal">0 ₽</span>
                        </div>

                        <div class="summary-total-row" style="margin-top: 16px; font-weight: 700; display: flex; justify-content: space-between;">
                            <span>Итого к оплате:</span>
                            <span id="summary-total">0 ₽</span>
                        </div>
                    </div>

                    ${sidebarContactHtml}
                </div>
            </div>
        `;

        const selectAllCb = cartContent.querySelector('#select-all-checkbox');

        selectAllCb.addEventListener('change', e => {
            cartContent.querySelectorAll('.item-select-checkbox').forEach(cb => {
                cb.checked = e.target.checked;
            });
            recalculateTotals();
        });

        cartContent.querySelectorAll('.item-select-checkbox').forEach(cb => {
            cb.addEventListener('change', () => {
                const allBoxes = [...cartContent.querySelectorAll('.item-select-checkbox')];
                selectAllCb.checked = allBoxes.every(c => c.checked);
                recalculateTotals();
            });
        });

        cartContent.querySelectorAll('.btn-delete-item').forEach(btn => {
            btn.addEventListener('click', async () => {
                if (isProcessing) return;

                isProcessing = true;
                btn.disabled = true;

                try {
                    const response = await fetchWithAuth(`/api/cart/items/${btn.dataset.id}/`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        cartItems = cartItems.filter(item => item.id != btn.dataset.id);
                        renderCart();
                    }
                } finally {
                    isProcessing = false;
                }
            });
        });

        cartContent.querySelector('#clear-cart-btn').addEventListener('click', async () => {
            if (isProcessing || !confirm('Очистить корзину?')) return;

            isProcessing = true;

            try {
                const response = await fetchWithAuth('/api/cart/clear/', {
                    method: 'POST'
                });

                if (response.ok) {
                    cartItems = [];
                    renderCart();
                }
            } finally {
                isProcessing = false;
            }
        });

        cartContent.querySelector('#checkout-btn').addEventListener('click', async () => {
            if (isProcessing) return;

            const emailInput = document.getElementById('checkout-email');

            if (emailInput && !emailInput.reportValidity()) return;

            const selectedPayload = [...cartContent.querySelectorAll('.item-select-checkbox:checked')].map(cb => {
                const original = cartItems.find(item => item.id == cb.dataset.id);

                return {
                    id: original.id,
                    product_id: original.product.id,
                    quantity: original.quantity || 1,
                    price: original.product.price
                };
            });

            isProcessing = true;
            recalculateTotals();

            try {
                const response = await fetchWithAuth('/api/orders/', {
                    method: 'POST',
                    body: JSON.stringify({
                        items: selectedPayload,
                        guest_email: emailInput?.value
                    })
                });

                if (response.ok) {
                    const orderData = await response.json();

                    if (orderData.payment_url) {
                        window.location.href = orderData.payment_url;
                        return;
                    }

                    alert('Заказ успешно создан!');

                    const checkedIds = selectedPayload.map(i => i.id);
                    cartItems = cartItems.filter(item => !checkedIds.includes(item.id));

                    isProcessing = false;
                    renderCart();
                } else {
                    alert('Ошибка при оформлении заказа');
                    isProcessing = false;
                    recalculateTotals();
                }
            } catch (error) {
                console.error('Ошибка отправки заказа:', error);
                isProcessing = false;
                recalculateTotals();
            }
        });

        recalculateTotals();
    }

    if (cartContent) {
        (async () => {
            try {
                const response = await fetchWithAuth('/api/cart/');
                cartItems = response.ok ? ((await response.json()).items || []) : [];
                renderCart();
            } catch (error) {
                console.error('Ошибка инициализации корзины:', error);
                cartContent.innerHTML = '<p style="text-align:center; padding:20px; color:#ef4444;">Ошибка загрузки</p>';
            }
        })();
    }
});