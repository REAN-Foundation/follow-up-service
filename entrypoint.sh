#!/bin/bash

if [ -z "$S3_CONFIG_BUCKET" ] || [ -z "$S3_CONFIG_PATH" ]; then
  echo "Error: S3_CONFIG_BUCKET and S3_CONFIG_PATH environment variables must be set."
  exit 1
fi

# Copy config/creds from the S3 bucket
aws s3 cp s3://$S3_CONFIG_BUCKET/$S3_CONFIG_PATH/GMU_admin.json /app/assets
aws s3 cp s3://$S3_CONFIG_BUCKET/$S3_CONFIG_PATH/.env /app/.env

cd /app
# Add any other scripts here...
# Start the service
# npm run start
python main.py
