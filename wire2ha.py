#!/usr/bin/python3

from requests import get
from requests import post
import json
import sys
from secrets import token, host

debug = False
debug = True

# Home Assistant URLs
url_states = host + "api/states/"

sensors = [ 
    {"path": "/1wire/28.A8BED5030000/temperature", "id": "sensor.kitchen_temperature", "fname": "Kitchen Temperature"},
    {"path": "/1wire/28.70B9D5030000/temperature", "id": "sensor.street_temperature", "fname": "Street Temperature"}
]

headers = {
    "Authorization": token,
    "content-type": "application/json",
}

temp_sensor = {
    "attributes": {
         "friendly_name": "Study Temperature",
         "icon": "mdi:thermometer",
         "unit_of_measurement": "\u00b0C"
    },
    "entity_id": "sensor.study_temperature",
    "state": "22.7"
}

# First read data from 1Wire temperature sensors and push it to HA
for s in sensors:
    f = open(s["path"], "r")
    temp_sensor["state"] = f.read()
    f.close()
    temp_sensor["attributes"]["friendly_name"] = s["fname"]
    temp_sensor["entity_id"] = s["id"]
    url = url_states + s["id"]
    if debug:
        print("URL:", url, "JSON:", json.dumps(temp_sensor))
    response = post(url, headers = headers, json = temp_sensor)
    if debug:
        print(response.text)
