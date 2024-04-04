FROM python:3.12.1
WORKDIR /app
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --fix-missing \
    ffmpeg \
    libsm6 \
    libxext6 \
    ghostscript \
    awscli \
    dos2unix 

# Download and install aom 3.8.2-2
# RUN wget http://security.ubuntu.com/ubuntu/pool/universe/a/aom/libaom0_3.8.2-2_amd64.deb \
#     && dpkg -i libaom0_3.8.2-2_amd64.deb \
#     && rm libaom0_3.8.2-2_amd64.deb

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --upgrade setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt
    
RUN apt-get remove libaom3:amd64 -y

COPY . /app

EXPOSE 3000

COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]


# FROM python:3.12
# WORKDIR /app
# RUN python -m venv venv
# RUN . venv/bin/activate
# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 ghostscript -y --fix-missing
# RUN apt-get install -y awscli dos2unix 
# COPY requirements.txt /app/
# RUN python -m pip install --upgrade pip
# RUN pip install --upgrade setuptools wheel
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . /app
# #RUN aws s3 cp s3://duploservices-dev-configs-new-167414264568/document-processor/GMU_admin.json /app/assets
# EXPOSE 3232
# #CMD ["python", "main.py"]
# COPY entrypoint.sh /app/entrypoint.sh
# RUN dos2unix /app/entrypoint.sh
# RUN chmod +x /app/entrypoint.sh
# ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]