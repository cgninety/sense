#!/usr/bin/env python3
"""
Blinking Rate Demo Script
Demonstrates the dynamic blinking rates at different distances.
"""

import json
import math

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        # Default values if config not found
        return {
            "thresholds": {"safe_distance": 100, "caution_distance": 50, "danger_distance": 10},
            "blinking": {"base_bpm": 60, "min_bpm": 30, "max_bpm": 120}
        }

def calculate_blink_rate(distance, config):
    """Calculate blink rate for a given distance."""
    thresholds = config['thresholds']
    blinking = config['blinking']
    
    safe_distance = thresholds['safe_distance']
    caution_distance = thresholds['caution_distance'] 
    danger_distance = thresholds['danger_distance']
    
    base_bpm = blinking['base_bpm']
    min_bpm = blinking['min_bpm']
    max_bpm = blinking['max_bpm']
    
    if distance >= safe_distance:
        return 0, "Green SOLID", "Safe zone"
        
    elif distance >= caution_distance:
        # Caution zone: yellow blinking
        zone_range = safe_distance - caution_distance
        position_in_zone = distance - caution_distance
        normalized_pos = position_in_zone / zone_range
        bpm = min_bpm + (base_bpm - min_bpm) * (1 - normalized_pos)
        return max(min_bpm, min(base_bpm, bpm)), "Yellow BLINKING", "Caution zone"
        
    elif distance >= danger_distance:
        # Danger zone: red blinking
        zone_range = caution_distance - danger_distance
        position_in_zone = distance - danger_distance
        normalized_pos = position_in_zone / zone_range if zone_range > 0 else 0
        bpm = base_bpm + (max_bpm - base_bpm) * (1 - normalized_pos)
        return max(base_bpm, min(max_bpm, bpm)), "Red BLINKING", "Danger zone"
        
    else:
        # Critical zone
        return max_bpm, "Red FAST BLINKING", "Critical zone"

def bpm_to_description(bpm):
    """Convert BPM to human readable description."""
    if bpm == 0:
        return "No blinking"
    elif bpm <= 60:
        return f"{bpm:.0f} BPM (Slow)"
    elif bpm <= 120:
        return f"{bpm:.0f} BPM (Medium)"
    elif bpm <= 180:
        return f"{bpm:.0f} BPM (Fast)"
    else:
        return f"{bpm:.0f} BPM (Very Fast)"

def main():
    """Demo the blinking rates."""
    config = load_config()
    
    print("🚨 Dynamic LED Blinking Rate Demo")
    print("=" * 60)
    
    # Show configuration
    thresholds = config['thresholds']
    blinking = config['blinking']
    
    print(f"Configuration:")
    print(f"  Safe distance: ≥{thresholds['safe_distance']}mm")
    print(f"  Caution distance: {thresholds['caution_distance']}-{thresholds['safe_distance']-1}mm")
    print(f"  Danger distance: {thresholds['danger_distance']}-{thresholds['caution_distance']-1}mm")
    print(f"  Critical distance: <{thresholds['danger_distance']}mm")
    print()
    print(f"  Blink rates: {blinking['min_bpm']}-{blinking['max_bpm']} BPM (base: {blinking['base_bpm']})")
    print()
    
    # Test distances
    test_distances = [
        150, 120, 100,  # Safe zone and threshold
        80, 60, 50,     # Caution zone  
        40, 30, 20, 10, # Danger zone and threshold
        8, 5, 2, 1      # Critical zone
    ]
    
    print(f"{'Distance':<12} {'LED Status':<20} {'Blink Rate':<20} {'Zone':<15}")
    print("-" * 70)
    
    for distance in test_distances:
        bpm, led_status, zone = calculate_blink_rate(distance, config)
        bpm_desc = bpm_to_description(bpm)
        
        # Add units
        distance_str = f"{distance}mm"
        inches = distance / 25.4
        if inches >= 1:
            distance_str += f" ({inches:.1f}in)"
        else:
            distance_str += f" ({inches:.2f}in)"
        
        print(f"{distance_str:<12} {led_status:<20} {bpm_desc:<20} {zone:<15}")
    
    print()
    print("💡 Blinking Pattern Examples:")
    print(f"  30 BPM = 1 blink every 2 seconds (slowest)")
    print(f"  60 BPM = 1 blink per second (base rate)")
    print(f"  120 BPM = 2 blinks per second (fastest)")
    
    print()
    print("🎯 The closer you get, the faster it blinks!")
    print("   This creates an intuitive 'parking sensor' experience.")

if __name__ == "__main__":
    main()