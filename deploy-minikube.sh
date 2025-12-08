#!/bin/bash

# Deploy Mazarbul to Minikube
set -e

echo "🚀 Deploying Mazarbul to Minikube..."

# Get Minikube IP for frontend configuration
MINIKUBE_IP=$(minikube ip)
echo "📍 Minikube IP: $MINIKUBE_IP"

# Calculate Allowed Origins
ALLOWED_ORIGINS="http://${MINIKUBE_IP}:30081,http://localhost:3000"

# Create namespace
kubectl create namespace mazarbul-dev --dry-run=client -o yaml | kubectl apply -f -

# Deploy using Helm with Minikube-specific values
helm upgrade --install mazarbul ./helm/mazarbul \
  --namespace mazarbul-dev \
  --values ./helm/mazarbul/values-minikube.yaml \
  --set frontend.env.NUXT_PUBLIC_API_BASE="http://${MINIKUBE_IP}:30080" \
  --set backend.env.ALLOWED_ORIGINS="${ALLOWED_ORIGINS}" \
  --wait \
  --timeout 10m

echo "✅ Deployment completed!"
echo ""
echo "📊 Checking deployment status..."
kubectl get pods -n mazarbul-dev
echo ""
kubectl get services -n mazarbul-dev
echo ""
echo "🔗 Access URLs:"
echo "   Backend API: http://${MINIKUBE_IP}:30080"
echo "   Frontend:    http://${MINIKUBE_IP}:30081"
echo "   API Docs:    http://${MINIKUBE_IP}:30080/docs"
echo ""
echo "📝 To check logs:"
echo "   kubectl logs -f deployment/mazarbul-backend -n mazarbul-dev"
echo "   kubectl logs -f deployment/mazarbul-frontend -n mazarbul-dev"