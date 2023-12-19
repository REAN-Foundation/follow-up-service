FROM python:3.10
WORKDIR /app
RUN python -m venv venv
RUN . venv/bin/activate
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 ghostscript -y
RUN apt-get install -y awscli

COPY requirement.txt /app/
RUN pip install --no-cache-dir -r requirement.txt
COPY . /app
RUN aws s3 cp s3://duploservices-dev-configs-new-167414264568/document-processor/GMU_admin.json  /app/assets/
EXPOSE 3000
CMD ["python", "main.py"]