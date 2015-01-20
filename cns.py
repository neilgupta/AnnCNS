#!/usr/bin/python

# Ann CNS Controller
# Copyright Neil Gupta 2015
import serial, time, json, requests, re

#### CONFIGURE HERE ####

# Enter your full xbee address here
CNS_ADDRESS = "\\x00\\x13\\xA2\\x00\\x40\\x68\\x2F\\xB6"
# Enter where your xbee is connected. On Pi's with only 2 USB ports, the lower one is USB0 and the higher one is USB1
SERIAL_PORT = '/dev/ttyUSB0' # rPi
# SERIAL_PORT = '/dev/tty.usbserial-A501FXLG' # mac
# The default should be fine
BAUD_RATE = 9600
# Where is Ann server located? (Do NOT include the trailing slash)
SERVER = "http://ann.metamorphium.com"
# SERVER = "http://localhost:3000"

#### END CONFIGURATION ####

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
get_url = SERVER + "/brains/" + CNS_ADDRESS + "/instructions"
post_url = SERVER + "/brains/" + CNS_ADDRESS + "/senses"

print get_url
ser.write('d')

while True:
  try:
    # Check for new instructions
    r = requests.get(get_url)
    if r.status_code == 200:
      j = json.loads(r.content)
      if len(j) > 0:
        for k in j:
          for c in k['content']:
            # Broadcast instruction
            ser.write(str(c))
            # Wait for command to finish executing
            time.sleep(k['timer'])
    # Check again in 2 seconds
    time.sleep(2)
  except:
    # wait 5 seconds if there's an exception
    time.sleep(5)

# halt() must be called before closing the serial
# port in order to ensure proper thread shutdown
# xbee.halt()
ser.close()

# xbee.send("tx", data="b\n", dest_addr_long="\x00\x13\xA2\x00\x40\x68\x2E\xA4", dest_addr="\xff\xff")
