from xbee import ZigBee
import serial
import time
import json
import requests
import re

ser = serial.Serial('/dev/ttyUSB0', 9600)

get_url = "http://ann.metamorphium.com/brains/\\x00\\x13\\xA2\\x00\\x40\\x68\\x2F\\xB6/instructions"
post_url = "http://ann.metamorphium.com/brains/\\x00\\x13\\xA2\\x00\\x40\\x68\\x2F\\xB6/senses"

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
