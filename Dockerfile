FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements file for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV BROWSER_USE_HEADLESS=true
ENV CONTAINER=true

# Copy application code
COPY . .

# Make the healthcheck script executable
RUN chmod +x playwright_healthcheck.py

# Expose port for Railway
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]