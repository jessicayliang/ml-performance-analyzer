import psutil
import GPUtil
import time
import threading
from .metrics import GPU_MEMORY_USAGE, CPU_USAGE_PERCENT, RAM_USAGE_BYTES

def update_resource_metrics():
    CPU_USAGE_PERCENT.set(psutil.cpu_percent())
    RAM_USAGE_BYTES.set(psutil.virtual_memory().used)
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            GPU_MEMORY_USAGE.set(gpus[0].memoryUsed * 1024 * 1024)
    except Exception:
        pass

def start_metrics_updater():
    def _loop():
        while True:
            update_resource_metrics()
            time.sleep(5)
    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
