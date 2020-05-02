#!/bin/sh

EACH=60
CMD=wire2ha.py

[ -n "$1" ] && CMD=$1
[ -n "$2" ] && EACH=$2
while true; do
	/usr/local/sbin/$CMD
	sleep $EACH
done
