from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
import re


class CategorySchema(Schema):
    """Schema for validating and serializing Category objects."""
    id = fields.Int(dump_only=True)  # Read-only
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    color = fields.Str(allow_none=True)  # Optional hex color
    task_count = fields.Int(dump_only=True)  # Computed field for API responses
    
    @validates('color')
    def validate_color(self, value):
        """Validate that color is a valid hex code format (#RRGGBB)."""
        if value is not None:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
                raise ValidationError('Must be valid hex color format (#RRGGBB)')


class TaskSchema(Schema):
    """Schema for validating and serializing Task objects."""
    id = fields.Int(dump_only=True)  # Read-only
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True, validate=validate.Length(max=500))
    completed = fields.Bool(load_default=False)  # Defaults to False if not provided
    due_date = fields.DateTime(allow_none=True, format='iso')  # ISO 8601 format
    category_id = fields.Int(allow_none=True)  # Optional category assignment
    category = fields.Nested(CategorySchema, dump_only=True)  # Nested category info in responses
    created_at = fields.DateTime(dump_only=True)  # Read-only
    updated_at = fields.DateTime(dump_only=True)  # Read-only


class TaskCreateSchema(TaskSchema):
    """Extended schema for task creation responses that includes notification status."""
    notification_queued = fields.Bool(dump_only=True)


class TaskListSchema(Schema):
    """Schema for wrapping a list of tasks in API responses."""
    tasks = fields.List(fields.Nested(TaskSchema))


class TaskDetailSchema(Schema):
    """Schema for individual task responses with notification status."""
    task = fields.Nested(TaskSchema)
    notification_queued = fields.Bool(dump_only=True)


class CategoriesListSchema(Schema):
    """Schema for wrapping a list of categories in API responses."""
    categories = fields.List(fields.Nested(CategorySchema))


class CategoryDetailSchema(Schema):
    """Schema for category detail response with nested task list."""
    id = fields.Int()
    name = fields.Str()
    color = fields.Str(allow_none=True)
    tasks = fields.List(fields.Nested(lambda: TaskMinimalSchema()))


class TaskMinimalSchema(Schema):
    """Lightweight schema for tasks nested within category responses."""
    id = fields.Int()
    title = fields.Str()
    completed = fields.Bool()
