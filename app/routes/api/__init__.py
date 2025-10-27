from flask import Blueprint
from app.routes.api.admin import api_admin_bp
from app.routes.api.user import api_user_bp
from app.routes.api.product import api_product_bp
from app.routes.api.order import api_order_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')
api_bp.register_blueprint(api_admin_bp)
api_bp.register_blueprint(api_user_bp)
api_bp.register_blueprint(api_order_bp)
api_bp.register_blueprint(api_product_bp)


@api_bp.route('/')
def index():
    return {"message": "Welcome to the API!"}
