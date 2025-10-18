# Proximity Sensor for Raspberry Pi Zero

A Python-based proximity sensor system using an HC-SR04 ultrasonic sensor with LED feedback indicators. Perfect for distance monitoring, obstacle detection, or parking assistance projects.

## Features

- **Real-time distance measurement** using HC-SR04 ultrasonic sensor
- **Visual feedback** with three LEDs (Green/Yellow/Red)
- **Configurable thresholds** and GPIO pins
- **Robust error handling** and logging
- **Graceful shutdown** handling
- **Easy deployment** to Raspberry Pi Zero

## Hardware Requirements

- Raspberry Pi Zero/Zero W/Zero 2W
- HC-SR04 Ultrasonic Distance Sensor
- 3x LEDs (Green, Yellow, Red)
- 3x 220Ω resistors (for LEDs)
- Breadboard and jumper wires
- MicroSD card (16GB recommended)

## Wiring Diagram

```
HC-SR04 Ultrasonic Sensor:
- VCC → 5V (Pin 2)
- GND → Ground (Pin 6)
- Trig → GPIO 23 (Pin 16)
- Echo → GPIO 24 (Pin 18)

LEDs (with 220Ω resistors):
- Green LED → GPIO 17 (Pin 11)
- Yellow LED → GPIO 27 (Pin 13)
- Red LED → GPIO 22 (Pin 15)
- All LED cathodes → Ground
```

## Installation

### Method 1: One-Line Install (Recommended)

```bash
# Download and run the simple installation script (no git required)
curl -sSL https://raw.githubusercontent.com/cgninety/sense/main/install_simple.sh | bash
```

### Method 2: Git Clone

```bash
# Clone the repository
git clone https://github.com/cgninety/sense.git proximity-sensor
cd proximity-sensor

# Install dependencies
pip3 install --user -r requirements.txt

# Make executable
chmod +x proximity_sensor.py

# Run the sensor
python3 proximity_sensor.py
```

### Method 3: Full Auto-Install (with git)

```bash
# Download and run the full installation script
curl -sSL https://raw.githubusercontent.com/cgninety/sense/main/install.sh | bash
```

## Configuration

Edit `config.json` to customize:

### GPIO Pins
Change pin assignments for your wiring:
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
Adjust sensitivity (values always in millimeters):
```json
{
  "thresholds": {
    "safe_distance": 100,     // 100mm = ~3.94 inches (Green LED)
    "caution_distance": 50,   // 50mm = ~1.97 inches (Yellow LED)
    "danger_distance": 10     // 10mm = ~0.39 inches (Red LED solid)
  }
}
```

### Display Units
Configure how distances are displayed:
```json
{
  "display": {
    "units": "both",          // Options: "mm", "inches", "cm", "both", "all"
    "primary_unit": "mm",     // Primary unit when showing "both"  
    "decimal_places": 2       // Number of decimal places
  }
}
```

**Unit Display Options:**
- `"mm"` → `150.25mm`
- `"inches"` → `5.91in`  
- `"cm"` → `15.03cm`
- `"both"` → `150.25mm (5.91in)` or `5.91in (150.25mm)`
- `"all"` → `150.25mm | 15.03cm | 5.91in`

### Dynamic Blinking
Configure the intelligent LED blinking system:
```json
{
  "blinking": {
    "enabled": true,          // Enable/disable dynamic blinking
    "base_bpm": 60,           // Base blink rate (1 blink/second)
    "min_bpm": 30,            // Minimum rate (1 blink every 2 seconds)
    "max_bpm": 120            // Maximum rate (2 blinks/second)
  }
}
```

### Sensor Settings
Modify timeout and retry settings:
```json
{
  "sensor": {
    "timeout": 0.5,           // Sensor timeout in seconds
    "measurement_interval": 0.1,  // Time between readings (shorter for smooth blinking)
    "max_retries": 5          // Max failed readings before stopping
  }
}

## Usage

### Manual Start
```bash
python3 proximity_sensor.py
```

### Run as Service (Auto-start on boot)
```bash
# Install as systemd service
sudo ./install_service.sh

