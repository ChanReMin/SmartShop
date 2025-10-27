# app/routes/admin/product_routes.py
from flask import Blueprint, request, jsonify
from app.services.product_service import ProductService
from app.utils.decorators import admin_required
import logging

logger = logging.getLogger(__name__)

api_admin_product_bp = Blueprint('api_admin_products', __name__, url_prefix='/products')

# ========================================
# ✅ CREATE PRODUCT
# ========================================
@api_admin_product_bp.route('', methods=['POST'])
@admin_required
def create_product():
    """
    ✅ Refactored: Gọi ProductService thay vì query DB trực tiếp.
    
    Request body:
    {
        "sku": "SKU001",
        "name": "Product Name",
        "price": 100.00,
        "category_id": 1,
        "description": "Optional description",
        "initial_stock": 50  // ✅ Thay vì "stock"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    # ✅ Validate required fields
    required_fields = ['sku', 'name', 'price', 'category_id']
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        return jsonify({
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400

    try:
        # ✅ Validate data types
        sku = str(data['sku']).strip()
        name = str(data['name']).strip()
        price = float(data['price'])
        category_id = int(data['category_id'])
        description = data.get('description', '')
        initial_stock = int(data.get('initial_stock', 0))  # ✅ Default 0
        
        # ✅ Business validation
        if not sku or len(sku) < 3:
            return jsonify({'error': 'SKU must be at least 3 characters'}), 400
        
        if not name or len(name) < 2:
            return jsonify({'error': 'Name must be at least 2 characters'}), 400
        
        if price <= 0:
            return jsonify({'error': 'Price must be greater than 0'}), 400
        
        if initial_stock < 0:
            return jsonify({'error': 'Initial stock cannot be negative'}), 400

        # ✅ Gọi Service
        product_service = ProductService()
        result = product_service.create_product(
            sku=sku,
            name=name,
            price=price,
            category_id=category_id,
            description=description,
            initial_stock=initial_stock
        )
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'message': result['message'],
            'product': result['product']
        }), 201

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to create product'}), 500


# ========================================
# ✅ UPDATE PRODUCT
# ========================================
@api_admin_product_bp.route('/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """
    ✅ Refactored: Gọi ProductService.
    
    Request body (all fields optional):
    {
        "sku": "SKU001",
        "name": "New Name",
        "price": 150.00,
        "category_id": 2,
        "description": "Updated description"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    try:
        # ✅ Build update dict (chỉ update fields được gửi lên)
        update_fields = {}
        
        if 'sku' in data:
            sku = str(data['sku']).strip()
            if not sku or len(sku) < 3:
                return jsonify({'error': 'SKU must be at least 3 characters'}), 400
            update_fields['sku'] = sku
        
        if 'name' in data:
            name = str(data['name']).strip()
            if not name or len(name) < 2:
                return jsonify({'error': 'Name must be at least 2 characters'}), 400
            update_fields['name'] = name
        
        if 'price' in data:
            price = float(data['price'])
            if price <= 0:
                return jsonify({'error': 'Price must be greater than 0'}), 400
            update_fields['price'] = price
        
        if 'category_id' in data:
            update_fields['category_id'] = int(data['category_id'])
        
        if 'description' in data:
            update_fields['description'] = data['description']
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400

        # ✅ Gọi Service
        product_service = ProductService()
        result = product_service.update_product(product_id, **update_fields)
        
        if not result['success']:
            if 'not found' in result['error'].lower():
                return jsonify({'error': 'Product not found'}), 404
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'message': result['message'],
            'product': result['product']
        }), 200

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"Failed to update product {product_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to update product'}), 500


