import psutil
import json

def get_metrics():
    uptime_seconds = int(psutil.boot_time())
    uptime_hours = uptime_seconds // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    uptime_seconds = (uptime_seconds % 3600) % 60
    module_data = {
        "module_name": "Health_Module",
        "metrics": {
            "uptime": {
                "hours": uptime_hours,
                "minutes": uptime_minutes,
                "seconds": uptime_seconds
            }
        }
    }
    return module_data
    print(module_data)
