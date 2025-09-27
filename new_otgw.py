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
from secrets import new_token, new_host

debug = False
debug = True

# Home
url_setpoint = new_host + "api/states/input_number.heatant_setpoint"
url_heatant_temp = new_host + "api/states/input_number.heatant_temp"
url_boiler_power = new_host + "api/states/input_number.boiler_power"
url_boiler_fault = new_host + "api/states/input_text.boiler_fault"
url_boiler_flame = new_host + "api/states/input_boolean.boiler_flame"

headers = {
    "Authorization": new_token,
    "content-type": "application/json",
}

heatant_temp = {
    "attributes": {
         "friendly_name": "Heatant Temperature",
         "icon": "mdi:thermometer",
         "unit_of_measurement": "\u00b0C"
    },
    "entity_id": "input_number.heatant_temp",
    "state": "22.7"
}

boiler_power = {
    "attributes": {
         "friendly_name": "Boiler Power",
         "unit_of_measurement": "%"
    },
    "entity_id": "input_number.boiler_power",
    "state": "30"
}

boiler_fault = {
    "attributes": {
         "friendly_name": "Boiler Fault",
    },
    "entity_id": "input_text.boiler_fault",
    "state": False
}

boiler_flame = {
    "attributes": {
         "friendly_name": "Boiler Flame",
    },
    "entity_id": "input_boolean.boiler_flame",
    "state": False
}

# Fetch setpoint from HA
setpoint = 41
try:
    setpoint = round(float(get(url_setpoint, headers=headers).json()["state"]))
except Exception as ex:
    if debug: print("Error", ex)

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

    if len(sys.argv) != 1 and int(sys.argv[1] is not None):
        print("Override setpoint:", int(sys.argv[1]))
        setpoint = int(sys.argv[1])

    if setpoint != None:
        if debug: print("Setpoint:", setpoint)
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
        if debug: print("From boiler", data_str)
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

if 'Modulation' in boiler_data:
    boiler_power['state'] = boiler_data['Modulation']
    response = post(url_boiler_power, headers = headers, json = boiler_power)
    if debug: print(json.dumps(boiler_power))

if 'Fault' in boiler_data:
    boiler_fault['state'] = boiler_data['Fault']
    response = post(url_boiler_fault, headers = headers, json = boiler_fault)
    if debug: print(json.dumps(boiler_fault))

if 'Flame' in boiler_data:
    boiler_flame['state'] = "off"
    if boiler_data['Flame'] == True: boiler_flame['state'] = "on"
    response = post(url_boiler_flame, headers = headers, json = boiler_flame)
    if debug: print(json.dumps(boiler_flame))

