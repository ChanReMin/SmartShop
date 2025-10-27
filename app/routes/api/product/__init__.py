# app/routes/product/__init__.py
from flask import Blueprint, request, jsonify
from app.services.product_service import ProductService
import logging

logger = logging.getLogger(__name__)

api_product_bp = Blueprint('api_product_bp', __name__, url_prefix='/products')

# ========================================
# ✅ PUBLIC ENDPOINTS (Không cần auth)
# ========================================

@api_product_bp.route('', methods=['GET'])
def get_products():
    """
    Get all products (public view).
    
    Query params:
    - page: int (default: 1)
    - per_page: int (default: 20, max: 100)
    - order_by: id|name|price (default: id)
    - desc: true|false (default: true)
    - category_id: filter by category
    - in_stock_only: true|false (default: false)
    """
    try:
        # Parse query params
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        order_by = request.args.get('order_by', 'id')
        desc = request.args.get('desc', 'true').lower() == 'true'
        category_id = request.args.get('category_id', type=int)
        in_stock_only = request.args.get('in_stock_only', 'false').lower() == 'true'
        
        product_service = ProductService()
        
        # Filter by category
        if category_id:
            products = product_service.get_products_by_category(category_id)
        else:
            products = product_service.get_all_products(
                order_by=order_by,
                desc=desc,
                include_inventory=True
            )
        
        # Filter in stock only
        if in_stock_only:
            products = [p for p in products if p.stock > 0]
        
        # Manual pagination (hoặc dùng repo.get_paginated)
        total = len(products)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_products = products[start:end]
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
            'products': [p.to_dict(include_stock=True) for p in paginated_products]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get products: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get products'}), 500


@api_product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product detail."""
    try:
        product_service = ProductService()
        product = product_service.get_product(product_id, with_inventory=True)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # ✅ Check if product có sẵn hàng
        is_in_stock = product.stock > 0
        
        return jsonify({
            'product': {
                **product.to_dict(include_stock=True),
                'is_in_stock': is_in_stock,
                'is_available': product.is_available(1)  # Business logic từ model
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get product {product_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get product'}), 500


@api_product_bp.route('/search', methods=['GET'])
def search_products():
    """
    Search products by name.
    Query params: ?q=search_term&limit=10
    """
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    if limit < 1 or limit > 50:
        return jsonify({'error': 'Limit must be between 1 and 50'}), 400
    
    try:
        product_service = ProductService()
        products = product_service.search_products(query, limit)
        
        return jsonify({
            'query': query,
            'count': len(products),
            'products': [p.to_summary() for p in products]  # Lightweight response
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to search products: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to search products'}), 500


@api_product_bp.route('/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    """Get all products in a category."""
    try:
        product_service = ProductService()
        products = product_service.get_products_by_category(category_id)
        
        # Filter only in-stock products for public view (optional)
        in_stock_only = request.args.get('in_stock_only', 'false').lower() == 'true'
        if in_stock_only:
            products = [p for p in products if p.stock > 0]
        
        return jsonify({
            'category_id': category_id,
            'count': len(products),
            'products': [p.to_dict(include_stock=True) for p in products]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get products by category: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get products'}), 500


@api_product_bp.route('/check-availability', methods=['POST'])
def check_availability():
    """
    Check if products are available in requested quantities.
    
    Request body:
    {
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ]
    }
    
    Response:
    {
        "available": true/false,
        "items": [
            {
                "product_id": 1,
                "requested": 2,
                "available": true,
                "current_stock": 10
            },
            ...
        ]
    }
    """
    data = request.get_json()
    if not data or 'items' not in data:
        return jsonify({'error': 'Request must contain "items" array'}), 400
    
    items = data['items']
    if not isinstance(items, list) or not items:
        return jsonify({'error': 'Items must be a non-empty array'}), 400
    
    try:
        product_service = ProductService()
        
        results = []
        all_available = True
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            if not product_id:
                continue
            
            product = product_service.get_product(product_id, with_inventory=True)
            
            if not product:
                results.append({
                    'product_id': product_id,
                    'requested': quantity,
                    'available': False,
                    'error': 'Product not found'
                })
                all_available = False
                continue
            
            is_available = product.is_available(quantity)
            
            results.append({
                'product_id': product_id,
                'product_name': product.name,
                'requested': quantity,
                'available': is_available,
                'current_stock': product.stock,
                'available_stock': product.available_stock
            })
            
            if not is_available:
                all_available = False
        
        return jsonify({
            'available': all_available,
            'items': results
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to check availability: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to check availability'}), 500