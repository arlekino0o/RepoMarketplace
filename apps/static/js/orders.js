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

const statusMap = {
    'pending': { text: 'Ожидает оплаты', cardClass: 'status-pending', badgeClass: 'badge-pending' },
    'paid': { text: 'Оплачен', cardClass: 'status-paid', badgeClass: 'badge-paid' },
    'completed': { text: 'Завершен', cardClass: 'status-completed', badgeClass: 'badge-completed' }
};

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit'
    });
}

async function fetchOrders() {
    const container = document.getElementById('orders-container');
    const loading = document.getElementById('loading');
    const empty = document.getElementById('empty-state');
    const error = document.getElementById('error-state');

    if (!container) return;

    try {
        const response = await fetchWithAuth('/api/orders/', { method: 'GET' });
        if (!response.ok) throw new Error();

        const orders = await response.json();
        if (loading) loading.classList.add('hidden');

        if (!orders || orders.length === 0) {
            if (empty) empty.classList.remove('hidden');
            return;
        }

        orders.forEach(order => {
            const config = statusMap[order.status] || { text: order.status, cardClass: '', badgeClass: '' };

            let itemsHtml = '';
            order.items.forEach(item => {
                const price = parseFloat(item.price_at_purchase || item.product.price || 0);

                const productTitle = item.product.title || 'Скрипт';
                const productSlug = item.product.slug ? `/${item.product.slug}/` : '#';

                itemsHtml += `
                    <div class="order-product-row">
                        <div class="order-product-info">
                            <a href="${productSlug}">${productTitle}</a>
                        </div>
                        <div class="order-product-price">${item.item_cost.toLocaleString()} руб.</div>
                    </div>
                `;
            });

            let paymentBtn = '';
            if (order.status === 'pending') {
                paymentBtn = `
                    <div class="payment-block">
                        <a href="/orders/mock-payment-page/?order_id=${order.id}" class="btn-pay">
                            Оплатить заказ
                        </a>
                    </div>
                `;
            }

            const card = document.createElement('div');

            card.className = `order-card ${config.cardClass}`;
            card.innerHTML = `
                <div class="order-header">
                    <div class="order-title">Заказ №${order.id} <span class="order-date">${formatDate(order.created_at)}</span></div>
                    <span class="badge ${config.badgeClass}">${config.text}</span>
                </div>

                <div class="order-body">
                    ${itemsHtml}
                </div>

                <div class="order-footer">
                    <div class="order-total-block">
                        <span class="total-label">Итого:</span>
                        <span class="total-price">${parseFloat(order.total_price || 0).toLocaleString()} руб.</span>
                    </div>
                    ${paymentBtn}
                </div>
            `;
            container.appendChild(card);
        });

    } catch (err) {
        console.error(err);
        if (loading) loading.classList.add('hidden');
        if (error) error.classList.remove('hidden');
    }
}

document.addEventListener('DOMContentLoaded', fetchOrders);
