#!/bin/sh
#(sleep 60; sudo mount -f -o ro,remount / ) &
sleep 30
#echo 'connect 3C:A0:67:44:06:C5' | bluetoothctl
echo 'connect E8:07:BF:1A:0C:D8' | bluetoothctl
#sleep 10
python -u /home/pi/SamplerBox/samplerbox.py
