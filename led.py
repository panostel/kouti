#!/usr/bin/env python3
"""
LED Breathing Pattern Script for Raspberry Pi
Emulates a breathing pattern using PWM on GPIO pin 5.
Waits for /tmp/soundbox_ready before starting — LED breathing signals device is ready.
"""

import RPi.GPIO as GPIO
import time
import math
import signal
import sys
import os

# Configuration
LED_PIN = 5
PWM_FREQUENCY = 1000  # 1kHz PWM frequency
BREATH_DURATION = 4.0  # Total breathing cycle duration in seconds
FADE_STEPS = 100       # Number of steps in fade transition
READY_FLAG_FILE = '/tmp/soundbox_ready'


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


def wait_for_ready():
    """Wait until soundbox.py signals it is ready"""
    print("Waiting for soundbox to be ready...")
    while not os.path.exists(READY_FLAG_FILE):
        time.sleep(0.5)
    print("Soundbox ready — starting LED breathing pattern")


def breathing_pattern(pwm):
    """
    Create a breathing pattern using sine wave for smooth transitions
    """
    step_delay = BREATH_DURATION / FADE_STEPS

    while True:
        for i in range(FADE_STEPS):
            angle = (i / FADE_STEPS) * math.pi
            brightness = math.sin(angle) * 100  # Scale to 0-100%
            pwm.ChangeDutyCycle(brightness)
            time.sleep(step_delay)


def main():
    """Main function"""
    print("LED Breathing Pattern")
    print(f"LED connected to GPIO pin {LED_PIN}")
    print("Press Ctrl+C to exit")

    signal.signal(signal.SIGINT, signal_handler)

    try:
        pwm = setup_gpio()
        wait_for_ready()
        breathing_pattern(pwm)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
