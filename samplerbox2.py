#  SamplerBox2
#
#  author:          Joseph Ernest (twitter: @JosephErnest, mail: contact@samplerbox.org)
#  contributor:     Alex MacRae (alex.finlay.macrae@gmail.com)
#  url:             http://www.samplerbox.org/
#  license:         Creative Commons ShareAlike 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)
#
#  samplerbox2.py:  Main file
#


#########################################
# IMPORT
# MODULES
#########################################
import time
usleep = lambda x: time.sleep(x / 1000000.0)
msleep = lambda x: time.sleep(x / 1000.0)
#import curses
import numpy
import os
import glob
import re
import pyaudio
import threading
from chunk import Chunk
import struct
#import rtmidi_python as rtmidi
import rtmidi2               # Use rtmidi2 instead. Make sure when installing rtmidi2 to change RPI date: $sudo date -s "Sept 23 18:31 2016". Then installing takes a while

import ctypes # For freeverb
#from filters import FilterType, Filter, FilterChain
#from utility import byteToPCM, floatToPCM, pcmToFloat, sosfreqz
from collections import OrderedDict
from time import sleep



import globalvars as gvars
import loadsamples as ls
import sound
import navigator
import midicallback
import lcd
import buttons


#########################################
# LOCAL
# CONFIG
#########################################

gvars.AUDIO_DEVICE_ID         = 3                  # change this number to use another soundcard
gvars.AUDIO_DEVICE_NAME       = "USB Audio DAC"   # If we know the name (or part of the name), match by name instead
#gvars.SAMPLES_DIR            = "../../media"     # The root directory containing the sample-sets. Example: "/media/" to look for samples on a USB stick / SD card
gvars.SAMPLES_DIR             = "./media"         # The root directory containing the sample-sets. Example: "/media/" to look for samples on a USB stick / SD card
gvars.USE_SERIALPORT_MIDI     = False             # Set to True to enable MIDI IN via SerialPort (e.g. RaspberryPi's GPIO UART pins)
gvars.USE_I2C_7SEGMENTDISPLAY = False             # Set to True to use a 7-segment display via I2C
gvars.USE_BUTTONS             = False             # Set to True to use momentary buttons (connected to RaspberryPi's GPIO pins) to change preset
gvars.MAX_POLYPHONY           = 80                # This can be set higher, but 80 is a safe value
gvars.MIDI_CHANNEL            = 1
gvars.USE_HD44780_16x2_LCD    = True             # Set to True to use a HD44780 based 16x2 LCD
gvars.USE_FREEVERB            = False             # Set to True to enable FreeVerb
gvars.USE_TONECONTOL          = False	            # Set to True to enable Tonecontrol (also remove comments in code
gvars.CHANNELS                = 2	                # set to 2 for normal stereo output, 4 for 4 channel playback
gvars.BUFFERSIZE              = 64              # Buffersize: lower means less latency, higher more polyphony and stability
gvars.SAMPLERATE              = 44100
gvars.VERSION1                = " -=SAMPLER-BOX=- "
gvars.VERSION2                = "V2.0.1 15-06-2016"

gvars.LCD_DEBUG = True                       # Print LCD messages to python

#lcd.init()

############################################################
# Start the Navigator
############################################################

gvars.nav = navigator.Navigator(navigator.PresetNav)
gvars.nav.parseConfig()



# Volumes from 0-127 0=-20db, 127=0db

# Set Sampler volume
def setSamplerVol(vol):                 # volume in db
    vol = (vol * 20.0 / 127.0) - 20
    gvars.globalvolumeDB = vol
    gvars.globalvolume = 10 ** (vol / 20.0)

# Set Backing volume
def setBackVol(vol):                 # volume in db
    vol = (vol * 20.0 / 127.0) - 20
    gvars.backvolumeDB = vol
    gvars.backvolume = 10 ** (vol / 20.0)

# Set Click volume
def setClickVol(vol):                 # volume in db
    vol = (vol * 20.0 / 127.0) - 20
    gvars.clickvolumeDB = vol
    gvars.clickvolume = 10 ** (vol / 20.0)

