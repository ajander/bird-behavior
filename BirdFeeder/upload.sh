#!/bin/bash

#upload
arduino-cli upload -p /dev/cu.SLAB_USBtoUART --fqbn esp8266:esp8266:huzzah /Users/adrienneanderson/bird-behavior/BirdFeeder

# start serial monitor - not needed, actually, since VSCode has a built in Serial Monitor (I guess? I never noticed it before)
arduino-cli monitor -p /dev/cu.usbserial-02856F70 -c baudrate=115200