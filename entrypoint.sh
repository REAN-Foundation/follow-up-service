#!/bin/bash

# Add config/creds copying here..
aws s3 cp s3://duploservices-dev-configs-new-167414264568/document-processor/GMU_admin.json /app/assets

cd /app
# Add any other scripts here...
# Start the service
# npm run start
python main.py
