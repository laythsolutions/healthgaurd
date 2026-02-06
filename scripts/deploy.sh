#!/bin/bash
# HealthGuard Production Deployment Script
# Usage: ./scripts/deploy.sh [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
NAMESPACE="healthguard-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}
CLUSTER_NAME="healthguard-${ENVIRONMENT}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}HealthGuard Deployment Script${NC}"
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}========================================${NC}"

# Functions
check_prerequisites() {
    echo -e "\n${YELLOW}Checking prerequisites...${NC}"

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl is not installed${NC}"
        exit 1
    fi

    # Check if aws CLI is installed
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}Error: aws CLI is not installed${NC}"
        exit 1
    fi

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: docker is not installed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Prerequisites check passed${NC}"
}

build_images() {
    echo -e "\n${YELLOW}Building Docker images...${NC}"

    # Backend
    echo -e "${YELLOW}Building backend image...${NC}"
    docker build -t healthguard-backend:${ENVIRONMENT} -f cloud-backend/Dockerfile .

    # Frontend
    echo -e "${YELLOW}Building frontend image...${NC}"
    docker build -t healthguard-frontend:${ENVIRONMENT} -f web-dashboard/Dockerfile .

    # Edge Gateway
    echo -e "${YELLOW}Building edge gateway image...${NC}"
    docker build -t healthguard-edge:${ENVIRONMENT} -f edge-gateway/Dockerfile .

    echo -e "${GREEN}✓ Images built successfully${NC}"
}

push_images() {
    echo -e "\n${YELLOW}Pushing images to registry...${NC}"

    # Tag and push images
    # Adjust registry URL as needed
    REGISTRY="your-registry.com"

    docker tag healthguard-backend:${ENVIRONMENT} ${REGISTRY}/healthguard-backend:${ENVIRONMENT}
    docker tag healthguard-frontend:${ENVIRONMENT} ${REGISTRY}/healthguard-frontend:${ENVIRONMENT}
    docker tag healthguard-edge:${ENVIRONMENT} ${REGISTRY}/healthguard-edge:${ENVIRONMENT}

    docker push ${REGISTRY}/healthguard-backend:${ENVIRONMENT}
    docker push ${REGISTRY}/healthguard-frontend:${ENVIRONMENT}
    docker push ${REGISTRY}/healthguard-edge:${ENVIRONMENT}

    echo -e "${GREEN}✓ Images pushed successfully${NC}"
}

deploy_kubernetes() {
    echo -e "\n${YELLOW}Deploying to Kubernetes...${NC}"

    # Update kubeconfig for EKS
    aws eks update-kubeconfig --region ${REGION} --name ${CLUSTER_NAME}

    # Create namespace if it doesn't exist
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

    # Apply secrets
    echo -e "${YELLOW}Applying secrets...${NC}"
    kubectl apply -f kubernetes/secrets-${ENVIRONMENT}.yaml

    # Apply ConfigMaps
    echo -e "${YELLOW}Applying configurations...${NC}"
    kubectl apply -f kubernetes/configmaps.yaml

    # Deploy database
    echo -e "${YELLOW}Deploying databases...${NC}"
    kubectl apply -f kubernetes/databases.yaml
    kubectl rollout status deployment/postgres -n ${NAMESPACE}
    kubectl rollout status deployment/timescale -n ${NAMESPACE}
    kubectl rollout status deployment/redis -n ${NAMESPACE}

    # Run database migrations
    echo -e "${YELLOW}Running database migrations...${NC}"
    kubectl run migration-job \
        --image=healthguard-backend:${ENVIRONMENT} \
        --namespace=${NAMESPACE} \
        --restart=Never \
        --command -- python manage.py migrate

    # Wait for migration to complete
    kubectl wait --for=condition=complete --timeout=300s job/migration-job -n ${NAMESPACE}
    kubectl delete job migration-job -n ${NAMESPACE}

    # Deploy application
    echo -e "${YELLOW}Deploying applications...${NC}"
    envsubst < kubernetes/deployments.yaml | kubectl apply -f -

    # Wait for deployments to be ready
    echo -e "${YELLOW}Waiting for deployments to be ready...${NC}"
    kubectl rollout status deployment/healthguard-backend -n ${NAMESPACE}
    kubectl rollout status deployment/healthguard-frontend -n ${NAMESPACE}
    kubectl rollout status deployment/celery-worker -n ${NAMESPACE}

    # Deploy monitoring
    echo -e "${YELLOW}Deploying monitoring stack...${NC}"
    kubectl apply -f monitoring/prometheus.yaml
    kubectl apply -f monitoring/grafana.yaml
    kubectl apply -f monitoring/alertmanager.yaml

    echo -e "${GREEN}✓ Deployment completed successfully${NC}"
}

run_health_checks() {
    echo -e "\n${YELLOW}Running health checks...${NC}"

    # Get backend service URL
    BACKEND_URL=$(kubectl get svc backend-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

    # Wait for service to be ready
    echo -e "${YELLOW}Waiting for backend service...${NC}"
    sleep 30

    # Health check
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${BACKEND_URL}/health)

    if [ ${HTTP_CODE} -eq 200 ]; then
        echo -e "${GREEN}✓ Backend health check passed${NC}"
    else
        echo -e "${RED}✗ Backend health check failed (HTTP ${HTTP_CODE})${NC}"
        exit 1
    fi

    # Get frontend service URL
    FRONTEND_URL=$(kubectl get svc frontend-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${FRONTEND_URL}/)

    if [ ${HTTP_CODE} -eq 200 ]; then
        echo -e "${GREEN}✓ Frontend health check passed${NC}"
    else
        echo -e "${RED}✗ Frontend health check failed (HTTP ${HTTP_CODE})${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ All health checks passed${NC}"
}

display_info() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"

    BACKEND_URL=$(kubectl get svc backend-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    FRONTEND_URL=$(kubectl get svc frontend-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

    echo -e "\n${YELLOW}Service URLs:${NC}"
    echo -e "  Backend API:  http://${BACKEND_URL}"
    echo -e "  Frontend:     http://${FRONTEND_URL}"
    echo -e "  API Docs:     http://${BACKEND_URL}/api/docs"

    echo -e "\n${YELLOW}Useful Commands:${NC}"
    echo -e "  Get logs:     kubectl logs -f -n ${NAMESPACE} deployment/healthguard-backend"
    echo -e "  Get pods:     kubectl get pods -n ${NAMESPACE}"
    echo -e "  Scale up:     kubectl scale -n ${NAMESPACE} deployment/healthguard-backend --replicas=5"
    echo -e "  Port forward: kubectl port-forward -n ${NAMESPACE} svc/backend-service 8000:80"

    echo -e "\n${YELLOW}Monitoring:${NC}"
    echo -e "  Grafana:      kubectl port-forward -n ${NAMESPACE} svc/grafana 3000:80"
    echo -e "  Prometheus:  kubectl port-forward -n ${NAMESPACE} svc/prometheus 9090:80"

    echo ""
}

# Main execution
main() {
    check_prerequisites

    # Parse arguments
    SKIP_BUILD=false
    SKIP_PUSH=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-push)
                SKIP_PUSH=true
                shift
                ;;
            *)
                ENVIRONMENT=$1
                shift
                ;;
        esac
    done

    if [ "$SKIP_BUILD" = false ]; then
        build_images
    fi

    if [ "$SKIP_PUSH" = false ]; then
        push_images
    fi

    deploy_kubernetes
    run_health_checks
    display_info
}

# Run main function
main "$@"
