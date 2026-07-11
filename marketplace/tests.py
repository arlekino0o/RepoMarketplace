from django.test import TestCase
from django.urls import reverse

from .models import Category, Message, Order, Repository, RepositoryCategory, Review, User


class MarketplaceFlowTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='safe-password',
            role=User.Role.BUYER,
        )
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='safe-password',
            role=User.Role.SELLER,
        )
        self.category = Category.objects.create(name='Python', slug='python')
        self.repository = Repository.objects.create(
            seller=self.seller,
            title='Useful repository',
            price='10.00',
            language='Python',
            repo_url='https://example.com/repository',
            status=Repository.Status.ACTIVE,
        )
        RepositoryCategory.objects.create(repository=self.repository, category=self.category)
        self.client.force_login(self.buyer)

    def test_category_page_shows_its_repositories(self):
        response = self.client.get(
            reverse('marketplace:category_detail', kwargs={'slug': self.category.slug})
        )

        self.assertContains(response, self.repository.title)

    def test_purchase_and_payment(self):
        response = self.client.post(
            reverse('marketplace:order_create', kwargs={'repository_id': self.repository.pk})
        )

        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(buyer=self.buyer, repository=self.repository)

        response = self.client.post(reverse('marketplace:payment_create', kwargs={'pk': order.pk}))

        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(order.payment.status, order.payment.Status.SUCCESS)

    def test_send_message(self):
        response = self.client.post(
            reverse('marketplace:message_conversation', kwargs={'user_id': self.seller.pk}),
            {'text': 'Hello'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Message.objects.filter(sender=self.buyer, receiver=self.seller, text='Hello').exists()
        )

    def test_paid_order_can_receive_one_review(self):
        order = Order.objects.create(
            buyer=self.buyer,
            repository=self.repository,
            price=self.repository.price,
            status=Order.Status.PAID,
        )

        response = self.client.post(
            reverse('marketplace:review_create', kwargs={'order_id': order.pk}),
            {'rating': 5, 'comment': 'Useful repository.'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(order=order, rating=5).exists())
        self.assertEqual(
            self.client.get(
                reverse('marketplace:review_list', kwargs={'repository_id': self.repository.pk})
            ).status_code,
            200,
        )

    def test_cart_api_creates_orders_at_checkout(self):
        response = self.client.post(
            reverse('marketplace:cart_api'),
            data='{"repository_id": %d, "quantity": 2}' % self.repository.pk,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['items'][0]['quantity'], 2)

        response = self.client.post(reverse('marketplace:cart_checkout_api'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Order.objects.filter(buyer=self.buyer, repository=self.repository).exists())


class AuthenticationTests(TestCase):
    def test_register_creates_authenticated_user(self):
        response = self.client.post(
            reverse('marketplace:register'),
            {
                'username': 'new-user',
                'email': 'new-user@example.com',
                'role': User.Role.BUYER,
                'password1': 'safe-password-123',
                'password2': 'safe-password-123',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='new-user')
        self.assertTrue(user.check_password('safe-password-123'))
