# ML Performance Analyzer

Term project for coms6998 applied machine learning in the cloud

A performance analysis framework for pre-trained ML models in cloud environments

---

## Setup

### Deploy GKE Cluster using Terraform

1. Authenticate your Google Cloud Account

```
gcloud auth application-default login
```

2. Build the Docker image and push to GCR

```
PROJECT_ID={your-gcp-project-id}
docker build -t gcr.io/$PROJECT_ID/llm-inference:latest .
gcloud auth configure-docker
docker push gcr.io/$PROJECT_ID/llm-inference:latest
```

3. Install Terraform (for macOS)

```
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

4. Deploy cluster

First, ensure that the `project_id`, `cluster_name`, `image_repository`, and `image_tag` variables are configured correctly in `terraform.tfvars`. Similarly, in `deploy.sh`, configure the correct values for `CLUSTER_NAME`, `ZONE`, and `PROJECT_ID`.

Next, `cd` into the `infra` directory

```
cd infra
```

If you want to redeploy your stack, first clean up your local terraform states:

```
rm -rf .terraform terraform.tfstate terraform.tfstate.backup
```

Next, build your stack:

```
terraform init
bash deploy.sh
```

Wait until your cluster is set up. You can check the pods within the cluster by:

```
kubectl get pods
kubectl logs <pod-name>
```

5. Test performing inference on the cluster

```
// Port-forward inference port
kubectl port-forward svc/llm-monitoring 8000:8000

// Run inference on external IP address
curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" \
 -d '{"prompt": "Explain how transformers work.", "max_tokens": 100, "user_id": "user_1", "model": "qwen"}'
```

To view metrics collected by Prometheus, just go to http://localhost:8000/metrics

6. Open Grafana Dashboards

```
// Port-forward Grafana web UI
kubectl port-forward svc/llm-monitoring-grafana 8080:80
```

Now, just open http://localhost:8080/ for Grafana Web UI. You will need to obtain a password from the secret:

```
kubectl get secret llm-monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

Use the username "admin", and the password decoded from the secret above. You can now navigate to the Dashboard menu to see the custom dashboards for our application (prefixed with LLM).

7. (Optional) Open Prometheus and Alert Manager Web UI

```
// Port-forward Prometheus web UI
kubectl port-forward svc/llm-monitoring-kube-promet-prometheus 9090:9090

// Port-forward Alert Manager web UI
kubectl port-forward svc/llm-monitoring-kube-promet-alertmanager 9093:9093
```

You can now access the Prometheus Web UI at http://localhost:9090 and the Alertmanager UI at http://localhost:9093.
