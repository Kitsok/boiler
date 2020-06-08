#!/usr/bin/python3

import serial
import time
import json
import sys
import termios
from collections import namedtuple
from requests import get
from requests import post
import json
from secrets import token, host

debug = False
debug = True

# Home
url_setpoint = host + "api/states/sensor.heatant_setpoint"
url_heatant_temp = host + "api/states/sensor.heatant_temp"

headers = {
    "Authorization": token,
    "content-type": "application/json",
}

heatant_temp = {
    "attributes": {
         "friendly_name": "Heatant Temperature",
         "icon": "mdi:thermometer",
         "unit_of_measurement": "\u00b0C"
    },
    "entity_id": "sensor.heatant_temp",
    "state": "22.7"
}

# Fetch setpoint from HA
setpoint = 41
try:
    setpoint = round(float(get(url_setpoint, headers=headers).json()["state"]))
except Exception as ex:
    if debug: print("Error", ex)

if debug: print("Setpoint:", setpoint)


# Talk to OpenTherm gateway
port = '/dev/otgw'
try:
    ser = open(port)
    attrs = termios.tcgetattr(ser)
    attrs[2] = attrs[2] & ~termios.HUPCL
    termios.tcsetattr(ser, termios.TCSAFLUSH, attrs)
    ser.close()
    ser = serial.Serial(port, 115200, timeout=2)
except Exception as ex:
    print("Error:", ex)
    sys.exit()

# Flush the garbage
ser.write(bytearray("\r", "ascii"))
ser.flush()
ser.reset_input_buffer()

# Request data
tries = 0
maxtries = 5
boiler_data = None

while (True):
    if tries >= maxtries:
        sys.exit()

    if setpoint != None:
        ser.write(bytearray("s " + str(setpoint) + "\r", "ascii"))
        ser.flush()
        trash = ser.readline().decode('ascii').rstrip()
        ser.reset_input_buffer()

    ser.write(bytearray("g\r", "ascii"))
    ser.flush()
    data_str = ser.readline().decode('ascii').rstrip()
    if "{" not in data_str:
        tries = tries + 1
        continue
    try:
        boiler_data = json.loads(data_str)
    except:
        tries = tries + 1
        continue
    if 'Flame' in boiler_data:
        boiler_data['Setpoint'] = setpoint
        if debug: print(json.dumps(boiler_data))
        break
    tries = tries + 1

if 'Tout' in boiler_data:
    heatant_temp['state'] = boiler_data['Tout']
    response = post(url_heatant_temp, headers = headers, json = heatant_temp)
    if debug: print(json.dumps(heatant_temp))

