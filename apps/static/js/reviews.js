document.addEventListener('DOMContentLoaded', () => {
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const productSlug = pathParts[pathParts.length - 1];

    const reviewsListContainer = document.getElementById('reviews-list-container');
    const reviewFormContainer = document.getElementById('review-form-container');

    if (!reviewsListContainer) return;

    const token = localStorage.getItem('accessToken');
    const authHeaders = {};
    if (token) {
        authHeaders['Authorization'] = `Bearer ${token}`;
    }

    let productId = null;

    fetch(`/api/products/?slug=${productSlug}`, { headers: authHeaders })
        .then(res => res.json())
        .then(data => {
            const product = Array.isArray(data) ? data[0] : data;

            if (!product) {
                console.error("Товар не найден");
                return;
            }

            productId = product.id;

            loadReviewsList(productId);

            if (product.has_purchased) {
                renderReviewForm(productId);
            }
        })
        .catch(err => console.error("Ошибка инициализации отзывов:", err));

    function renderReviewForm(prodId) {
        reviewFormContainer.innerHTML = `
            <div class="add-review-card card">
                <h4 style="margin-bottom: 12px; font-size: 16px; font-weight: 700;">Оставить отзыв о коде</h4>
                <form id="product-review-form">

                    <!-- Выбор звезд (Radio-кнопки в обратном порядке для CSS) -->
                    <div class="rating-picker">
                        <input type="radio" id="star5" name="rating" value="5" required /><label for="star5" title="Отлично">★</label>
                        <input type="radio" id="star4" name="rating" value="4" /><label for="star4" title="Хорошо">★</label>
                        <input type="radio" id="star3" name="rating" value="3" /><label for="star3" title="Нормально">★</label>
                        <input type="radio" id="star2" name="rating" value="2" /><label for="star2" title="Плохо">★</label>
                        <input type="radio" id="star1" name="rating" value="1" /><label for="star1" title="Ужасно">★</label>
                    </div>

                    <div class="form-group" style="margin-bottom: 16px;">
                        <textarea id="review-comment" class="cart-input" style="height: 100px; resize: vertical;" placeholder="Расскажите о качестве кода, стабильности работы и документации..." required></textarea>
                    </div>

                    <button type="submit" class="btn btn-primary" id="submit-review-btn" style="width: auto; height: 40px; font-size: 14px;">
                        Отправить отзыв
                    </button>
                </form>
            </div>
        `;

        document.getElementById('product-review-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const ratingValue = document.querySelector('input[name="rating"]:checked').value;
            const commentValue = document.getElementById('review-comment').value;
            const submitBtn = document.getElementById('submit-review-btn');

            const requestHeaders = {
                'Content-Type': 'application/json'
            };

            if (token) {
                requestHeaders['Authorization'] = `Bearer ${token}`;
            } else {
                alert('Ошибка: Вы не авторизованы. Пожалуйста, войдите в систему.');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerText = 'Отправка...';

            try {
                const response = await fetch(`/api/products/${prodId}/reviews/`, {
                    method: 'POST',
                    headers: requestHeaders,
                    body: JSON.stringify({
                        rating: parseInt(ratingValue),
                        comment: commentValue
                    })
                });

                if (response.ok) {
                    alert('Спасибо! Ваш отзыв успешно опубликован.');
                    reviewFormContainer.innerHTML = '';
                    loadReviewsList(prodId);
                } else {
                    const err = await response.json();
                    alert(`Ошибка: ${err.detail || JSON.stringify(err)}`);
                }
            } catch (error) {
                console.error('Ошибка сети при отправке отзыва:', error);
                alert('Не удалось связаться с сервером.');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerText = 'Отправить отзыв';
                }
            }
        });
    }

    function loadReviewsList(prodId) {
        fetch(`/api/orders/` ? `/api/products/${prodId}/reviews/` : `/api/products/${prodId}/reviews/`)
            .then(res => res.json())
            .then(reviews => {
                reviewsListContainer.innerHTML = '';

                if (!reviews || reviews.length === 0) {
                    reviewsListContainer.innerHTML = '<p style="color: var(--muted); font-size: 15px;">У этого кода пока нет отзывов. Станьте первым!</p>';
                    return;
                }

                reviews.forEach(review => {
                    const dateHtml = new Date(review.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });

                    reviewsListContainer.innerHTML += `
                        <div class="review-item-card" style="margin-bottom: 16px;">
                            <div class="review-item-header">
                                <span style="font-size: 16px; font-weight: 700; color: #1e293b;">@${review.username}</span>
                                <span style="color: var(--muted);">${dateHtml}</span>
                            </div>
                            <div style="color: #f59e0b; font-size: 25px; margin-bottom: 8px;">
                                ${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}
                            </div>
                            <p style="color: #475569; font-size: 20px; line-height: 1.5; white-space: pre-line;">
                                ${review.comment}
                            </p>
                        </div>
                    `;
                });
            })
            .catch(err => console.error("Ошибка загрузки списка отзывов:", err));
    }
});
