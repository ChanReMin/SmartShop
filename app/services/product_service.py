# app/services/product_service.py
from app.repositories import ProductRepository, InventoryRepository
from app import db
import logging

logger = logging.getLogger(__name__)

class ProductService:
    """
    ✅ Service layer để orchestrate business logic.
    Coordinate giữa ProductRepository và InventoryRepository.
    """
    
    def __init__(self, session=None):
        self.session = session or db.session
        self.product_repo = ProductRepository(self.session)
        self.inventory_repo = InventoryRepository(self.session)

    # ========================================
    # ✅ PRODUCT OPERATIONS
    # ========================================

    def get_all_products(self, order_by='id', desc=True, include_inventory=True):
        """
        Get all products.
        Use include_inventory=True khi cần show stock info.
        """
        if include_inventory:
            return self.product_repo.get_all_with_inventory(order_by, desc)
        return self.product_repo.get_all_ordered(order_by, desc)

    def get_product(self, product_id, with_inventory=True):
        """Get single product."""
        if with_inventory:
            return self.product_repo.get_by_id_with_inventory(product_id)
        return self.product_repo.get_by_id(product_id)

    def search_products(self, name, limit=10):
        """Search products by name."""
        return self.product_repo.search_by_name(name, limit)

    def get_products_by_category(self, category_id):
        """Get products in a category."""
        return self.product_repo.get_by_category(category_id)

    def create_product(self, sku, name, price, category_id, description=None, initial_stock=0):
        """
        Create product and inventory.
        """
        try:
            product = self.product_repo.create_with_inventory(
                sku=sku,
                name=name,
                price=price,
                category_id=category_id,
                description=description,
                initial_stock=initial_stock
            )
            
            return {
                "success": True,
                "product": product.to_dict(include_stock=True),
                "message": "Product created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create product: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def update_product(self, product_id, **kwargs):
        """
        Update product.
        """
        try:
            product = self.product_repo.update_product(product_id, **kwargs)
            
            return {
                "success": True,
                "product": product.to_dict(include_stock=True),
                "message": "Product updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to update product: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def delete_product(self, product_id):
        """
        Delete product.
        """
        try:
            # Check if product exists in any pending orders
            # (Optional: add this check if needed)
            
            success = self.product_repo.delete_product(product_id)
            
            if success:
                return {
                    "success": True,
                    "message": "Product deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Product not found"
                }
                
        except Exception as e:
            logger.error(f"Failed to delete product: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    # ========================================
    # ✅ INVENTORY OPERATIONS
    # ========================================

    def get_product_stock(self, product_id):
        """Get current stock level."""
        inventory = self.inventory_repo.get_inventory_by_product(product_id)
        if not inventory:
            return {
                "success": False,
                "error": "Inventory not found"
            }
        
        return {
            "success": True,
            "stock": inventory.quantity,
            "available": inventory.quantity - inventory.reserved_quantity,
            "reserved": inventory.reserved_quantity
        }

    def update_stock(self, product_id, new_quantity):
        """
        Update stock level (for admin/stock adjustment).
        """
        try:
            inventory = self.inventory_repo.get_inventory_by_product(product_id)
            if not inventory:
                raise ValueError(f"Inventory not found for product {product_id}")
            
            old_quantity = inventory.quantity
            inventory.quantity = new_quantity
            self.session.commit()
            
            logger.info(f"Updated stock for product {product_id}: {old_quantity} -> {new_quantity}")
            
            return {
                "success": True,
                "old_stock": old_quantity,
                "new_stock": new_quantity,
                "message": "Stock updated successfully"
            }
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update stock: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def adjust_stock(self, product_id, adjustment, reason=None):
        """
        Adjust stock by delta (+/-).
        For manual adjustments (damage, returns, etc.)
        """
        try:
            inventory = self.inventory_repo.get_inventory_by_product(product_id)
            if not inventory:
                raise ValueError(f"Inventory not found for product {product_id}")
            
            old_quantity = inventory.quantity
            inventory.quantity += adjustment
            
            if inventory.quantity < 0:
                raise ValueError("Stock cannot be negative")
            
            self.session.commit()
            
            logger.info(
                f"Adjusted stock for product {product_id}: {old_quantity} -> {inventory.quantity} "
                f"(delta: {adjustment:+d}). Reason: {reason}"
            )
            
            return {
                "success": True,
                "old_stock": old_quantity,
                "new_stock": inventory.quantity,
                "adjustment": adjustment,
                "message": "Stock adjusted successfully"
            }
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to adjust stock: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    # ========================================
    # ✅ REPORTING
    # ========================================

    def get_low_stock_report(self, threshold=10):
        """Get products with low stock."""
        products = self.product_repo.get_low_stock_products(threshold)
        
        return {
            "success": True,
            "count": len(products),
            "threshold": threshold,
            "products": [
                {
                    **p.to_dict(),
                    "stock": p.stock,
                    "available": p.available_stock
                }
                for p in products
            ]
        }

    def get_out_of_stock_report(self):
        """Get out of stock products."""
        products = self.product_repo.get_out_of_stock_products()
        
        return {
            "success": True,
            "count": len(products),
            "products": [p.to_dict() for p in products]
        }

    def get_product_stats(self):
        """Get overall product statistics."""
        total = self.product_repo.get_total_count()
        in_stock = len(self.product_repo.get_in_stock_products())
        out_of_stock = len(self.product_repo.get_out_of_stock_products())
        low_stock = len(self.product_repo.get_low_stock_products())
        
        return {
            "success": True,
            "stats": {
                "total_products": total,
                "in_stock": in_stock,
                "out_of_stock": out_of_stock,
                "low_stock": low_stock,
                "in_stock_percentage": round((in_stock / total * 100) if total > 0 else 0, 2)
            }
        }