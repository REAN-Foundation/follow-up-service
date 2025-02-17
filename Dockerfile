# FROM python:3.10
# WORKDIR /app
# RUN python -m venv venv
# RUN . venv/bin/activate
# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 ghostscript -y
# RUN apt-get install -y awscli dos2unix
# RUN pip install --upgrade pip
# RUN pip install setuptools wheel
# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . /app
# # RUN aws s3 cp s3://duploservices-dev-configs-new-167414264568/document-processor/GMU_admin.json /app/assets
# EXPOSE 3000
# #CMD ["python", "main.py"]
# COPY entrypoint.sh /app/entrypoint.sh
# RUN dos2unix /app/entrypoint.sh
# RUN chmod +x /app/entrypoint.sh
# ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]
# Use the latest secure Python image
FROM python:3.12-slim-bookworm 

# Set the working directory
WORKDIR /app

# Upgrade system libraries to remove vulnerabilities
RUN apt-get update && apt-get upgrade -y && \
    # apt-get install -y --only-upgrade aom jpeg-xl zlib1g && \
    apt-get install -y --no-install-recommends \
    libaom-dev \
    # jpeg-xl \
    libjxl-dev \
    zlib1g \
    ffmpeg \
    libstdc++6 \
    libx11-6 \
    ghostscript \
    awscli \
    dos2unix \
    libexpat1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

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