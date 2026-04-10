import os
import logging
import redis
from rq import Worker, Queue
from app import create_app

# Configure worker logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask application context for database access
app = create_app()

# Initialize Redis connection for job queue
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
redis_conn = redis.from_url(redis_url)

# Create queue and worker instance
# Worker will process background jobs (like sending notifications)
q = Queue(connection=redis_conn)
worker = Worker([q], connection=redis_conn)

if __name__ == '__main__':
    # Start worker process - continuously polls for and executes jobs
    with app.app_context():
        worker.work()
