from flask import Blueprint, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.inventory_log import InventoryLog

user_bp = Blueprint('user', __name__)

@user_bp.route('/index')
@jwt_required(optional=True)
def index():
    current_user_id = get_jwt_identity()

    if isinstance(current_user_id, dict):
        current_user_id = current_user_id.get("id")
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return render_template('user/index.html', user=user)

@user_bp.route('/products')
@jwt_required()
def products():
    products = Product.query.all()
    return render_template('user/products.html', products=products)

@user_bp.route('/orders')
@jwt_required()
def orders():
    orders = Order.query.filter_by(user_id=get_jwt_identity()['id']).all()
    return render_template('user/orders.html', orders=orders)

@user_bp.route('/inventory')
@jwt_required()
def inventory():
    inventory = InventoryLog.query.filter_by(user_id=get_jwt_identity()['id']).all()
    return render_template('user/inventory.html', inventory=inventory)
