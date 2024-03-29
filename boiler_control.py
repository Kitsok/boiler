#!/usr/bin/python3

from requests import get
from requests import post
import json
import sys
from secrets import token, host
import time

debug = False
debug = True

# Home
url_boiler_settings_tmpl = host + 'api/states/input_number.'
url_boiler_data_tmpl = host + 'api/states/sensor.'
url_ui_thermostate = host + 'api/states/climate.kitchen'
url_setpoint = host + 'api/states/sensor.heatant_setpoint'

ha_boiler_settings = [
    'boiler_min_temp',
    'boiler_max_temp',
    'boiler_heatant_cold',
    'boiler_min_outside',
    'boiler_max_outside',
    'boiler_hyst'
]

ha_current_temps = [
    'kitchen_temperature',
    'street_temperature',
    'heatant_temp'
]

headers = {
    'Authorization': token,
    'content-type': 'application/json',
}

heatant_setpoint = {
    'attributes': {
         'friendly_name': 'Heatant setpoint',
         'icon': 'mdi:thermometer',
         'unit_of_measurement': '\u00b0C'
    },
    'entity_id': 'sensor.heatant_setpoint',
    'state': 41
}


boiler = {}
boiler['settings'] = {}
boiler['data'] = {}

for n in ha_boiler_settings:
   response = get(url_boiler_settings_tmpl + n, headers=headers).json()
   boiler['settings'][n] = float(response['state'])

for n in ha_current_temps:
   response = get(url_boiler_data_tmpl + n, headers=headers).json()
   boiler['data'][n] = float(response['state'])

# Calculate target temperature
target_temp = 41
heater_on = True
heatant_off = 39

pid = {}
try:
    settings = boiler['settings']
    temps = boiler['data']

    # FIXME DEBUG
    # settings["boiler_min_outside"] = -10
    # settings["boiler_max_outside"] = 15
    # temps["street_temperature"] = 6
    # temps["heatant_temp" ] = 20
    # FIXME DEBUG

    k = (settings['boiler_max_temp'] - settings['boiler_min_temp']) / (settings['boiler_min_outside'] - settings['boiler_max_outside'])
    b = settings['boiler_max_temp'] - (k * settings['boiler_min_outside'])
    calc_heatant = b + (k * temps['street_temperature'])
    if debug: print('DEPRECATED: Calculated heatant temperature:', calc_heatant)

    setpoint = get(url_ui_thermostate, headers=headers).json()['attributes']['temperature']
    current_temp = temps['kitchen_temperature']

    try:
        json_file = open('/tmp/pid.json', 'r')
        pid = json.load(json_file)
        if debug: print('Saved data:', json.dumps(pid))
    except Exception as ex:
        print('Unable to open json file', ex)
        pid['current'] = current_temp
        pid['E'] = setpoint - current_temp
        pid['I'] = 0
        pid['D'] = 0
        pid['ts'] = round(time.time())

    deltaT = pid['ts'] - round(time.time())
    if (deltaT == 0):
        deltaT = 1
    E = setpoint - current_temp
    deltaE = pid['E'] - E
    D = deltaE / deltaT
    D = 0.0 # FIXME This is to disable derivative component
    I = pid['I'] + (E * 0.8)

    # Constants
    Kp = 13.4
    Ti = 39.2
    Td = 0
    MAX_I = 73.0
    MIN_I = 0.0

    # Anti wind-up
    if (I > MAX_I): I = MAX_I
    if (I < MIN_I): I = MIN_I

    # Calculate P.I.D.
    pid['ts'] = round(time.time())
    pid['current'] = current_temp
    pid['I'] = I
    pid['D'] = D
    pid['E'] = E
    pid['setpoint'] = setpoint
    P = Kp * (E + D*Td + I/Ti) + heatant_off + 1 # FIXME
    pid['P'] = P
    calc_heatant = P # FIXME

    with open('/tmp/pid.json', 'w') as outfile:
        json.dump(pid, outfile)
    if debug:
        print(json.dumps(pid))
        print('{6} = {0} * ({1} + {2} + {3} / {4} ({5})) + 40'.format(Kp, E, D*Td, I, Ti, I/Ti, P))

    heater_on = False
    if (calc_heatant > 40):
        heater_on = True
    else:
        calc_heatant = heatant_off
        heater_on = False
    #if temps['kitchen_temperature'] > (setpoint + settings['boiler_hyst']):
    #    heater_on = False
    #if temps['kitchen_temperature'] < (setpoint - settings['boiler_hyst']):
    #    heater_on = True

    # Protect from freezing
    if temps['heatant_temp'] < settings['boiler_heatant_cold']:
        heater_on = True
        if (calc_heatant < 41): calc_heatant = 41
        if debug: print('Antifreezing action')

    # Normilize heatant setpoint temperature
    if calc_heatant < settings['boiler_min_temp']:
        calc_heatant = settings['boiler_min_temp']
    if calc_heatant > settings['boiler_max_temp']:
        calc_heatant = settings['boiler_max_temp']


except Exception as ex:
    print('Error:', ex)
    heater_on = True
    calc_heatant = 50 # FIXME must be settable (failsafe heatant temperature

target_temp = round(calc_heatant)

if not heater_on:
    target_temp = heatant_off
if debug: print('Heater:', heater_on, 'Heatant:', target_temp)

# Update thermostate in HA
response = get(url_ui_thermostate, headers=headers).json()
if heater_on:
    response["state"] = 'heat'
else:
    response["state"] = 'off'
response = post(url_ui_thermostate, headers = headers, json = response)

# Update boiler setpoint
heatant_setpoint['state'] = target_temp
response = post(url_setpoint, headers = headers, json = heatant_setpoint)
