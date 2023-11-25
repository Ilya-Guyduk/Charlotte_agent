from flask import Flask, request
import json
import os
import importlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
modules = []

# Класс для отслеживания изменений в каталоге modules
class ModuleHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".py"):
            module_name = os.path.basename(event.src_path)[:-3]  # Получаем имя модуля
            importlib.invalidate_caches()  # Очищаем кеш импортов, чтобы модуль был перезагружен
            module = importlib.import_module("modules." + module_name)
            modules.append(module)

# Роут для добавления модулей
@app.route('/add_module', methods=['POST'])
def add_module():
    module_data = request.get_json()
    module_name = module_data.get("module_name")
    if module_name:
        importlib.invalidate_caches()  # Очищаем кеш импортов, чтобы модуль был перезагружен
        module = importlib.import_module("modules." + module_name)
        modules.append(module)
        return 'Модуль успешно добавлен!'
    else:
        return 'Ошибка: не указано имя модуля', 400

# Роут для получения метрик
@app.route('/get_metrics', methods=['GET'])
def get_metrics():
    all_metrics = {}
    for module in modules:
        if hasattr(module, 'get_metrics'):
            module_metrics = module.get_metrics()
            all_metrics.update(module_metrics)
    return json.dumps(all_metrics)

# Начинаем отслеживание изменений в каталоге modules
observer = Observer()
observer.schedule(ModuleHandler(), path='./modules', recursive=False)
observer.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()

observer.join()
