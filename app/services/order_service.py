# app/services/order_service.py
from app import db
from app.repositories import OrderRepository, ProductRepository, InventoryRepository
from app.models.order import OrderStatus

import logging

logger = logging.getLogger(__name__)
class OrderService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.order_repo = OrderRepository(self.session)
        self.inventory_repo = InventoryRepository(self.session)
        self.product_repo = ProductRepository(self.session)
    
    def create_order(self, user_id, items, total_amount=0, status=OrderStatus.PENDING.value):
        """Tạo đơn hàng (mặc định pending)."""
        try:
            order = self.order_repo.create_order(user_id, total_amount)
            self.order_repo.add_items(order, items)
            order.status = status
            self.session.flush()
            logger.info(f"Order {order.id} created with status {status}")
            return order
        except Exception as e:
            logger.error(f"Failed to create order: {str(e)}")
            raise

    def reduce_inventory_after_payment(self, items):
        """Trừ kho sau thanh toán (với lock)."""
        try:
            for item in items:
                self.inventory_repo.reduce_stock(item["product_id"], item["quantity"])
            self.session.flush()
            logger.info(f"Reduced inventory for {len(items)} items")
        except Exception as e:
            logger.error(f"Failed to reduce inventory: {str(e)}")
            raise

    def get_order_with_items(self, order_id):
        return self.order_repo.get_order_with_items(order_id)

    def get_orders_by_user(self, user_id):
        return self.order_repo.get_orders_by_user(user_id)
    
    def update_order_status(self, order_id, status):
        try:
            order = self.order_repo.update_status(order_id, status)
            logger.info(f"Order {order_id} status updated to {status}")
            return order
        except Exception as e:
            logger.error(f"Failed to update order status: {str(e)}")
            raise

    def get_pending_orders(self):
        return self.order_repo.get_pending_orders()
