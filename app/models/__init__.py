from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Import từng model
from .user import User
from .category import Category
from .inventory import Inventory
from .product import Product
from .order import Order, OrderItem
from .inventory_log import InventoryLog

# Export để có thể import từ app.models
__all__ = [
    "User",
    "Category",
    "Product",
    "Inventory",
    "Order",
    "OrderItem",
    "InventoryLog",
    "db"  # nếu bạn muốn export db
]