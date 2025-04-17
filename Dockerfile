FROM mcr.microsoft.com/playwright:v1.42.1-jammy

# Install Python 3.11 and git
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a symbolic link for python and pip
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    python -m ensurepip && \
    python -m pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements file for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV BROWSER_USE_HEADLESS=true
ENV CONTAINER=true
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY . .

# Make the healthcheck script executable if it exists
RUN if [ -f playwright_healthcheck.py ]; then chmod +x playwright_healthcheck.py; fi

# Install Playwright browsers
RUN python -m playwright install chromium

# Expose port for Railway
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]