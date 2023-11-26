import psutil
import json
import requests

def get_cpu_load():
    cpu_percent = psutil.cpu_percent(interval=1)  # Получаем загрузку процессора за последнюю секунду
    module_data = {
        "module_name": "CPU_Module",
        "metrics": {
            "cpu_load": cpu_percent
        }
    }
    return json.dumps(module_data)

def get_metrics():
    cpu_percent = psutil.cpu_percent(interval=1)  # Получаем загрузку процессора за последнюю секунду
    module_metrics = {
                "module_name": {
                    "Health_Module": {
                        "metrics": {
                            "cpu_load": cpu_percent
                }
            }
        }
    }
    return module_metrics


