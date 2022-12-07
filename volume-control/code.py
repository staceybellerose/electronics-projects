# SPDX-FileCopyrightText: © 2018 Kattni Rembor for Adafruit Industries
# SPDX-FileCopyrightText: © 2022 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

# Adafruit Rotary Trinkey Volume Control, NeoPixel Color Rotation,
#   and Capacitive Touch Brightness Control
#
# Get a Rotary Trinkey from Adafruit here: https://www.adafruit.com/product/4964
# Get a Rotary Encoder from Adafruit here: https://www.adafruit.com/product/377
# Get the Mu editor for Python here: https://codewith.mu/
# Download CircuitPython for this board here:
#   https://circuitpython.org/board/adafruit_rotary_trinkey_m0/

import time
import board
import usb_hid
import neopixel
import rotaryio
import digitalio
import touchio
import microcontroller
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from rainbowio import colorwheel

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.5)
encoder = rotaryio.IncrementalEncoder(board.ROTA, board.ROTB)
switch = digitalio.DigitalInOut(board.SWITCH)
switch.switch_to_input(pull=digitalio.Pull.DOWN)
touch = touchio.TouchIn(board.TOUCH)

cc = ConsumerControl(usb_hid.devices)

sleep_time = 0.1 # seconds to sleep between loops
cpu_output_cutoff = 20 # number of loops between output of cpu temperature
switch_state = None
last_position = encoder.position
color = 0
cap_forward = True
cpu_counter = 0

while True:
    # handle the rotary encoder
    current_position = encoder.position
    position_change = current_position - last_position
    if position_change > 0:
        for _ in range(position_change):
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        color += 2
    elif position_change < 0:
        for _ in range(-position_change):
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        color -= 2
    last_position = current_position
    color = (color + 256) % 256  # wrap around to 0-256
    pixel.fill(colorwheel(color))

    # handle the rotary switch
    if not switch.value and switch_state is None:
        switch_state = "pressed"
    if switch.value and switch_state == "pressed":
        cc.send(ConsumerControlCode.PLAY_PAUSE)
        switch_state = None

    # handle the capacitive touch pad
    if touch.value:
        if cap_forward:
            pixel.brightness = pixel.brightness + 0.1
        else:
            pixel.brightness = pixel.brightness - 0.1
        if pixel.brightness == 1:
            cap_forward = False
        if pixel.brightness == 0:
            cap_forward = True

    # output the CPU temperature to the serial console
    if cpu_counter == 0:
        print(microcontroller.cpu.temperature)
    cpu_counter = (cpu_counter + 1) % cpu_output_cutoff

    # sleep for a bit so serial console isn't flooded
    time.sleep(sleep_time)

