#!/bin/bash

# Add config/creds copying here..
aws s3 cp s3://gmu-demo-bucket/config-files/GMU_admin.json /app/assets
aws s3 cp s3://gmu-demo-bucket/config-files/.env /app/.env

cd /app
# Add any other scripts here...
# Start the service
# npm run start
python main.py
