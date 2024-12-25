# Stage 1: Builder
FROM alpine:3.21.0 AS builder

# Install build tools and dependencies
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

# Create a virtual environment and install dependencies
RUN python3 -m venv /app/venv
COPY requirements.txt /app/
RUN /app/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Clone and build the Highway library and libjxl
RUN git clone --depth 1 https://github.com/google/highway.git /tmp/highway && \
    cd /tmp/highway && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j4 && \
    make install && \
    rm -rf /tmp/highway

RUN git clone https://github.com/libjxl/libjxl.git /tmp/libjxl && \
    cd /tmp/libjxl && \
    ./deps.sh && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DJPEGXL_FORCE_SYSTEM_LIBPNG=ON .. && \
    make -j4 && \
    make install && \
    rm -rf /tmp/libjxl

# Stage 2: Final Image (Runtime)
FROM alpine:3.21.0

RUN apk --no-cache update && apk --no-cache upgrade openssl && \
    apk --no-cache add \
    bash \
    python3 \
    py3-pip \
    py3-virtualenv \
    libpng \
    libjpeg-turbo \
    zlib \
    libffi \
    dos2unix \
    && rm -rf /var/cache/apk/*  # Clean up unnecessary files

# Set work directory
WORKDIR /app

COPY --from=builder /app/venv /app/venv
COPY --from=builder /app /app

RUN if [ -f /app/entrypoint.sh ]; then dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh; fi

# Expose the application port
EXPOSE 3000

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]
