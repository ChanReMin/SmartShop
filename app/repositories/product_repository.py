# app/repositories/product_repository.py
from .base_repository import BaseRepository
from app.models.product import Product
from app.models.inventory import Inventory
from app import db
import logging

logger = logging.getLogger(__name__)

class ProductRepository(BaseRepository):
    """
    ✅ Repository chứa TẤT CẢ database operations cho Product.
    Thay thế các methods đã xóa khỏi Product model.
    """
    
    def __init__(self, session=None):
        super().__init__(Product, session)

    # ========================================
    # ✅ QUERY METHODS (thay thế @classmethod trong Model)
    # ========================================
    
    def get_all_ordered(self, order_by='id', desc=True):
        """
        ✅ Thay thế Product.get_all_ordered()
        Get all products ordered by a specific column.
        """
        try:
            column = getattr(self.model, order_by, self.model.id)
            query = self.session.query(self.model)
            
            if desc:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)
            
            return query.all()
        except AttributeError:
            logger.warning(f"Invalid order_by column: {order_by}, using default 'id'")
            return self.session.query(self.model).order_by(self.model.id.desc()).all()

    def get_all_with_inventory(self, order_by='id', desc=True):
        """Get all products (inventory sẽ lazy load khi cần)."""
        column = getattr(self.model, order_by, self.model.id)
        query = self.session.query(self.model)
        
        if desc:
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column)
        
        return query.all()

    def get_by_sku(self, sku):
        """Get product by SKU."""
        return self.session.query(self.model).filter_by(sku=sku).first()

    def get_by_id_with_inventory(self, product_id):
        """Get product (inventory sẽ lazy load khi access product.inventory)."""
        return self.session.query(self.model).filter_by(id=product_id).first()

    def get_total_count(self):
        """
        ✅ Thay thế Product.get_total_count()
        Get total count of products.
        """
        return self.session.query(self.model).count()

    def search_by_name(self, name, limit=10):
        """Search products by name (case-insensitive)."""
        return (
            self.session.query(self.model)
            .filter(self.model.name.ilike(f'%{name}%'))
            .limit(limit)
            .all()
        )

    def get_by_category(self, category_id, order_by='name', desc=False):
        """Get all products in a category."""
        column = getattr(self.model, order_by, self.model.id)
        query = self.session.query(self.model).filter_by(category_id=category_id)
        
        if desc:
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column)
        
        return query.all()

    def get_in_stock_products(self, min_quantity=1):
        """Get products with stock >= min_quantity."""
        return (
            self.session.query(self.model)
            .join(Inventory)
            .filter(Inventory.quantity >= min_quantity)
            .all()
        )

    def get_low_stock_products(self, threshold=10):
        """Get products with stock below threshold."""
        return (
            self.session.query(self.model)
            .join(Inventory)
            .filter(Inventory.quantity < threshold)
            .filter(Inventory.quantity > 0)
            .all()
        )

    def get_out_of_stock_products(self):
        """Get products with 0 stock."""
        return (
            self.session.query(self.model)
            .join(Inventory)
            .filter(Inventory.quantity == 0)
            .all()
        )

    # ========================================
    # ✅ CREATE METHODS
    # ========================================

    def create_with_inventory(self, sku, name, price, category_id, description=None, initial_stock=0):
        """
        ✅ Enhanced: Tạo Product kèm Inventory mặc định.
        Validate trước khi tạo.
        """
        try:
            # Validate SKU unique
            existing = self.get_by_sku(sku)
            if existing:
                raise ValueError(f"SKU {sku} already exists")
            
            # Validate price
            if price <= 0:
                raise ValueError("Price must be greater than 0")
            
            # Create product
            product = Product(
                sku=sku,
                name=name,
                price=price,
                category_id=category_id,
                description=description
            )
            
            # Validate business rules
            product.validate_sku()
            product.validate_price()
            
            self.session.add(product)
            self.session.flush()  # Lấy product.id
            
            # Create inventory
            inventory = Inventory(
                product_id=product.id, 
                quantity=initial_stock,
                reserved_quantity=0
            )
            self.session.add(inventory)
            self.session.commit()
            
            logger.info(f"Created product {product.id} with inventory stock={initial_stock}")
            return product
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create product: {str(e)}")
            raise

    # ========================================
    # ✅ UPDATE METHODS (thay thế Model.update())
    # ========================================

    def update_product(self, product_id, **kwargs):
        """
        ✅ Thay thế product.update()
        Update product fields với validation.
        """
        try:
            product = self.get_by_id(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            # Validate sau khi update
            if 'price' in kwargs:
                product.validate_price()
            if 'sku' in kwargs:
                product.validate_sku()
            
            self.session.commit()
            logger.info(f"Updated product {product_id}")
            return product
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update product {product_id}: {str(e)}")
            raise

    def update_price(self, product_id, new_price):
        """Update price với validation riêng."""
        if new_price <= 0:
            raise ValueError("Price must be greater than 0")
        
        return self.update_product(product_id, price=new_price)

    # ========================================
    # ✅ DELETE METHODS (thay thế Model.delete())
    # ========================================

    def delete_product(self, product_id):
        """
        ✅ Thay thế product.delete()
        Delete product (inventory sẽ tự động xóa do cascade).
        """
        try:
            product = self.get_by_id(product_id)
            if not product:
                logger.warning(f"Product {product_id} not found for deletion")
                return False
            
            self.session.delete(product)
            self.session.commit()
            
            logger.info(f"Deleted product {product_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to delete product {product_id}: {str(e)}")
            raise

    def bulk_delete(self, product_ids):
        """Delete multiple products at once."""
        try:
            deleted_count = (
                self.session.query(self.model)
                .filter(self.model.id.in_(product_ids))
                .delete(synchronize_session=False)
            )
            self.session.commit()
            
            logger.info(f"Bulk deleted {deleted_count} products")
            return deleted_count
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to bulk delete products: {str(e)}")
            raise

    # ========================================
    # ✅ PAGINATION (bonus)
    # ========================================

    def get_paginated(self, page=1, per_page=20, order_by='id', desc=True):
        """
        Get paginated products.
        Returns: (products, total_count, total_pages)
        """
        column = getattr(self.model, order_by, self.model.id)
        query = self.session.query(self.model)
        
        if desc:
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column)
        
        # Get total count
        total_count = query.count()
        total_pages = (total_count + per_page - 1) // per_page
        
        # Get page data
        offset = (page - 1) * per_page
        products = query.offset(offset).limit(per_page).all()
        
        return products, total_count, total_pages