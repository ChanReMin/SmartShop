from flask import Blueprint

product_bp = Blueprint('product', __name__)

@product_bp.route('/')
def index():
    return {"message": "product bp"}