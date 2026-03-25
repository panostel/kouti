from pirc522 import RFID
import subprocess
import os
import signal
import json

TAGS_FILE = os.path.join(os.path.dirname(__file__), 'tags.json')
AUDIO_PGID_FILE = '/tmp/audio_pgid'
REGISTER_MODE_FILE = '/tmp/register_mode'
PENDING_UID_FILE = '/tmp/pending_uid'
READY_FLAG_FILE = '/tmp/soundbox_ready'


def load_tags():
    try:
        with open(TAGS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"default": "/home/pte/pi-rfid/king-of-apes-16.mp3", "tags": {}}


rdr = RFID()

# Signal ready — LED breathing will start once this flag exists
open(READY_FLAG_FILE, 'w').close()

UID_Temp = "empty"
UID_Temp_flag = "on"
count_error = 0
proc = None

try:
    while True:
        count_error += 1
        (error, tag_type) = rdr.request()
        UID_Temp_flag = "on"

        if not error:
            print("Tag detected")
            (error, uid) = rdr.anticoll()
            if not error:
                uid_key = str(uid)
                if UID_Temp != uid_key:
                    UID_Temp = uid_key
                    UID_Temp_flag = "off"
                print("UID: " + uid_key)
                count_error = 0
            if not rdr.select_tag(uid):
                if not rdr.card_auth(rdr.auth_a, 10, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid):
                    print("Reading block 10: " + str(rdr.read(10)))
                    rdr.stop_crypto()

        if UID_Temp_flag == "off":
            # Register mode: write UID to pending file instead of playing audio
            if os.path.exists(REGISTER_MODE_FILE):
                with open(PENDING_UID_FILE, 'w') as f:
                    f.write(UID_Temp)
                print("Register mode: wrote UID " + UID_Temp)
            else:
                config = load_tags()
                audio_file = config["tags"].get(UID_Temp, config["default"])
                print("Playing: " + audio_file)
                proc = subprocess.Popen(
                    ["mpg321", "-a", "pulse", audio_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid,
                    env={**os.environ, "PULSE_SERVER": "unix:/run/user/1000/pulse/native"}
                )
                with open(AUDIO_PGID_FILE, 'w') as f:
                    f.write(str(os.getpgid(proc.pid)))

        if error and count_error == 2:
            if proc is not None:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    os.remove(AUDIO_PGID_FILE)
                except FileNotFoundError:
                    pass
                proc = None
                print("stopping")
            UID_Temp = "empty"
            count_error = 0

except KeyboardInterrupt:
    rdr.cleanup()
    try:
        os.remove(READY_FLAG_FILE)
    except FileNotFoundError:
        pass
