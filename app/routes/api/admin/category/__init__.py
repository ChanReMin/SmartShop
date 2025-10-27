from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.category import Category
from app.utils.decorators import admin_required
import time

api_admin_category_bp = Blueprint('api_admin_category', __name__, url_prefix='/category')


# GET /categories/<id> — Lấy chi tiết category
@api_admin_category_bp.route('/<int:category_id>', methods=['GET'])
@admin_required
def get_category(category_id):
    start_time = time.time()
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    exec_time = time.time() - start_time
    return jsonify({
        "category": category.to_dict(),
        "exec_time_seconds": round(exec_time, 6)
    }), 200


# GET /categories — Liệt kê tất cả categories (phân trang)
@api_admin_category_bp.route('', methods=['GET'])
@admin_required
def list_categories():
    start_time = time.time()
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # max 100

    paginated = Category.query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    exec_time = time.time() - start_time
    return jsonify({
        "categories": [cat.to_dict() for cat in paginated.items],
        "pagination": {
            "page": page,
            "pages": paginated.pages,
            "per_page": per_page,
            "total": paginated.total
        },
        "exec_time_seconds": round(exec_time, 6)
    }), 200


# POST /categories — Tạo category mới
@api_admin_category_bp.route('', methods=['POST'])
@admin_required
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # Validate required fields
    if 'name' not in data or not data['name'].strip():
        return jsonify({'error': 'Missing required field: name'}), 400

    # Kiểm tra name đã tồn tại chưa (unique)
    if Category.query.filter_by(name=data['name'].strip()).first():
        return jsonify({'error': 'Category name already exists'}), 400

    try:
        category = Category(
            name=data['name'].strip(),
            description=data.get('description', '').strip() or None
        )
        category.save()

        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201

    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to create category'}), 500


# PUT /categories/<id> — Cập nhật category
@api_admin_category_bp.route('/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # Cập nhật name (kiểm tra unique)
    if 'name' in data:
        new_name = data['name'].strip()
        if new_name != category.name:
            if Category.query.filter_by(name=new_name).first():
                return jsonify({'error': 'Category name already exists'}), 400
            category.name = new_name

    # Cập nhật description
    if 'description' in data:
        category.description = data['description'].strip() or None

    try:
        category.save()
        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update category'}), 500


# DELETE /categories/<id> — Xóa category
@api_admin_category_bp.route('/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    # Kiểm tra xem category có product nào không
    if category.products.first():
        return jsonify({'error': 'Cannot delete category with associated products'}), 400

    try:
        category.delete()
        return jsonify({'message': 'Category deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete category'}), 500