import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import pynvml
import time
import threading

class GPUMonitor(threading.Thread):
    def __init__(self, gpu_index=0, interval=0.5):
        super().__init__()
        self.gpu_index = gpu_index
        self.interval = interval
        self.running = False
        self.peak_vram = 0
        self.handle = None

    def __enter__(self):
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(self.gpu_index)
        self.running = True
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        self.join()
        pynvml.nvmlShutdown()

    def run(self):
        while self.running:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            used_mb = mem_info.used / (1024**2)
            self.peak_vram = max(self.peak_vram, used_mb)
            time.sleep(self.interval)
