# Use the latest secure Python image
FROM python:3.12-slim-bookworm

# Set the working directory
WORKDIR /app

# Upgrade system libraries to remove vulnerabilities
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libstdc++6 \
    libx11-6 \
    ghostscript \
    awscli \
    dos2unix \
    libexpat1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get remove -y --allow-remove-essential libaom zlib1g jpeg-xl || true

# Upgrade pip and install Python packages
RUN pip install --upgrade pip setuptools wheel

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Convert the entrypoint script to Unix format and make it executable
RUN dos2unix /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 3000

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]