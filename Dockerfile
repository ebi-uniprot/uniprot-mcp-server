# Use slim Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system deps and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies with uv
RUN uv sync --frozen --no-dev

# Copy app source
COPY . .
COPY src ./src

# Remove any copied .venv and recreate clean environment
RUN rm -rf .venv && uv sync --frozen --no-dev

# Set environment variables (default values can be overridden by Kubernetes)
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000

# Expose port
EXPOSE 8000

# Drop root privileges
RUN useradd -m appuser
USER appuser

# Run your server using uv
CMD ["uv", "run", "src/uniprot/tools/server.py"]