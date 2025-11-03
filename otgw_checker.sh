#!/bin/bash

[ -e /dev/otgw ] && exit 0

echo "No /dev/otgw, resetting USB device"
echo 0 > /sys/bus/usb/devices/2-1.2.1.4/authorized || :
sleep 1
echo 1 > /sys/bus/usb/devices/2-1.2.1.4/authorized || :
sleep 2
[ -e /dev/otgw ] && echo "Success" || echo "Fail"
