#!/bin/bash

set -e

CLUSTER_NAME="llm-gke-cluster"
ZONE="us-east1-b"
PROJECT_ID="coms6998-term-project"

echo "Phase 1: Creating GKE cluster and node pool..."
terraform apply -target=google_container_cluster.primary -target=google_container_node_pool.gpu_pool -auto-approve

echo "Phase 2: Authenticating to GKE..."
gcloud container clusters get-credentials "$CLUSTER_NAME" --zone "$ZONE" --project "$PROJECT_ID"

echo "Kubernetes context is now set. Verifying nodes..."
kubectl get nodes

echo "Phase 3: Deploying application via Helm (Terraform)..."
terraform apply -auto-approve

echo "Done! Your app and monitoring stack should now be live."

echo "Check the external IP of your service:"
echo "    kubectl get svc"
