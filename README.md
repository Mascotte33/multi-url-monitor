# Multi-URL Monitor

A URL monitoring tool built to learn the full DevOps stack end-to-end. It checks whether websites are up, measures response times, generates reports, and stores them in S3. Runs in Kubernetes, monitored with Prometheus and Grafana, alerts via AWS CloudWatch and SNS, infrastructure managed with Terraform, and automatically built and deployed through GitHub Actions.

---

## What it does

- Periodically checks a list of URLs for availability and response time
- Logs results and generates HTML/text summary reports with charts
- Uploads reports to AWS S3
- Sends error logs to AWS CloudWatch; triggers SNS email alerts on errors
- Exposes a `/metrics` endpoint with `url_up` and `url_response_time_seconds` Prometheus metrics
- Grafana dashboard provisioned as code via Kubernetes ConfigMap

---

## Architecture

```
worker.py          — URL checking loop, S3 upload, CloudWatch logging
api.py             — Flask API with /health, /ready, /metrics endpoints
                     Background thread runs the URL check loop for Prometheus metrics

AWS
  S3               — stores generated reports and charts
  CloudWatch Logs  — receives error log events from worker
  SNS              — sends email alerts when error threshold is breached

Kubernetes (Minikube)
  url-monitor namespace
    worker deployment  — runs worker.py
    api deployment     — runs api.py
  monitoring namespace
    Prometheus         — scrapes /metrics via ServiceMonitor
    Grafana            — displays dashboards, provisioned from ConfigMap

Terraform
  modules/s3         — S3 bucket with versioning
  modules/iam        — IAM user with least-privilege s3:PutObject policy
  modules/monitoring — CloudWatch log group, metric filter, alarm, SNS topic

CI/CD (GitHub Actions)
  test job    — runs pytest and py_compile
  build job   — builds Docker image, pushes to GHCR
  deploy job  — kubectl set image (currently failing -> requires accessible cluster)
```

---

## Prerequisites

- Python 3.13+
- Docker
- kubectl + Minikube
- Helm 3
- Terraform
- AWS account with credentials configured
- GitHub account (for CI/CD)

---

## How to run it

### Locally

```bash
cp .env.example .env  # fill in your AWS credentials and URLs
pip install -r requirements.txt
python3 src/worker.py      # runs the monitoring loop
python3 src/api.py         # runs the Flask API with /metrics
```

### Docker

```bash
docker build -t url-monitor .
docker run --env-file .env url-monitor
```

### Kubernetes

```bash
minikube start --force

# Create namespace and secret
kubectl apply -f k8s/namespace.yml
kubectl create secret generic url-monitor-secret \
  --from-env-file=.env \
  --namespace url-monitor

# Deploy the app
kubectl apply -f k8s/

# Deploy Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# Apply ServiceMonitor and Grafana dashboard ConfigMap
kubectl apply -f k8s/api-servicemonitor.yml
kubectl apply -f k8s/grafana-config-map.yml
```

### Terraform (AWS infrastructure)

```bash
cd terraform
terraform init
terraform apply
```

---

## Tech stack

| Area | Technology |
|---|---|
| Language | Python 3.13 |
| Web framework | Flask |
| Containerization | Docker |
| Orchestration | Kubernetes (Minikube) |
| Package manager | Helm |
| Infrastructure as Code | Terraform |
| Cloud | AWS (S3, IAM, CloudWatch, SNS) |
| Metrics | Prometheus, prometheus-client |
| Dashboards | Grafana |
| CI/CD | GitHub Actions |
| Container registry | GitHub Container Registry (GHCR) |
