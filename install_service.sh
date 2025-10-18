#!/bin/bash

# Service installation script for proximity sensor
# Run this script to install the proximity sensor as a systemd service

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for systemd operations
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script with sudo"
    exit 1
fi

# Get the current directory and user
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)

print_status "Installing proximity sensor service..."
print_status "Script directory: $SCRIPT_DIR"
print_status "User: $ACTUAL_USER"

# Create the systemd service file
SERVICE_FILE="/etc/systemd/system/proximity-sensor.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Proximity Sensor with LED Indicators
Documentation=https://github.com/yourusername/proximity-sensor-rpi
After=multi-user.target
Wants=network-online.target

[Service]
Type=simple
User=$ACTUAL_USER
Group=$ACTUAL_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/proximity_sensor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=proximity-sensor

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$SCRIPT_DIR $USER_HOME/.local

# Environment
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/usr/local/lib/python3/dist-packages:/usr/lib/python3/dist-packages

[Install]
WantedBy=multi-user.target
EOF

print_status "Created service file: $SERVICE_FILE"

# Set proper permissions
chmod 644 "$SERVICE_FILE"

# Add user to gpio group if not already added
if ! groups "$ACTUAL_USER" | grep -q gpio; then
    print_status "Adding user $ACTUAL_USER to gpio group..."
    usermod -a -G gpio "$ACTUAL_USER"
    print_warning "User added to gpio group. You may need to log out and back in for changes to take effect."
fi

# Reload systemd daemon
print_status "Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service
print_status "Enabling proximity-sensor service..."
systemctl enable proximity-sensor.service

print_status "✅ Service installed successfully!"
echo ""
echo "🎯 Service management commands:"
echo "  Start service:    sudo systemctl start proximity-sensor"
echo "  Stop service:     sudo systemctl stop proximity-sensor"
echo "  Service status:   sudo systemctl status proximity-sensor"
echo "  View logs:        sudo journalctl -u proximity-sensor -f"
echo "  Disable service:  sudo systemctl disable proximity-sensor"
echo ""
echo "🔧 The service is enabled and will start automatically on boot."
echo "   To start it now: sudo systemctl start proximity-sensor"