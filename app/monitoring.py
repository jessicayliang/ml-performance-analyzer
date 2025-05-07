import psutil
import GPUtil
import time
import threading
from app.metrics import GPU_MEMORY_USAGE, CPU_USAGE_PERCENT, RAM_USAGE_BYTES

def _update_resource_metrics():
    CPU_USAGE_PERCENT.set(psutil.cpu_percent())
    RAM_USAGE_BYTES.set(psutil.virtual_memory().used)
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            GPU_MEMORY_USAGE.set(gpus[0].memoryUsed * 1024 * 1024)
    except Exception as e:
        print(f"Unexpected exception: {e}")

def start_metrics_updater():
    def _loop():
        while True:
            _update_resource_metrics()
            time.sleep(5)
    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()