from flask import Blueprint, request, jsonify
from app import db
from app.models import Task, Category
from app.schemas import TaskSchema, TaskListSchema, TaskDetailSchema
from marshmallow import ValidationError
from app.jobs import should_queue_notification, send_notification
import redis
from rq import Queue
import os

# Create Blueprint for task-related endpoints
tasks_bp = Blueprint('tasks', __name__)

# Initialize Redis connection and job queue for background notifications
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
redis_conn = redis.from_url(redis_url)
q = Queue(connection=redis_conn)

# Initialize Marshmallow schema instances for data serialization/deserialization
task_schema = TaskSchema()
tasks_list_schema = TaskListSchema()


@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Retrieve all tasks with optional filtering by completion status.
    
    Query Parameters:
        completed (optional): Filter by completion status ('true' or 'false')
    
    Returns:
        200: JSON response with list of all tasks matching the filter
    """
    # Parse optional completion filter from query params
    completed = request.args.get('completed', type=lambda x: x.lower() == 'true')
    
    # Start with base query
    query = Task.query
    
    # Apply filter if provided
    if completed is not None:
        query = query.filter_by(completed=completed)
    
    # Fetch all matching tasks and serialize
    tasks = query.all()
    result = tasks_list_schema.dump({'tasks': tasks})
    return jsonify(result), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Retrieve a single task by its ID.
    
    Returns:
        200: JSON response with the task details
        404: If task with given ID doesn't exist
    """
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    result = task_schema.dump(task)
    return jsonify(result), 200


@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task with optional due date and category assignment.
    
    Request Body:
        title (required): Task title (1-100 characters)
        description (optional): Detailed description (max 500 characters)
        due_date (optional): When task is due (ISO 8601 format)
        category_id (optional): ID of category to assign task to
    
    Returns:
        201: JSON with created task details and notification_queued status
        400: If validation fails or category doesn't exist
    """
    # Get JSON data
    json_data = request.get_json()
    if not json_data:
        return jsonify({'errors': {'_form': ['No JSON data provided']}}), 400
    
    # Validate incoming data against schema
    try:
        data = task_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Verify that referenced category exists (if provided)
    if data.get('category_id'):
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'errors': {'category_id': ['Category not found']}}), 400
    
    # Create and save new task
    task = Task(
        title=data['title'],
        description=data.get('description'),
        completed=data.get('completed', False),
        due_date=data.get('due_date'),
        category_id=data.get('category_id')
    )
    db.session.add(task)
    db.session.commit()
    
    # Check if we should queue a reminder notification for this task
    notification_queued = False
    if should_queue_notification(task.due_date):
        q.enqueue(send_notification, task.id, task.title)
        notification_queued = True
    
    result = task_schema.dump(task)
    response = {
        'task': result,
        'notification_queued': notification_queued
    }
    return jsonify(response), 201


@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task with partial or complete data.
    
    Request Body:
        Any subset of: title, description, completed, due_date, category_id
    
    Returns:
        200: JSON with updated task details
        404: If task doesn't exist
        400: If validation fails or category doesn't exist
    """
    # Fetch the task to update
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Validate incoming data (partial=True allows partial updates)
    try:
        data = task_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Verify category exists if one is being assigned
    if 'category_id' in data and data['category_id']:
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'errors': {'category_id': ['Category not found']}}), 400
    
    # Apply updates to task
    for key, value in data.items():
        setattr(task, key, value)
    
    db.session.commit()
    
    result = task_schema.dump(task)
    return jsonify(result), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task by its ID.
    
    Returns:
        200: Confirmation message
        404: If task doesn't exist
    """
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Remove task from database
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted'}), 200
