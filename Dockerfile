# Optimized base image for production
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY . .

# Run the ETL pipeline
CMD ["python", "etl_pipeline.py"]
