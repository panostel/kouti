#***************************************************************************************
#               Code for Controlling Pi Volume Using Rotary Encoder
#                     Original Code: https://bit.ly/2OcaQGq
#                    Re-Written by Sid for Sid's E Classroom
#                    https://www.youtube.com/c/SidsEClassroom
#             All text above must be included in any redistribution.
#  If you find this useful and want to make a donation -> https://paypal.me/sidsclass
# ***************************************************************************************

from RPi import GPIO
from time import sleep
import os
import signal
import subprocess

PULSE_SERVER = "unix:/run/user/1000/pulse/native"

# Wait for PipeWire to be ready
print("Waiting for audio system to initialize...")
sleep(5)

# Change the following pins based on your application or HAT in use
encoder_clk = 26
encoder_data = 13
encoder_button = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(encoder_clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_data, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set desired minimum and maximum values
min_vol = 0
max_vol = 100

# Set the volume change step size
volume_step_size = 5


def set_volume(vol):
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{int(vol)}%"],
        env={**os.environ, "PULSE_SERVER": PULSE_SERVER},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def get_volume():
    try:
        result = subprocess.run(
            ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
            env={**os.environ, "PULSE_SERVER": PULSE_SERVER},
            capture_output=True, text=True
        )
        # Output: "Volume: front-left: 65536 / 100% / ..."
        parts = result.stdout.split("/")
        if len(parts) >= 2:
            return int(parts[1].strip().rstrip("%"))
    except Exception:
        pass
    return 100


# Wait for PipeWire to have the sink ready
volume = 100
while True:
    v = get_volume()
    if v is not None:
        volume = v
        break
    print("Waiting for PipeWire sink...")
    sleep(2)

print("Volume: " + str(volume))
clkLastState = GPIO.input(encoder_clk)
btnLastState = GPIO.input(encoder_button)
is_paused = False

try:
    while True:
        btnPushed = GPIO.input(encoder_button)
        if ((not btnLastState) and btnPushed):
            try:
                with open('/tmp/audio_pgid', 'r') as f:
                    pgid = int(f.read().strip())
                if is_paused:
                    os.killpg(pgid, signal.SIGCONT)
                    is_paused = False
                    print("Resumed")
                else:
                    os.killpg(pgid, signal.SIGSTOP)
                    is_paused = True
                    print("Paused")
            except (FileNotFoundError, ValueError, ProcessLookupError):
                print("No audio playing")
            sleep(0.05)
        else:
            clkState = GPIO.input(encoder_clk)
            dtState = GPIO.input(encoder_data)
            if clkState != clkLastState:
                if dtState != clkState:
                    volume += volume_step_size / 2
                    if volume > max_vol:
                        volume = max_vol
                else:
                    volume -= volume_step_size / 2
                    if volume < min_vol:
                        volume = min_vol
                if clkState == 1:
                    print("Volume: " + str(int(volume)))
                    set_volume(volume)
            clkLastState = clkState
        btnLastState = btnPushed
finally:
    GPIO.cleanup()
