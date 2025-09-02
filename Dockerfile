# Use slim Python image
FROM python:3.12-slim
# Set work directory
WORKDIR /app

# Install system deps (if needed later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Set environment variables (default values can be overridden by Kubernetes)
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000

# Expose port
EXPOSE 8000

# Drop root privileges
RUN useradd -m appuser
USER appuser

# Run your server
CMD ["python", "src/uniprot/tools/server.py"]
