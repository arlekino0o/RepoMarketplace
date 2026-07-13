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
    window.location.href = '/users/login/';
    return null;
}

async function fetchWithAuth(url, options = {}) {
    let token = localStorage.getItem('accessToken');
    options.headers = options.headers || {};
    
    if (!token) {
        window.location.href = '/users/login/'; 
        return;
    }

    options.headers['Authorization'] = `Bearer ${token}`;
    let response = await fetch(url, options);

    if (response.status === 401) {
        token = await refreshAccessToken();
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
            response = await fetch(url, options); 
        }
    }
    return response;
}

class PaymentForm {}