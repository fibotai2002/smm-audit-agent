#!/bin/bash
set -e

# Configuration
SERVICE_NAME="smm-audit-agent"
REGION="us-central1"

echo "🚀 Deploying $SERVICE_NAME to Google Cloud Run..."

# Check for .env file
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Deploy directly from source
# This uploads the code, builds it with Cloud Build (using Dockerfile if present), and deploys.
echo "☁️  Submitting build and deploying..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --env-vars-file .env \
    --port 8080

echo "✅ Deployment succeeded!"
