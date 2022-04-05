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

up = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
down = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
left = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
right = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)

ssd.fill(0)
ssd.text('GameBoi', 32, 48, 0xffff)
ssd.text('Loading...', 25, 60, 0xffff)
functions.border(ssd)
ssd.show()

speaker = PWM(Pin(0))
speaker.duty_u16(1000)
speaker.freq(600)
sleep(.25)
speaker.freq(800)
sleep(.25)
speaker.freq(1200)
sleep(.25)
speaker.duty_u16(0)

games = [
    {"name": "Snake", "path": 'games/snake.py', "selected": True},
    {"name": "Tetris", "path": 'games/tetris.py', "selected": False}
]

selected = 0

def drawGames():
    for n,i in enumerate(games):
            ssd.text(i["name"], 10, 15+(n+1)*15, ssd.rgb(255,64,64) if selected == n else ssd.rgb(255,255,255))

while True:
    up = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
    down = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
    left = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
    right = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
    try:
        ssd.fill(0)
        ssd.text("GameBoi", 5, 15, ssd.rgb(64,64,255))
        ssd.hline(6, 23, 53, ssd.rgb(64,64,255))
        drawGames()
        ssd.show()
        while True:
            if not up.value():
                while True:
                    if up.value():
                        selected -= 1 if selected > 0 else 0
                        drawGames()
                        ssd.show()
                        break
            if not down.value():
                while True:
                    if down.value():
                        selected += 1 if selected < len(games)-1 else 0
                        drawGames()
                        ssd.show()
                        break
            if not right.value():
                while True:
                    if right.value():
                        exec(open(games[selected]["path"]).read())
                        break
    except SystemExit:
        if not right.value():
                while True:
                    if right.value():
                        break
        ssd.fill(0)
        ssd.show()