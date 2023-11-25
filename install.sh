#!/bin/bash

echo "
[Unit]
Description=Your Awesome Python App
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $(pwd)/charlotte_agent.py
WorkingDirectory=$(pwd)
Restart=on-failure
User=$(whoami)

[Install]
WantedBy=multi-user.target
" > charlotte_agent.service

# Шаг 3: Копирование unit-файла в каталог systemd и запуск приложения
sudo cp charlotte_agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start charlotte_agent
sudo systemctl enable charlotte_agent