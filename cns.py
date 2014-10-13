# Ann CNS Controller
# Copyright Neil Gupta 2014

from xbee import ZigBee
import serial, time, json, requests, re

#### CONFIGURE HERE ####

# Enter your full xbee address here
CNS_ADDRESS = "\\x00\\x13\\xA2\\x00\\x40\\x68\\x2F\\xB6"
# Enter where your xbee is connected. On Pi's with only 2 USB ports, the lower one is USB0 and the higher one is USB1
SERIAL_PORT = '/dev/ttyUSB0'
# The default should be fine
BAUD_RATE = 9600
# Where is Ann server located? (Do NOT include the trailing slash)
SERVER = "http://ann.metamorphium.com"

#### END CONFIGURATION ####

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
get_url = SERVER + "/brains/" + CNS_ADDRESS + "/instructions"
post_url = SERVER + "/brains/" + CNS_ADDRESS + "/senses"

# Send incoming data to server for processing
def message_received(data):
  try:
    addr = data['source_addr_long'].encode("hex")
    addr = re.sub("(.{2})", "\\x\\1", addr, 0, re.DOTALL)
    payload = {'sensor_addr': addr, 'payload': data['rf_data']}
    r = requests.post(post_url, payload)

xbee = ZigBee(ser, escaped=True, callback=message_received)

while True:
  try:
    # Check for new instructions every 60 seconds
    r = requests.get(get_url)
    j = json.loads(r.content)
    if len(j) > 0:
      for k in j:
        xbee.send("tx", data=k['content'] + "\n", dest_addr_long=k['address'].decode('string_escape'), dest_addr="\xff\xff")
    time.sleep(60)
  except KeyboardInterrupt:
    break

# halt() must be called before closing the serial
# port in order to ensure proper thread shutdown
xbee.halt()
ser.close()

# xbee.send("tx", data="b\n", dest_addr_long="\x00\x13\xA2\x00\x40\x68\x2E\xA4", dest_addr="\xff\xff")
