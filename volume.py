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
import alsaaudio
import os
import signal

# Wait for audio system to be ready
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

m = alsaaudio.Mixer()

# Set desired minimum and maximum values
min = 0
max = 100

# Set the volume change step size
volume_step_size = 5

is_paused = False
volume = m.getvolume()[0]

print("Volume: " + str(volume))
print("")
clkLastState = GPIO.input(encoder_clk)
btnLastState = GPIO.input(encoder_button)

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
                    if volume > max:
                        volume = max
                else:
                    volume -= volume_step_size / 2
                    if volume < min:
                        volume = min
                if clkState == 1:
                    print("Volume: " + str(int(volume)))
                    print("")
                    m.setvolume(int(volume))
            clkLastState = clkState
        btnLastState = btnPushed
finally:
    GPIO.cleanup()
