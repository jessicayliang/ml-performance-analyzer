output "kubeconfig_hint" {
  value = "Run: gcloud container clusters get-credentials ${var.cluster_name} --region ${var.region} --project ${var.project_id}"
}
