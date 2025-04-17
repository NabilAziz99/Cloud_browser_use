FROM mcr.microsoft.com/playwright:v1.42.1-jammy

# Set working directory
WORKDIR /app

# Copy requirements file for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set environment variable to force headless mode
ENV BROWSER_USE_HEADLESS=true
ENV CONTAINER=true

# Copy application code
COPY . .

# Expose port 8080 for Railway
EXPOSE 8080

# Run the application on port 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]