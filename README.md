# ml-performance-analyzer

Term project for coms6998 applied machine learning in the cloud

A performance analysis framework for pre-trained ML models in cloud environments

## Run inference

```bash
// Set up
git clone https://github.com/jessicayliang/ml-performance-analyzer.git
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000

// Run inference
curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" \
    -d '{"prompt": "Explain how transformers work.", "max_tokens": 100}'
```

## Setting Up Prometheus and Grafana on a GKE Cluster

1. Create cluster:
``` bash
gcloud container clusters create aml-project \                                                           
  --zone=asia-east1-c \                                                                                          
  --machine-type=n1-standard-1 \
  --accelerator type=nvidia-tesla-t4,count=1 \
  --num-nodes=1 \
  --project=coms6998-term-project \
  --enable-ip-alias
```

2. Install NVIDIA GPU drivers:
```bash
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
```

3. Install Helm

```bash
brew install helm
```
4. Add Prometheus Community Helm Repository

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

5. Install kube-prometheus-stack

```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

## Deploy and monitor tst-app

1. Configure Docker to Authenticate with Google Container Registry (GCR)

```bash
gcloud auth configure-docker
```

2. Retrieve Credentials and Set Cluster Context

```bash
gcloud container clusters get-credentials aml-project --zone asia-east1-c --project coms6998-term-project
```

3. Build and Push Docker Image for tst-app

```bash
docker buildx build --platform linux/amd64 -t gcr.io/coms6998-term-project/tst-app:latest --push .
```

4. Deploy tst-app and monitoring service for Prometheus
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f servicemonitor.yaml

```

## Accessing Dashboards

1. Port-forward the Grafana service:

``` bash
kubectl port-forward svc/kube-prometheus-stack-grafana 3000:80 -n monitoring
```
Access Grafana at: http://localhost:3000

**Login Credentials**

- **Username:** `admin`  
- **Password:** `prom-operator`


2. Port-forward the Prometheus service:
``` bash
kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring
```
Access Prometheus at: http://localhost:9090