setSamplerVol(50)
setBackVol(50)
setClickVol(50)










#########################################
##  based on 16x2 LCD interface code by Rahul Kar, see:
##  http://www.rpiblog.com/2012/11/interfacing-16x2-lcd-with-raspberry-pi.html
#########################################

# class HD44780:
#
#     def __init__(self, pin_rs=7, pin_e=8, pins_db=[25, 24, 23, 18]):
#         self.pin_rs = pin_rs
#         self.pin_e = pin_e
#         self.pins_db = pins_db
#
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(self.pin_e, GPIO.OUT)
#         GPIO.setup(self.pin_rs, GPIO.OUT)
#         for pin in self.pins_db:
#             GPIO.setup(pin, GPIO.OUT)
#
#         self.clear()
#
#     def clear(self):
#         """ Blank / Reset LCD """
#
#         self.cmd(0x33) # Initialization by instruction
#         msleep(5)
#         self.cmd(0x33)
#         usleep(100)
#         self.cmd(0x32) # set to 4-bit mode
#         self.cmd(0x28) # Function set: 4-bit mode, 2 lines
#         #self.cmd(0x38) # Function set: 8-bit mode, 2 lines
#         self.cmd(0x0C) # Display control: Display on, cursor off, cursor blink off
#         self.cmd(0x06) # Entry mode set: Cursor moves to the right
#         self.cmd(0x01) # Clear Display: Clear & set cursor position to line 1 column 0
#
#     def cmd(self, bits, char_mode=False):
#         """ Send command to LCD """
#
#         sleep(0.002)
#         bits = bin(bits)[2:].zfill(8)
#
#         GPIO.output(self.pin_rs, char_mode)
#
#         for pin in self.pins_db:
#             GPIO.output(pin, False)
#
#         #for i in range(8):       # use range 4 for 4-bit operation
#         for i in range(4):       # use range 4 for 4-bit operation
#             if bits[i] == "1":
#                 GPIO.output(self.pins_db[::-1][i], True)
#
#         GPIO.output(self.pin_e, True)
#         usleep(1)      # command needs to be > 450 nsecs to settle
#         GPIO.output(self.pin_e, False)
#         usleep(100)    # command needs to be > 37 usecs to settle
#
#         """ 4-bit operation start """
#         for pin in self.pins_db:
#             GPIO.output(pin, False)
#
#         for i in range(4, 8):
#             if bits[i] == "1":
#                 GPIO.output(self.pins_db[::-1][i-4], True)
#
#         GPIO.output(self.pin_e, True)
#         usleep(1)      # command needs to be > 450 nsecs to settle
#         GPIO.output(self.pin_e, False)
#         usleep(100)    # command needs to be > 37 usecs to settle
#         """ 4-bit operation end """
#
#     def message(self, text):
#         """ Send string to LCD. Newline wraps to second line"""
#
#         self.cmd(0x02) # Home Display: set cursor position to line 1 column 0
#         x = 0
#         for char in text:
#             if char == '\n':
#                 self.cmd(0xC0) # next line
#                 x = 0
#             else:
#                 x += 1
#                 if x < 17: self.cmd(ord(char), True)
#


#########################################
# OPEN AUDIO DEVICE
#########################################

# Use pyaudio only to list devices. sounddevice doesn't seem to have that option

p = pyaudio.PyAudio()

print "Here is a list of audio devices:"
foundByDeviceName = False
dev_name = ''
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    s = ""
    if not foundByDeviceName:
        if i == gvars.AUDIO_DEVICE_ID:
            s += " <--- SELECTED BY ID"
            dev_name = dev['name']
        if (gvars.AUDIO_DEVICE_NAME in dev['name']):
            gvars.AUDIO_DEVICE_ID = i
            s += " <--- SELECTED BY MATCHED NAME (takes precedence)"
            dev_name = dev['name']
            foundByDeviceName = True
        if dev['maxOutputChannels'] > 0:
            print str(i) + ": " + dev['name'] + s
        # if (s != ""):
        #     break
        # else:
        #     continue


