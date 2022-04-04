from machine import Pin, PWM, Timer
from utime import sleep, ticks_ms
from primitives import Pushbutton
from random import randrange
from color_setup import ssd as oled
from math import sqrt, floor
import sys
import functions
import _thread
import gc
import uasyncio as asyncio

multiplier = 10
block_size = 8
game_width = block_size*multiplier
next_block_area = 128-game_width
empty = oled.rgb(64,64,64)
empty_row = []
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

Pushbutton.long_press_ms=250

pbRight = Pushbutton(buttonRight)
pbLeft = Pushbutton(buttonLeft)
pbDown = Pushbutton(buttonDown)
pbUp = Pushbutton(buttonUp)

tetrominos = [
     {"object":
      [[[1,1,1,1], # rotate=0
      [2,2,2,2],
      [2,2,2,0],
      [2,2,0,0], 4],
     [[1,2,2,2], # rotate=1
      [1,2,2,2],
      [1,2,2,0],
      [1,2,0,0], 1]],
      "color": oled.rgb(0, 240, 240)},
     {"object":
        [
         [[1,1,1,0], # rotate=0
          [1,2,2,0],
          [0,2,2,0],
          [0,0,0,0], 3],
         [[1,1,2,0], # rotate=1
          [2,1,2,0],
          [2,1,2,0],
          [0,0,0,0], 2],
         [[2,2,1,0], # rotate=2
          [1,1,1,0],
          [2,2,2,0],
          [0,0,0,0], 3],
         [[1,2,2,0], # rotate=3
          [1,2,2,0],
          [1,1,2,0],
          [0,0,0,0], 2]
        ],
      "color": oled.rgb(240, 160, 0)},
     {"object":
        [ # 3
         [[1,2,0,0], # rotate=0
          [1,1,1,0],
          [2,2,2,0],
          [0,0,0,0], 3],
         [[1,1,2,0], # rotate=1
          [1,2,2,0],
          [1,2,0,0],
          [0,0,0,0], 2],
         [[1,1,1,0], # rotate=2
          [2,2,1,0],
          [2,2,2,0],
          [0,0,0,0], 3],
         [[2,1,2,0], # rotate=3
          [2,1,2,0],
          [1,1,0,0],
          [0,0,0,0], 2]
        ],
      "color": oled.rgb(0, 0, 240)},
     {"object":
        [ # 4
         [[2,1,2,0], # rotate=0
          [1,1,1,0],
          [2,2,2,0],
          [0,0,0,0], 3],
         [[1,2,2,0], # rotate=1
          [1,1,0,0],
          [1,0,0,0],
          [0,0,0,0], 2],
         [[1,1,1,0], # rotate=2
          [2,1,2,0],
          [2,2,2,0],
          [0,0,0,0], 3],
         [[2,1,2,0], # rotate=3
          [1,1,2,0],
          [2,1,0,0],
          [0,0,0,0], 2],
        ],
      "color": oled.rgb(160, 0, 240)},
     {"object":
        [ # 5
         [[0,1,1,0], # rotate=0
          [1,1,2,0],
          [2,2,2,0],
          [0,0,0,0], 3],
         [[1,2,2,0], # rotate=1
          [1,1,0,0],
          [2,1,0,0],
          [0,0,0,0], 2]
        ],
      "color": oled.rgb(0, 240, 0)},
     {"object":
        [ #  6
         [[1,1,0,0], # rotate=0
          [2,1,1,0],
          [2,2,2,0],
          [0,0,0,0], 3],
         [[0,1,0,0], # rotate=1
          [1,1,2,0],
          [1,2,0,0],
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
temp_random = int(randrange(0,13)/2)
unmerged = {"number": temp_random, "rotation": 0, "x": floor(multiplier/2) - floor(tetrominos[temp_random]["object"][0][-1]/2), "y": -1}
del temp_random
next = int(randrange(0,7))
score = 0
delay = .8

# for i in range(2):
#     functions.play_tune(tetris_tune)

def createGrid():
    global game_height
    for row in range(int(128/block_size)):
        grid.append([])
        for cell in range(multiplier):
            grid[row].append(empty)
    game_height = len(grid)
    global empty_row
    for i in range(multiplier):
        empty_row.append(empty)

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

def shiftLeft(*args):
    if unmerged["y"] <= -1: return
    isEmpty = True
    tetrominoObject = tetrominos[unmerged["number"]]["object"][unmerged["rotation"]]
    for row in range(4):
        for cell in range(4):
            if tetrominoObject[row][cell] == 1:
                try:
                    if grid[unmerged["y"]+row][unmerged["x"]+cell-1] != empty or unmerged["x"]+cell-1 < 0:
                        isEmpty = False
                        break
                except IndexError:
                    isEmpty = False
                    break
    if isEmpty:
        unmerged["x"] -= 1
        render()

def shiftRight(*args):
    if unmerged["y"] <= -1: return
    isEmpty = True
    tetrominoObject = tetrominos[unmerged["number"]]["object"][unmerged["rotation"]]
    for row in range(4):
        for cell in range(4):
            if tetrominoObject[row][cell] == 1:
                try:
                    if grid[unmerged["y"]+row][unmerged["x"]+cell+1] != empty or unmerged["x"]+cell+1 > multiplier:
                        isEmpty = False
                        break
                except IndexError:
                    isEmpty = False
                    break
    if isEmpty:
        unmerged["x"] += 1
        render()

def shiftDown(*args, renderResult:bool=True):
    isEmpty = True
    tetrominoObject = tetrominos[unmerged["number"]]["object"][unmerged["rotation"]]
    for row in range(4):
        for cell in range(4):
            if tetrominoObject[row][cell] == 1:
                try:
                    if grid[unmerged["y"]+row+1][unmerged["x"]+cell] != empty or unmerged["y"]+row+1 > game_height:
                        isEmpty = False
                        break
                except IndexError:
                    isEmpty = False
                    break
    if unmerged["y"] <= 0 and not isEmpty:
        return [isEmpty, True]
    if isEmpty:
        unmerged["y"] += 1
        if renderResult:
            render()
    return [isEmpty, False]

def rotate(*args):
    if unmerged["y"] <= -1: return False
    isEmpty = True
    tetrominoObject = tetrominos[unmerged["number"]]["object"][unmerged["rotation"]]
    nextRotation = unmerged["rotation"] + 1 if unmerged["rotation"] < len(tetrominos[unmerged["number"]]["object"]) - 1 else 0
    rotatedObject = tetrominos[unmerged["number"]]["object"][nextRotation] 
    for row in range(4):
        for cell in range(4):
            if rotatedObject[row][cell] == 1 or tetrominoObject[row][cell] == 2:
                try:
                    if grid[unmerged["y"]+row][unmerged["x"]+cell] != empty:
                        isEmpty = False
                        break
                except IndexError:
                    isEmpty = False
                    break
    if isEmpty:
        unmerged["rotation"] = nextRotation
        render()
    return isEmpty

def render(*args):
    showSquares()
    oled.show()

timer = Timer(-1)

def timerRight():
    global timer
    timer.init(period=100, callback=shiftRight)

def timerLeft():
    global timer
    timer.init(period=100, callback=shiftLeft)

def timerUp():
    global timer
    timer.init(period=100, callback=rotate)

def down():
    if unmerged["y"] <= -1: return False
    while True:
        result, gameOver = shiftDown(renderResult=False)
        if not result:
            break
    render()

def spawnTetromino(merge:bool=True):
    global unmerged, multiplier, tetrominos, next
    if merge:
        mergeTetromino(tetromino=unmerged["number"], rotation=unmerged["rotation"], gridX=unmerged["x"], gridY=unmerged["y"])
    unmerged["number"] = next
    unmerged["rotation"] = 0
    unmerged["x"] = floor(multiplier/2) - floor(tetrominos[next]["object"][0][-1]/2)
    unmerged["y"] = -1
    next = int(randrange(0,13)/2)
    drawNext()

def circle(x,y,r,c):
  oled.hline(round(x-r),y,round(r*2),c)
  for i in range(1,r):
    a = round(sqrt(r*r-i*i)) # Pythagoras!
    oled.hline(x-a,y+i,a*2,c) # Lower half
    oled.hline(x-a,y-i,a*2,c) # Upper half

def drawNext():
    oled.fill_rect(game_width+1, 28, 60, 40, 0)
    tetrominoObject = tetrominos[next]["object"][0]
    color = tetrominos[next]["color"]
    for row in range(4):
        for cell in range(4):
            if tetrominoObject[row][cell] == 1:
                oled.fill_rect((game_width + int((next_block_area-tetrominoObject[-1]*block_size)/2) + cell) + block_size*cell+1, (5 + row) * block_size - 8, block_size, block_size - 1, color)

def drawScore():
    global score, game_width, next_block_area
    oled.fill_rect(game_width + 1, 110, next_block_area, 9, 0)
    oled.text(str(score), int(game_width + next_block_area/2-7*len(str(score))/2), 112, 0xffff)

def null_func(*args, **kwargs):
    pass

async def main():
    global empty_list, score, delay, grid, block_size
    break_loop = False
    while True:
        if break_loop: break
        oled.fill(0)
        createGrid()
        oled.text('NEXT', int(game_width + next_block_area/2-7*len("NEXT")/2), 20, 0xffff)
        oled.text('SCORE', int(game_width + next_block_area/2-7*len("SCORE")/2), 100, 0xffff)
        drawNext()
        drawScore()
        render()
        pbRight.press_func(shiftRight, ())
        pbLeft.press_func(shiftLeft, ())
        pbDown.press_func(down, ())
        pbUp.press_func(rotate, ())
        
        pbRight.long_func(timerRight, ())
        pbLeft.long_func(timerLeft, ())
        pbUp.long_func(timerUp, ())
        
        pbRight.release_func(timer.deinit, ())
        pbLeft.release_func(timer.deinit, ())
        pbUp.release_func(timer.deinit, ())
        
        isNotStopped = True
        gameOver = False
        speed = .8
        
        while True:
            [isNotStopped, gameOver] = shiftDown()
            if gameOver:
                break
            if not isNotStopped:
                spawnTetromino()
                fullRows = 0
                for row in range(int(128/block_size)):
                    rowFull = True
                    for cell in range(game_width/block_size):
                        if grid[row][cell] == empty:
                            rowFull = False
                            break
                    if rowFull:
                        grid.pop(row)
                        grid.insert(0,empty_row)
                        fullRows += 1
                        delay -= .02 if delay > 0.35 else 0
                if fullRows > 0:
                    score += 1 if fullRows == 1 else fullRows * 2
                    drawScore()
                render()
                isNotStopped = True
            await asyncio.sleep(delay)
        
        hOffset = int((128 - 7*len("GAME OVER"))/2)
        oled.fill(0)
        oled.text("GAME OVER", hOffset, int((128/2) - 6), oled.rgb(255,255,255))
        hOffset = int((128 - 7*len("SCORE: " + str(score)))/2)
        oled.text("SCORE: " + str(score), hOffset, int((128/2) + 6), oled.rgb(255,255,255))
        circle(34,103,5,oled.rgb(255,255,0))
        oled.text("CONTINUE", 42, 100, oled.rgb(255,255,255))
        hOffset = int((128 - 7*len(" QUIT" + str(score)))/2)
        circle(43,115,5,oled.rgb(255,0,0))
        oled.text(" QUIT", hOffset, 112, oled.rgb(255,255,255))
        oled.show()
        grid = []
        temp_random = int(randrange(0,13)/2)
        unmerged = {"number": temp_random, "rotation": 0, "x": floor(multiplier/2) - floor(tetrominos[temp_random]["object"][0][-1]/2), "y": -1}
        del temp_random
        next = int(randrange(0,7))
        score = 0
        pbRight.press_func(null_func, ())
        pbLeft.press_func(null_func, ())
        pbDown.press_func(null_func, ())
        pbUp.press_func(null_func, ())
        
        pbRight.long_func(null_func, ())
        pbLeft.long_func(null_func, ())
        pbUp.long_func(null_func, ())
        
        pbRight.release_func(null_func, ())
        pbLeft.release_func(null_func, ())
        pbUp.release_func(null_func, ())
        
        while True:
            if not buttonUp.value():
                break
            elif not buttonRight.value():
                asyncio.new_event_loop()
                sys.exit()

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()