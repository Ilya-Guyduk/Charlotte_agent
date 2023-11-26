#!/bin/bash

# Функция для установки приложения
install_application() {
    if sudo systemctl is-active --quiet charlotte_agent; then
        echo "Приложение уже добавлено в systemd"
    else
        echo "Создаем init-файл"
        echo "
        [Unit]
        Description=Charlotte_agent
        After=network.target

        [Service]
        Type=simple
        ExecStart=/usr/bin/python3 /usr/bin/charlotte_agent.py --config=/etc/charlotte_agent/agent.conf
        Restart=on-failure

        [Install]
        WantedBy=multi-user.target
        " > charlotte_agent.service

        echo "Init-файл создан!"
        echo "Великое перемещение файлов!"
        sudo mkdir /etc/charlotte_agent
        sudo mv charlotte_agent.service /etc/systemd/system/charlotte_agent.service
        sudo mv charlotte_agent.py /usr/bin/charlotte_agent.py
        sudo mv agent.conf /etc/charlotte_agent/agent.conf
        sudo mv ./modules/ /etc/charlotte_agent/modules/
        sudo mv README.md /etc/charlotte_agent/README.md
        sudo mv LICENSE /etc/charlotte_agent/LICENSE
        sudo mv setting.sh /etc/charlotte_agent/setting.sh

        echo "Удаляем лишнее!"
        rm -rf ./.git
        rm ./.gitattributes
        rm -r ../Charlotte_agent

        echo "Конфигурация файлов окончена!"

        # Открытие порта 5000
        sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
        sudo iptables-save > /etc/iptables/rules.v4
        echo "Фаерфолл настроен!"

        # Запуск приложения
        sudo systemctl daemon-reload
        sudo systemctl start charlotte_agent
        sudo systemctl enable charlotte_agent
    fi
}

# Функция для удаления приложения
delete_application() {
    if sudo systemctl is-active --quiet charlotte_agent; then
        echo "Останавливаем и удаляем приложение из systemd"
        sudo systemctl stop charlotte_agent
        sudo systemctl disable charlotte_agent
        sudo rm /etc/systemd/system/charlotte_agent.service
        sudo systemctl daemon-reload
    fi

    echo "Удаляем установленные файлы и закрываем порт 5000"
    sudo rm -rf /etc/charlotte_agent
    sudo iptables -D INPUT -p tcp --dport 5000 -j ACCEPT
    sudo iptables-save > /etc/iptables/rules.v4
    echo "Приложение удалено и порт закрыт"
}

# Проверка аргументов и вызов соответствующей функции
if [ "$1" = "--install" ]; then
    install_application
elif [ "$1" = "--delete" ]; then
    delete_application
else
    echo "Usage: $0 --install|--delete"
    exit 1
fi
