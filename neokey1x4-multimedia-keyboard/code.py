"""
Requires multiple libraries from the Adafruit CircuitPython Library Bundle.
Download the bundle from circuitpython.org/libraries and copy the
following files or folders to your CIRCUITPY/lib folder:

* neopixel.mpy
* adafruit_hid/
* adafruit_neokey/
* adafruit_seesaw/

Once the libraries are copied, save this file as code.py to your CIRCUITPY
drive to run it.
"""

import time
import board
import neopixel
import busio
import usb_hid
from rainbowio import colorwheel
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# use STEMMA I2C bus
i2c_bus = board.STEMMA_I2C()

# Create a NeoKey object
neokey = NeoKey1x4(i2c_bus, addr=0x30)

# create a consumer control object
cc = ConsumerControl(usb_hid.devices)

#  states for key presses
key_count = len(neokey.pixels)
key_states = [False] * key_count
keypress_color = 0xFF00FF

# controller board's NeoPixel
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.2
hue = 0

# Keycodes to send on keypresses
keycodes = [
    [], # used as a shift key for the other three neokeys
    [ConsumerControlCode.SCAN_PREVIOUS_TRACK],
    [ConsumerControlCode.PLAY_PAUSE],
    [ConsumerControlCode.SCAN_NEXT_TRACK]
]
keycodes_shifted = [
    [],
    [ConsumerControlCode.MUTE],
    [ConsumerControlCode.VOLUME_DECREMENT],
    [ConsumerControlCode.VOLUME_INCREMENT]
]

# Reset a NeoKey: switch debouncing, and turn off NeoPixel on release
def reset_key(keynum):
    if not neokey[keynum] and key_states[keynum]:
        neokey.pixels[keynum] = 0x0
        key_states[keynum] = False

# Handle a NeoKey keypress
def handle_keypress(keynum):
    if neokey[keynum] and not key_states[keynum]:
        print("Button ", keynum)
        #  turn on NeoPixel
        neokey.pixels[keynum] = keypress_color
        #  send key presses for codes
        if keynum != 0:
            if key_states[0]:
                print("Shifted")
                for i in keycodes_shifted[keynum]:
                    cc.send(i)
                    time.sleep(0.05)
            else:
                for i in keycodes[keynum]:
                    cc.send(i)
                    time.sleep(0.05)
        #  update key state
        key_states[keynum] = True

while True:
    # rotate the color of the controller board's NeoPixel
    pixel[0] = colorwheel(hue)
    pixel.show()
    hue = (hue + 2) % 256

    # reset the neokeys
    for i in range(key_count):
        reset_key(i)

    # if neokey is pressed, handle it
    for i in range(key_count):
        handle_keypress(i)
