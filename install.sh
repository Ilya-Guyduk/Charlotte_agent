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
    ExecStart=/usr/bin/python3 /usr/bin/charlotte_agent.py --config=/etc/charlotte_agent/agent.conf
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    " > /etc/systemd/system/charlotte_agent.service

    mv charlotte_agent.py /usr/bin/charlotte_agent.py -t
    mv agent.conf /etc/charlotte_agent/agent.conf -t

    # Шаг 2: Открытие порта 5000
    sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
    sudo iptables-save > /etc/iptables/rules.v4

    # Шаг 3: запуск приложения
    sudo systemctl daemon-reload
    sudo systemctl start charlotte_agent
    sudo systemctl enable charlotte_agent
fi
