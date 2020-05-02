#!/usr/bin/python3

from requests import get
from requests import post
import json
import sys
from secrets import token, host

debug = False
debug = True

# Home
url_boiler_settings_tmpl = host + "api/states/input_number."
url_boiler_data_tmpl = host + "api/states/sensor."
url_ui_thermostate = host + "api/states/climate.kitchen"
url_setpoint = host + "api/states/sensor.heatant_setpoint"

ha_boiler_settings = [
    "boiler_min_temp",
    "boiler_max_temp",
    "boiler_heatant_cold",
    "boiler_min_outside",
    "boiler_max_outside",
    "boiler_hyst"
]

ha_current_temps = [
    "kitchen_temperature",
    "street_temperature",
    "heatant_temp"
]

headers = {
    "Authorization": token,
    "content-type": "application/json",
}

heatant_setpoint = {
    "attributes": {
         "friendly_name": "Heatant setpoint",
         "icon": "mdi:thermometer",
         "unit_of_measurement": "\u00b0C"
    },
    "entity_id": "sensor.heatant_setpoint",
    "state": 41
}


boiler = {}
boiler["settings"] = {}
boiler["data" ] = {}

for n in ha_boiler_settings:
   response = get(url_boiler_settings_tmpl + n, headers=headers).json()
   boiler["settings"][n] = float(response['state'])

for n in ha_current_temps:
   response = get(url_boiler_data_tmpl + n, headers=headers).json()
   boiler["data"][n] = float(response['state'])

# Calculate target temperature
target_temp = 41
heater_on = True
heatant_off = 39

try:
    settings = boiler["settings"]
    temps = boiler["data"]

    # FIXME DEBUG
    # settings["boiler_min_outside"] = -10
    # settings["boiler_max_outside"] = 15
    # temps["street_temperature"] = 6
    # temps["heatant_temp" ] = 20
    # FIXME DEBUG

    k = (settings["boiler_max_temp"] - settings["boiler_min_temp"]) / (settings["boiler_min_outside"] - settings["boiler_max_outside"])
    b = settings["boiler_max_temp"] - (k * settings["boiler_min_outside"])
    calc_heatant = b + (k * temps["street_temperature"])
    if debug: print("Calculated heatant temperature:", calc_heatant)

    target_air_temp = get(url_ui_thermostate, headers=headers).json()["attributes"]["temperature"]
    heater_on = False
    if temps["kitchen_temperature"] > (target_air_temp + settings["boiler_hyst"]):
        heater_on = False
    if temps["kitchen_temperature"] < (target_air_temp - settings["boiler_hyst"]):
        heater_on = True

    # Protect from freezing
    if temps["heatant_temp"] < settings["boiler_heatant_cold" ]:
        heater_on = True
        if debug: print("Antifreezing action")

    # Normilize heatant setpoint temperature
    if calc_heatant < settings["boiler_min_temp"]:
        calc_heatant = settings["boiler_min_temp"]
    if calc_heatant > settings["boiler_max_temp"]:
        calc_heatant = settings["boiler_max_temp"]

    target_temp = round(calc_heatant)

except Exception as ex:
    print("Error:", ex)

if not heater_on:
    target_temp = heatant_off
if debug: print("Heater:", heater_on, "Heatant:", target_temp)

# Update thermostate in HA
response = get(url_ui_thermostate, headers=headers).json()
if heater_on:
    response["state"] = 'heat'
else:
    response["state"] = 'off'
response = post(url_ui_thermostate, headers = headers, json = response)

# Update boiler setpoint
heatant_setpoint["state"] = target_temp
response = post(url_setpoint, headers = headers, json = heatant_setpoint)