# Control the service
sudo systemctl start proximity-sensor
sudo systemctl stop proximity-sensor
sudo systemctl status proximity-sensor
```

## LED Behavior

| Distance Range | LED Status | Description |
|----------------|------------|-------------|
| ≥ 100mm (≥3.94in) | 🟢 Green SOLID | Safe distance - no blinking |
| 50-99mm (1.97-3.90in) | 🟡 Yellow BLINKING | Caution zone - slower near safe, faster near danger |
| 10-49mm (0.39-1.93in) | 🔴 Red BLINKING | Danger zone - faster as you get closer |
| < 10mm (<0.39in) | 🔴 Red FAST BLINKING | Critical proximity - maximum blink rate |

### Dynamic Blinking System

The LEDs now use **intelligent blinking** that responds to your proximity:

- **Slowest rate**: 30 BPM (1 blink every 2 seconds)
- **Base rate**: 60 BPM (1 blink per second)  
- **Fastest rate**: 120 BPM (2 blinks per second)
- **Caution zone**: Yellow LED blinks 30-60 BPM (slower → faster as you approach danger)
- **Danger zone**: Red LED blinks 60-120 BPM (faster as you get closer)
- **Critical zone**: Red LED at maximum 120 BPM (2 blinks/second)

**The closer you get, the faster it blinks!** ⚡

## Monitoring

- **Console output**: Real-time distance readings
- **Log file**: `proximity_sensor.log` with timestamps
- **System logs**: `sudo journalctl -u proximity-sensor -f`

## Troubleshooting

### Quick Diagnostics

**If you get `ModuleNotFoundError: No module named 'RPi'`:**
```bash
python3 troubleshoot_gpio.py
```

**If you get "Timeout waiting for echo start" errors:**
```bash
# Test GPIO pins and wiring
python3 test_wiring.py

# Test with diagnostics mode
python3 proximity_sensor.py --test-gpio

# Check your wiring connections (see wiring diagram above)
```

### Common Issues

1. **RPi.GPIO not found**: 
   ```bash
   # Try these in order:
   sudo apt install python3-rpi.gpio
   pip3 install --user RPi.GPIO
   sudo pip3 install RPi.GPIO
   ```

2. **Permission denied accessing GPIO**:
   ```bash
   sudo usermod -a -G gpio $USER
   # Log out and back in
   ```

3. **"Timeout waiting for echo start" - No distance readings**: 
   ```bash
   # Step-by-step diagnosis:
   python3 test_wiring.py        # Interactive wiring test
   python3 proximity_sensor.py --test-gpio  # GPIO diagnostics
   ```
   **Common causes:**
   - Echo pin not connected to GPIO 24
   - Sensor not getting 5V power (check Pin 2)
   - Loose breadboard connections
   - Wrong GPIO pin numbers in config.json
   - Faulty HC-SR04 sensor

4. **Erratic readings**: 
   - Ensure stable mounting and clean sensor face
   - Check for loose connections
   - Add delay between readings in config

5. **Service won't start**: 
   ```bash
   sudo journalctl -u proximity-sensor -f
   ```

### Debug Mode
```bash
# Enable debug logging
python3 proximity_sensor.py --log-level DEBUG
```

### Manual Testing
```bash
# Test without service
sudo systemctl stop proximity-sensor
cd /home/pi/proximity-sensor
python3 proximity_sensor.py
```

## Development

### Running Tests
```bash
python3 -m pytest tests/
```

### Code Style
```bash
# Format code
black proximity_sensor.py

# Check style
flake8 proximity_sensor.py
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Hardware Notes

- **Raspberry Pi Zero compatibility**: Tested on Zero, Zero W, and Zero 2W
- **Power requirements**: Use quality power supply (≥2A recommended)
- **GPIO voltage**: Pi Zero is 3.3V, ensure level compatibility
- **Sensor range**: HC-SR04 effective range is 2cm to 4m
