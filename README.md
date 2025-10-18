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

- **GPIO pins**: Change pin assignments for your wiring
- **Distance thresholds**: Adjust safe/caution/danger distances
- **Sensor settings**: Modify timeout and retry settings
- **Logging**: Set log level and file location

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
| ≥ 100mm | Green ON | Safe distance |
| 50-99mm | Yellow ON | Caution zone |
| 10-49mm | Red ON | Danger zone |
| < 10mm | Red FLASHING | Critical proximity |

## Monitoring

- **Console output**: Real-time distance readings
- **Log file**: `proximity_sensor.log` with timestamps
- **System logs**: `sudo journalctl -u proximity-sensor -f`

## Troubleshooting

### Common Issues

1. **Permission denied**: Run with `sudo` or add user to `gpio` group
2. **No distance readings**: Check wiring and 5V power supply
3. **Erratic readings**: Ensure stable mounting and clean sensor face
4. **Service won't start**: Check logs with `sudo journalctl -u proximity-sensor`

### Debug Mode
```bash
# Enable debug logging
python3 proximity_sensor.py --log-level DEBUG
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
