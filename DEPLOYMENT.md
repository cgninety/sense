# Deployment Guide - Proximity Sensor to Raspberry Pi Zero

## Quick Setup (5 minutes)

### 1. Prepare Your Raspberry Pi Zero
```bash
# SSH into your Pi Zero
ssh pi@your-pi-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

### 2. Deploy from GitHub

#### Option A: One-line Install
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/proximity-sensor-rpi/main/install.sh | bash
```

#### Option B: Manual Clone
```bash
git clone https://github.com/yourusername/proximity-sensor-rpi.git
cd proximity-sensor-rpi
./install.sh
```

### 3. Install as System Service
```bash
sudo ./install_service.sh
sudo systemctl start proximity-sensor
```

### 4. Verify Installation
```bash
sudo systemctl status proximity-sensor
sudo journalctl -u proximity-sensor -f
```

## Hardware Setup

### Wiring Connections
Connect your components according to this diagram:

```
Raspberry Pi Zero    →    Component
==========================================
5V (Pin 2)          →    HC-SR04 VCC
Ground (Pin 6)      →    HC-SR04 GND, LED cathodes
GPIO 23 (Pin 16)    →    HC-SR04 Trig
GPIO 24 (Pin 18)    →    HC-SR04 Echo
GPIO 17 (Pin 11)    →    Green LED + (via 220Ω resistor)
GPIO 27 (Pin 13)    →    Yellow LED + (via 220Ω resistor)  
GPIO 22 (Pin 15)    →    Red LED + (via 220Ω resistor)
```

### Parts List
- 1x Raspberry Pi Zero W (recommended) or Zero 2W
- 1x HC-SR04 Ultrasonic Distance Sensor
- 3x LEDs (Green, Yellow, Red)
- 3x 220Ω resistors
- 1x Half-size breadboard
- Jumper wires (Male-to-Female and Male-to-Male)
- MicroSD card (16GB Class 10)
- Micro USB power supply (2A minimum)

## GitHub Repository Setup

### 1. Create Repository
1. Create a new GitHub repository: `proximity-sensor-rpi`
2. Initialize with README
3. Add this project to the repository

### 2. Configure Secrets (for Auto-Deploy)
In your GitHub repository settings → Secrets and variables → Actions:

```
RPI_HOST: your-raspberry-pi-ip-address
RPI_USER: pi
RPI_SSH_KEY: your-private-ssh-key
```

### 3. Enable Auto-Deploy
Push changes to `main` branch to trigger automatic deployment:

```bash
git add .
git commit -m "Initial deployment setup"
git push origin main
```

## Configuration Options

### Custom GPIO Pins
Edit `config.json` to change pin assignments:
```json
{
  "pins": {
    "trig": 23,
    "echo": 24,
    "led_green": 17,
    "led_yellow": 27,
    "led_red": 22
  }
}
```

### Distance Thresholds
Adjust sensitivity by modifying thresholds:
```json
{
  "thresholds": {
    "safe_distance": 100,     // Green LED (mm)
    "caution_distance": 50,   // Yellow LED (mm)
    "danger_distance": 10     // Red LED solid (mm)
  }
}
```

## Monitoring & Maintenance

### Check Service Status
```bash
sudo systemctl status proximity-sensor
```

### View Live Logs
```bash
sudo journalctl -u proximity-sensor -f
```

### Update Deployment
```bash
cd /home/pi/proximity-sensor
git pull
sudo systemctl restart proximity-sensor
```

### Performance Tuning
For better performance on Pi Zero:
```json
{
  "sensor": {
    "measurement_interval": 0.2,  // Slower for Pi Zero
    "timeout": 0.2,               // Longer timeout
    "max_retries": 5              // More retries
  }
}
```

## Troubleshooting

### Common Issues

**❌ Permission denied accessing GPIO**
```bash
sudo usermod -a -G gpio pi
# Log out and back in
```

**❌ No distance readings**
- Check 5V power connection to sensor
- Verify wiring connections
- Ensure sensor face is clean and unobstructed

**❌ Service fails to start**
```bash
sudo journalctl -u proximity-sensor --no-pager
```

**❌ Erratic readings**
- Move sensor away from vibrations
- Check for loose connections
- Add delay between readings

### Debug Mode
```bash
# Stop service and run manually with debug
sudo systemctl stop proximity-sensor
cd /home/pi/proximity-sensor
python3 proximity_sensor.py
```

## Advanced Usage

### Remote Monitoring
Add webhook notifications for distance alerts:
```python
# In proximity_sensor.py, add to update_leds()
if distance < self.danger_distance:
    send_webhook_alert(distance)
```

### Data Logging
Enable CSV logging for data analysis:
```json
{
  "logging": {
    "csv_file": "distance_data.csv",
    "csv_enabled": true
  }
}
```

### Multiple Sensors
Run multiple instances with different configs:
```bash
python3 proximity_sensor.py --config sensor1_config.json &
python3 proximity_sensor.py --config sensor2_config.json &
```

## Security Notes

- Change default Pi credentials
- Use SSH keys instead of passwords
- Enable UFW firewall if exposed to internet
- Regular system updates with `sudo apt update && sudo apt upgrade`

## Support

- 📖 Full documentation: [README.md](README.md)
- 🐛 Report issues: [GitHub Issues](https://github.com/yourusername/proximity-sensor-rpi/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/proximity-sensor-rpi/discussions)