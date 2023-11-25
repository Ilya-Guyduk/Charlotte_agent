from flask import Flask, request
import json

app = Flask(__name__)
modules = []

# Роут для добавления модулей
@app.route('/add_module', methods=['POST'])
def add_module():
    module_data = request.get_json()
    modules.append(module_data)
    return 'Модуль успешно добавлен!'

# Роут для получения метрик
@app.route('/metrics', methods=['GET'])
def get_metrics():
    all_metrics = {}
    for module in modules:

        pass
    return json.dumps(all_metrics)

if __name__ == '__main__':
    app.run()
