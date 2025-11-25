# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY main.py db.py constants.py ./
COPY cogs/ ./cogs/

# Install dependencies using uv
RUN uv sync --frozen

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Set environment variable for Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Run the bot using uv
CMD ["uv", "run", "main.py"]