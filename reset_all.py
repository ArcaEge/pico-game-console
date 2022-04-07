from color_setup import ssd as oled
from machine import Pin, PWM, reset
from time import sleep
import functions
import json
import _thread
import sys

up = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
down = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
left = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
right = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
pause = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_UP)

f = open("settings.json", "r")
lines = f.read()
db = json.loads(lines)
# f.close()
# f = open("settings.json", "w+t")

speaker = PWM(Pin(0))
functions.setSpeaker(speaker)

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

selected = 0

def drawItems():
    oled.text("Reset All?", 12, 15, oled.rgb(255,48,32))
#     functions.border(oled, oled.rgb(128,64,32))
    oled.text("Cancel", 15, 30, oled.rgb(255,255,255))
    oled.text("Reset", 15, 45, oled.rgb(255,48,32))
    for n in range(2):
        if n == 0:
            color = oled.rgb(255,255,255)
            y_pos = 29
        elif n == 1:
            color = oled.rgb(255,48,32)
            y_pos = 44
        for y, row in enumerate(arrow):
            for x, c in enumerate(row):
                if c:
                    oled.pixel(x+3, y+y_pos, color if selected == n else 0)

oled.fill(0)
drawItems()
oled.show()
while True:
    if not right.value():
        while True:
            if right.value():
                functions.changeDirection()
                if selected == 0:
                    reset()
                    oled.show()
                elif selected == 1:
                    db = {"highScores": {"tetris": 0, "snake": 0}, "volume": 30000}
                    with open('settings.json', 'w') as file:
                        file.write(json.dumps(db))
                    reset()
                    oled.show()
    if not pause.value():
        while True:
            if pause.value():
                functions.changeDirection()
                f.close()
                sys.exit()
    if not up.value():
        while True:
            if up.value():
                selected -= 1 if selected > 0 else 0
                oled.fill(0)
                drawItems()
                oled.show()
                functions.changeDirection()
                sleep(.1)
                break
    if not down.value():
        while True:
            if down.value():
                selected += 1 if selected < 2 else 0
                oled.fill(0)
                drawItems()
                oled.show()
                functions.changeDirection()
                sleep(.1)
                break
