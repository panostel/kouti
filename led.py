#!/usr/bin/env python3
"""
LED State Indicator for Raspberry Pi Soundbox
- idle:    breathing pattern (slow sine-wave pulse)
- playing: steady on
- paused:  slow blink (0.8s on / 0.8s off)
Waits for /tmp/soundbox_ready before starting.
"""

import RPi.GPIO as GPIO
import time
import math
import signal
import sys
import os

LED_PIN = 5
PWM_FREQUENCY = 1000
BREATH_DURATION = 4.0
FADE_STEPS = 100
READY_FLAG_FILE = '/tmp/soundbox_ready'
STATE_FILE = '/tmp/soundbox_state'

BLINK_ON = 0.8
BLINK_OFF = 0.8


def read_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return 'idle'


def signal_handler(sig, frame):
    print("\nExiting...")
    GPIO.cleanup()
    sys.exit(0)


def wait_for_ready():
    print("Waiting for soundbox to be ready...")
    while not os.path.exists(READY_FLAG_FILE):
        time.sleep(0.5)
    print("Soundbox ready — starting LED")


def run(pwm):
    step_delay = BREATH_DURATION / FADE_STEPS
    breath_index = 0  # track position in breath cycle across iterations
    blink_phase_start = None
    last_state = None

    while True:
        state = read_state()

        if state != last_state:
            print(f"LED state: {state}")
            last_state = state
            blink_phase_start = time.monotonic()
            breath_index = 0

        if state == 'playing':
            pwm.ChangeDutyCycle(100)
            time.sleep(0.05)

        elif state == 'paused':
            now = time.monotonic()
            elapsed = (now - blink_phase_start) % (BLINK_ON + BLINK_OFF)
            if elapsed < BLINK_ON:
                pwm.ChangeDutyCycle(100)
            else:
                pwm.ChangeDutyCycle(0)
            time.sleep(0.05)

        else:  # idle — breathing
            angle = (breath_index / FADE_STEPS) * math.pi
            brightness = math.sin(angle) * 100
            pwm.ChangeDutyCycle(brightness)
            time.sleep(step_delay)
            breath_index = (breath_index + 1) % FADE_STEPS


def main():
    print("LED State Indicator")
    signal.signal(signal.SIGINT, signal_handler)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    pwm = GPIO.PWM(LED_PIN, PWM_FREQUENCY)
    pwm.start(0)

    try:
        wait_for_ready()
        run(pwm)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
