#!/bin/bash

# Ensure running as root
if [ "$EUID" -ne 0 ]
then echo "Please run as root"
    exit
fi

# Download and extract the repository
cd /var
git clone https://github.com/tornikebcw/pickleprobe.git
cd pickleprobe

# Check if Python is installed
if command -v python3 &>/dev/null
then
    echo "Python 3 is installed"
else
    echo "Python 3 is not installed"
    exit 1
fi

# Check if pip is installed, and install if not
if command -v pip3 &>/dev/null
then
    echo "pip3 is installed"
else
    echo "pip3 is not installed, installing now"
    apt update
    apt install python3-pip -y
fi

# Create a virtual environment and install requirements.txt
pip install -r requirements.txt

# Create systemd service file
cat > /etc/systemd/system/pickleprobe.service <<EOF
[Unit]
Description=PickleProbe Service
After=network.target

[Service]
ExecStart=/var/pickleprobe/.venv/bin/python3 /var/lib/pickleprobe/main.py
WorkingDirectory=/var/pickleprobe
User=root
Group=root
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=pickleprobe

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
systemctl daemon-reload
systemctl enable pickleprobe
systemctl start pickleprobe
