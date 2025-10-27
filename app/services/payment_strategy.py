class PaymentStrategy:
    def pay(self, order_id, amount):
        raise NotImplementedError


class PayPalPayment(PaymentStrategy):
    def pay(self, order_id, amount):
        print(f"[PayPal] Payment successful for order #{order_id} - ${amount}")
        return {
            "success": True,
            "status": "success",
            "transaction_id": f"PAYPAL-{order_id}",
            "message": f"Payment of ${amount} completed via PayPal."
        }


class CreditCardPayment(PaymentStrategy):
    def pay(self, order_id, amount):
        print(f"[CreditCard] Payment successful for order #{order_id} - ${amount}")
        return {
            "success": True,
            "status": "success",
            "transaction_id": f"CREDIT-{order_id}",
            "message": f"Payment of ${amount} completed via Credit Card."
        }
    
class TestPendingPayment:
    def pay(self, order_id, amount):
        return {
            "success": False,
            "message": "Payment intentionally left pending for testing",
            "status": "pending",
            "transaction_id": f"TEST-PENDING-{order_id}"
        }
