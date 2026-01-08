
import psutil

class HardwareSensor:
    def read(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            return {'cpu_percent': cpu_percent, 'memory_percent': memory_percent}
        except Exception:
            return {'cpu_percent': 0.0, 'memory_percent': 0.0}
