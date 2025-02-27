FROM python:3.12-alpine

WORKDIR /app

RUN apk add \
    ffmpeg \
    libstdc++ \
    libx11 \
    ghostscript \
    aws-cli \
    dos2unix \
    expat \
    cmake \
    make \
    g++ \
    gcc \
    musl-dev \
    python3-dev \
    jpeg-dev \
    tiff-dev \
    libpng-dev \
    openblas-dev \
    freetype-dev \
    harfbuzz-dev

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 3000

# CMD ["python", "main.py"]

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]


# FROM python:3.12-slim-bookworm

# # Set the working directory
# WORKDIR /app

# # Upgrade system libraries to remove vulnerabilities
# RUN apt-get update && apt-get upgrade -y && \
#     # apt-get install -y --only-upgrade aom jpeg-xl zlib1g && \
#     apt-get install -y --no-install-recommends \
#     libaom-dev \
#     # jpeg-xl \
#     libjxl-dev \
#     zlib1g \
#     ffmpeg \
#     libstdc++6 \
#     libx11-6 \
#     ghostscript \
#     awscli \
#     dos2unix \
#     libexpat1 && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# # Upgrade pip and install Python packages
# RUN pip install --upgrade pip setuptools wheel

# # Copy requirements and install dependencies
# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code
# COPY . /app

# # Convert the entrypoint script to Unix format and make it executable
# RUN dos2unix /app/entrypoint.sh && \
#     chmod +x /app/entrypoint.sh

# # Expose port
# EXPOSE 3000

# # Set the entrypoint
# ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]