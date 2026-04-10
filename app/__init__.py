from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialize SQLAlchemy and Flask-Migrate for database operations
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Application factory function that creates and configures the Flask app."""
    app = Flask(__name__)
    
    # Configure database connection from environment variable,
    # defaults to local development PostgreSQL instance
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/task_manager')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models to register them with SQLAlchemy
    from app.models import Task, Category
    
    # Register API blueprints
    from app.routes.tasks import tasks_bp
    from app.routes.categories import categories_bp
    
    app.register_blueprint(tasks_bp)
    app.register_blueprint(categories_bp)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app
