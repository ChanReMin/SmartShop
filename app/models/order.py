# app/models/order.py
from app import db
from datetime import datetime
from enum import Enum
from app.models.order_item import OrderItem

class OrderStatus(Enum):
    PENDING = "pending"        # Chờ xác nhận
    PAID = "paid"              # Đã thanh toán
    CONFIRMED = "confirmed"    # Đã xác nhận xử lý
    SHIPPED = "shipped"        # Đang giao hàng
    DELIVERED = "delivered"    # Đã giao hàng
    CANCELLED = "cancelled"    # Đã hủy
    FAILED = "failed"          # Thanh toán thất bại

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(db.String(32), default=OrderStatus.PENDING.value, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan", lazy=True)

    def add_item(self, product_id, quantity, price):
        """Thêm item vào đơn hàng (chưa commit)."""
        item = OrderItem(order_id=self.id, product_id=product_id, quantity=quantity, price=price)
        db.session.add(item)
        return item

    def calculate_total(self):
        """Tính lại tổng tiền (chưa commit)."""
        self.total_amount = sum(item.total for item in self.items)

    def confirm(self):
        self.status = OrderStatus.CONFIRMED.value

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_amount": float(self.total_amount),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [item.to_dict() for item in self.items]
        }
