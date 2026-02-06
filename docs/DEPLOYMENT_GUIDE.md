# HealthGuard Production Deployment Guide

## Overview

This guide covers deploying the complete HealthGuard platform to production infrastructure using Kubernetes, Docker, and cloud services.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Application Deployment](#application-deployment)
4. [Monitoring & Alerting](#monitoring--alerting)
5. [Scaling Strategies](#scaling-strategies)
6. [Disaster Recovery](#disaster-recovery)
7. [Security Hardening](#security-hardening)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **kubectl** 1.27+ - Kubernetes CLI
- **docker** 20.10+ - Container runtime
- **aws-cli** 2.0+ - AWS CLI (or gcloud for GCP)
- **helm** 3.0+ - Kubernetes package manager
- **terraform** 1.5+ - Infrastructure as Code

### Cloud Provider Setup

#### AWS (Recommended)

```bash
# Configure AWS credentials
aws configure

# Create EKS cluster
aws eks create-cluster \
  --name healthguard-production \
  --region us-east-1 \
  --kubernetes-version 1.27 \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/EKSClusterRole \
  --resources-vpc-config subnetIds=SUBNET_ID1,SUBNET_ID2,securityGroupIds=SG_ID

# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name healthguard-production
```

#### Google Cloud

```bash
# Create GKE cluster
gcloud container clusters create healthguard-production \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type e2-standard-4 \
  --enable-autoscaling --min-nodes 3 --max-nodes 10

# Get credentials
gcloud container clusters get-credentials healthguard-production \
  --region us-central1
```

---

## Infrastructure Setup

### 1. Create Namespaces

```bash
kubectl create namespace healthguard-production
kubectl create namespace healthguard-staging
kubectl create namespace monitoring
```

### 2. Deploy Databases

#### PostgreSQL

```bash
kubectl apply -f kubernetes/databases/postgres.yaml
kubectl rollout status deployment/postgres -n healthguard-production
```

#### TimescaleDB

```bash
kubectl apply -f kubernetes/databases/timescale.yaml
kubectl rollout status deployment/timescale -n healthguard-production

# Initialize TimescaleDB
kubectl exec -it -n healthguard-production deployment/timescale -- psql -U postgres
\i /docker-entrypoint-initdb.d/timescale_setup.sql
```

#### Redis

```bash
kubectl apply -f kubernetes/databases/redis.yaml
kubectl rollout status deployment/redis -n healthguard-production
```

### 3. Configure Secrets

```bash
# Generate secrets
kubectl create secret generic healthguard-secrets \
  --from-literal=DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=TIMESCALE_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=REDIS_PASSWORD=$(openssl rand -base64 32) \
  -n healthguard-production
```

### 4. Deploy MQTT Broker

```bash
kubectl apply -f kubernetes/mosquitto.yaml
kubectl rollout status deployment/mosquitto -n healthguard-production
```

---

## Application Deployment

### 1. Build and Push Images

```bash
# Using the deployment script
./scripts/deploy.sh production

# Or manually
docker build -t healthguard-backend:latest -f cloud-backend/Dockerfile .
docker build -t healthguard-frontend:latest -f web-dashboard/Dockerfile .

docker tag healthguard-backend:latest YOUR_REGISTRY/healthguard-backend:latest
docker push YOUR_REGISTRY/healthguard-backend:latest
```

### 2. Deploy Backend

```bash
# Apply deployment
kubectl apply -f kubernetes/deployments/backend.yaml

# Wait for rollout
kubectl rollout status deployment/healthguard-backend -n healthguard-production

# Run migrations
kubectl run migration-job --rm -i --restart=Never \
  --image=YOUR_REGISTRY/healthguard-backend:latest \
  --namespace=healthguard-production \
  -- python manage.py migrate
```

### 3. Deploy Frontend

```bash
kubectl apply -f kubernetes/deployments/frontend.yaml
kubectl rollout status deployment/healthguard-frontend -n healthguard-production
```

### 4. Deploy Celery Workers

```bash
kubectl apply -f kubernetes/deployments/celery.yaml
kubectl rollout status deployment/celery-worker -n healthguard-production
```

### 5. Expose Services

```bash
# Using LoadBalancer (AWS/GCP)
kubectl apply -f kubernetes/services/loadbalancer.yaml

# Using Ingress (recommended)
kubectl apply -f kubernetes/ingress.yaml
```

---

## Monitoring & Alerting

### 1. Deploy Prometheus

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --set grafana.adminPassword=admin \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### 2. Apply Custom Rules

```bash
kubectl apply -f monitoring/prometheus-config.yml
kubectl apply -f monitoring/alert-rules.yml
```

### 3. Configure Grafana Dashboards

```bash
# Import dashboards
kubectl apply -f monitoring/grafana-dashboards/

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Login: admin / admin
# Navigate to Dashboards → Import → Import dashboard JSONs
```

### 4. Set Up Alerting

Edit `monitoring/alertmanager-config.yml`:

```yaml
receivers:
- name: 'slack'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts'
    title: 'HealthGuard Alert: {{ .GroupLabels.alertname }}'

- name: 'email'
  email_configs:
  - to: 'oncall@healthguard.com'
    from: 'alerts@healthguard.com'
    smarthost: 'smtp.gmail.com:587'
    auth_username: 'alerts@healthguard.com'
    auth_password: 'YOUR_PASSWORD'
```

Apply configuration:

```bash
kubectl apply -f monitoring/alertmanager-config.yml
```

---

## Scaling Strategies

### Horizontal Pod Autoscaling

```bash
# View HPA status
kubectl get hpa -n healthguard-production

# Manually scale
kubectl scale deployment/healthguard-backend --replicas=5 -n healthguard-production
```

### Vertical Scaling

Edit deployment YAML and adjust resource limits:

```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Database Scaling

#### PostgreSQL Read Replicas

```bash
# Add read replicas in kubernetes/databases/postgres.yaml
replicas:
  - replicas: 2
    replicaLoadBalanceStrategy: roundrobin
```

#### TimescaleDB Compression

```sql
-- Enable compression
ALTER TABLE sensor_readings SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'restaurant_id, device_id'
);

-- Set retention policy
SELECT add_retention_policy('sensor_readings', INTERVAL '2 years');
```

---

## Disaster Recovery

### Backups

#### Database Backups

```bash
# PostgreSQL daily backups
kubectl create cronjob postgres-backup \
  --image=postgres:14 \
  --schedule="0 2 * * *" \
  --namespace=healthguard-production \
  -- pg_dump -h postgres -U postgres healthguard | gzip > /backup/healthguard-$(date +%Y%m%d).sql.gz
```

#### Automated Backups (AWS)

```bash
# Enable AWS Backup for EBS volumes
aws backup create-backup-vault \
  --backup-vault-name healthguard-backups \
  --region us-east-1
```

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective):** 4 hours
2. **RPO (Recovery Point Objective):** 1 hour

Steps:

```bash
# 1. Restore from backup
kubectl run postgres-restore --rm -i \
  --image=postgres:14 \
  -- psql -h postgres-restored -U postgres < /backup/latest.sql

# 2. Update DNS
kubectl apply -f kubernetes/disaster-recovery/restore-service.yaml

# 3. Verify
./scripts/health-check.sh
```

---

## Security Hardening

### 1. Network Policies

```bash
kubectl apply -f kubernetes/security/network-policies.yaml
```

### 2. Pod Security Policies

```bash
kubectl apply -f kubernetes/security/pod-security-policy.yaml
```

### 3. Enable TLS

```yaml
# ingress.yaml
spec:
  tls:
  - hosts:
    - api.healthguard.com
    secretName: healthguard-tls
```

Generate certificates:

```bash
cert-manager:
  kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

  # Create ClusterIssuer
  kubectl apply -f kubernetes/security/cert-manager-clusterissuer.yaml
```

### 4. Secrets Management

```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n healthguard-production

# Integrate with AWS Secrets Manager
kubectl apply -f kubernetes/security/external-secrets.yaml
```

---

## Troubleshooting

### Common Issues

#### Pod Not Starting

```bash
# Check pod status
kubectl describe pod POD_NAME -n healthguard-production

# Check logs
kubectl logs POD_NAME -n healthguard-production

# Common fixes:
# - Image pull error: Check image name and registry credentials
# - CrashLoopBackOff: Check application logs for errors
# - Pending: Check resource requests/limits
```

#### Database Connection Errors

```bash
# Verify database is running
kubectl get pods -n healthguard-production -l app=postgres

# Test connection
kubectl run test-db --rm -it --image=postgres:14 -- psql -h postgres -U postgres

# Check secrets
kubectl get secret healthguard-secrets -n healthguard-production -o yaml
```

#### High Memory/CPU Usage

```bash
# Check resource usage
kubectl top pods -n healthguard-production

# Identify memory leaks
kubectl exec -it POD_NAME -n healthguard-boundary -- python -m memory_profiler

# Scale up if needed
kubectl scale deployment/healthguard-backend --replicas=5 -n healthguard-production
```

### Debugging Commands

```bash
# Port forward to local machine
kubectl port-forward -n healthguard-production svc/backend-service 8000:80

# Execute shell in pod
kubectl exec -it POD_NAME -n healthguard-production -- /bin/bash

# Get events
kubectl get events -n healthguard-production --sort-by='.lastTimestamp'

# Check resource quotas
kubectl describe resourcequota -n healthguard-production
```

---

## Maintenance

### Rolling Updates

```bash
# Update image
kubectl set image deployment/healthguard-backend \
  backend=YOUR_REGISTRY/healthguard-backend:v1.2.3 \
  -n healthguard-production

# Monitor rollout
kubectl rollout status deployment/healthguard-backend -n healthguard-production

# Rollback if needed
kubectl rollout undo deployment/healthguard-backend -n healthguard-production
```

### Database Migrations

```bash
# Run migration job
kubectl apply -f kubernetes/jobs/migration.yaml

# Monitor
kubectl logs -f job/migration-job -n healthguard-production
```

---

## Performance Tuning

### PostgreSQL

```sql
-- Tune postgresql.conf
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Django

```python
# settings.py
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 100}
        }
    }
}
```

---

## Support

For issues or questions:
- Documentation: https://docs.healthguard.com
- Support: support@healthguard.com
- Status Page: https://status.healthguard.com

---

**Last Updated:** 2026-02-06
**Version:** 2.0.0
