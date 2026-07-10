from .payment import MockPaymentProvider
from django.utils.module_loading import import_string
from config import settings


def get_payment_provider():
    provider_class = import_string(settings.PAYMENT_PROVIDER_CLASS)
    return provider_class()