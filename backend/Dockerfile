# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m appuser
USER appuser

# Copy backend and data
COPY --chown=appuser:appuser backend/ ./backend/
COPY --chown=appuser:appuser data/ ./data/

# Expose FastAPI port
EXPOSE 8000

# Run the backend
CMD ["python", "backend/main.py"]
