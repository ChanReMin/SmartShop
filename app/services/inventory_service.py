# app/services/inventory_service.py
from app.repositories import ProductRepository, InventoryRepository
from app import db

import logging

logger = logging.getLogger(__name__)

class InventoryService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.product_repo = ProductRepository(self.session)
        self.inventory_repo = InventoryRepository(self.session)

    def check_stock(self, items):
        """
        ✅ Kiểm tra tồn kho của danh sách sản phẩm.
        Validate input và check inventory thông qua Inventory model.
        """
        if not items:
            return ["Cart is empty"]
        
        insufficient = []
        
        for item in items:
            # Validate quantity
            if item.get("quantity", 0) <= 0:
                insufficient.append(
                    f"Invalid quantity for product ID {item.get('product_id')}"
                )
                continue
            
            product_id = item["product_id"]
            required_qty = item["quantity"]
            
            # ✅ Check product exists
            product = self.product_repo.get_by_id(product_id)
            if not product:
                insufficient.append(f"Product ID {product_id} not found")
                continue
            
            # ✅ Check inventory thông qua Inventory model
            available, current_stock = self.inventory_repo.check_stock_availability(
                product_id, 
                required_qty
            )
            
            if not available:
                insufficient.append(
                    f"Not enough stock for {product.name}. "
                    f"Available: {current_stock}, Requested: {required_qty}"
                )
        
        return insufficient

    def check_stock_bulk(self, items):
        """
        ✅ Kiểm tra tồn kho tối ưu hơn (1 query thay vì N queries).
        Return: list of error messages
        """
        if not items:
            return ["Cart is empty"]
        
        # Validate quantities
        insufficient = []
        for item in items:
            if item.get("quantity", 0) <= 0:
                insufficient.append(
                    f"Invalid quantity for product ID {item.get('product_id')}"
                )
        
        if insufficient:
            return insufficient
        
        # ✅ Bulk check inventory
        inventory_issues = self.inventory_repo.bulk_check_stock(items)
        
        # Format error messages với tên sản phẩm
        for issue in inventory_issues:
            product = self.product_repo.get_by_id(issue["product_id"])
            product_name = product.name if product else f"Product {issue['product_id']}"
            
            if issue["error"] == "Inventory not found":
                insufficient.append(f"No inventory record for {product_name}")
            else:
                insufficient.append(
                    f"Not enough stock for {product_name}. "
                    f"Available: {issue['available']}, Requested: {issue['required']}"
                )
        
        return insufficient
    
    def reserve_stock(self, items):
        """Dành cho order PENDING."""
        for item in items:
            self.inventory_repo.reserve_stock(item["product_id"], item["quantity"])
        self.session.flush()

    def release_reserved_stock(self, items):
        for item in items:
            self.inventory_repo.release_reserved_stock(item["product_id"], item["quantity"])
        self.session.flush()

    def reduce_stock(self, items):
        """
        ✅ Trừ kho với SELECT FOR UPDATE để tránh race condition.
        Throw exception nếu không đủ hàng (double-check).
        """
        try:
            for item in items:
                success = self.inventory_repo.reduce_stock_with_lock(
                    item["product_id"], 
                    item["quantity"]
                )
                
                if not success:
                    # Lấy thông tin product để error message rõ ràng hơn
                    product = self.product_repo.get_by_id(item["product_id"])
                    product_name = product.name if product else f"Product {item['product_id']}"
                    
                    raise ValueError(
                        f"Failed to reduce stock for {product_name}. "
                        "Stock may have changed. Please try again."
                    )
            
            self.session.flush()
            logger.info(f"Successfully reduced stock for {len(items)} items")
            
        except Exception as e:
            logger.error(f"Stock reduction failed: {str(e)}")
            raise

    def restore_stock(self, items):
        """
        ✅ Hoàn trả kho (dùng khi cancel order hoặc rollback).
        """
        try:
            for item in items:
                self.inventory_repo.increase_stock(
                    item["product_id"], 
                    item["quantity"]
                )
            
            self.session.flush()
            logger.info(f"Successfully restored stock for {len(items)} items")
            
        except Exception as e:
            logger.error(f"Stock restoration failed: {str(e)}")
            raise

    def get_product_stock(self, product_id):
        """✅ Lấy số lượng tồn kho hiện tại của 1 sản phẩm."""
        inventory = self.inventory_repo.get_inventory_by_product(product_id)
        return inventory.quantity if inventory else 0

    def update_stock(self, product_id, new_quantity):
        """✅ Cập nhật số lượng tồn kho (dùng cho admin)."""
        inventory = self.inventory_repo.get_inventory_by_product(product_id)
        
        if not inventory:
            raise ValueError(f"Inventory not found for product {product_id}")
        
        old_quantity = inventory.quantity
        inventory.quantity = new_quantity
        self.session.commit()
        
        logger.info(
            f"Updated stock for product {product_id}: "
            f"{old_quantity} -> {new_quantity}"
        )
        
        return inventory
