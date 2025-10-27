from app import db

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, 
        db.ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    reserved_quantity = db.Column(db.Integer, nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=False, default=0)

    # Quan hệ
    product = db.relationship("Product", back_populates="inventory")

    def restock(self, amount):
        if amount <= 0:
            raise ValueError("Số lượng nhập kho phải lớn hơn 0.")
        self.quantity += amount

    def reduce_stock(self, quantity):
        """Giảm hàng tồn kho (dành cho trường hợp quản lý inventory trực tiếp)"""
        if quantity <= 0:
            raise ValueError("Số lượng giảm phải lớn hơn 0.")
        if self.quantity < quantity:
            raise ValueError("Không đủ hàng tồn kho.")
        self.quantity -= quantity