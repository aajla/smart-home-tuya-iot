from __future__ import print_function
import time
import coloredlogs
from tuyalinksdk.client import TuyaClient
from tuyalinksdk.console_qrcode import qrcode_generate
import serial

coloredlogs.install(level='DEBUG')

# -----------------------------------------------------------
# Serial port
# -----------------------------------------------------------
ser = serial.Serial('COM4', 115200)

lt = None
lh = None
q  = 0
t  = None
h  = None

# -----------------------------------------------------------
# Tuya credentials
# -----------------------------------------------------------
client = TuyaClient(
    productid = 'YOUR_PRODUCT_ID',
    uuid      = 'YOUR_UUID',
    authkey   = 'YOUR_AUTH_KEY'
)

# -----------------------------------------------------------
# Motion state descriptions (104 = PIR, 105 = RCWL)
# Matches Arduino state machine:
#  0 - no motion on either sensor
#  1 - RCWL detecting, PIR not detecting
#  2 - PIR detecting, RCWL not detecting
#  3 - both sensors detecting
#  4 - PIR not detecting, RCWL finished
#  5 - PIR detecting, RCWL finished
#  6 - PIR finished, RCWL not detecting
#  7 - PIR finished, RCWL detecting
#  8 - both sensors finished
# -----------------------------------------------------------
MOTION_STATES = {
    0: ('Not detecting!', 'Not detecting!'),
    1: ('Not detecting!', 'Detecting!'),
    2: ('Detecting!',     'Not detecting!'),
    3: ('Detecting!',     'Detecting!'),
    4: ('Not detecting!', 'Finished!'),
    5: ('Detecting!',     'Finished!'),
    6: ('Finished!',      'Not detecting!'),
    7: ('Finished!',      'Detecting!'),
    8: ('Finished!',      'Finished!'),
}

MOTION_MESSAGES = {
    0: "No motion detected on either sensor",
    1: "Motion detected by RCWL sensor, PIR not detecting",
    2: "Motion detected by PIR sensor, RCWL not detecting",
    3: "Motion detected by both PIR and RCWL sensors",
    4: "PIR not detecting, RCWL finished detecting",
    5: "Motion detected by PIR sensor, RCWL finished detecting",
    6: "PIR finished detecting, RCWL not detecting",
    7: "PIR finished detecting, motion detected by RCWL sensor",
    8: "Both sensors finished detecting",
}

# -----------------------------------------------------------
# Callbacks
# -----------------------------------------------------------
def on_connected():
    print('Connected.')

def on_qrcode(url):
    qrcode_generate(url)

def on_reset(data):
    print('Reset:', data)

def on_dps(dps):
    """Called when the app sends a command (e.g. toggle LED)."""
    global lt, lh, t, h, q
    print('DataPoints:', dps)
    if dps == {'101': True}:
        print("LED is on.")
        time.sleep(0.1)
        ser.write(b'H')
    elif dps == {'101': False}:
        print("LED is off.")
        time.sleep(0.1)
        ser.write(b'L')
    client.push_dps(dps)

client.on_connected = on_connected
client.on_qrcode    = on_qrcode
client.on_reset     = on_reset
client.on_dps       = on_dps

client.connect()
client.loop_start()

# -----------------------------------------------------------
# Main loop - read serial data from Arduino
# -----------------------------------------------------------
while True:
    arduino_data   = ser.readline()
    decoded_values = arduino_data.decode().strip()

    if decoded_values.startswith('T'):          # Temperature
        t = int(decoded_values[1:])
        if t != lt:
            lt  = t
            dps = {'102': lt}
            on_dps(dps)

    elif decoded_values.startswith('H'):        # Humidity
        h = int(decoded_values[1:])
        if h != lh:
            lh  = h
            dps = {'103': lh}
            on_dps(dps)

    elif decoded_values.startswith('M'):        # Motion
        q = int(decoded_values[1:])
        pir_state, rcwl_state = MOTION_STATES.get(q, ('Not detecting!', 'Not detecting!'))
        dps = {'104': pir_state, '105': rcwl_state}
        client.push_dps(dps)
        print(MOTION_MESSAGES.get(q, "Unknown state"))

    else:
        dps = {'104': 'Not detecting!', '105': 'Not detecting!'}
        on_dps(dps)

    time.sleep(0.1)
