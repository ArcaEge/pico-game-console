from machine import Pin, PWM
from utime import sleep, ticks_ms
from random import randrange
from color_setup import ssd as oled
from math import sqrt
import sys
import functions
import _thread
import gc
from games.tetris.tetromino import *

oled.fill(0)
oled.show()

buttonRight = Pin(5, Pin.IN, Pin.PULL_UP)
buttonLeft = Pin(4, Pin.IN, Pin.PULL_UP)
buttonDown = Pin(3, Pin.IN, Pin.PULL_UP)
buttonUp = Pin(2, Pin.IN, Pin.PULL_UP)

block_size = 8
game_width = block_size*10
next_block_area = 128-game_width

tetris_tune = [[659, 0.5, 0], [493, 0.25, 0], [523, 0.25, 0], [587, 0.25, 0],
               [659, 0.125, 0], [587, 0.125, 0], [523, 0.25, 0], [493, 0.25, 0],
               [440, 0.4, 0.1], [440, 0.25, 0], [523, 0.25, 0], [659, 0.5, 0],
               [587, 0.25, 0], [523, 0.25, 0], [493, 0.75, 0], [523, 0.25, 0],
               [587, 0.5, 0], [659, 0.5, 0], [523, 0.5, 0], [440, 0.4, 0.1],
               [440, 1, 0],
               [146, 0.25, 0], [587, 0.5, 0], [698, 0.25, 0], [880, 0.5, 0],
               [783, 0.25, 0], [698, 0.25, 0], [656, 0.75, 0], [523, 0.25, 0],
               [656, 0.5, 0], [587, 0.25, 0], [523, 0.25, 0], [493, 0.4, 0.1],
               [493, 0.25, 0], [523, 0.25, 0], [587, 0.5, 0], [656, 0.5, 0],
               [523, 0.5, 0], [440, 0.4, 0.1], [440, 0.5, 0.5],
               [329, 1, 0], [261, 1, 0], [293, 1, 0], [246, 1, 0], [261, 1, 0],
               [220, 1, 0], [207, 1, 0], [246, 1, 0], [329, 1, 0], [261, 1, 0],
               [293, 1, 0], [246, 1, 0], [261, 0.5, 0], [329, 0.5, 0], [440, 1, 0],
               [415, 2, 0]]

speaker = PWM(Pin(0))
functions.setSpeaker(speaker)

# for i in range(2):
#     functions.play_tune(tetris_tune)

def drawWalls(show:bool = False):
    oled.rect(0, 0, game_width, 128, oled.rgb(128,128,128))
    if show:
        oled.show()

oled.text('NEXT', int(game_width + next_block_area/2-7*len("NEXT")/2), 20, 0xffff)
drawWalls()
oled.show()

block_1 = Tetromino_1(oled, 24, 0, block_size)

while True:
    sleep(0.5)
    block_1.move(y = block_1.y+block_size)
    block_1.rotate(block_1.rotation + 1 if block_1.rotation < 3 else 0)
    drawWalls()
    oled.show()
