#!/bin/bash

# Deploy Ebrose to Minikube
set -e

echo "🚀 Deploying Ebrose to Minikube..."

# Get Minikube IP for frontend configuration
MINIKUBE_IP=$(minikube ip)
echo "📍 Minikube IP: $MINIKUBE_IP"

# Create namespace
kubectl create namespace ebrose-dev --dry-run=client -o yaml | kubectl apply -f -

# Deploy using Helm with Minikube-specific values
helm upgrade --install ebrose ./helm/ebrose \
  --namespace ebrose-dev \
  --values ./helm/ebrose/values-minikube.yaml \
  --set frontend.env.NUXT_PUBLIC_API_BASE="http://${MINIKUBE_IP}:30080" \
  --wait \
  --timeout 10m

echo "✅ Deployment completed!"
echo ""
echo "📊 Checking deployment status..."
kubectl get pods -n ebrose-dev
echo ""
kubectl get services -n ebrose-dev
echo ""
echo "🔗 Access URLs:"
echo "   Backend API: http://${MINIKUBE_IP}:30080"
echo "   Frontend:    http://${MINIKUBE_IP}:30081"
echo "   API Docs:    http://${MINIKUBE_IP}:30080/docs"
echo ""
echo "📝 To check logs:"
echo "   kubectl logs -f deployment/ebrose-backend -n ebrose-dev"
echo "   kubectl logs -f deployment/ebrose-frontend -n ebrose-dev"
