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
import json
import _thread
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
pause = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)

ssd.fill(0)
ssd.text('Loading...', 25, 60, 0xffff)
functions.border(ssd)
ssd.show()

speaker = PWM(Pin(0))

f = open("settings.json", "r+b")

db = json.load(f)
volume = db["volume"]

f.close()

functions.setSpeaker(speaker)

speaker.duty_u16(volume)
speaker.freq(600)
sleep(.25)
speaker.freq(800)
sleep(.25)
speaker.freq(1200)
sleep(.25)
speaker.duty_u16(0)

games = [
    {"name": "Snake", "path": 'games/snake.py', "selected": True},
    {"name": "Tetris", "path": 'games/tetris.py', "selected": False},
    {"name": "Settings", "path": 'settings.py', "selected": False}
]

selected = 0

arrow = [
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0],
    [0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,0,1,1,0],
    [0,0,0,0,0,1,1,0,0],
    [0,0,0,0,1,1,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
]

def drawGames():
    for n,i in enumerate(games):
        if i["name"] == "Settings":
            ssd.text(i["name"], 12, 15+(n+1)*15, ssd.rgb(128,128,128))
            for y, row in enumerate(arrow):
                for x, c in enumerate(row):
                    if c:
                        ssd.pixel(x, y+14+(n+1)*15, ssd.rgb(128,128,128) if n == selected else 0)
            continue
        else:
            ssd.text(i["name"], 15, 15+(n+1)*15, ssd.rgb(255,255,255))
        for y, row in enumerate(arrow):
            for x, c in enumerate(row):
                if c:
                    ssd.pixel(x+3, y+14+(n+1)*15, ssd.rgb(255,255,255) if n == selected else 0)

while True:
    up = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
    down = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
    left = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
    right = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
    pause = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)
    try:
        ssd.fill(0)
        ssd.text("Games", 12, 15, ssd.rgb(32,32,255))
#         ssd.hline(6, 23, 39, ssd.rgb(64,64,255))
        drawGames()
        ssd.show()
        while True:
            if not up.value():
                while True:
                    if up.value():
                        selected -= 1 if selected > 0 else 0
                        drawGames()
                        ssd.show()
                        functions.changeDirection()
                        sleep(.1)
                        break
            if not down.value():
                while True:
                    if down.value():
                        selected += 1 if selected < len(games)-1 else 0
                        drawGames()
                        ssd.show()
                        functions.changeDirection()
                        sleep(.1)
                        break
            if not right.value():
                while True:
                    if right.value():
                        functions.changeDirection()
                        exec(open(games[selected]["path"]).read())
                        break
    except SystemExit:
        if not right.value():
                while True:
                    if right.value():
                        break
        ssd.fill(0)
        ssd.show()