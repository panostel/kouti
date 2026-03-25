#!/usr/bin/env python3
"""
LED Breathing Pattern Script for Raspberry Pi
Emulates a breathing pattern using PWM on GPIO pin 5
"""

import RPi.GPIO as GPIO
import time
import math
import signal
import sys

# Configuration
LED_PIN = 5
PWM_FREQUENCY = 1000  # 1kHz PWM frequency
BREATH_DURATION = 4.0  # Total breathing cycle duration in seconds
FADE_STEPS = 100  # Number of steps in fade transition

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    cleanup()
    sys.exit(0)

def setup_gpio():
    """Initialize GPIO settings"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    pwm = GPIO.PWM(LED_PIN, PWM_FREQUENCY)
    pwm.start(0)  # Start with 0% duty cycle (LED off)
    return pwm

def cleanup():
    """Clean up GPIO settings"""
    GPIO.cleanup()

def breathing_pattern(pwm):
    """
    Create a breathing pattern using sine wave for smooth transitions
    """
    step_delay = BREATH_DURATION / FADE_STEPS
    
    while True:
        # One complete breathing cycle
        for i in range(FADE_STEPS):
            # Use sine wave for smooth breathing effect
            # sin goes from 0 to 1 and back to 0 over pi radians
            angle = (i / FADE_STEPS) * math.pi
            brightness = math.sin(angle) * 100  # Scale to 0-100%
            
            pwm.ChangeDutyCycle(brightness)
            time.sleep(step_delay)

def main():
    """Main function"""
    print("LED Breathing Pattern")
    print(f"LED connected to GPIO pin {LED_PIN}")
    print("Press Ctrl+C to exit")
    
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize GPIO and PWM
        pwm = setup_gpio()
        
        # Start breathing pattern
        breathing_pattern(pwm)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()