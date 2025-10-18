#!/usr/bin/env python3
"""
Simple LED Test Script
Tests basic LED functionality without the complex blinking system.
"""

import time
import json
import sys

# Try to import GPIO with fallback
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    print("✅ RPi.GPIO imported successfully")
except ImportError:
    print("❌ RPi.GPIO not available - using mock mode")
    
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT" 
        IN = "IN"
        @staticmethod
        def setmode(mode): pass
        @staticmethod
        def setwarnings(warnings): pass
        @staticmethod
        def setup(pin, mode): print(f"   Setup GPIO {pin} as {mode}")
        @staticmethod
        def output(pin, state): 
            state_str = "ON" if state else "OFF"
            print(f"   GPIO {pin} → {state_str}")
        @staticmethod
        def cleanup(): print("   GPIO cleanup")
    
    GPIO = MockGPIO()
    GPIO_AVAILABLE = False

def load_config():
    """Load GPIO pins from config."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config['pins']
    except:
        return {
            "trig": 23, "echo": 24,
            "led_green": 17, "led_yellow": 27, "led_red": 22
        }

def test_leds_simple():
    """Test LEDs with simple on/off patterns."""
    pins = load_config()
    
    print("🔧 Simple LED Test")
    print("=" * 40)
    
    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup LED pins
    GPIO.setup(pins['led_green'], GPIO.OUT)
    GPIO.setup(pins['led_yellow'], GPIO.OUT)
    GPIO.setup(pins['led_red'], GPIO.OUT)
    
    # Turn off all LEDs
    def all_off():
        GPIO.output(pins['led_green'], False)
        GPIO.output(pins['led_yellow'], False)
        GPIO.output(pins['led_red'], False)
    
    try:
        print("Testing each LED individually...")
        
        # Test Green LED
        print("\n🟢 Testing Green LED (Safe zone simulation)")
        all_off()
        GPIO.output(pins['led_green'], True)
        time.sleep(2)
        all_off()
        
        # Test Yellow LED blinking (Caution zone simulation)
        print("\n🟡 Testing Yellow LED blinking (Caution zone simulation)")
        for i in range(6):  # 3 second test
            GPIO.output(pins['led_yellow'], True)
            time.sleep(0.25)  # On for 0.25s
            GPIO.output(pins['led_yellow'], False)
            time.sleep(0.25)  # Off for 0.25s
            print(f"   Blink {i+1}/6")
        
        # Test Red LED fast blinking (Danger zone simulation)
        print("\n🔴 Testing Red LED fast blinking (Danger zone simulation)")
        for i in range(15):  # 3 second test
            GPIO.output(pins['led_red'], True)
            time.sleep(0.1)  # On for 0.1s
            GPIO.output(pins['led_red'], False)
            time.sleep(0.1)  # Off for 0.1s
            print(f"   Fast blink {i+1}/15")
        
        print("\n✅ LED test completed successfully!")
        
        # Test distance simulation
        print("\n📏 Distance simulation test...")
        distances = [150, 75, 25, 5]  # Safe, Caution, Danger, Critical
        
        for dist in distances:
            print(f"\nSimulating {dist}mm distance:")
            
            if dist >= 100:
                print("   Zone: SAFE - Green solid")
                all_off()
                GPIO.output(pins['led_green'], True)
                time.sleep(1)
                
            elif dist >= 50:
                print("   Zone: CAUTION - Yellow blinking")
                all_off()
                for _ in range(3):  # 3 blinks
                    GPIO.output(pins['led_yellow'], True)
                    time.sleep(0.3)
                    GPIO.output(pins['led_yellow'], False)
                    time.sleep(0.3)
                    
            else:
                print("   Zone: DANGER - Red fast blinking")
                all_off()
                for _ in range(6):  # 6 fast blinks
                    GPIO.output(pins['led_red'], True)
                    time.sleep(0.15)
                    GPIO.output(pins['led_red'], False)
                    time.sleep(0.15)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
    finally:
        all_off()
        GPIO.cleanup()
        print("\n🔧 GPIO cleanup completed")

if __name__ == "__main__":
    test_leds_simple()