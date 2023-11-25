#!/bin/bash

# Шаг 1: Проверка наличия приложения в systemd
if sudo systemctl is-active --quiet charlotte_agent; then
    echo "Приложение уже добавлено в systemd"
else
    echo "
    [Unit]
    Description=Your Awesome Python App
    After=network.target

    [Service]
    Type=simple
    ExecStart=/usr/bin/python3 $(pwd)/agent.py
    WorkingDirectory=$(pwd)
    Restart=on-failure
    User=$(whoami)

    [Install]
    WantedBy=multi-user.target
    " > charlotte_agent.service

    # Шаг 2: Открытие порта 5000
    sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
    sudo iptables-save > /etc/iptables/rules.v4

    # Шаг 3: Копирование unit-файла в каталог systemd и запуск приложения
    sudo cp charlotte_agent.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl start charlotte_agent
    sudo systemctl enable charlotte_agent
fi
