#!/bin/bash

# Proximity Sensor Installation Script for Raspberry Pi Zero
# This script sets up the proximity sensor system and all dependencies

set -e

echo "🚀 Installing Proximity Sensor System..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "This doesn't appear to be a Raspberry Pi. Continuing anyway..."
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python dependencies
print_status "Installing Python dependencies..."
sudo apt install -y python3-pip python3-dev python3-setuptools

# Install RPi.GPIO
print_status "Installing RPi.GPIO library..."
pip3 install --user RPi.GPIO

# Enable GPIO (if not already enabled)
print_status "Enabling GPIO interface..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
fi

# Create project directory
PROJECT_DIR="$HOME/proximity-sensor"
if [ ! -d "$PROJECT_DIR" ]; then
    print_status "Creating project directory at $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
fi

# Download project files (replace with your actual repository)
print_status "Setting up project files..."
cd "$PROJECT_DIR"

# If git is available and this is a git repo
if command -v git &> /dev/null && [ -d ".git" ]; then
    print_status "Updating from git repository..."
    git pull
else
    print_status "Copying project files..."
    # Copy files from current directory if they exist
    for file in proximity_sensor.py config.json README.md; do
        if [ -f "../sense/$file" ]; then
            cp "../sense/$file" .
            print_status "Copied $file"
        fi
    done
fi

# Make the main script executable
chmod +x proximity_sensor.py

# Test the installation
print_status "Testing installation..."
if python3 -c "import RPi.GPIO; print('RPi.GPIO imported successfully')" 2>/dev/null; then
    print_status "✅ RPi.GPIO installation verified"
else
    print_error "❌ RPi.GPIO installation failed"
    exit 1
fi

# Create systemd service file
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/proximity-sensor.service > /dev/null <<EOF
[Unit]
Description=Proximity Sensor Service
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/proximity_sensor.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable proximity-sensor.service

print_status "✅ Installation completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Connect your HC-SR04 sensor and LEDs according to the wiring diagram"
echo "2. Test the sensor: python3 proximity_sensor.py"
echo "3. Start the service: sudo systemctl start proximity-sensor"
echo "4. Check status: sudo systemctl status proximity-sensor"
echo ""
echo "📖 For detailed instructions, see README.md"
echo "🔧 To customize settings, edit config.json"
echo ""
print_status "Happy sensing! 🎉"