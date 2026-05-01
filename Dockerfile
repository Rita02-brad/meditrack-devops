# Use the official slim Python 3.11 image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (leverages Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 so the container port is accessible from the host
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
