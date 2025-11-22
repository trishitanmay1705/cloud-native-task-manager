# Cloud-Native Task Manager

A demo cloud-native task manager (Flask + PostgreSQL + NGINX frontend), containerized and deployable to Azure AKS.

## What’s included
- Flask backend with `/api/tasks`, `/health`, `/metrics` (Prometheus)
- Simple static frontend served by NGINX
- Dockerfiles for backend/frontend
- `docker-compose.yml` for local development
- Kubernetes manifests to deploy to AKS (Deployments, Services, Ingress, HPA)
- GitHub Actions workflow for CI/CD
- Starter Terraform for Resource Group + ACR

---

## Quick local run

1. Build & run with docker-compose:
```bash
docker-compose up --build
