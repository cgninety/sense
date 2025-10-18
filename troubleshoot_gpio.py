#!/usr/bin/env python3
"""
GPIO Troubleshooting Script for Proximity Sensor
Helps diagnose and fix common GPIO and RPi.GPIO installation issues.
"""

import sys
import subprocess
import os

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[94m",   # Blue
        "SUCCESS": "\033[92m", # Green  
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"     # Reset
    }
    print(f"{colors.get(status, '')}{message}{colors['RESET']}")

def run_command(command):
    """Run a shell command and return success status and output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_raspberry_pi():
    """Check if we're running on a Raspberry Pi."""
    print_header("Raspberry Pi Detection")
    
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        
        if 'Raspberry Pi' in cpuinfo:
            print_status("✅ Running on Raspberry Pi", "SUCCESS")
            
            # Extract Pi model
            for line in cpuinfo.split('\n'):
                if 'Model' in line:
                    print_status(f"   {line.strip()}", "INFO")
                    break
            return True
        else:
            print_status("❌ Not running on Raspberry Pi", "WARNING")
            print_status("   RPi.GPIO will not work on this system", "WARNING")
            return False
            
    except FileNotFoundError:
        print_status("❌ Cannot determine system type", "ERROR")
        return False

def check_python_version():
    """Check Python version."""
    print_header("Python Version Check")
    
    version = sys.version
    print_status(f"Python version: {version}", "INFO")
    
    if sys.version_info >= (3, 6):
        print_status("✅ Python version is compatible", "SUCCESS")
        return True
    else:
        print_status("❌ Python version too old (need 3.6+)", "ERROR")
        return False

def check_rpi_gpio():
    """Check RPi.GPIO installation and functionality."""
    print_header("RPi.GPIO Check")
    
    # Try importing RPi.GPIO
    try:
        import RPi.GPIO as GPIO
        print_status("✅ RPi.GPIO imported successfully", "SUCCESS")
        
        # Check GPIO version
        if hasattr(GPIO, 'VERSION'):
            print_status(f"   RPi.GPIO version: {GPIO.VERSION}", "INFO")
        
        return True
        
    except ImportError as e:
        print_status(f"❌ Cannot import RPi.GPIO: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ RPi.GPIO error: {e}", "ERROR")
        return False

def check_gpio_permissions():
    """Check GPIO permissions."""
    print_header("GPIO Permissions Check")
    
    # Check if user is in gpio group
    success, output, error = run_command("groups")
    if success and 'gpio' in output:
        print_status("✅ User is in gpio group", "SUCCESS")
        return True
    else:
        print_status("❌ User not in gpio group", "ERROR")
        print_status("   Run: sudo usermod -a -G gpio $USER", "INFO")
        print_status("   Then log out and back in", "INFO")
        return False

def check_gpio_interface():
    """Check if GPIO interface is enabled."""
    print_header("GPIO Interface Check")
    
    # Check if /dev/gpiomem exists (indicates GPIO interface is enabled)
    if os.path.exists('/dev/gpiomem'):
        print_status("✅ GPIO interface is enabled", "SUCCESS")
        return True
    else:
        print_status("❌ GPIO interface not enabled", "ERROR")
        print_status("   Run: sudo raspi-config", "INFO")
        print_status("   Go to: Advanced Options > SPI > Enable", "INFO")
        return False

def suggest_fixes():
    """Suggest fixes for common issues."""
    print_header("Installation Fixes")
    
    print_status("Try these installation methods in order:", "INFO")
    print()
    
    print_status("1. Install via apt (recommended):", "INFO")
    print("   sudo apt update")
    print("   sudo apt install python3-rpi.gpio")
    print()
    
    print_status("2. Install via pip3:", "INFO") 
    print("   pip3 install --user RPi.GPIO")
    print()
    
    print_status("3. Install system-wide:", "INFO")
    print("   sudo pip3 install RPi.GPIO")
    print()
    
    print_status("4. Enable GPIO and add user to group:", "INFO")
    print("   sudo raspi-config  # Enable SPI interface")
    print("   sudo usermod -a -G gpio $USER")
    print("   # Log out and back in")
    print()

def main():
    """Main troubleshooting routine."""
    print_header("Proximity Sensor GPIO Troubleshooter")
    print("This script will help diagnose GPIO and RPi.GPIO issues")
    
    # Run all checks
    checks = [
        ("Raspberry Pi Detection", check_raspberry_pi),
        ("Python Version", check_python_version), 
        ("RPi.GPIO Import", check_rpi_gpio),
        ("GPIO Permissions", check_gpio_permissions),
        ("GPIO Interface", check_gpio_interface)
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    # Summary
    print_header("Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    print_status(f"Checks passed: {passed}/{total}", "INFO")
    
    if passed == total:
        print_status("🎉 All checks passed! RPi.GPIO should work.", "SUCCESS")
        print_status("   Try running: python3 proximity_sensor.py", "INFO")
    else:
        print_status("❌ Some issues found. See fixes below.", "ERROR")
        suggest_fixes()

if __name__ == "__main__":
    main()