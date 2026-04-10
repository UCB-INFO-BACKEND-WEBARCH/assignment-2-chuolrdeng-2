import os
import logging
from app import create_app

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Run Flask development server
    # Accessible on http://0.0.0.0:5000
    app.run(host='0.0.0.0', port=5000, debug=False)
