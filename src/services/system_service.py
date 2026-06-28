"""System metrics service."""
from __future__ import annotations
import platform, socket

try:
    import psutil; _PSUTIL = True
except ImportError:
    _PSUTIL = False

class SystemService:
    @classmethod
    def memory_status(cls) -> str:
        if not _PSUTIL: return "ok"
        return "warning" if psutil.virtual_memory().percent > 90 else "ok"

    @classmethod
    def snapshot(cls) -> dict:
        base = {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
        }
        if _PSUTIL:
            vm = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            base.update({
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory": {
                    "total_mb": round(vm.total/1_048_576, 1),
                    "used_mb": round(vm.used/1_048_576, 1),
                    "percent": vm.percent,
                },
                "disk": {
                    "total_gb": round(disk.total/1_073_741_824, 1),
                    "free_gb": round(disk.free/1_073_741_824, 1),
                    "percent": disk.percent,
                },
            })
        else:
            base["note"] = "Install psutil for full system metrics."
        return base
