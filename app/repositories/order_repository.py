# app/repositories/order_repository.py
from .base_repository import BaseRepository
from app.models.order import Order, OrderItem

class OrderRepository(BaseRepository):
    def __init__(self, session=None):
        super().__init__(Order, session)

    def create_order(self, user_id, total_amount=0):
        """Tạo đơn hàng mới (chưa commit)."""
        order = Order(user_id=user_id, total_amount=total_amount)
        self.session.add(order)
        self.session.flush()
        return order

    def add_items(self, order, items):
        """Thêm danh sách sản phẩm vào đơn hàng."""
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"]
            )
            self.session.add(order_item)

    def update_status(self, order_id, status):
        order = self.get_order_with_items(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        order.status = status
        self.session.flush()
        return order

    def get_orders_by_user(self, user_id):
        return self.session.query(Order).filter_by(user_id=user_id).all()

    def get_order_with_items(self, order_id):
        return self.session.query(Order).filter_by(id=order_id).first()
    
    def get_pending_orders(self):
        """Lấy tất cả order có status PENDING"""
        return self.session.query(Order).filter(Order.status == "PENDING").all()
