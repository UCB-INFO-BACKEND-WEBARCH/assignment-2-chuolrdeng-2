import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


def send_notification(task_id, task_title):
    """
    Background job executed by rq worker to send due-date reminders.
    
    This simulates sending an external notification by waiting 5 seconds
    and then logging a reminder message to the application logs.
    
    Args:
        task_id: The ID of the task (for future extensibility)
        task_title: The title of the task to include in the reminder
    """
    # Simulate network latency for sending notification
    time.sleep(5)
    logger.info(f"Reminder: Task '{task_title}' is due soon!")


def should_queue_notification(due_date):
    """
    Determine whether a background notification should be queued for this task.
    
    A notification is queued if and only if:
    1. The task has a due_date
    2. The due_date is in the future
    3. The due_date is within the next 24 hours
    
    Args:
        due_date: A datetime object or None
        
    Returns:
        boolean: True if notification should be queued, False otherwise
    """
    if due_date is None:
        return False
    
    now = datetime.utcnow()
    time_until_due = due_date - now
    
    # Past due dates don't get notifications
    if time_until_due.total_seconds() <= 0:
        return False
    
    # Only queue notifications for tasks due within the next 24 hours
    if time_until_due.total_seconds() <= 86400:  # 86400 seconds = 24 hours
        return True
    
    return False
