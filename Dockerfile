FROM alpine:3.19 AS builder

# Install build tools, Python, and dependencies
RUN apk --no-cache add \
    bash \
    curl \
    cmake \
    make \
    g++ \
    gcc \
    git \
    musl-dev \
    linux-headers \
    libpng-dev \
    libjpeg-turbo-dev \
    gtest-dev \
    zlib-dev \
    expat-dev \
    openssl-dev \
    python3 \
    py3-pip \
    py3-virtualenv \
    python3-dev \
    py3-numpy \
    libffi-dev \
    build-base

# Set work directory
WORKDIR /app

# Create a virtual environment
RUN python3 -m venv /app/venv

# Install build tools for Python and dependencies
COPY requirements.txt /app/
RUN /app/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Clone and build the Highway library
RUN git clone --depth 1 https://github.com/google/highway.git /tmp/highway && \
    cd /tmp/highway && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j4 && \
    make install && \
    rm -rf /tmp/highway

# Clone and build libjxl
RUN git clone https://github.com/libjxl/libjxl.git /tmp/libjxl && \
    cd /tmp/libjxl && \
    ./deps.sh && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DJPEGXL_FORCE_SYSTEM_LIBPNG=ON .. && \
    make -j4 && \
    make install && \
    rm -rf /tmp/libjxl

# Copy the rest of the application code
COPY . /app

# Convert the entrypoint script to Unix format and make it executable
RUN dos2unix /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 3000

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]
