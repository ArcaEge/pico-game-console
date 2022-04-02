# fpt.py Test/demo program for framebuf plot. Cross-patform,
# but requires a large enough display.
# Tested on Adafruit ssd1351-based OLED displays:
# Adafruit 1.5" 128*128 OLED display: https://www.adafruit.com/product/1431
# Adafruit 1.27" 128*96 display https://www.adafruit.com/product/1673

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2018-2020 Peter Hinch

# Initialise hardware and framebuf before importing modules.
from color_setup import ssd  # Create a display instance

import uos


from machine import Pin, PWM
from time import sleep
import functions
# from wavePlayer import wavePlayer
# player = wavePlayer()

# try:
#     player.play('intro.wav')
# except KeyboardInterrupt:
#     player.stop()

ssd.fill(0)
ssd.text('Loading...', 25, 60, 0xffff)
functions.border(ssd)
ssd.show()

test = Pin(2, Pin.IN, Pin.PULL_UP)
speaker = PWM(Pin(0))
speaker.duty_u16(1000)
speaker.freq(600)
sleep(.25)
speaker.freq(800)
sleep(.25)
speaker.freq(1200)
sleep(.25)
speaker.duty_u16(0)

try:
    if test.value() == False:
        exec(open('games/tetris/tetris.py').read())
    else:
        exec(open('games/snake.py').read())
except SystemExit:
    pass