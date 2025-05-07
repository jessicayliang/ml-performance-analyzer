#!/bin/bash

set -e

CLUSTER_NAME="llm-gke-cluster"
ZONE="us-east1-b"

CHART_DIR="../helm_chart"
RELEASE_NAME="llm-monitoring"
NAMESPACE="default"
VALUES_FILE="$CHART_DIR/values.yaml"
ALERTMANAGER_FILE="$CHART_DIR/alertmanager.yaml"

function upgrade_helm_only() {
  echo "Upgrading Helm release '$RELEASE_NAME' in namespace '$NAMESPACE'..."
  helm upgrade "$RELEASE_NAME" "$CHART_DIR" -n "$NAMESPACE" -f "$VALUES_FILE"

  echo "Updating Alertmanager config secret..."
  kubectl delete secret alertmanager-llm-monitoring -n "$NAMESPACE" --ignore-not-found
  kubectl create secret generic alertmanager-llm-monitoring \
    --from-file=alertmanager.yaml="$ALERTMANAGER_FILE" -n "$NAMESPACE"

  echo "Helm upgrade complete."
  helm status "$RELEASE_NAME" -n "$NAMESPACE"
  echo "Service endpoints:"
  kubectl get svc -n "$NAMESPACE"
}

if [ "$1" == "helm" ]; then
  upgrade_helm_only
  exit 0
fi

echo "Phase 1: Creating GKE cluster and node pool..."
terraform apply -target=google_container_cluster.primary -target=google_container_node_pool.gpu_pool -auto-approve

echo "Phase 2: Authenticating to GKE..."
gcloud container clusters get-credentials "$CLUSTER_NAME" --zone "$ZONE" --project "$PROJECT_ID"

echo "Kubernetes context is now set. Verifying nodes..."
kubectl get nodes

echo "Creating Alertmanager config secret..."
kubectl delete secret alertmanager-llm-monitoring -n default --ignore-not-found
kubectl create secret generic alertmanager-llm-monitoring \
  --from-file=alertmanager.yaml=../helm_chart/alertmanager.yaml \
  -n default

echo "Phase 3: Deploying application via Helm (Terraform)..."
terraform apply -auto-approve

echo "Done! Your app and monitoring stack should now be live."

echo "Check the external IP of your service:"
echo "    kubectl get svc"
