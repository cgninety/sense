#!/usr/bin/env python3
"""
Proximity Sensor with LED Indicators
Uses HC-SR04 ultrasonic sensor to detect object distance and provide visual feedback.
"""

# Try to import RPi.GPIO with fallback for testing/development
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError as e:
    print("⚠️  RPi.GPIO not available. This might be because:")
    print("   1. You're not running on a Raspberry Pi")
    print("   2. RPi.GPIO is not installed")
    print("   3. You need to run: sudo apt install python3-rpi.gpio")
    print("   4. Or try: pip3 install RPi.GPIO")
    print(f"   Error: {e}")
    
    # Create a mock GPIO for testing on non-Pi systems
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT" 
        IN = "IN"
        HIGH = 1
        LOW = 0
        
        @staticmethod
        def setmode(mode): pass
        @staticmethod
        def setwarnings(warnings): pass
        @staticmethod
        def setup(pin, mode): pass
        @staticmethod
        def output(pin, state): pass
        @staticmethod
        def input(pin): return 0
        @staticmethod
        def cleanup(): pass
    
    GPIO = MockGPIO()
    GPIO_AVAILABLE = False

import time
import logging
import signal
import sys
import json
from pathlib import Path
from typing import Optional


class UnitConverter:
    """Handle unit conversions for distance measurements."""
    
    @staticmethod
    def mm_to_inches(mm: float) -> float:
        """Convert millimeters to inches with high precision."""
        # 1 inch = 25.4 mm exactly (international definition)
        return mm / 25.4
    
    @staticmethod
    def mm_to_cm(mm: float) -> float:
        """Convert millimeters to centimeters."""
        return mm / 10.0
    
    @staticmethod
    def mm_to_feet(mm: float) -> float:
        """Convert millimeters to feet."""
        return mm / 304.8  # 25.4 * 12
    
    @staticmethod
    def format_distance(mm: float, units: str = "both", primary: str = "mm", decimal_places: int = 2) -> str:
        """Format distance with specified units."""
        if units == "mm":
            return f"{mm:.{decimal_places}f}mm"
        elif units == "inches":
            inches = UnitConverter.mm_to_inches(mm)
            return f"{inches:.{decimal_places}f}in"
        elif units == "cm":
            cm = UnitConverter.mm_to_cm(mm)
            return f"{cm:.{decimal_places}f}cm"
        elif units == "both":
            inches = UnitConverter.mm_to_inches(mm)
            if primary == "mm":
                return f"{mm:.{decimal_places}f}mm ({inches:.{decimal_places}f}in)"
            else:
                return f"{inches:.{decimal_places}f}in ({mm:.{decimal_places}f}mm)"
        elif units == "all":
            inches = UnitConverter.mm_to_inches(mm)
            cm = UnitConverter.mm_to_cm(mm)
            return f"{mm:.{decimal_places}f}mm | {cm:.{decimal_places}f}cm | {inches:.{decimal_places}f}in"
        else:
            return f"{mm:.{decimal_places}f}mm"


