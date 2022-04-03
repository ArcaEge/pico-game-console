from machine import Pin, PWM
from utime import sleep, ticks_ms
from random import randrange
from color_setup import ssd as oled
from math import sqrt
import sys
import functions
import _thread
import gc

multiplier = 10
block_size = 8
game_width = block_size*multiplier
next_block_area = 128-game_width
empty = oled.rgb(64,64,64)
game_height = None

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

buttonRight = Pin(5, Pin.IN, Pin.PULL_UP)
buttonLeft = Pin(4, Pin.IN, Pin.PULL_UP)
buttonDown = Pin(3, Pin.IN, Pin.PULL_UP)
buttonUp = Pin(2, Pin.IN, Pin.PULL_UP)

tetrominos = [
     {"object":
      [[[1,1,1,1], # rotate=0
      [0,0,0,0],
      [0,0,0,0],
      [0,0,0,0], 4],
     [[1,0,0,0], # rotate=1
      [1,0,0,0],
      [1,0,0,0],
      [1,0,0,0], 1]],
      "color": oled.rgb(0, 240, 240)},
     {"object":
        [
         [[1,1,1,0], # rotate=0
          [1,0,0,0],
          [0,0,0,0],
          [0,0,0,0], 3],
         [[1,1,0,0], # rotate=1
          [0,1,0,0],
          [0,1,0,0],
          [0,0,0,0], 2],
         [[0,0,1,0], # rotate=2
          [1,1,1,0],
          [0,0,0,0],
          [0,0,0,0], 3],
         [[1,0,0,0], # rotate=3
          [1,0,0,0],
          [1,1,0,0],
          [0,0,0,0], 2]
        ],
      "color": oled.rgb(240, 160, 0)},
     {"object":
        [ # 3
         [[1,0,0,0], # rotate=0
          [1,1,1,0],
          [0,0,0,0],
          [0,0,0,0], 3],
         [[1,1,0,0], # rotate=1
          [1,0,0,0],
          [1,0,0,0],
          [0,0,0,0], 2],
         [[1,1,1,0], # rotate=2
          [0,0,1,0],
          [0,0,0,0],
          [0,0,0,0], 3],
         [[0,1,0,0], # rotate=3
          [0,1,0,0],
          [1,1,0,0],
          [0,0,0,0], 2]
        ],
      "color": oled.rgb(0, 0, 240)},
     {"object":
        [ # 4
         [[0,1,0,0], # rotate=0
          [1,1,1,0],
          [0,0,0,0],
          [0,0,0,0], 3],
         [[1,0,0,0], # rotate=1
          [1,1,0,0],
          [1,0,0,0],
          [0,0,0,0], 2],
         [[1,1,1,0], # rotate=2
          [0,1,0,0],
          [0,0,0,0],
          [0,0,0,0], 3],
         [[0,1,0,0], # rotate=3
          [1,1,0,0],
          [0,1,0,0],
          [0,0,0,0], 2],
        ],
      "color": oled.rgb(160, 0, 240)},
     {"object":
        [ # 5
         [[0,1,1,0], # rotate=0
          [1,1,0,0],
          [0,0,0,0],
          [0,0,0,0], 3],
         [[1,0,0,0], # rotate=1
          [1,1,0,0],
          [0,1,0,0],
          [0,0,0,0], 2]
        ],
      "color": oled.rgb(0, 240, 0)},
     {"object":
        [ #  6
         [[1,1,0,0], # rotate=0
          [0,1,1,0],
          [0,0,0,0],
          [0,0,0,0], 3],
         [[0,1,0,0], # rotate=1
          [1,1,0,0],
          [1,0,0,0],
          [0,0,0,0], 2]
        ],
      "color": oled.rgb(240, 0, 0)},
     {"object":
        [ #  7
         [[1,1,0,0], # rotate=0
          [1,1,0,0],
          [0,0,0,0],
          [0,0,0,0], 2]
        ],
      "color": oled.rgb(240, 240, 0)},
]

speaker = PWM(Pin(0))
functions.setSpeaker(speaker)

grid = []
unmerged = {"number": 0, "rotation": 0, "x": 1, "y": 13}
next = None

# for i in range(2):
#     functions.play_tune(tetris_tune)

