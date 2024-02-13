FROM python:3.10
WORKDIR /app
RUN python -m venv venv
RUN . venv/bin/activate
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 ghostscript -y
RUN apt-get install -y awscli dos2unix
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
#RUN aws s3 cp s3://duploservices-dev-configs-new-167414264568/document-processor/GMU_admin.json /app/assets
EXPOSE 3232
#CMD ["python", "main.py"]

COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]