import uuid
from abc import ABC, abstractmethod

class BasePaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, order_id: int, amount: float):
        pass

class MockPaymentProvider(BasePaymentProvider):
    def create_payment(self, order_id: int, amount: float):
        payment_id = str(uuid.uuid4())

        redirect_url = f'/orders/mock-payment-page/?order_id={order_id}&payment_id={payment_id}"'

        return {
            'payment_id': payment_id,
            'redirect_url': redirect_url,
        }