try:
    stream = p.open(format=pyaudio.paInt16, channels=gvars.CHANNELS, rate=gvars.SAMPLERATE, frames_per_buffer=gvars.BUFFERSIZE, output=True,
                    output_device_index=gvars.AUDIO_DEVICE_ID, stream_callback=sound.AudioCallback)
except:
    print "Sample audio:  Invalid Audio Device ID"
    exit(1)

# initFilter()
# updateFilter(0, 1000.0, 12.0, 1.0)

# try:
#     sd = sounddevice.OutputStream(device=gvars.AUDIO_DEVICE_ID, blocksize=gvars.BUFFERSIZE, samplerate=gvars.SAMPLERATE, channels=gvars.CHANNELS, dtype='int16', callback=sound.AudioCallback)
#     sd.start()
#     print 'Opened audio device #' + str(gvars.AUDIO_DEVICE_ID) + ' (' + dev_name + ')'
#
# except:
#     print 'Invalid audio device #%i' % gvars.AUDIO_DEVICE_ID
#     exit(1)





#########################################

if gvars.USE_BUTTONS and gvars.IS_DEBIAN:
    ButtonsThread = threading.Thread(target=buttons.Buttons)
    ButtonsThread.daemon = True
    ButtonsThread.start()


#########################################
# MIDI IN via SERIAL PORT
#########################################

if gvars.USE_SERIALPORT_MIDI:
    import serial

    ser = serial.Serial('/dev/ttyAMA0', baudrate=38400)       # see hack in /boot/cmline.txt : 38400 is 31250 baud for MIDI!

    def MidiSerialCallback():
        message = [0, 0, 0]
        while True:
            i = 0
            while i < 3:
                data = ord(ser.read(1))  # read a byte
                if data >> 7 != 0:
                    i = 0      # status byte!   this is the beginning of a midi message: http://www.midi.org/techspecs/midimessages.php
                message[i] = data
                i += 1
                if i == 2 and message[0] >> 4 == 12:  # program change: don't wait for a third byte: it has only 2 bytes
                    message[2] = 0
                    i = 3
            midicallback.MidiCallback(message, None)

    MidiThread = threading.Thread(target=MidiSerialCallback)
    MidiThread.daemon = True
    MidiThread.start()



#########################################
# LOAD FIRST SOUNDBANK
#
#########################################
'''
fvsetdry(0.7)
print 'freeverb Roomsize: ' + str(fvgetroomsize())
print 'freeverb Damp: ' + str(fvgetdamp())
print 'freeverb Wet: ' + str(fvgetwet())
print 'freeverb Dry: ' + str(fvgetdry())
print 'freeverb Width: ' + str(fvgetwidth())
'''
#


ls.LoadSamples()


#########################################
# MIDI DEVICES DETECTION
# MAIN LOOP
#########################################

stopit = False

midi_in = rtmidi2.MidiInMulti()#.open_ports("*")

curr_ports = []
prev_ports = []
first_loop = True

lcd.display('Running', 1)
try:
    while True:
        #System info
        #print 'CPU: '+ str (psutil.cpu_percent(None)) + '%', 'MEM: ' + str(float(psutil.virtual_memory().percent)) + '%'

        if stopit:
            break
        curr_ports = rtmidi2.get_in_ports()
        #print curr_ports
        if (len(prev_ports) != len(curr_ports)):
            midi_in.close_ports()
            prev_ports = []
        for port in curr_ports:
            if port not in prev_ports and 'Midi Through' not in port and (len(prev_ports) != len(curr_ports)):
                midi_in.open_ports(port)
                midi_in.callback = midicallback.MidiCallback
                if first_loop:
                    print 'Opened MIDI port: ' + port
                else:
                    print 'Reopening MIDI port: ' + port
        prev_ports = curr_ports
        first_loop = False
        time.sleep(2)
except KeyboardInterrupt:
  print "\nstopped by ctrl-c\n"
except:
  print "Other Error"
finally:
    lcd.display('Stopped')
    sleep(0.5)
    if gvars.IS_DEBIAN:
        import RPi.GPIO as GPIO
        GPIO.cleanup()
