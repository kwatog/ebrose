#!/bin/bash

# Development deployment script for Ebrose
set -e

NAMESPACE="ebrose-development"
CHART_PATH="./helm/ebrose"
VALUES_FILE="./helm/ebrose/values-development.yaml"

echo "🚀 Deploying Ebrose to development environment..."

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy using Helm
helm upgrade --install ebrose-dev $CHART_PATH \
    --namespace $NAMESPACE \
    --values $VALUES_FILE \
    --set backend.image.tag=development-latest \
    --set frontend.image.tag=development-latest \
    --wait \
    --timeout 10m

echo "✅ Development deployment completed!"
echo ""
echo "Services:"
kubectl get services -n $NAMESPACE
echo ""
echo "Pods:"
kubectl get pods -n $NAMESPACE
echo ""
echo "🔗 Access the application:"
echo "   Frontend: kubectl port-forward -n $NAMESPACE svc/ebrose-dev-frontend 3000:3000"
echo "   Backend:  kubectl port-forward -n $NAMESPACE svc/ebrose-dev-backend 8000:8000"
