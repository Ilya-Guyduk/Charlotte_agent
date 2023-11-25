from flask import Flask, request
import json
import os
import importlib
import importlib.util
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import os
import configparser
from modules import *

# Чтение конфигурационных данных из файла
config = configparser.ConfigParser()
config.read('agent.conf')

# Установка переменных среды
os.environ['FLASK_ENV'] = config.get('general', 'ENV', fallback='development')

# Настройка логирования
logging.basicConfig(filename=config.get('general', 'LOG_FILE_PATH', fallback='app.log'), level=logging.DEBUG)
watchdog_logger = logging.getLogger('watchdog')
watchdog_logger.setLevel(getattr(logging, config.get('general', 'WATCHDOG_LOG_LEVEL', fallback='ERROR')))


app = Flask(__name__)
modules = []

logging.debug("Запуск")

# Класс для отслеживания изменений в каталоге modules
class ModuleHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path != 'app.log':  # Исключаем файл app.log из обработки
            logging.info(f'Файл {event.src_path} был создан')
            if event.src_path.endswith(".py"):
                module_name = os.path.basename(event.src_path)[:-3]
                importlib.invalidate_caches()
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

    module_files = [f for f in os.listdir('modules') if f.endswith('.py')]  # получаем список файлов модулей

    for file in module_files:
        module_name = os.path.splitext(file)[0]  # получаем имя модуля из имени файла
        spec = importlib.util.spec_from_file_location(module_name, os.path.join('modules', file))  # создаем спецификацию модуля
        module = importlib.util.module_from_spec(spec)  # создаем объект модуля
        spec.loader.exec_module(module)  # загружаем модуль

        if hasattr(module, 'get_metrics'):
            module_metrics = module.get_metrics()
            all_metrics.update(module_metrics)

    return json.dumps(all_metrics)
# Начинаем отслеживание изменений в каталоге modules
observer = Observer()
observer.schedule(ModuleHandler(), path='./modules', recursive=False)
observer.start()
logging.debug("Отслеживание запущено")


if __name__ == "__main__":
    app.run(host=config.get('general', 'host', fallback='0.0.0.0'), port=config.get('general', 'port', fallback=5000), debug=True)

