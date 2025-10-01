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

url_tmpl = new_host + "api/states/"

headers = {
    'Authorization': new_token,
    'content-type': 'application/json',
}

state_sensor = { }

port = '/dev/ttyMAP'
try:
	ser = open(port)
	attrs = termios.tcgetattr(ser)
	attrs[2] = attrs[2] & ~termios.HUPCL
	termios.tcsetattr(ser, termios.TCSAFLUSH, attrs)
	ser.close()
	ser = serial.Serial(port, 19200, timeout=2)
except Exception as ex:
	print('Error', ex)
	sys.exit()

# Flush the garbage
ser.flush()
ser.reset_input_buffer()

# Request data
tries = 0
maxtries = 3
boiler_data = None

def getMap(ser, cmd):
	command = bytearray(cmd, 'ascii')
	command.append(0x0d)
	command.append(0x0a)
	ser.write(command)
	if debug: print('DEBUG', '>>>>', command)
	rc = bytearray()
	echo = False
	while(True):
		tmp = ser.read(1)
		if echo == False and tmp == b'\n':
			echo = True
			continue
		if tmp == b'':
			rc = ''
			break
		if echo:
			ser.write(tmp)
			if tmp != b'\r' and tmp != b'\n':
				rc.append(tmp[0])
			if tmp == b'\n':
				if debug: print('DEBUG', '<<<<', rc.decode('ascii'))
				if rc.decode('ascii').find('MOk') == 0:
					answer = bytearray()
					answer.append(rc[3])
					answer.append(rc[4])
					return int(answer.decode('ascii'), 16)
				else:
					return -1
				break

commands = [
	{'addr': 'PCRD4006C', 'name': 'Mode', 'unit': '', 'times': 0, 'add': 0, 
		'desc': [
			'Откл, сети нет',
			'Откл, сеть есть',
			'Вкл, разряд',
			'Вкл, на сети',
			'Вкл, заряд',
			'Вкл, насквозь'
		], 'url': 'input_text.sostoianie' },
	{'addr': 'PCRD40765', 'name': 'Vacc',  'unit': 'V',  'times': 0.1, 'add': 0,   'url': 'input_number.napriazhenie_batarei'},
	{'addr': 'PCRD40963', 'name': 'Pacc',  'unit': 'A',  'times': 1,   'add': 0,   'url': 'input_number.battery_power'},
	{'addr': 'PCRD42268', 'name': 'Vgrid', 'unit': 'V',  'times': 1,   'add': 100, 'url': 'input_number.napriazhenie_seti'},
	{'addr': 'PCRD42367', 'name': 'Igrid', 'unit': 'A',  'times': 1,   'add': 0,   'url': 'input_number.tok_iz_seti'},
	{'addr': 'PCRD42565', 'name': 'Fgrid', 'unit': 'Hz', 'times': 1,   'add': 0,   'url': 'input_number.chastota'},
	{'addr': 'PCRD42466', 'name': 'Pgrid', 'unit': 'W',  'times': 100, 'add': 0,   'url': 'input_number.grid_power'},
]

#commands = [
#	{'addr': 'PCRD40864', 'name': 'Iacc',  'unit': 'A',  'times': 1,   'add': 0,   'url': 'input_number.battery_power'},
#	{'addr': 'PCRD40963', 'name': 'Pacc',  'unit': 'A',  'times': 1,   'add': 0,   'url': 'input_number.battery_power'},
#
#]

state = ''
for cmd in commands:
	rc = getMap(ser, cmd['addr'])
	if rc == -1:
		if debug: print('{} ERROR'.format(cmd['addr']))
		continue
	desc = ''
	if 'desc' in cmd:
		desc = cmd['desc'][rc]
	value = rc
	if cmd['times'] != 0:
		value = cmd['add'] + rc * cmd['times']
	if desc == '':
		desc = round(value, 2)
	state_sensor['state'] = desc
	state_sensor['entity_id'] = cmd['url']
	if debug: print(">>>>>", state_sensor)
	response = post(url_tmpl + cmd['url'], headers=headers, json = state_sensor).json()
	if debug: print("<<<<<", response)

