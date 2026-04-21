from flask import Blueprint, request, jsonify
from app import db
from app.models import Category, Task
from app.schemas import CategorySchema, CategoriesListSchema, CategoryDetailSchema
from marshmallow import ValidationError
from sqlalchemy import func

# Create Blueprint for category-related endpoints
categories_bp = Blueprint('categories', __name__)

# Initialize Marshmallow schema instances for data serialization/deserialization
category_schema = CategorySchema()
categories_list_schema = CategoriesListSchema()
category_detail_schema = CategoryDetailSchema()


@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """Retrieve all categories with the number of tasks in each.
    
    Returns:
        200: JSON response with list of all categories and their task counts
    """
    # Fetch all categories from database
    categories = Category.query.all()
    
    # Serialize each category and add task count
    result = []
    for cat in categories:
        cat_data = category_schema.dump(cat)
        cat_data['task_count'] = len(cat.tasks)  # Count associated tasks
        result.append(cat_data)
    
    return jsonify({'categories': result}), 200


@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Retrieve a single category with all its associated tasks.
    
    Returns:
        200: JSON with category details and list of tasks
        404: If category doesn't exist
    """
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Build response with category info and minimal task data
    result = {
        'id': category.id,
        'name': category.name,
        'color': category.color,
        'tasks': [
            {
                'id': task.id,
                'title': task.title,
                'completed': task.completed
            }
            for task in category.tasks
        ]
    }
    
    return jsonify(result), 200


@categories_bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new task category.
    
    Request Body:
        name (required): Category name (1-50 characters, must be unique)
        color (optional): Hex color code for UI display (#RRGGBB format)
    
    Returns:
        201: JSON with created category details
        400: If validation fails or name already exists
    """
    # Get JSON data
    try:
        json_data = request.get_json(force=True, silent=False)
    except Exception as e:
        return jsonify({'errors': {'_form': [f'Invalid JSON: {str(e)}']}}), 400
    
    if not json_data:
        return jsonify({'errors': {'_form': ['No JSON data provided']}}), 400
    
    # Validate incoming data
    try:
        data = category_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except TypeError as e:
        return jsonify({'errors': {'_form': [f'Type error during validation: {str(e)}']}}), 400
    
    # Ensure category name is unique
    existing = Category.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'errors': {'name': ['Category with this name already exists.']}}), 400
    
    # Create and save new category
    try:
        category = Category(
            name=data['name'],
            color=data.get('color')
        )
        db.session.add(category)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': {'_form': [f'Database error: {str(e)}']}}), 400
    
    # Build response with category info
    result = {
        'id': category.id,
        'name': category.name,
        'color': category.color
    }
    return jsonify(result), 201


@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category (only allowed if it has no associated tasks).
    
    Returns:
        200: Confirmation message
        400: If category contains tasks
        404: If category doesn't exist
    """
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Prevent deletion of categories with existing tasks
    if len(category.tasks) > 0:
        return jsonify({'error': 'Cannot delete category with existing tasks. Move or delete tasks first.'}), 400
    
    # Safe to delete - no tasks attached
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted'}), 200


@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update an existing category with partial or complete data.
    
    Request Body:
        Any subset of: name, color
    
    Returns:
        200: JSON with updated category details
        404: If category doesn't exist
        400: If validation fails or name already exists
    """
    # Fetch the category to update
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Get JSON data
    json_data = request.get_json()
    if not json_data:
        return jsonify({'errors': {'_form': ['No JSON data provided']}}), 400
    
    # Validate incoming data (partial=True allows partial updates)
    try:
        data = category_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Check if name is being changed and if new name already exists
    if 'name' in data and data['name'] != category.name:
        existing = Category.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'errors': {'name': ['Category with this name already exists.']}}), 400
    
    # Apply updates to category
    for key, value in data.items():
        setattr(category, key, value)
    
    db.session.commit()
    
    # Build response with category info
    result = {
        'id': category.id,
        'name': category.name,
        'color': category.color
    }
    return jsonify(result), 200
