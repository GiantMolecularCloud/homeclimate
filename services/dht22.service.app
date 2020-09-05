[Unit]
Description=homeclimate temperature humidity monitoring at pin17
After=influxdb.service
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=5
User=root
ExecStart=/usr/bin/python3 /home/pi/homeclimate/scripts/dht22.py

[Install]
WantedBy=multi-user.target
