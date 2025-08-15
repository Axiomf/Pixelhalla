# ...existing code...
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Copy and install Python deps (use python -m pip and no cache)
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
 && python -m pip install --no-cache-dir -r /app/requirements.txt

# Copy project files
COPY . /app

# Create a non-root user and fix permissions (optional but recommended)
RUN useradd --create-home --shell /bin/bash appuser \
 && chown -R appuser:appuser /app
USER appuser

# Expose port (ensure this matches your server)
EXPOSE 5555

# Run as a module
CMD ["python", "-m", "src.engine.server_side"]
# ...existing code...