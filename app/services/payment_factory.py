from .payment_strategy import PayPalPayment, CreditCardPayment, TestPendingPayment

class PaymentFactory:
    @staticmethod
    def get_strategy(method: str):
        method = method.lower()
        if method == "paypal":
            return PayPalPayment()
        elif method == "creditcard":
            return CreditCardPayment()
        elif method == "pending":
            return TestPendingPayment()
        else:
            raise ValueError(f"Unsupported payment method: {method}")
