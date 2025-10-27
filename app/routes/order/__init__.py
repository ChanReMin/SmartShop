from flask import Blueprint

order_bp = Blueprint('order', __name__)

@order_bp.route('/')
def index():
    return {"message": "order bp"}