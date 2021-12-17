#!/bin/bash
# replicate the host dev file to another place in order to read it from docker container
DEVFILE=/proc/net/dev

while [ true ]; do
	echo "$(<$DEVFILE)" > /tmp/dev
	sleep 0.5
done

