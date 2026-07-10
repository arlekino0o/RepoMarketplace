const cartContent = document.getElementById('cart-content');
const CART_API_URL = '/api/cart/';

let globalCartData = null;
let isProcessing = false;

async function loadCart() {
    try {
        const response = await fetch(CART_API_URL);
        if (!response.ok) throw new Error('Не удалось получить ответ от сервера');

        globalCartData = await response.json();
        renderCart(globalCartData);
    } catch (error) {
        console.error('Ошибка загрузки корзины:', error);
        cartContent.innerHTML = `<p style="color: red; font-weight: bold;">Ошибка загрузки корзины. Перезагрузите страницу.</p>`;
    }
}

function renderCart(cartData) {
    if (!cartData || !cartData.items || cartData.items.length === 0) {
        cartContent.innerHTML = '<h3>Ваша корзина пуста :(</h3>';
        return;
    }

    const sortedItems = [...cartData.items].sort((a, b) => a.product.id - b.product.id);

    let tableRows = '';
    sortedItems.forEach(item => {
        const price = parseFloat(item.product.price) || 0;
        const cost = parseFloat(item.item_cost) || (price * item.quantity);

        tableRows += `
            <tr>
                <td>${item.product.name}</td>
                <td>${price.toLocaleString()} руб.</td>
                <td>
                    <!-- Добавили класс управления disabled через CSS, если идет запрос -->
                    <button class="qty-btn minus-btn" data-id="${item.product.id}" ${isProcessing ? 'disabled' : ''}>-</button>
                    <span style="margin: 0 10px; font-weight: bold; display: inline-block; min-width: 20px; text-align: center;">${item.quantity}</span>
                    <button class="qty-btn plus-btn" data-id="${item.product.id}" ${isProcessing ? 'disabled' : ''}>+</button>
                </td>
                <td>${cost.toLocaleString()} руб.</td>
                <td>
                    <button class="delete-btn" data-id="${item.product.id}" ${isProcessing ? 'disabled' : ''}>Удалить</button>
                </td>
            </tr>
        `;
    });

    const totalCartPrice = parseFloat(cartData.total_price) || 0;

    cartContent.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Товар</th>
                    <th>Цена за шт.</th>
                    <th>Количество</th>
                    <th>Итого</th>
                    <th>Действие</th>
                </tr>
            </thead>
            <tbody>
                ${tableRows}
            </tbody>
        </table>

        <div class="cart-summary">Общая стоимость: ${totalCartPrice.toLocaleString()} руб.</div>

        <div class="guest-inputs" id="guest-form">
            <h3>Контакты для оформления</h3>
            <input type="email" id="guest-email" placeholder="Введите ваш Email" required ${isProcessing ? 'disabled' : ''}>
        </div>

        <div class="checkout-section">
            <button class="btn btn-clear" id="clear-cart-btn" ${isProcessing ? 'disabled' : ''}>Очистить корзину</button>
            <button class="btn btn-checkout" id="checkout-btn" ${isProcessing ? 'disabled' : ''}>Оформить заказ</button>
        </div>
    `;
}

function initCartListeners() {
    cartContent.addEventListener('click', async (event) => {
        const target = event.target;
        const csrfToken = getCookie('csrftoken');

        if (isProcessing) return;

        if (target.classList.contains('plus-btn') || target.classList.contains('minus-btn')) {
            const productId = target.getAttribute('data-id');
            const currentItem = globalCartData.items.find(item => item.product.id == productId);
            if (!currentItem) return;

            let newQty = currentItem.quantity;
            if (target.classList.contains('plus-btn')) newQty += 1;
            if (target.classList.contains('minus-btn')) newQty -= 1;

            if (newQty <= 0) return;

            isProcessing = true;
            renderCart(globalCartData);

            try {
                const response = await fetch(`${CART_API_URL}${productId}/`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                    body: JSON.stringify({ quantity: newQty })
                });
                if (response.ok) {
                    globalCartData = await response.json();
                }
            } catch (err) {
                console.error(err);
            } finally {
                isProcessing = false;
                renderCart(globalCartData);
            }
        }

        if (target.classList.contains('delete-btn')) {
            const productId = target.getAttribute('data-id');
            if (confirm('Удалить товар из корзины?')) {
                isProcessing = true;
                try {
                    const response = await fetch(`${CART_API_URL}${productId}/`, {
                        method: 'DELETE',
                        headers: { 'X-CSRFToken': csrfToken }
                    });
                    if (response.ok) {
                        globalCartData = await response.json();
                    }
                } catch (err) {
                    console.error(err);
                } finally {
                    isProcessing = false;
                    renderCart(globalCartData);
                }
            }
        }

        if (target.id === 'clear-cart-btn') {
            if (confirm('Вы уверены, что хотите полностью очистить корзину?')) {
                isProcessing = true;
                try {
                    const response = await fetch(`${CART_API_URL}clear/`, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': csrfToken }
                    });
                    if (response.ok) {
                        globalCartData = await response.json();
                    }
                } catch (err) {
                    console.error(err);
                } finally {
                    isProcessing = false;
                    renderCart(globalCartData);
                }
            }
        }

        if (target.id === 'checkout-btn') {
            const emailInput = document.getElementById('guest-email');
            if (emailInput && !emailInput.value.trim()) {
                alert('Пожалуйста, введите ваш Email.');
                return;
            }

            isProcessing = true;
            const bodyData = { email: emailInput.value.trim() };

            try {
                const response = await fetch(`${CART_API_URL}checkout/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                    body: JSON.stringify(bodyData)
                });

                const result = await response.json();
                if (response.ok) {
                    alert(`Заказ успешно оформлен!`);
                    const paymentId = result.payment_id || '';
                    window.location.href = `/orders/mock-payment-page/?order_id=${result.order_id}&payment_id=${paymentId}`;
                } else {
                    alert(`Ошибка оформления: ${result.error || JSON.stringify(result)}`);
                    isProcessing = false;
                    renderCart(globalCartData);
                }
            } catch (err) {
                console.error(err);
                isProcessing = false;
                renderCart(globalCartData);
            }
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    initCartListeners();
    loadCart();
});