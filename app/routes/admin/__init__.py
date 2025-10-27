from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import admin_required
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.inventory_log import InventoryLog
from app.utils.auth_helpers import get_current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/index')
@jwt_required(optional=True)
def index():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get statistics using model methods
    total_products = Product.get_total_count()
    
    # Check if Order model exists
    try:
        from models.order import Order
        total_orders = Order.get_total_count()
        total_revenue = Order.get_total_revenue()
    except (ImportError, AttributeError):
        total_orders = 0
        total_revenue = 0
    
    # Check if User model exists
    try:
        total_users = User.get_total_count()
    except (ImportError, AttributeError):
        total_users = 0

    return render_template('admin/index.html',
                        user=user,
                        total_products=total_products,
                        total_orders=total_orders,
                        total_revenue=total_revenue,
                        total_users=total_users
                        )

@admin_bp.route('/products')
@admin_required
def product_index():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Number of products per page
    
    # Get all products
    all_products = Product.get_all()
    
    # Manual pagination
    total = len(all_products)
    start = (page - 1) * per_page
    end = start + per_page
    products = all_products[start:end]
    
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page
    
    return render_template(
        'admin/products/index.html',
        products=products,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        user=user
    )

@admin_bp.route('/orders')
@admin_required
def order_index():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Number of orders per page
    
    # Get all orders
    all_orders = Order.get_all()
    
    # Manual pagination
    total = len(all_orders)
    start = (page - 1) * per_page
    end = start + per_page
    orders = all_orders[start:end]
    
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page
    
    return render_template(
        'admin/orders/index.html',
        orders=orders,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        user=user
    )


@admin_bp.route('/users')
@admin_required
def user_index():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Number of orders per page
    
    # Get all orders
    all_users = User.get_all()
    print(all_users[:5])
    print(all_users[0].email)
    
    # Manual pagination
    total = len(all_users)
    start = (page - 1) * per_page
    end = start + per_page
    all_users = all_users[start:end]
    
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page
    
    return render_template(
        'admin/users/index.html',
        all_users=all_users,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        user=user
    )

