from color_setup import ssd as oled
from machine import Pin, PWM
from time import sleep
import functions
import json
import _thread
import sys

up = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
down = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
left = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
right = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
pause = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)

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
selectedGames = []

def drawItems():
    oled.text("Reset High", 12, 15, oled.rgb(255,128,96))
    oled.text("Scores?", 12, 27, oled.rgb(255,128,96))
#     functions.border(oled, oled.rgb(128,64,32))
    oled.text("[ ] Snake:  " + str(db["highScores"]["snake"]), 0, 45, oled.rgb(255,255,255))
    oled.text("[ ] Tetris: " + str(db["highScores"]["tetris"]), 0, 60, oled.rgb(255,255,255))
    oled.text("Reset Selected", 15, 75, oled.rgb(255,48,32))
    for i in selectedGames:
        if i == "snake":
            oled.text("*", 8, 45, oled.rgb(255,255,255) if selected == 0 else oled.rgb(128,128,128))
        elif i == "tetris":
            oled.text("*", 8, 60, oled.rgb(255,255,255) if selected == 1 else oled.rgb(128,128,128))
    if (selected == 0 and not any(elem == "snake" for elem in selectedGames)) or (selected == 1 and not any(elem == "tetris" for elem in selectedGames)):
        oled.text("*", 8, selected*15+45, oled.rgb(255,128,128))
    elif selected == 2:
        for y, row in enumerate(arrow):
            for x, c in enumerate(row):
                if c:
                    oled.pixel(x+3, y+74, oled.rgb(255,48,32))

oled.fill(0)
drawItems()
oled.show()
while True:
    if not right.value():
        while True:
            if right.value():
                if selected == 0:
                    if any(elem == "snake" for elem in selectedGames):
                        selectedGames.remove("snake")
                    else:
                        selectedGames.append("snake")
                    drawItems()
                    oled.show()
                elif selected == 1:
                    if any(elem == "tetris" for elem in selectedGames):
                        selectedGames.remove("tetris")
                    else:
                        selectedGames.append("tetris")
                    drawItems()
                    oled.show()
                elif selected == 2:
                    forloopran = False
                    for i in selectedGames:
                        db["highScores"][i] = 0
                        forloopran = True
                    if forloopran:
                        with open('settings.json', 'w') as file:
                            file.write(json.dumps(db))
                    f.close()
                    sys.exit()
                functions.changeDirection()
                break
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