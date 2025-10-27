from .base_repository import BaseRepository
from app.models.inventory import Inventory

import logging
logger = logging.getLogger(__name__)

class InventoryRepository(BaseRepository):
    def __init__(self, session=None):
        super().__init__(Inventory, session)

    def get_by_product_id(self, product_id):
        return self.session.query(Inventory).filter_by(product_id=product_id).first()

    def reduce_stock_with_lock(self, product_id, quantity):
        """
        ✅ Thread-safe stock reduction với SELECT FOR UPDATE.
        Đảm bảo không có race condition khi nhiều requests đồng thời.
        """
        try:
            # Lock row để tránh concurrent updates
            inventory = (
                self.session.query(Inventory)
                .filter_by(product_id=product_id)
                .with_for_update()
                .first()
            )
            
            if not inventory:
                logger.error(f"Inventory not found for product {product_id}")
                return False
            
            available = inventory.quantity - inventory.reserved_quantity
            if available < quantity:
                logger.warning(
                    f"Insufficient stock for product {product_id}. "
                    f"Available: {inventory.quantity}, Requested: {quantity}"
                )
                return False
            
            # Trừ kho
            old_quantity = inventory.quantity
            inventory.quantity -= quantity
            inventory.reserved_quantity -= quantity
            
            logger.info(
                f"Reduced stock for product {product_id}: "
                f"{old_quantity} -> {inventory.quantity}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error reducing stock: {str(e)}")
            raise

    def increase_stock(self, product_id, quantity):
        """Hoàn trả kho khi cần rollback."""
        inventory = self.get_by_product_id(product_id)
        if not inventory:
            raise ValueError(f"Inventory not found for product {product_id}")
        
        inventory.quantity += quantity
        logger.info(f"Increased stock for product {product_id}: +{quantity}")


    def check_stock_availability(self, product_id, required_quantity):
        """
        Return: (available: bool, current_stock: int)
        """
        inventory = self.get_by_product_id(product_id)
        if not inventory:
            return False, 0
        
        available = inventory.quantity - inventory.reserved_quantity
        return available >= required_quantity, available
    

    def bulk_check_stock(self, items):
        """
        ✅ Kiểm tra nhiều sản phẩm cùng lúc (tối ưu query).
        items: [{"product_id": 1, "quantity": 2}, ...]
        Return: list of insufficient items
        """
        product_ids = [item["product_id"] for item in items]
        
        # Lấy tất cả inventory records trong 1 query
        inventories = (
            self.session.query(Inventory)
            .filter(Inventory.product_id.in_(product_ids))
            .all()
        )
        
        # Map product_id -> inventory
        inventory_map = {inv.product_id: inv for inv in inventories}
        
        insufficient = []
        for item in items:
            product_id = item["product_id"]
            required_qty = item["quantity"]
            
            inventory = inventory_map.get(product_id)
            
            if not inventory:
                insufficient.append({
                    "product_id": product_id,
                    "error": "Inventory not found",
                    "available": 0,
                    "required": required_qty
                })
            else:
                available = inventory.quantity - inventory.reserved_quantity
                if available < required_qty:
                    insufficient.append({
                        "product_id": product_id,
                        "error": "Insufficient stock",
                        "available": available,
                        "required": required_qty
                    })
        
        return insufficient

    def reserve_stock(self, product_id, quantity):
        """Tăng reserved_quantity với SELECT FOR UPDATE để tránh race condition."""
        try:
            inventory = (
                self.session.query(Inventory)
                .filter_by(product_id=product_id)
                .with_for_update()
                .first()
            )
            if not inventory:
                raise ValueError(f"Inventory not found for product {product_id}")
            
            available = inventory.quantity - inventory.reserved_quantity
            if available < quantity:
                raise ValueError(
                    f"Cannot reserve {quantity} items for product {product_id}, only {inventory.quantity} available"
                )
            
            inventory.reserved_quantity += quantity
            self.session.flush()
            return True
        except Exception as e:
            raise

    def release_reserved_stock(self, product_id, quantity):
        inventory = self.get_by_product_id(product_id)
        if not inventory:
            raise ValueError(f"Inventory not found for product {product_id}")
        
        release_qty = min(quantity, inventory.reserved_quantity)
        inventory.reserved_quantity -= release_qty
        self.session.flush()
        logger.info(
            f"Released {release_qty} reserved stock for product {product_id}, remaining reserved: {inventory.reserved_quantity}"
        )