#!/usr/bin/env python3
"""
Proximity Sensor with LED Indicators
Uses HC-SR04 ultrasonic sensor to detect object distance and provide visual feedback.
"""

import RPi.GPIO as GPIO
import time
import logging
import signal
import sys
import json
from pathlib import Path
from typing import Optional


class ProximitySensor:
    """Ultrasonic proximity sensor with LED feedback system."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the proximity sensor with configuration."""
        self.config = self._load_config(config_file)
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # GPIO pins from config
        self.trig_pin = self.config['pins']['trig']
        self.echo_pin = self.config['pins']['echo']
        self.led_green = self.config['pins']['led_green']
        self.led_yellow = self.config['pins']['led_yellow']
        self.led_red = self.config['pins']['led_red']
        
        # Distance thresholds
        self.safe_distance = self.config['thresholds']['safe_distance']
        self.caution_distance = self.config['thresholds']['caution_distance']
        self.danger_distance = self.config['thresholds']['danger_distance']
        
        # Setup GPIO
        self._setup_gpio()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Proximity sensor initialized successfully")

    def _load_config(self, config_file: str) -> dict:
        """Load configuration from JSON file."""
        config_path = Path(__file__).parent / config_file
        
        # Default configuration
        default_config = {
            "pins": {
                "trig": 23,
                "echo": 24,
                "led_green": 17,
                "led_yellow": 27,
                "led_red": 22
            },
            "thresholds": {
                "safe_distance": 100,
                "caution_distance": 50,
                "danger_distance": 10
            },
            "sensor": {
                "timeout": 0.1,
                "measurement_interval": 0.1,
                "max_retries": 3
            },
            "logging": {
                "level": "INFO",
                "file": "proximity_sensor.log"
            }
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                # Merge user config with defaults
                default_config.update(user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration")
        else:
            # Create default config file
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config file: {config_path}")
        
        return default_config

    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config['logging']['level'].upper())
        log_file = self.config['logging']['file']
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _setup_gpio(self):
        """Initialize GPIO pins."""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup pins
            GPIO.setup(self.trig_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.setup(self.led_green, GPIO.OUT)
            GPIO.setup(self.led_yellow, GPIO.OUT)
            GPIO.setup(self.led_red, GPIO.OUT)
            
            # Initialize all LEDs to off
            self._turn_off_all_leds()
            
            self.logger.info("GPIO setup completed")
            
        except Exception as e:
            self.logger.error(f"GPIO setup failed: {e}")
            raise

    def _turn_off_all_leds(self):
        """Turn off all LEDs."""
        GPIO.output(self.led_green, False)
        GPIO.output(self.led_yellow, False)
        GPIO.output(self.led_red, False)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def get_distance(self) -> Optional[float]:
        """
        Measure distance using ultrasonic sensor.
        Returns distance in millimeters or None if measurement fails.
        """
        try:
            # Ensure trigger is low
            GPIO.output(self.trig_pin, False)
            time.sleep(0.05)
            
            # Send trigger pulse
            GPIO.output(self.trig_pin, True)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(self.trig_pin, False)
            
            # Wait for echo start with timeout
            pulse_start = None
            timeout_start = time.time()
            while GPIO.input(self.echo_pin) == 0:
                pulse_start = time.time()
                if time.time() - timeout_start > self.config['sensor']['timeout']:
                    self.logger.warning("Timeout waiting for echo start")
                    return None
            
            # Wait for echo end with timeout
            pulse_end = None
            timeout_start = time.time()
            while GPIO.input(self.echo_pin) == 1:
                pulse_end = time.time()
                if time.time() - timeout_start > self.config['sensor']['timeout']:
                    self.logger.warning("Timeout waiting for echo end")
                    return None
            
            if pulse_start is None or pulse_end is None:
                return None
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Convert to mm
            
            # Validate reasonable distance (HC-SR04 range: 2cm to 4m)
            if distance < 20 or distance > 4000:
                self.logger.warning(f"Distance out of range: {distance}mm")
                return None
            
            return round(distance, 2)
            
        except Exception as e:
            self.logger.error(f"Distance measurement failed: {e}")
            return None

    def update_leds(self, distance: float):
        """Update LED status based on distance."""
        try:
            # Turn off all LEDs first
            self._turn_off_all_leds()
            
            if distance >= self.safe_distance:
                # Safe distance - green LED
                GPIO.output(self.led_green, True)
                
            elif distance >= self.caution_distance:
                # Caution distance - yellow LED
                GPIO.output(self.led_yellow, True)
                
            elif distance >= self.danger_distance:
                # Danger distance - red LED solid
                GPIO.output(self.led_red, True)
                
            else:
                # Very close - flash red LED with variable speed
                flash_delay = max(0.05, distance / 200.0)
                GPIO.output(self.led_red, True)
                time.sleep(flash_delay)
                GPIO.output(self.led_red, False)
                time.sleep(flash_delay)
                
        except Exception as e:
            self.logger.error(f"LED update failed: {e}")

    def run(self):
        """Main sensor loop."""
        self.logger.info("Starting proximity sensor monitoring...")
        self.running = True
        
        failed_readings = 0
        max_retries = self.config['sensor']['max_retries']
        
        try:
            while self.running:
                distance = self.get_distance()
                
                if distance is not None:
                    failed_readings = 0
                    self.logger.debug(f"Distance: {distance}mm")
                    self.update_leds(distance)
                    
                    # Print to console for monitoring
                    print(f"Distance: {distance}mm")
                    
                else:
                    failed_readings += 1
                    if failed_readings >= max_retries:
                        self.logger.error("Too many failed readings, stopping sensor")
                        break
                    
                time.sleep(self.config['sensor']['measurement_interval'])
                
        except Exception as e:
            self.logger.error(f"Sensor loop error: {e}")
        finally:
            self.cleanup()

    def stop(self):
        """Stop the sensor monitoring."""
        self.running = False

    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            self._turn_off_all_leds()
            GPIO.cleanup()
            self.logger.info("GPIO cleanup completed")
        except Exception as e:
            self.logger.error(f"GPIO cleanup failed: {e}")


def main():
    """Main entry point."""
    try:
        sensor = ProximitySensor()
        sensor.run()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Main execution error: {e}")
    finally:
        print("Proximity sensor stopped")


if __name__ == "__main__":
    main()