import psutil
import json

def get_cpu_load():
    cpu_percent = psutil.cpu_percent(interval=1)  # Получаем загрузку процессора за последнюю секунду
    return cpu_percent

# Пример использования функции
cpu_load = get_cpu_load()
print(f"Нагрузка процессора: {cpu_load}%")

# Предположим, что для отправки метрик к агенту мы будем использовать библиотеку requests
# Здесь мы отправим данные о нагрузке процессора в формате JSON на сервер агента

agent_url = ' http://0.0.0.0:5000/add_module'
module_data = {
    "module_name": "CPU_Module",
    "metrics": {
        "cpu_load": cpu_load
    }
}

response = requests.post(agent_url, json=module_data)
print(response.text)
