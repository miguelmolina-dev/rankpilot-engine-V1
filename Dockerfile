# Use a slim Python image for speed and size
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (needed for some PDF libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code (including your agents and state.py)
COPY . .

# Create the mount point for the shared data
RUN mkdir -p /app/shared_data

# Expose the port your API runs on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]