def createGrid():
    global game_height
    for row in range(int(128/block_size)):
        grid.append([])
        for cell in range(multiplier):
            grid[row].append(empty)
    game_height = len(grid)

def drawWalls(show:bool = False):
    oled.rect(0, 0, game_width, 128, oled.rgb(128,128,128))
    if show:
        oled.show()

def showSquares(show:bool = False, showUnmerged:bool=True):
    for row in range(int(128/block_size)):
        start = row * block_size
        for cell in range(game_width/block_size):
            oled.fill_rect(cell * block_size + 1 , start + 1, block_size - 1, block_size - 1, grid[row][cell])
    if showUnmerged:
        tetrominoObject = tetrominos[unmerged["number"]]["object"][unmerged["rotation"]]
        color = tetrominos[unmerged["number"]]["color"]
        for row in range(4):
            for cell in range(4):
                if tetrominoObject[row][cell] == 1:
                    oled.fill_rect((unmerged["x"] + cell) * block_size + 1 , (unmerged["y"] + row) * block_size + 1, block_size - 1, block_size - 1, color)
    if show:
        oled.show()

def mergeTetromino(tetromino:int=unmerged["number"], rotation:int=unmerged["rotation"], gridX:int=unmerged["x"], gridY:int=unmerged["y"]):
    tetrominoObject = tetrominos[tetromino]["object"][rotation]
    color = tetrominos[tetromino]["color"]
    for row in range(4):
        for cell in range(4):
            if tetrominoObject[row][cell] == 1:
                grid[gridY+row][gridX+cell] = color

def shiftLeft():
    isEmpty = True
    tetrominoObject = tetrominos[unmerged["number"]]["object"][unmerged["rotation"]]
    for row in range(4):
        for cell in range(4):
            if tetrominoObject[row][cell] == 1:
                try:
                    if grid[unmerged["y"]+row][unmerged["x"]+cell-1] != empty or unmerged["x"]+cell-1 < 0:
                        isEmpty = False
                except IndexError:
                    isEmpty = False
    if isEmpty:
        unmerged["x"] -= 1

def shiftRight():
    isEmpty = True
    tetrominoObject = tetrominos[unmerged["number"]]["object"][unmerged["rotation"]]
    for row in range(4):
        for cell in range(4):
            if tetrominoObject[row][cell] == 1:
                try:
                    if grid[unmerged["y"]+row][unmerged["x"]+cell+1] != empty or unmerged["x"]+cell+1 > multiplier:
                        isEmpty = False
                except IndexError:
                    isEmpty = False
    if isEmpty:
        unmerged["x"] += 1

def shiftDown():
    isEmpty = True
    tetrominoObject = tetrominos[unmerged["number"]]["object"][unmerged["rotation"]]
    for row in range(4):
        for cell in range(4):
            if tetrominoObject[row][cell] == 1:
                try:
                    if grid[unmerged["y"]+row+1][unmerged["x"]+cell] != empty or unmerged["y"]+cell+1 > game_height:
                        isEmpty = False
                except IndexError:
                    isEmpty = False
    if isEmpty:
        unmerged["y"] += 1
    return isEmpty

def rotate():
    isEmpty = True
    tetrominoObject = tetrominos[unmerged["number"]]["object"][unmerged["rotation"]]
    nextRotation = unmerged["rotation"] + 1 if unmerged["rotation"] < len(tetrominos[unmerged["number"]]["object"]) - 1 else 0
    rotatedObject = tetrominos[unmerged["number"]]["object"][nextRotation] 
    for row in range(4):
        for cell in range(4):
            if rotatedObject[row][cell] == 1:
                try:
                    if grid[unmerged["y"]+row][unmerged["x"]+cell] != empty:
                        isEmpty = False
                except IndexError:
                    isEmpty = False
    if isEmpty:
        unmerged["rotation"] = nextRotation
    return isEmpty

createGrid()
# oled.text('NEXT', int(game_width + next_block_area/2-7*len("NEXT")/2), 20, 0xffff)
mergeTetromino(0, 1, 5, 12)
showSquares()
oled.show()

sleep(1)

rotate()
showSquares()
oled.show()

sleep(1)

rotate()
showSquares()
oled.show()

sleep(1)

rotate()
showSquares()
oled.show()

sleep(1)

rotate()
showSquares()
oled.show()