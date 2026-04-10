# Use lightweight Python 3.11 image as base
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies (postgresql-client for database connectivity checks)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements file
COPY requirements.txt .

# Install Python packages (--no-cache-dir reduces image size)
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application code into container
COPY . .

# Create non-root user for security (reduces risk if container is compromised)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port on which Flask app listens
EXPOSE 5000

# Default command when container starts
CMD ["python", "main.py"]
