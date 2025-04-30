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

## Metrics Collected

### Garbage collection

`python_gc_objects_collected_total`: The total number of objects collected during garbage collection.
`python_gc_objects_uncollectable_total`: Number of uncollectable objects found during GC.
`python_gc_collections_total`: The number of times each generation was collected.
`process_virtual_memory_bytes`: Total virtual memory used by the process.

### Process

`process_resident_memory_bytes`: The amount of physical memory (RAM) used by the process.
`process_cpu_seconds_total`: Total CPU time spent in user and system mode.
`process_open_fds`: Number of open file descriptors.
`process_max_fds`: The maximum number of open file descriptors.

### Request Latency

`llm_request_latency_seconds`: Latency in processing requests.
`llm_time_to_first_token_seconds`: Time from request to the first token generation.

### Request and Token

`llm_request_count_total`: Total number of requests made.
`llm_tokens_generated_total`: Total number of tokens generated in response to requests.
`llm_tokens_input_total`: Total number of input tokens processed.
`llm_error_count_total`: Total number of failed requests.

### Resource Utilization

`llm_gpu_memory_usage_bytes`: GPU memory usage.
`llm_cpu_usage_percent`: CPU usage percentage.
`llm_ram_usage_bytes`: RAM usage.

### Token Length

`llm_token_length_input`: Distribution of input token lengths.
`llm_token_length_output`: Distribution of output token lengths.

### Queue and Rate Limit

`llm_queue_time_seconds`: Time spent in the queue before processing.
`llm_queue_size`: Current size of the request queue.
`llm_rate_limit_breaches_total`: Number of rate-limit breaches.
`llm_throttling_incidents_total`: Number of throttling incidents.
