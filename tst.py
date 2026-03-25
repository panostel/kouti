from pirc522 import RFID
import subprocess
import os
import signal

rdr = RFID()
UID_Temp = "empty"
UID_Temp_flag = "on"
count_error = 0;
ch = "7]"

try:
	while True:
		# rdr.wait_for_tag()
		count_error += 1
		(error, tag_type) = rdr.request()
		UID_Temp_flag = "on"
		if not error:
			print("Tag detected")
			(error,uid) = rdr.anticoll()
			if not error:
				print(str(uid))
				if UID_Temp != str(uid):
					UID_Temp = str(uid)
					UID_Temp_flag = "off"
					print(str(uid))
				print("UID: " + str(uid))
				ch = UID_Temp[-2:]
				print(ch)
				count_error = 0;
			if not rdr.select_tag(uid):
				if not rdr.card_auth(rdr.auth_a, 10, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid):
					print("Reading block 10: " + str(rdr.read(10)))
					rdr.stop_crypto()
		if UID_Temp_flag == "off":
			match ch:
				case "1]":
					proc = subprocess.Popen("mpg321 /home/pte/pi-rfid/7].mp3", stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
				case "9]":
					proc = subprocess.Popen("mpg321 /home/pte/pi-rfid/05.mp3", stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
				case "3]":
					proc = subprocess.Popen("mpg321 /home/pte/pi-rfid/02.mp3", stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
				case _:
					proc = subprocess.Popen("mpg321 /home/pte/pi-rfid/king-of-apes-16.mp3", stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
							
		if error and count_error == 2:
			try:
				proc
			except NameError:
				print("proc not defined")
			else:		
				os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
				print("stopping")
				UID_Temp = "empty"  
			count_error = 0;
			

except KeyboardInterrupt:
	rdr.cleanup()
