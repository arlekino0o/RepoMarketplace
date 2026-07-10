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

    try {
        const response = await fetch('/api/orders/', { method: 'GET' });
        if (!response.ok) throw new Error();

        const orders = await response.json();
        loading.classList.add('hidden');
        if (orders.length === 0) {
            empty.classList.remove('hidden');
            return;
        }

        orders.forEach(order => {
            const config = statusMap[order.status] || { text: order.status, cardClass: '', badgeClass: '' };

            let itemsHtml = '';
            order.items.forEach(item => {
                const price = item.price_at_purchase ? item.price_at_purchase : item.product.price;
                itemsHtml += `
                    <div class="item-row">
                        <div>${item.product.name} <span class="item-quantity">x${item.quantity}</span></div>
                        <div class="item-price">${(price * item.quantity).toLocaleString()} руб.</div>
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
                <div class="card-header">
                    <div class="order-title">Заказ №${order.id} <span class="order-date">${formatDate(order.created_at)}</span></div>
                    <span class="badge ${config.badgeClass}">${config.text}</span>
                </div>
                <div class="card-body">${itemsHtml}</div>
                <div class="card-footer">
                    <span class="total-label">Итого к оплате:</span>
                    <span class="total-price">${parseFloat(order.total_price).toLocaleString()} руб.</span>
                </div>
                ${paymentBtn}
            `;
            container.appendChild(card);
        });

    } catch (err) {
        loading.classList.add('hidden');
        error.classList.remove('hidden');
    }
}

document.addEventListener('DOMContentLoaded', fetchOrders);