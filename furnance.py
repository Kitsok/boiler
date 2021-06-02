#!/usr/bin/python3
# -*- coding: utf8 -*-

import time
import minimalmodbus

import json
from requests import get, post
from secrets import token, host

DEBUG = False
DEBUG = True

# Home
url_temp = host + "api/states/sensor.furnance_temp"
url_power = host + "api/states/sensor.furnance_power"
url_state = host + "api/states/sensor.furnance_state"

headers = {
              "Authorization": token,
              "content-type": "application/json",
          }

furnance_temp = {
            "attributes": {
                "friendly_name": "Furnance Temperature",
                "icon": "mdi:thermometer",
                "unit_of_measurement": "\u00b0C"
            },
            "entity_id": "sensor.furnance_temp",
            "state": "10.0"
}

furnance_power = {
            "attributes": {
                "friendly_name": "Furnance Power",
                "unit_of_measurement": "%"
            },
            "entity_id": "sensor.furnance_power",
            "state": "0.0"
}

furnance_state = {
            "attributes": { "friendly_name": "Furnance State", },
            "entity_id": "sensor.furnance_state",
            "state": "0"
}

########################################################################################

def Run():
    instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 16)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout  = 0.7
    instrument.mode = minimalmodbus.MODE_ASCII

    while True:
        try:
            State = 0
            Temp = 0
            Power = 0
            Step = 0

            State = instrument.read_register(17, 0)
            # Manual alternative, ignores sign FIXME
            #temp_lo = instrument.read_register(2,0)
            #temp_hi = instrument.read_register(1,0)
            #temp_res = ((temp_hi << 16) + temp_lo) / 10
            #print('DEBUG Temp read_register', temp_res)
            Temp = instrument.read_long(1, functioncode=3, signed=True, byteorder=minimalmodbus.BYTEORDER_BIG) / 10
            Power = instrument.read_register(12, 1)
            if State == 1:
                Step = instrument.read_register(16, 0)

            if DEBUG: print('ON::State: {} Step: {} Power: {}% Temp: {}'.format(State, Step, Power, Temp))
            furnance_temp['state'] = Temp
            furnance_power['state'] = Power
            furnance_state['state'] = State

            response = post(url_temp, headers = headers, json = furnance_temp)
            response = post(url_power, headers = headers, json = furnance_power)
            response = post(url_state, headers = headers, json = furnance_state)
            time.sleep(60.0)
        except Exception as e:
            if DEBUG: print('Retry reading', e)
            time.sleep(1.0)
            pass

while True:
    try:
        Run()
    except Exception as e:
        if DEBUG: print(e)
        time.sleep(1.0)
        pass
