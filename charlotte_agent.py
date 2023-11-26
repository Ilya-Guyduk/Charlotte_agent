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

class ModuleHandler(FileSystemEventHandler):
    def __init__(self, modules):
        self.modules = modules

    def on_created(self, event):
        if event.src_path != 'app.log':
            logging.info(f'Файл {event.src_path} был создан')
            if event.src_path.endswith(".py"):
                module_name = os.path.basename(event.src_path)[:-3]
                importlib.invalidate_caches()
                module = importlib.import_module("modules." + module_name)
                self.modules.append(module)

class ModuleManager:
    def __init__(self, config):
        self.app = Flask(__name__)
        self.modules = []
        self.config = config

    def setup_environment_variables(self):
        os.environ['FLASK_ENV'] = self.config.get('general', 'ENV', fallback='development')

    def configure_logging(self):
        log_file_path = self.config.get('general', 'LOG_FILE_PATH', fallback='app.log')
        logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
        watchdog_logger = logging.getLogger('watchdog')
        watchdog_logger.setLevel(getattr(logging, self.config.get('general', 'WATCHDOG_LOG_LEVEL', fallback='ERROR')))

    def add_routes(self):
        @self.app.route('/add_module', methods=['POST'])
        def add_module():
            module_data = request.get_json()
            module_name = module_data.get("module_name")
            if module_name:
                importlib.invalidate_caches()
                module = importlib.import_module("modules." + module_name)
                self.modules.append(module)
                return 'Модуль успешно добавлен!'
            else:
                return 'Ошибка: не указано имя модуля', 400

        @self.app.route('/get_metrics', methods=['GET'])
        def get_metrics():
            all_metrics = {}

            module_files = [f for f in os.listdir('/etc/charlotte_agent/modules') if f.endswith('.py')]


            for file in module_files:
                module_name = os.path.splitext(file)[0]
                spec = importlib.util.spec_from_file_location(module_name, os.path.join('/etc/charlotte_agent/modules', file))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'get_metrics'):
                    module_metrics = module.get_metrics()
                    all_metrics.update(module_metrics)

            return json.dumps(all_metrics)

    def start_watching(self):
        observer = Observer()
        observer.schedule(ModuleHandler(self.modules), path='/etc/charlotte_agent/modules', recursive=False)
        observer.start()
        logging.debug("Отслеживание запущено")

    def run(self):
        self.app.run(host=self.config.get('general', 'FLASK_HOST', fallback='0.0.0.0'),
                     port=self.config.get('general', 'FLASK_PORT', fallback=5000),
                     debug=False)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('/etc/charlotte_agent/agent.conf')

    module_manager = ModuleManager(config)
    module_manager.setup_environment_variables()
    module_manager.configure_logging()
    module_manager.add_routes()
    module_manager.start_watching()
    module_manager.run()
