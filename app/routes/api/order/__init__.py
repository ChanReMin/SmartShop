# app/routes/order_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.order_facade import OrderFacade
from app.services.payment_strategy import PayPalPayment, CreditCardPayment

api_order_bp = Blueprint('api_order', __name__, url_prefix='/order')

@api_order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    user_id = data.get('user_id')
    items = data.get('items', [])
    payment_method = data.get('payment', 'creditcard')

    result = OrderFacade.place_order(user_id, items, payment_method)
    return jsonify(result)


@api_order_bp.route('/<int:order_id>', methods=['GET'], endpoint='get_order')
@jwt_required()
def get_order(order_id):
    result = OrderFacade.get_order(order_id)
    return jsonify(result)


@api_order_bp.route('/user/<int:user_id>', methods=['GET'], endpoint='get_user_orders')
@jwt_required()
def get_user_orders(user_id):
    result = OrderFacade.get_user_orders(user_id)
    return jsonify(result)

@api_order_bp.route('/<int:order_id>/cancel', methods=['POST'], endpoint='cancel_order')
@jwt_required()
def cancel_order(order_id):
    """
    Hủy đơn hàng — chỉ chủ đơn mới được hủy.
    Body (optional): {"reason": "Lý do hủy"}
    """
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    reason = data.get('reason', None)
    
    result = OrderFacade.cancel_order(order_id, current_user_id, reason=reason)
    
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code

@api_order_bp.route('/<int:order_id>/pay', methods=['POST'], endpoint='pay_order')
@jwt_required()
def pay_order(order_id):
    """
    Thanh toán một đơn hàng đang ở trạng thái PENDING.
    Body: {"payment": "creditcard"}  (hoặc "paypal")
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    payment_method = data.get('payment')

    if not payment_method:
        return jsonify({"success": False, "error": "payment is required"}), 400

    result = OrderFacade.pay_pending_order(order_id, current_user_id, payment_method)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code
