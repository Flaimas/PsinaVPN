from src.core.exceptions import AppError


class PaymentServiceError(AppError):
    """Ошибка при работе с с платежным шлюхом"""


class PaymentProviderUnavailableError(PaymentServiceError):
    """Ошибка при выборе отключенного/недоступного провайдера"""
