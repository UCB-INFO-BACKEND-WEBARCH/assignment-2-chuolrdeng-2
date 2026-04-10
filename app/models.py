from app import db
from datetime import datetime


class Category(db.Model):
    """Represents a task category for organizing tasks."""
    __tablename__ = 'categories'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Category name must be unique (e.g., 'Work', 'Personal')
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Optional hex color code for UI display (e.g., '#FF5733')
    color = db.Column(db.String(7), nullable=True)
    
    # One-to-many relationship: a category has many tasks
    # Cascade delete ensures tasks are deleted when category is deleted
    tasks = db.relationship('Task', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Task(db.Model):
    """Represents a task that can be organized into categories."""
    __tablename__ = 'tasks'
    
    # Primary key, auto-generated
    id = db.Column(db.Integer, primary_key=True)
    
    # Task title (required, max 100 characters)
    title = db.Column(db.String(100), nullable=False)
    
    # Detailed description of the task (optional, max 500 characters)
    description = db.Column(db.Text, nullable=True)
    
    # Whether the task has been completed (defaults to False)
    completed = db.Column(db.Boolean, default=False)
    
    # When the task is due (optional, used for notifications)
    due_date = db.Column(db.DateTime, nullable=True)
    
    # Foreign key to Category (optional - not all tasks need a category)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    # Timestamps for auditing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.title}>'
