document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('jwt-login-form');
    const errorBlock = document.getElementById('js-error-block');

    async function loadOrders(token) {
        try {
            const response = await fetch('/api/orders/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const ordersData = await response.json();
                console.log('Список заказов из ViewSet:', ordersData);
                window.location.href = '/';
            } else {
                console.error('Ошибка DRF при получении заказов:', response.status);
            }
        } catch (err) {
            console.error('Ошибка сети при получении заказов:', err);
        }
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            if (errorBlock) {
                errorBlock.style.display = 'none';
                errorBlock.innerText = '';
            }
            document.querySelectorAll('.field-errors-js').forEach(el => el.innerHTML = '');

            const usernameInput = loginForm.querySelector('[name="username"]');
            const passwordInput = loginForm.querySelector('[name="password"]');

            const payload = {
                username: usernameInput.value,
                password: passwordInput.value
            };

            try {
                const response = await fetch('/api/token/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('accessToken', data.access);
                    localStorage.setItem('refreshToken', data.refresh);

                    await loadOrders(data.access);
                } else {
                    if (errorBlock) {
                        errorBlock.style.display = 'block';
                        errorBlock.innerText = data.detail || 'Неверное имя пользователя или пароль.';
                    }
                }
            } catch (error) {
                console.error('Ошибка авторизации:', error);
                if (errorBlock) {
                    errorBlock.style.display = 'block';
                    errorBlock.innerText = 'Произошла ошибка на сервере. Попробуйте позже.';
                }
            }
        });
    }
});

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