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
pause = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)

f = open("settings.json", "r")
lines = f.read()
db = json.loads(lines)
# f.close()
# f = open("settings.json", "w+t")

speaker = PWM(Pin(0))
functions.setSpeaker(speaker)

arrow_right = [
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,1,1,1,0],
    [0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
]

arrow_left = [
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,1,0,0,0,0,0],
    [0,0,1,1,0,0,0,0,0],
    [0,1,1,1,0,0,0,0,0],
    [0,0,1,1,0,0,0,0,0],
    [0,0,0,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
]

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
total_rows = 3
volume_name_list = ["OFF", "1", "2", "3", "4", "5"]
volume_value_list = [0, 100, 250, 500, 1000, 30000]
volume_selected = volume_name_list[volume_value_list.index(db["volume"])]

def drawItems():
    global f
    oled.text("Volume", 15, 30, oled.rgb(255,255,255))
    oled.text(volume_selected, 73, 30, oled.rgb(255,255,255) if selected == 0 else oled.rgb(255,255,255))
    if selected == 0:
        if volume_selected != volume_name_list[0]:
            for y, row in enumerate(arrow_left):
                for x, c in enumerate(row):
                    if c:
                        oled.pixel(x+67, y+29, oled.rgb(128,128,128))
        if volume_selected != volume_name_list[-1]:
            for y, row in enumerate(arrow_right):
                for x, c in enumerate(row):
                    if c:
                        oled.pixel(x+62+(len(volume_selected)+1)*8, y+29, oled.rgb(128,128,128))
    
    oled.text("Reset High", 15, 45, oled.rgb(255,128,96))
    oled.text("Scores", 15, 57, oled.rgb(255,128,96))
    oled.text("Reset All", 15, 72, oled.rgb(255,48,32))
    
    for n in range(total_rows):
        if n == 0:
            color = oled.rgb(255,255,255)
            y_pos = 29
        elif n == 1:
            color = oled.rgb(255,128,96)
            y_pos = 44
        elif n == 2:
            color = oled.rgb(255,48,32)
            y_pos = 71
        for y, row in enumerate(arrow):
                for x, c in enumerate(row):
                    if c:
                        oled.pixel(x+3, y+y_pos, color if selected == n else 0)

def play_test_sound():
    functions.update_volume()
    try:
        _thread.start_new_thread(functions.coin, ())
    except (OSError, MemoryError):
        pass

oled.fill(0)
oled.text("Settings", 12, 15, oled.rgb(128,128,128))
drawItems()
oled.show()
while True:
    if not right.value():
        while True:
            if right.value():
                if selected == 0 and volume_selected != volume_name_list[-1]:
                    volume_selected = volume_name_list[volume_name_list.index(volume_selected)+1]
                    db["volume"] = volume_value_list[volume_name_list.index(volume_selected)]
                    oled.fill(0)
                    oled.text("Settings", 12, 15, oled.rgb(128,128,128))
                    drawItems()
                    oled.show()
                    with open('settings.json', 'w') as file:
                        file.write(json.dumps(db))
                    play_test_sound()
                    sleep(.2)
                elif selected == 1:
                    try:
                        exec(open("reset_high_scores.py").read())
                    except SystemExit:
                        reset()
                break
    if not left.value():
        while True:
            if left.value():
                if selected == 0 and volume_selected != volume_name_list[0]:
                    volume_selected = volume_name_list[volume_name_list.index(volume_selected)-1]
                    db["volume"] = volume_value_list[volume_name_list.index(volume_selected)]
                    oled.fill(0)
                    oled.text("Settings", 12, 15, oled.rgb(128,128,128))
                    drawItems()
                    oled.show()
                    with open('settings.json', 'w') as file:
                        file.write(json.dumps(db))
                    play_test_sound()
                    sleep(.2)
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
                drawItems()
                oled.show()
                functions.changeDirection()
                sleep(.1)
                break
    if not down.value():
        while True:
            if down.value():
                selected += 1 if selected < total_rows-1 else 0
                drawItems()
                oled.show()
                functions.changeDirection()
                sleep(.1)
                break
