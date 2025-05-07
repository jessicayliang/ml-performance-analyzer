provider "google" {
  project = var.project_id
  region  = var.region
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.zone

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = "default"
  subnetwork = "default"
}

resource "google_container_node_pool" "gpu_nodes" {
  name       = "gpu-pool"
  cluster    = google_container_cluster.primary.name
  location   = var.zone
  node_count = 1

  node_config {
    machine_type = "g2-standard-4"  # Compatible with NVIDIA L4
    guest_accelerator {
      type  = "nvidia-l4"
      count = 1
    }

    labels = {
      gpu = "l4"
    }

    tags = ["gpu-node"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }
}

resource "kubernetes_priority_class" "dcgm_exporter_priority" {
  metadata {
    name = "dcgm-exporter"
  }
  value         = 10000000
  global_default = false
  description   = "Custom priority class for dcgm-exporter pods to avoid system-critical quota issues."
}

resource "helm_release" "llm_monitoring" {
  name       = "llm-monitoring"
  chart      = "../helm_chart"
  namespace  = "default"
  create_namespace = true
  dependency_update = true

  set {
	name  = "image.repository"
	value = var.image_repository
  }

  set {
    name  = "image.tag"
    value = var.image_tag
  }

  set {
	name  = "forceRedeploy"  # this is used to redeploy HELM each time "terraform apply" is called
	value = timestamp()
  }

  depends_on = [
	google_container_node_pool.gpu_nodes,
	kubernetes_priority_class.dcgm_exporter_priority
  ]
}