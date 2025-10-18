#!/usr/bin/env python3
"""
Distance Conversion Examples and Accuracy Test
Demonstrates the precision of unit conversions used in the proximity sensor.
"""

# Conversion functions (same as in proximity_sensor.py)
def mm_to_inches_precise(mm):
    """Convert millimeters to inches using exact conversion factor."""
    return mm / 25.4  # International definition: 1 inch = 25.4mm exactly

def old_calculation(pulse_duration):
    """Old distance calculation method."""
    return pulse_duration * 17150  # Original method

def new_calculation(pulse_duration):
    """New accurate distance calculation method."""
    # Speed of sound at 20°C (68°F) = 343 m/s = 343,000 mm/s
    # Distance = (speed × time) / 2
    return pulse_duration * 171500  # More accurate

def format_distance_demo(mm):
    """Show different formatting options."""
    inches = mm_to_inches_precise(mm)
    cm = mm / 10
    
    print(f"Distance: {mm}mm")
    print(f"  mm only:    {mm:.2f}mm")
    print(f"  inches only: {inches:.2f}in")
    print(f"  cm only:    {cm:.2f}cm")
    print(f"  both (mm):  {mm:.2f}mm ({inches:.2f}in)")
    print(f"  both (in):  {inches:.2f}in ({mm:.2f}mm)")
    print(f"  all units:  {mm:.2f}mm | {cm:.2f}cm | {inches:.2f}in")

def accuracy_comparison():
    """Compare old vs new calculation accuracy."""
    print("=" * 60)
    print(" Distance Calculation Accuracy Comparison")
    print("=" * 60)
    
    # Test pulse durations (typical HC-SR04 ranges)
    test_pulses = [
        0.000058,   # ~10mm
        0.000291,   # ~50mm  
        0.000583,   # ~100mm
        0.001166,   # ~200mm
        0.002915,   # ~500mm
        0.005831    # ~1000mm
    ]
    
    print(f"{'Pulse (s)':<12} {'Old Method':<12} {'New Method':<12} {'Difference':<12}")
    print("-" * 48)
    
    for pulse in test_pulses:
        old_dist = old_calculation(pulse)
        new_dist = new_calculation(pulse)
        diff = new_dist - old_dist
        
        print(f"{pulse:.6f}   {old_dist:8.1f}mm   {new_dist:8.1f}mm   {diff:+8.1f}mm")

def common_distances():
    """Show common distances in both units."""
    print("\n" + "=" * 60)
    print(" Common Distance Examples")
    print("=" * 60)
    
    distances = [
        (10, "Danger threshold"),
        (25.4, "Exactly 1 inch"),  
        (50, "Caution threshold"),
        (50.8, "Exactly 2 inches"),
        (100, "Safe threshold"),
        (152.4, "Exactly 6 inches"),
        (304.8, "Exactly 1 foot"),
        (500, "Typical max indoor range"),
        (1000, "1 meter"),
        (2000, "Typical outdoor range")
    ]
    
    print(f"{'Millimeters':<12} {'Inches':<10} {'Description':<25}")
    print("-" * 50)
    
    for mm, desc in distances:
        inches = mm_to_inches_precise(mm)
        print(f"{mm:8.1f}mm   {inches:6.2f}in   {desc}")

def precision_test():
    """Test precision of conversions."""
    print("\n" + "=" * 60)
    print(" Conversion Precision Test")
    print("=" * 60)
    
    # Test round-trip conversions
    test_values = [1.0, 10.0, 25.4, 50.0, 100.0, 254.0, 1000.0]
    
    print("Round-trip conversion test (mm → inches → mm):")
    print(f"{'Original (mm)':<15} {'To Inches':<12} {'Back to mm':<12} {'Error':<10}")
    print("-" * 52)
    
    for mm in test_values:
        inches = mm_to_inches_precise(mm)
        back_to_mm = inches * 25.4
        error = abs(back_to_mm - mm)
        
        print(f"{mm:10.1f}      {inches:8.4f}     {back_to_mm:8.1f}      {error:.2e}")

if __name__ == "__main__":
    print("🔧 Proximity Sensor - Distance Conversion & Accuracy Demo")
    
    accuracy_comparison()
    common_distances()  
    precision_test()
    
    print("\n" + "=" * 60)
    print(" Display Format Examples")
    print("=" * 60)
    
    # Show formatting examples
    example_distances = [10.0, 50.8, 152.4, 304.8]
    
    for dist in example_distances:
        print(f"\nFor {dist}mm:")
        format_distance_demo(dist)
    
    print(f"\n✅ All conversions use the international standard: 1 inch = 25.4mm exactly")
    print(f"✅ Speed of sound calculation: 343 m/s at 20°C (68°F)")
    print(f"✅ Distance formula: (speed × pulse_time) / 2")