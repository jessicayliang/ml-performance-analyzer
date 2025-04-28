import psutil
import GPUtil
import time
import threading
import os
import subprocess
from app.metrics import (
    GPU_MEMORY_USAGE, CPU_USAGE_PERCENT, RAM_USAGE_BYTES,
    GPU_UTILIZATION_PERCENT, GPU_POWER_USAGE_WATTS, GPU_TEMPERATURE_CELSIUS,
    NETWORK_BYTES_SENT, NETWORK_BYTES_RECEIVED, KV_CACHE_SIZE_BYTES
)

def update_resource_metrics():
    CPU_USAGE_PERCENT.set(psutil.cpu_percent())
    RAM_USAGE_BYTES.set(psutil.virtual_memory().used)

    # Network metrics
    net_io = psutil.net_io_counters()
    NETWORK_BYTES_SENT.inc(net_io.bytes_sent)
    NETWORK_BYTES_RECEIVED.inc(net_io.bytes_recv)

    # GPU metrics
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0] # assume first GPU
            GPU_MEMORY_USAGE.set(gpus[0].memoryUsed * 1024 * 1024)
            GPU_UTILIZATION_PERCENT.set(gpu.load * 100)  # Convert to percentage

            # For NVIDIA GPUs, use nvidia-smi for additional metrics
            try:
                # Get temperature
                temp_output = subprocess.check_output(
                    ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
                    universal_newlines=True
                )
                GPU_TEMPERATURE_CELSIUS.set(float(temp_output.strip()))

                # Get power usage
                power_output = subprocess.check_output(
                    ['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits'],
                    universal_newlines=True
                )
                GPU_POWER_USAGE_WATTS.set(float(power_output.strip()))
            except Exception as e:
                print(f"Error getting advanced GPU metrics: {e}")

            # Estimate KV cache size (this is a rough estimate)
            # In practice, you would need to get this from your LLM framework
            KV_CACHE_SIZE_BYTES.set(gpu.memoryUsed * 0.7 * 1024 * 1024)  # Rough estimate
    except Exception as e:
        print(f"Unexpected exception: {e}")

def start_metrics_updater():
    def _loop():
        while True:
            update_resource_metrics()
            time.sleep(5)
    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
