# Build Stage
FROM python:3.10-slim AS builder

# Set the working directory
WORKDIR /app

# Install build tools and dependencies for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libffi-dev \
    libsm6 \
    libxext6 \
    ffmpeg \
    ghostscript \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Set up Python virtual environment
RUN python -m venv /opt/venv

# Activate the virtual environment and install dependencies
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app

# Prepare the entrypoint script and set permissions
COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Runtime Stage
FROM gcr.io/distroless/python3-debian11

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

# Ensure Python virtual environment is used
ENV PATH="/opt/venv/bin:$PATH"

# Use non-root user for execution
USER nonroot:nonroot

# Expose application port
EXPOSE 3000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