# ========================================
# ✅ DELETE PRODUCT
# ========================================
@api_admin_product_bp.route('/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """
    ✅ Refactored: Gọi ProductService.
    Inventory sẽ tự động xóa (cascade).
    """
    try:
        product_service = ProductService()
        result = product_service.delete_product(product_id)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 404
        
        return jsonify({'message': result['message']}), 200
        
    except Exception as e:
        logger.error(f"Failed to delete product {product_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to delete product'}), 500


# ========================================
# ✅ GET SINGLE PRODUCT
# ========================================
@api_admin_product_bp.route('/<int:product_id>', methods=['GET'])
@admin_required
def get_product(product_id):
    """✅ Get single product với stock info."""
    try:
        product_service = ProductService()
        product = product_service.get_product(product_id, with_inventory=True)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'product': product.to_dict(include_stock=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get product {product_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get product'}), 500


# ========================================
# ✅ GET ALL PRODUCTS
# ========================================
@api_admin_product_bp.route('', methods=['GET'])
@admin_required
def get_all_products():
    """
    ✅ Get all products với filtering & sorting.
    
    Query params:
    - order_by: id|name|price (default: id)
    - desc: true|false (default: true)
    - category_id: filter by category
    """
    try:
        # Get query params
        order_by = request.args.get('order_by', 'id')
        desc = request.args.get('desc', 'true').lower() == 'true'
        category_id = request.args.get('category_id', type=int)
        
        product_service = ProductService()
        
        # Filter by category nếu có
        if category_id:
            products = product_service.get_products_by_category(category_id)
        else:
            products = product_service.get_all_products(
                order_by=order_by,
                desc=desc,
                include_inventory=True
            )
        
        return jsonify({
            'count': len(products),
            'products': [p.to_dict(include_stock=True) for p in products]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get products: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get products'}), 500


# ========================================
# ✅ SEARCH PRODUCTS
# ========================================
@api_admin_product_bp.route('/search', methods=['GET'])
@admin_required
def search_products():
    """
    Search products by name.
    Query params: ?q=search_term&limit=10
    """
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    if limit < 1 or limit > 100:
        return jsonify({'error': 'Limit must be between 1 and 100'}), 400
    
    try:
        product_service = ProductService()
        products = product_service.search_products(query, limit)
        
        return jsonify({
            'query': query,
            'count': len(products),
            'products': [p.to_dict(include_stock=True) for p in products]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to search products: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to search products'}), 500


# ========================================
# ✅ BONUS: UPDATE STOCK
# ========================================
@api_admin_product_bp.route('/<int:product_id>/stock', methods=['PUT'])
@admin_required
def update_stock(product_id):
    """
    Update stock level (admin manual adjustment).
    
    Request body:
    {
        "quantity": 100  // New stock level
    }
    
    OR
    
    {
        "adjustment": -5,  // Delta (+/-)
        "reason": "Damage"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    try:
        product_service = ProductService()
        
        # Check if it's absolute update or adjustment
        if 'quantity' in data:
            # Absolute update
            quantity = int(data['quantity'])
            if quantity < 0:
                return jsonify({'error': 'Quantity cannot be negative'}), 400
            
            result = product_service.update_stock(product_id, quantity)
        
        elif 'adjustment' in data:
            # Delta adjustment
            adjustment = int(data['adjustment'])
            reason = data.get('reason', 'Manual adjustment')
            
            result = product_service.adjust_stock(product_id, adjustment, reason)
        
        else:
            return jsonify({'error': 'Must provide either "quantity" or "adjustment"'}), 400
        
        if not result['success']:
            if 'not found' in result['error'].lower():
                return jsonify({'error': 'Product not found'}), 404
            return jsonify({'error': result['error']}), 400
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update stock: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to update stock'}), 500


# ========================================
# ✅ BONUS: INVENTORY REPORTS
# ========================================
@api_admin_product_bp.route('/reports/low-stock', methods=['GET'])
@admin_required
def low_stock_report():
    """Get products with low stock. Query param: ?threshold=10"""
    threshold = request.args.get('threshold', 10, type=int)
    
    try:
        product_service = ProductService()
        result = product_service.get_low_stock_report(threshold)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to get low stock report: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get report'}), 500


@api_admin_product_bp.route('/reports/out-of-stock', methods=['GET'])
@admin_required
def out_of_stock_report():
    """Get out of stock products."""
    try:
        product_service = ProductService()
        result = product_service.get_out_of_stock_report()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to get out of stock report: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get report'}), 500


@api_admin_product_bp.route('/stats', methods=['GET'])
@admin_required
def product_stats():
    """Get overall product statistics."""
    try:
        product_service = ProductService()
        result = product_service.get_product_stats()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to get product stats: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get stats'}), 500