class ProximitySensor:
    """Ultrasonic proximity sensor with LED feedback system."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the proximity sensor with configuration."""
        self.config = self._load_config(config_file)
        self.running = False
        
        # Check if GPIO is available
        if not GPIO_AVAILABLE:
            print("⚠️  Running in mock mode - GPIO operations will be simulated")
            print("   Install RPi.GPIO properly to use real hardware")
        
        # Setup logging
        self._setup_logging()
        
        # GPIO pins from config
        self.trig_pin = self.config['pins']['trig']
        self.echo_pin = self.config['pins']['echo']
        self.led_green = self.config['pins']['led_green']
        self.led_yellow = self.config['pins']['led_yellow']
        self.led_red = self.config['pins']['led_red']
        
        # Distance thresholds (always in mm internally)
        self.safe_distance = self.config['thresholds']['safe_distance']
        self.caution_distance = self.config['thresholds']['caution_distance']
        self.danger_distance = self.config['thresholds']['danger_distance']
        
        # Display settings
        self.display_units = self.config.get('display', {}).get('units', 'mm')
        self.primary_unit = self.config.get('display', {}).get('primary_unit', 'mm')
        self.decimal_places = self.config.get('display', {}).get('decimal_places', 2)
        
        # Blinking settings
        self.blinking_enabled = self.config.get('blinking', {}).get('enabled', True)
        self.base_bpm = self.config.get('blinking', {}).get('base_bpm', 120)
        self.min_bpm = self.config.get('blinking', {}).get('min_bpm', 30)
        self.max_bpm = self.config.get('blinking', {}).get('max_bpm', 300)
        
        # LED state tracking for blinking
        self.led_state = {'green': False, 'yellow': False, 'red': False}
        self.last_blink_time = time.time()
        self.current_led = None
        self.current_blink_interval = 0
        
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
                "safe_distance": 100,    # 100mm = ~3.94 inches
                "caution_distance": 50,  # 50mm = ~1.97 inches  
                "danger_distance": 10    # 10mm = ~0.39 inches
            },
            "sensor": {
                "timeout": 0.5,
                "measurement_interval": 0.1,  # Shorter for smooth blinking
                "max_retries": 5
            },
            "display": {
                "units": "both",        # Options: "mm", "inches", "cm", "both", "all"
                "primary_unit": "mm",   # Primary unit when showing "both"
                "decimal_places": 2     # Number of decimal places to display
            },
            "blinking": {
                "enabled": True,        # Enable dynamic blinking system
                "base_bpm": 120,        # Base blink rate (beats per minute)
                "min_bpm": 30,          # Minimum blink rate (slow end)
                "max_bpm": 300          # Maximum blink rate (fast end)
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
        self.led_state = {'green': False, 'yellow': False, 'red': False}

    def _calculate_blink_rate(self, distance: float) -> tuple:
        """
        Calculate blink rate based on distance within zones.
        Returns (bpm, led_type) where bpm is beats per minute.
        """
        if not self.blinking_enabled:
            return 0, None
            
        if distance >= self.safe_distance:
            # Safe zone - no blinking
            return 0, None
            
        elif distance >= self.caution_distance:
            # Caution zone: blink yellow LED
            # Faster blinking as we approach danger zone
            zone_range = self.safe_distance - self.caution_distance
            position_in_zone = distance - self.caution_distance
            # Normalize position (0 = at danger threshold, 1 = at safe threshold)
            normalized_pos = position_in_zone / zone_range
            
            # Blink rate: slow at safe end, faster at danger end
            bpm = self.min_bpm + (self.base_bpm - self.min_bpm) * (1 - normalized_pos)
            return max(self.min_bpm, min(self.base_bpm, bpm)), 'yellow'
            
        elif distance >= self.danger_distance:
            # Danger zone: blink red LED
            # Faster blinking as we approach closer distances
            zone_range = self.caution_distance - self.danger_distance
            position_in_zone = distance - self.danger_distance
            # Normalize position (0 = very close, 1 = at caution threshold)
            normalized_pos = position_in_zone / zone_range if zone_range > 0 else 0
            
            # Blink rate: base speed at caution end, faster as we get closer
            bpm = self.base_bpm + (self.max_bpm - self.base_bpm) * (1 - normalized_pos)
            return max(self.base_bpm, min(self.max_bpm, bpm)), 'red'
            
        else:
            # Critical zone: very fast red blashing
            # Even faster blinking for very close distances
            return self.max_bpm, 'red'

    def _update_blinking_led(self, distance: float):
        """Update LED blinking based on current distance.""" 
        current_time = time.time()
        bpm, led_type = self._calculate_blink_rate(distance)
        
        self.logger.debug(f"Blinking LED: distance={distance:.1f}mm, bpm={bpm:.0f}, led_type={led_type}")
        
        # Safe zone - solid green, no blinking
        if bpm == 0 or led_type is None:
            self._turn_off_all_leds()
            GPIO.output(self.led_green, True)
            self.led_state['green'] = True
            self.logger.debug("Safe zone: Green LED solid ON")
            return
        
        # Calculate blink period (full on/off cycle) 
        blink_period = 60.0 / bpm  # seconds per full blink cycle
        
        # Determine if LED should be on or off based on time
        time_in_cycle = (current_time * bpm / 60.0) % 1.0  # 0-1 within cycle
        led_should_be_on = time_in_cycle < 0.5  # On for first half, off for second half
        
        self.logger.debug(f"Blink timing: period={blink_period:.3f}s, time_in_cycle={time_in_cycle:.3f}, should_be_on={led_should_be_on}")
        
        # Update LEDs
        self._turn_off_all_leds()
        
        if led_should_be_on:
            if led_type == 'yellow':
                GPIO.output(self.led_yellow, True)
                self.led_state['yellow'] = True
                self.logger.debug("Yellow LED ON")
            elif led_type == 'red':
                GPIO.output(self.led_red, True) 
                self.led_state['red'] = True
                self.logger.debug("Red LED ON")
        else:
            self.logger.debug(f"{led_type.capitalize()} LED OFF (blinking)")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def test_gpio_pins(self):
        """Test GPIO pin functionality for diagnostics."""
        self.logger.info("Testing GPIO pin functionality...")
        
        try:
            # Test trigger pin
            self.logger.info(f"Testing trigger pin GPIO {self.trig_pin}")
            GPIO.output(self.trig_pin, True)
            time.sleep(0.1)
            GPIO.output(self.trig_pin, False)
            self.logger.info("✅ Trigger pin test passed")
            
            # Test echo pin - check if it's stuck
            echo_state = GPIO.input(self.echo_pin)
            self.logger.info(f"Echo pin GPIO {self.echo_pin} current state: {echo_state}")
            
            if echo_state == 1:
                self.logger.warning("⚠️ Echo pin is stuck HIGH - check wiring")
            else:
                self.logger.info("✅ Echo pin state looks normal")
            
            # Test LED pins
            for led_name, pin in [("Green", self.led_green), ("Yellow", self.led_yellow), ("Red", self.led_red)]:
                self.logger.info(f"Testing {led_name} LED on GPIO {pin}")
                GPIO.output(pin, True)
                time.sleep(0.2)
                GPIO.output(pin, False)
                time.sleep(0.1)
            
            self.logger.info("✅ GPIO pin tests completed")
            
        except Exception as e:
            self.logger.error(f"GPIO pin test failed: {e}")

    def _test_led_functionality(self):
        """Test LED functionality with different patterns."""
        self.logger.info("Testing LED functionality...")
        
        try:
            print("Testing Green LED (Safe zone)...")
            self._turn_off_all_leds()
            GPIO.output(self.led_green, True)
            time.sleep(1)
            self._turn_off_all_leds()
            
            print("Testing Yellow LED blinking (Caution zone)...")
            for i in range(4):
                GPIO.output(self.led_yellow, True)
                time.sleep(0.3)
                GPIO.output(self.led_yellow, False)
                time.sleep(0.3)
                print(f"  Blink {i+1}/4")
                
            print("Testing Red LED fast blinking (Danger zone)...")
            for i in range(8):
                GPIO.output(self.led_red, True)
                time.sleep(0.15)
                GPIO.output(self.led_red, False)
                time.sleep(0.15)
                print(f"  Fast blink {i+1}/8")
                
            print("✅ LED functionality test completed")
            
        except Exception as e:
            self.logger.error(f"LED test failed: {e}")

    def get_distance(self) -> Optional[float]:
        """
        Measure distance using ultrasonic sensor.
        Returns distance in millimeters or None if measurement fails.
        """
        # If GPIO is not available, return simulated distance for testing
        if not GPIO_AVAILABLE:
            import random
            # Simulate varying distance readings for demo (realistic HC-SR04 range)
            base_distance = 150.0  # 150mm = ~5.9 inches
            variation = random.uniform(-50, 50)
            simulated_distance = base_distance + variation
            return round(max(20.0, min(4000.0, simulated_distance)), 2)
        
        try:
            # Ensure trigger is low and wait for stabilization
            GPIO.output(self.trig_pin, False)
            time.sleep(0.1)  # Increased wait time
            
            # Check initial echo state
            initial_echo = GPIO.input(self.echo_pin)
            if initial_echo == 1:
                self.logger.warning("Echo pin is HIGH before trigger - possible wiring issue")
                # Try to wait for it to go low
                wait_start = time.time()
                while GPIO.input(self.echo_pin) == 1 and (time.time() - wait_start) < 0.5:
                    time.sleep(0.01)
                if GPIO.input(self.echo_pin) == 1:
                    self.logger.error("Echo pin stuck HIGH - aborting measurement")
                    return None
            
            # Send trigger pulse
            GPIO.output(self.trig_pin, True)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(self.trig_pin, False)
            
            # Wait for echo start with timeout and better logging
            pulse_start = None
            timeout_start = time.time()
            timeout_duration = self.config['sensor']['timeout']
            
            while GPIO.input(self.echo_pin) == 0:
                pulse_start = time.time()
                if time.time() - timeout_start > timeout_duration:
                    self.logger.warning(f"Timeout waiting for echo start after {timeout_duration}s")
                    self.logger.info("Possible causes:")
                    self.logger.info("  - Echo pin not connected or loose connection")
                    self.logger.info("  - Wrong GPIO pin number in config")
                    self.logger.info("  - Sensor not powered (needs 5V)")
                    self.logger.info("  - Faulty HC-SR04 sensor")
                    return None
            
            # Wait for echo end with timeout
            pulse_end = None
            timeout_start = time.time()
            while GPIO.input(self.echo_pin) == 1:
                pulse_end = time.time()
                if time.time() - timeout_start > timeout_duration:
                    self.logger.warning(f"Timeout waiting for echo end after {timeout_duration}s")
                    return None
            
            if pulse_start is None or pulse_end is None:
                self.logger.warning("Failed to capture pulse timing")
                return None
            
            # Calculate distance with accurate speed of sound
            pulse_duration = pulse_end - pulse_start
            
            # Speed of sound at 20°C (68°F) is 343 m/s = 343,000 mm/s
            # Distance = (speed × time) / 2 (divide by 2 because sound travels to object and back)
            # Distance in mm = (343,000 × pulse_duration) / 2 = 171,500 × pulse_duration
            distance = pulse_duration * 171500  # Accurate conversion to mm
            
            # Log pulse details for debugging
            self.logger.debug(f"Pulse duration: {pulse_duration:.6f}s, Distance: {distance:.2f}mm")
            
            # Validate reasonable distance (HC-SR04 range: 2cm to 4m)
            if distance < 20:
                self.logger.debug(f"Distance too close: {distance}mm (sensor minimum ~20mm)")
                return None
            elif distance > 4000:
                self.logger.debug(f"Distance too far: {distance}mm (sensor maximum ~4000mm)")
                return None
            
            return round(distance, 2)
            
        except Exception as e:
            self.logger.error(f"Distance measurement failed: {e}")
            return None

    def update_leds(self, distance: float):
        """Update LED status based on distance with dynamic blinking."""
        try:
            if self.blinking_enabled:
                # Use new blinking system
                self._update_blinking_led(distance)
            else:
                # Fall back to original solid LED behavior
                self._update_solid_leds(distance)
                
        except Exception as e:
            self.logger.error(f"LED update failed: {e}")
            # Emergency fallback - use simple solid LEDs
            self.logger.warning("Falling back to simple LED mode due to error")
            self._update_solid_leds(distance)

    def _update_solid_leds(self, distance: float):
        """Original solid LED behavior (fallback when blinking disabled)."""
        # Turn off all LEDs first
        self._turn_off_all_leds()
        
        if distance >= self.safe_distance:
            # Safe distance - green LED
            GPIO.output(self.led_green, True)
            self.led_state['green'] = True
            
        elif distance >= self.caution_distance:
            # Caution distance - yellow LED
            GPIO.output(self.led_yellow, True)
            self.led_state['yellow'] = True
            
        elif distance >= self.danger_distance:
            # Danger distance - red LED solid
            GPIO.output(self.led_red, True)
            self.led_state['red'] = True
            
        else:
            # Very close - flash red LED with variable speed
            flash_delay = max(0.05, distance / 200.0)
            GPIO.output(self.led_red, True)
            self.led_state['red'] = True
            time.sleep(flash_delay)
            GPIO.output(self.led_red, False)
            self.led_state['red'] = False
            time.sleep(flash_delay)

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
                    
                    # Format distance with configured units
                    distance_str = UnitConverter.format_distance(
                        distance, 
                        self.display_units, 
                        self.primary_unit, 
                        self.decimal_places
                    )
                    
                    # Get blinking info for display
                    bpm, led_type = self._calculate_blink_rate(distance)
                    
                    self.logger.debug(f"Distance: {distance_str}")
                    self.update_leds(distance)
                    
                    # Print to console with blinking info
                    if bpm > 0 and led_type:
                        zone = "CAUTION" if led_type == 'yellow' else "DANGER" if distance >= self.danger_distance else "CRITICAL"
                        print(f"Distance: {distance_str} | {zone} - {led_type.upper()} blinking at {bpm:.0f} BPM")
                    else:
                        zone = "SAFE" if distance >= self.safe_distance else "UNKNOWN"
                        print(f"Distance: {distance_str} | {zone} - GREEN solid")
                    
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Proximity Sensor with LED Indicators')
    parser.add_argument('--test-gpio', action='store_true', help='Test GPIO pins and exit')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-blinking', action='store_true', help='Disable LED blinking (use solid LEDs only)')
    parser.add_argument('--test-leds', action='store_true', help='Test LED functionality and exit')
    
    args = parser.parse_args()
    
    try:
        # Temporarily set debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        sensor = ProximitySensor(args.config)
        
        # Override blinking if disabled via command line
        if args.no_blinking:
            sensor.blinking_enabled = False
            print("🔧 LED blinking disabled - using solid LEDs only")
        
        if args.test_leds:
            print("🔧 Running LED functionality test...")
            sensor._test_led_functionality()
            sensor.cleanup()
            return
        
        if args.test_gpio:
            print("🔧 Running GPIO diagnostics...")
            sensor.test_gpio_pins()
            
            # Test a few distance readings
            print("📏 Testing distance measurements (5 attempts)...")
            for i in range(5):
                distance = sensor.get_distance()
                if distance is not None:
                    print(f"   Attempt {i+1}: {distance}mm ✅")
                else:
                    print(f"   Attempt {i+1}: Failed ❌")
                time.sleep(1)
            
            sensor.cleanup()
            return
        
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