#!/bin/bash

# Simple Proximity Sensor Installation Script (No Git Required)
# Downloads files directly from GitHub raw URLs

set -e

echo "🚀 Installing Proximity Sensor System (Direct Download)..."

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

# GitHub repository details
GITHUB_USER="cgninety"
REPO_NAME="sense"
BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${REPO_NAME}/${BRANCH}"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "This doesn't appear to be a Raspberry Pi. Continuing anyway..."
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y python3-pip python3-dev python3-setuptools curl wget python3-rpi.gpio

# Install RPi.GPIO (try multiple methods)
print_status "Installing RPi.GPIO library..."
if ! python3 -c "import RPi.GPIO" 2>/dev/null; then
    print_status "Installing RPi.GPIO via apt (system package)..."
    sudo apt install -y python3-rpi.gpio
    
    if ! python3 -c "import RPi.GPIO" 2>/dev/null; then
        print_status "Installing RPi.GPIO via pip3..."
        pip3 install --user RPi.GPIO
        
        if ! python3 -c "import RPi.GPIO" 2>/dev/null; then
            print_status "Installing RPi.GPIO via sudo pip3..."
            sudo pip3 install RPi.GPIO
        fi
    fi
fi

# Create project directory
PROJECT_DIR="$HOME/proximity-sensor"
print_status "Creating project directory at $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Download project files
print_status "Downloading project files from GitHub..."

FILES=(
    "proximity_sensor.py"
    "config.json" 
    "requirements.txt"
    "install_service.sh"
    "README.md"
    "DEPLOYMENT.md"
    "LICENSE"
)

for file in "${FILES[@]}"; do
    print_status "Downloading $file..."
    if curl -sSL "${BASE_URL}/${file}" -o "$file"; then
        print_status "✅ Downloaded $file"
    else
        print_error "❌ Failed to download $file"
        exit 1
    fi
done

# Make scripts executable
print_status "Making scripts executable..."
chmod +x proximity_sensor.py install_service.sh

# Verify main script
if [ -f "proximity_sensor.py" ] && [ -s "proximity_sensor.py" ]; then
    print_status "✅ Main script downloaded and verified"
else
    print_error "❌ Main script not found or empty"
    exit 1
fi

# Test Python dependencies
print_status "Testing installation..."
if python3 -c "import RPi.GPIO; print('RPi.GPIO imported successfully')" 2>/dev/null; then
    print_status "✅ RPi.GPIO installation verified"
else
    print_error "❌ RPi.GPIO installation failed"
    exit 1
fi

# Test configuration file
if python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
    print_status "✅ Configuration file is valid"
else
    print_error "❌ Configuration file is invalid"
    exit 1
fi

print_status "✅ Installation completed successfully!"
echo ""
echo "📁 Project installed in: $PROJECT_DIR"
echo "🎯 Next steps:"
echo "1. Connect your HC-SR04 sensor and LEDs according to the wiring diagram"
echo "2. Test the sensor: python3 proximity_sensor.py"
echo "3. Install as service: sudo ./install_service.sh"
echo "4. Start service: sudo systemctl start proximity-sensor"
echo ""
echo "📖 For detailed instructions, see README.md"
echo "🔧 To customize settings, edit config.json"
echo ""
print_status "Happy sensing! 🎉"