import psutil
import GPUtil
import time
import threading
import os
import subprocess
from app.metrics import (
    GPU_MEMORY_USAGE, CPU_USAGE_PERCENT, RAM_USAGE_BYTES,
    GPU_UTILIZATION_PERCENT, MODEL_TEMPERATURE, TOP_P_DISTRIBUTION,
    INFERENCE_COMPUTATION_TIME, CONTEXT_LENGTH_UTILIZATION
)

def initialize_metrics_with_defaults():
    """Initialize metrics with default values to ensure they appear in /metrics"""
    # Histograms need at least one observation to appear in metrics output
    MODEL_TEMPERATURE.observe(0.7)  # Default temperature
    TOP_P_DISTRIBUTION.observe(0.95)  # Default top_p
    INFERENCE_COMPUTATION_TIME.observe(0.0)  # Zero computation time as placeholder
    CONTEXT_LENGTH_UTILIZATION.observe(0.0)  # Zero utilization as placeholder

    # Initialize GPU metrics even if no GPU is available
    GPU_UTILIZATION_PERCENT.set(0.0)
    GPU_MEMORY_USAGE.set(0.0)

    print("Metrics initialized with default values")

def update_resource_metrics():
    # Initialize NVML
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # Assuming single GPU
    except Exception as e:
        print(f"Failed to initialize NVML: {e}")
        return

    while True:
        # CPU and RAM
        CPU_USAGE_PERCENT.set(psutil.cpu_percent())
        RAM_USAGE_BYTES.set(psutil.virtual_memory().used)

        # GPU memory and utilization
        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            util_info = pynvml.nvmlDeviceGetUtilizationRates(handle)

            GPU_MEMORY_USAGE.set(mem_info.used)
            GPU_UTILIZATION_PERCENT.set(util_info.gpu)  # Already in percent (0–100)

        except Exception as e:
            print(f"Failed to collect GPU metrics: {e}")

        time.sleep(5)

def start_metrics_updater():
    initialize_metrics_with_defaults()
    thread = threading.Thread(target=update_resource_metrics, daemon=True)
    thread.start()
