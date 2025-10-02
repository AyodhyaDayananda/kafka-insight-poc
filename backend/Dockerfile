# Use Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Metadata
LABEL authors="Ayodhya Dayananda"

# Install system dependencies (needed for confluent-kafka)
RUN apt-get update && apt-get install -y \
    gcc g++ librdkafka-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
