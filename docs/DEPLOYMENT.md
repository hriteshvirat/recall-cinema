# Cloud Run & Google Cloud Deployment Guide

RECALL is production-ready for deployment to **Google Cloud Run** with Secret Manager support.

---

## 1. Prerequisites

- Google Cloud Project with Billing Enabled.
- Enabled APIs:
  - Cloud Run (`run.googleapis.com`)
  - Artifact Registry (`artifactregistry.googleapis.com`)
  - Cloud Build (`cloudbuild.googleapis.com`)
  - Secret Manager (`secretmanager.googleapis.com`)
  - Vertex AI (`aiplatform.googleapis.com`)
  - Cloud Text-to-Speech (`texttospeech.googleapis.com`)

Enable services using `gcloud`:
```bash
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    texttospeech.googleapis.com
```

---

## 2. Managing Secrets with Secret Manager

Never store API keys or database passwords in plain text container images. Store them in Google Secret Manager:

```bash
# Create ClickHouse Password secret
echo -n "YOUR_CLICKHOUSE_PASSWORD" | gcloud secrets create clickhouse-password --data-file=-

# Create Gemini API Key secret
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
```

---

## 3. Deploying to Cloud Run

### Option A: Using Google Cloud Build
Run the automated build and deployment pipeline:
```bash
gcloud builds submit --config cloudbuild.yaml
```

### Option B: Direct Docker Build & Deploy
```bash
# 1. Build & Push Image
docker build -t gcr.io/$PROJECT_ID/recall:latest .
docker push gcr.io/$PROJECT_ID/recall:latest

# 2. Deploy to Cloud Run
gcloud run deploy recall \
    --image gcr.io/$PROJECT_ID/recall:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars CLICKHOUSE_HOST="your-instance.clickhouse.cloud",CLICKHOUSE_PORT="8443",CLICKHOUSE_USER="default",CLICKHOUSE_DATABASE="recall",CLICKHOUSE_SECURE="true" \
    --set-secrets CLICKHOUSE_PASSWORD=clickhouse-password:latest,GEMINI_API_KEY=gemini-api-key:latest
```

---

## 4. Health & Verification Endpoints

Once deployed, verify container readiness:
- **Liveness probe**: `GET /health`
- **Readiness probe**: `GET /ready` (tests ClickHouse database connectivity)
