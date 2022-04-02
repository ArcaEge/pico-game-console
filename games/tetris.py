from machine import Pin, PWM
from utime import sleep, ticks_ms
from random import randrange
from color_setup import ssd as oled
from math import sqrt
import sys
import functions
import _thread
import gc

block_size = 8
game_width = block_size*10
next_block_area = 128-game_width
empty = oled.rgb(64,64,64)

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

tetrominos = [
     {"object":
      [[[1,1,1,1], # rotate=0
      [0,0,0,0],
      [0,0,0,0],
      [0,0,0,0]],
     [[1,0,0,0], # rotate=1
      [1,0,0,0],
      [1,0,0,0],
      [1,0,0,0]]],
      "color": oled.rgb(0, 240, 240)},
     {"object":
        [
         [[1,1,1,0], # rotate=0
          [1,0,0,0],
          [0,0,0,0],
          [0,0,0,0]],
         [[1,1,0,0], # rotate=1
          [0,1,0,0],
          [0,1,0,0],
          [0,0,0,0]],
         [[0,0,1,0], # rotate=2
          [1,1,1,0],
          [0,0,0,0],
          [0,0,0,0]],
         [[1,0,0,0], # rotate=3
          [1,0,0,0],
          [1,1,0,0],
          [0,0,0,0]]
        ],
      "color": oled.rgb(240, 160, 0)},
     {"object":
        [ # 3
         [[1,0,0,0], # rotate=0
          [1,1,1,0],
          [0,0,0,0],
          [0,0,0,0]],
         [[1,1,0,0], # rotate=1
          [1,0,0,0],
          [1,0,0,0],
          [0,0,0,0]],
         [[1,1,1,0], # rotate=2
          [0,0,1,0],
          [0,0,0,0],
          [0,0,0,0]],
         [[0,1,0,0], # rotate=3
          [0,1,0,0],
          [1,1,0,0],
          [0,0,0,0]]
        ],
      "color": oled.rgb(0, 0, 240)},
    [ # 4
     [[0,1,0,0], # rotate=0
      [1,1,1,0],
      [0,0,0,0],
      [0,0,0,0]],
     [[1,0,0,0], # rotate=1
      [1,1,0,0],
      [1,0,0,0],
      [0,0,0,0]],
     [[1,1,1,0], # rotate=2
      [0,1,0,0],
      [0,0,0,0],
      [0,0,0,0]],
     [[0,1,0,0], # rotate=3
      [1,1,0,0],
      [0,1,0,0],
      [0,0,0,0]],
    ],
    [ # 5
     [[0,1,1,0], # rotate=0
      [1,1,0,0],
      [0,0,0,0],
      [0,0,0,0]],
     [[1,0,0,0], # rotate=1
      [1,1,0,0],
      [0,1,0,0],
      [0,0,0,0]]
    ],
    [ #  6
     [[1,1,0,0], # rotate=0
      [0,1,1,0],
      [0,0,0,0],
      [0,0,0,0]],
     [[0,1,0,0], # rotate=1
      [1,1,0,0],
      [1,0,0,0],
      [0,0,0,0]]
    ],
    [ #  7
     [[1,1,0,0], # rotate=0
      [1,1,0,0],
      [0,0,0,0],
      [0,0,0,0]]
    ]
]

speaker = PWM(Pin(0))
functions.setSpeaker(speaker)

grid = []
unmerged = {"number": 1, "rotation": 0, "x": 5, "y": 2}

# for i in range(2):
#     functions.play_tune(tetris_tune)

def createGrid():
    for row in range(int(128/block_size)):
        grid.append([])
        for cell in range(game_width/block_size):
            grid[row].append(empty)

def drawWalls(show:bool = False):
    oled.rect(0, 0, game_width, 128, oled.rgb(128,128,128))
    if show:
        oled.show()

# def drawSquares(show:bool = False):
#     for row in range(int(128/block_size)):
#         start = row * block_size
#         for cell in range(game_width/block_size):
#             oled.fill_rect(cell * block_size + 1 , start + 1, block_size - 1, block_size - 1, oled.rgb(64,64,64))
#     if show:
#         oled.show()

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

createGrid()
# oled.text('NEXT', int(game_width + next_block_area/2-7*len("NEXT")/2), 20, 0xffff)
# drawWalls()
showSquares()
oled.show()
