variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  default     = "us-east1"
  description = "GCP region"
}

variable "zone" {
  type        = string
  default     = "us-east1-b"
  description = "GCP zone"
}

variable "cluster_name" {
  type        = string
  default     = "llm-gke-cluster"
  description = "GKE Cluster name"
}

variable "image_repository" {
  type        = string
  description = "Full image repository path (e.g. gcr.io/PROJECT_ID/llm-inference)"
}

variable "image_tag" {
  type        = string
  default     = "latest"
  description = "Docker image tag to deploy"
}
