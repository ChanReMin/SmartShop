from app import db

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10,2), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    inventory = db.relationship("Inventory", uselist=False, back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        db.Index('ix_products_name_price', "name", "price"),
    )

    @property
    def stock(self):
        """Shortcut để lấy stock từ Inventory."""
        return self.inventory.quantity if self.inventory else 0

    @property
    def available_stock(self):
        """Stock thực tế có thể bán (trừ reserved)."""
        if not self.inventory:
            return 0
        return max(0, self.inventory.quantity - self.inventory.reserved_quantity)

    def is_available(self, quantity=1):
        """
        ✅ Business logic: Kiểm tra có đủ hàng không.
        Không thay đổi database, chỉ check.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        if not self.inventory:
            return False
        
        return self.available_stock >= quantity

    def calculate_total_price(self, quantity):
        """✅ Business logic: Tính tổng tiền."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        return float(self.price) * quantity

    def validate_price(self):
        """✅ Business logic: Validate giá."""
        if self.price <= 0:
            raise ValueError("Price must be greater than 0")

    def validate_sku(self):
        """✅ Business logic: Validate SKU format."""
        if not self.sku or len(self.sku) < 3:
            raise ValueError("SKU must be at least 3 characters")
    
    def to_dict(self, include_stock=False):
        """Convert to dictionary for API response."""
        data = {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "category_id": self.category_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        if include_stock and self.inventory:
            data["stock"] = self.stock
            data["available_stock"] = self.available_stock
            data["reserved_stock"] = self.inventory.reserved_quantity
        
        return data

    def to_summary(self):
        """Lightweight dict cho list views."""
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "price": float(self.price)
        }

    def __repr__(self):
        stock_info = f"Stock: {self.stock}" if self.inventory else "No inventory"
        return f"<Product {self.name} ({stock_info})>"