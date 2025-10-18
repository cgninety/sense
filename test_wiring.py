#!/usr/bin/env python3
"""
HC-SR04 Wiring Verification Script
Tests basic connectivity and helps identify wiring issues.
"""

import time
import json
import sys

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    print("❌ Could not load config.json")
    sys.exit(1)

# Try to import GPIO
try:
    import RPi.GPIO as GPIO
    print("✅ RPi.GPIO imported successfully")
except ImportError:
    print("❌ RPi.GPIO not available")
    print("   Run: sudo apt install python3-rpi.gpio")
    sys.exit(1)

def print_header(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

def test_pins():
    """Test individual pin functionality."""
    
    # Get pins from config
    trig_pin = config['pins']['trig']
    echo_pin = config['pins']['echo']
    led_pins = [config['pins']['led_green'], config['pins']['led_yellow'], config['pins']['led_red']]
    
    print_header("HC-SR04 Wiring Verification")
    print(f"Trigger Pin: GPIO {trig_pin}")
    print(f"Echo Pin: GPIO {echo_pin}")
    print(f"LED Pins: GPIO {led_pins}")
    
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup pins
        GPIO.setup(trig_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)
        for pin in led_pins:
            GPIO.setup(pin, GPIO.OUT)
        
        print_header("Pin Tests")
        
        # Test 1: LED Test
        print("🔍 Test 1: LED Functionality")
        colors = ['Green', 'Yellow', 'Red']
        for i, (pin, color) in enumerate(zip(led_pins, colors)):
            print(f"   Testing {color} LED on GPIO {pin}...")
            GPIO.output(pin, True)
            input(f"   Is the {color} LED ON? Press Enter to continue...")
            GPIO.output(pin, False)
            print(f"   {color} LED should now be OFF")
        
        # Test 2: Trigger Pin Test
        print("\n🔍 Test 2: Trigger Pin")
        print(f"   Testing trigger pin GPIO {trig_pin}")
        print("   Sending trigger pulses...")
        for i in range(3):
            GPIO.output(trig_pin, True)
            time.sleep(0.1)
            GPIO.output(trig_pin, False)
            time.sleep(0.5)
            print(f"   Pulse {i+1} sent")
        
        # Test 3: Echo Pin Test
        print("\n🔍 Test 3: Echo Pin Reading")
        print(f"   Reading echo pin GPIO {echo_pin} for 5 seconds...")
        print("   Cover and uncover the sensor during this test")
        
        start_time = time.time()
        last_state = None
        changes = 0
        
        while time.time() - start_time < 5:
            current_state = GPIO.input(echo_pin)
            if current_state != last_state:
                state_name = "HIGH" if current_state else "LOW"
                print(f"   Echo pin changed to {state_name}")
                changes += 1
                last_state = current_state
            time.sleep(0.1)
        
        print(f"   Echo pin state changes detected: {changes}")
        
        if changes == 0:
            print("   ⚠️  No state changes detected - possible issues:")
            print("      - Echo pin not connected")
            print("      - Wrong GPIO pin number")
            print("      - Sensor not powered")
        else:
            print("   ✅ Echo pin is responding")
        
        # Test 4: Basic Distance Test
        print("\n🔍 Test 4: Distance Measurement")
        print("   Attempting basic distance measurement...")
        
        for attempt in range(3):
            print(f"   Attempt {attempt + 1}:")
            
            # Ensure trigger is low
            GPIO.output(trig_pin, False)
            time.sleep(0.1)
            
            # Check initial echo state
            initial_echo = GPIO.input(echo_pin)
            print(f"      Initial echo state: {'HIGH' if initial_echo else 'LOW'}")
            
            if initial_echo == 1:
                print("      ⚠️  Echo is HIGH before trigger - wiring issue likely")
                continue
            
            # Send trigger pulse
            GPIO.output(trig_pin, True)
            time.sleep(0.00001)
            GPIO.output(trig_pin, False)
            
            # Wait for echo start
            timeout_start = time.time()
            pulse_start = None
            
            while GPIO.input(echo_pin) == 0:
                pulse_start = time.time()
                if time.time() - timeout_start > 1.0:  # 1 second timeout
                    print("      ❌ Timeout waiting for echo start")
                    break
            else:
                # Wait for echo end
                pulse_end = None
                timeout_start = time.time()
                
                while GPIO.input(echo_pin) == 1:
                    pulse_end = time.time()
                    if time.time() - timeout_start > 1.0:
                        print("      ❌ Timeout waiting for echo end")
                        break
                else:
                    if pulse_start and pulse_end:
                        pulse_duration = pulse_end - pulse_start
                        # Accurate speed of sound calculation: 343 m/s at 20°C
                        distance_mm = pulse_duration * 171500  # (343,000 mm/s) / 2
                        distance_inches = distance_mm / 25.4   # International standard conversion
                        print(f"      ✅ Distance: {distance_mm:.1f}mm ({distance_inches:.2f}in)")
                    else:
                        print("      ❌ Failed to measure pulse timing")
            
            time.sleep(1)
        
        print_header("Wiring Checklist")
        print("Verify your connections:")
        print(f"  HC-SR04 VCC  → Pi 5V (Pin 2)")
        print(f"  HC-SR04 GND  → Pi Ground (Pin 6)")
        print(f"  HC-SR04 Trig → Pi GPIO {trig_pin}")
        print(f"  HC-SR04 Echo → Pi GPIO {echo_pin}")
        print(f"  Green LED    → Pi GPIO {led_pins[0]} (via 220Ω resistor)")
        print(f"  Yellow LED   → Pi GPIO {led_pins[1]} (via 220Ω resistor)")
        print(f"  Red LED      → Pi GPIO {led_pins[2]} (via 220Ω resistor)")
        print(f"  All LED (-) → Pi Ground")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        # Cleanup
        try:
            GPIO.cleanup()
            print("\n✅ GPIO cleanup completed")
        except:
            pass

if __name__ == "__main__":
    try:
        test_pins()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        GPIO.cleanup()