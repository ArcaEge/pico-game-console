from machine import Pin, PWM, Timer
from utime import sleep, ticks_ms
from random import randrange
from color_setup import ssd as oled
from math import sqrt
import sys
import functions
import _thread
import gc
import json

# up = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
# down = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
# left = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
# right = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)

speaker = PWM(Pin(0))
functions.setSpeaker(speaker)

oled.fill(0)

snake = []
scale = 1
spd = 0.2 #0.05
originalSpd = spd
score = 0
buttonSpdScale = 10
WIDTH,HEIGHT = 128, 128
border=1
gameWidth = int(WIDTH/3/scale)
gameHeight =int(HEIGHT/3/scale)
arenaWidth=gameWidth*3*scale
arenaHeight=gameHeight*3*scale
isDead = False
startWasPressed = False
pause = False
direction = "left"
gameOver = False

f = open("settings.json", "r+b")

db = json.load(f)
high_score = db["highScores"]["snake"]

f.close()

gc.threshold(4096)

#=== SPRITES ===
# ..XX  ...X  XX..  X...  .XX.
# .X..  ...X  ..X.  X...  X..X
# X...  ..X.  ...X  .X..  X..X
# X...  XX..  ...X  ..XX  .XX.
# a     b     c     d      
a = [(0,0),(0,1),(1,2),(2,3),(3,3)]
b = [(0,0),(1,0),(2,1),(3,2),(3,3)]
c = [(3,0),(3,1),(2,2),(1,3),(0,3)]
d = [(3,0),(2,0),(1,1),(0,2),(0,3)]
#apple = [(),(),(),(),(),(),(),]

lrSeq = "c-=a-=b--d--c-=" #Left to Right (positive direction curve down first)
rlSeq = "d=-b=-a==c==d=-" #Left to Right (NEGATIVE direction curve down first)
duSeq = "c=-b=-a--d--c=-" #Bottom to top (positive direction curve left first)
udSeq = "d-=a-=b==c==d-=" #Bottom to top (NEGATIVE direction curve left first)

turnTable = {
# Left to right
"a+==+": "a", # a smooth, c backtracks
"a+==-": "d", # was d, b continues but with gap, d backtracks but no gap.
"b+==+": "d", # d tight, alternatively b if larger radius desired.
"b+==-": "c", # a loops, c is tight turn
"c+==+": "b", # b is tight turn
"c+==-": "a", # a is tight turn
"d+==+": "c", # c is continuing curve but with gap, a backtracks
"d+==-": "d", # d is larger arc, b backtracks

# Right to left
"a-==+": "d", # d tight, b loops
"a-==-": "c", # c tight, a larger arc
"b-==+": "a", # a continues but gap, c backtracks
"b-==-": "b", # d backtracks, b larger arc
"c-==+": "c", # a backtracks, c larger arc
"c-==-": "d", # b backtracks, d continues with gap
"d-==+": "a", # a tight, c larger arc
"d-==-": "a", # a tight turn, c bad coil

# Up
"a=++=": "d", # d tight, a big arc
"a=+-=": "c", # b loops, c tight
"b=++=": "b", # b big arc, c backtracks
"b=+-=": "a", # d backtracks, a continue with break
"c=++=": "a", # a tight, d loops
"c=+-=": "b", # c big arc, b tight
"d=++=": "c", # c continue with break, b backtracks
"d=+-=": "d", # d big arc, a backtracks

# Down
"a=-+=": "c", # b continue with gap, c backtracks
"a=--=": "d", # a big arc, d backtracks
"b=-+=": "d", # d tight, a loops
"b=--=": "c", # b big arc, c tight
"c=-+=": "b", # b backtracks, c big loop
"c=--=": "d", # d continue with gap, a backtracks
"d=-+=": "a", # d big arc, a tight
"d=--=": "b" # b tight, c loops
}


def plot(x,y,sprite,isDraw):
    for p in sprite:
        oled.rect(border+x*3*scale+p[0]*scale,border+127-y*3*scale-p[1]*scale, scale,scale, oled.rgb(0,255,0) if isDraw else 0)
        
def draw(c,r,a):
    plot(c,r,a,True)

def erase(c,r,a):
    plot(c,r,a,False)

def toSprite(spriteName):
    sprite = d
    if spriteName=='a': sprite = a
    if spriteName=='b': sprite = b
    if spriteName=='c': sprite = c
    return sprite

def circle(x,y,r,c):
  oled.hline(round(x-r),y,round(r*2),c)
  for i in range(1,r):
    a = round(sqrt(r*r-i*i)) # Pythagoras!
    oled.hline(x-a,y+i,a*2,c) # Lower half
    oled.hline(x-a,y-i,a*2,c) # Upper half
#   oled.display()
#     sleep(0.1)

def toOffset(offsetSymbol):
    result = 0
    if offsetSymbol=='-': result = -1
    if offsetSymbol=='+': result = +1
    return result

def fromOffset(dx,dy):
    sym = "-=+"
    return sym[dx+1] + sym[dy+1]

def deltaToSeq(dx,dy):
    if dx==1: seq = lrSeq
    if dx==-1: seq = rlSeq
    if dy==1: seq = duSeq
    if dy==-1: seq = udSeq
    return seq
    
def toCode(spriteName, dx,dy):
    seq = deltaToSeq(dx,dy)
    pos = seq.find(spriteName)
    return seq[pos:pos+3]
    
def initSnakeLR(x,y):
    global snake, dx, dy
    dx,dy=+1,0
    snake = []

    for i in range(4): # Go backward so the rightmost is head.
        j = i*3
        code = lrSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        x -= 1
    
def initSnakeRL(x,y):
    global snake, dx, dy
    dx,dy=-1,0
    snake = []
    for i in range(4): # Go backward so the leftmost is head.
        j = i*3
        code = rlSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        x += 1

def initSnakeUp(x,y):
    global snake, dx, dy
    dx,dy=0,+1
    snake = []
    for i in range(4): # Go Downward so the bottom most is head.
        j = i*3
        code = duSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        y -= 1

def initSnakeDown(x,y):
    global snake, dx, dy
    dx,dy=0,-1
    snake = []
    for i in range(4): # Go upward so the topmost is head.
        j = i*3
        code = udSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        y += 1

def plotSeg(x,y, segCode, isDraw): # segCode is like d--, x,y is virtual position before offsets
    spriteName = segCode[0] # grab the sprite name (ie d)
    sprite = toSprite(spriteName)
    x += toOffset(segCode[1])
    y += toOffset(segCode[2])
    plot( x, y, sprite, isDraw )

def drawSeg(x,y, segCode):
    plotSeg(x,y, segCode, True)

def eraseSeg(x,y, segCode):
    plotSeg(x,y, segCode, False)

def drawSnake():
    for s in snake:
        # each s is virtual x,y position followed by the segCode
        drawSeg(s[0], s[1], s[2])
    oled.show()

def ChopTail():
    global snake
    #-- Remove tail --
    tailIndex = len(snake)-1
    tail = snake[tailIndex] # d--, x, y
    eraseSeg(tail[0],tail[1], tail[2])
    snake.pop(tailIndex)
    
def CheckWalls():
    global isDead
    head = snake[0]
    headX, headY = head[0],head[1]
    if headX<=0: isDead=True
    if headY<=1: isDead=True
    if headX>=gameWidth: isDead=True
    if headY>=43: isDead=True

def DrawWalls():
    oled.rect(0,0,arenaWidth+2, arenaHeight+1, oled.rgb(128,128,128)) #OLED height is 1 pixel too short :-(
    
def moveSnake(dx,dy):
    global snake, isDead, score
    
    # Each direction has its own sequence of sprites
    seq = deltaToSeq(dx,dy)
    
    #-- New Head --
    curHead = snake[0]
    curHeadCode = curHead[2]
    curSeg = curHeadCode[0]
    nuX = curHead[0] + dx
    nuY = curHead[1] + dy
    pos = seq.rfind(curSeg) # seq is listed head to tail, so to find new head we need to go backward in the seq.
    nuHeadCode = seq[pos-3:pos]
        
    nuHead = (nuX, nuY, nuHeadCode)
    
    if isInSnake(nuX,nuY): # Ran into self
        isDead=True

    #-- Append New Head --
    snake.insert(0, nuHead)

    #-- Head coincides with apple? --
    if abs(nuX-appleX)<=1 and abs(nuY-appleY)<=1:
    #if nuX==appleX and nuY==appleY:
        drawApple(0) # erase the apple we just ate
        gc.collect()
#         functions.buzz(speaker, 1046, .03, 0)
        try:
            _thread.start_new_thread(functions.coin, ())
        except (OSError, MemoryError) as error:
            print(error)
        # Don't erase tail so snake becomes one segment longer after eating apple
        # Also, create a new apple (outside the snake)
        randomApple()
        drawApple(1) # draw new apple
        SpeedUp()
        score += 1
#         print(score, spd)
    else:
        if not isDead:
            ChopTail() # Normal path is to erase tail as snake slithers around

    #draw new head after erasing apple
    drawSeg(nuX, nuY, nuHeadCode)
    
    oled.show()

def buttonPressedHandle(p):
    global startWasPressed, pause, gameOver
    if gameOver:
        gameOver = False
        return
    if startWasPressed:
        pause = not pause
        return
    startWasPressed = True

timer = Timer(-1)

def debounce(pin):
    global timer
    timer.init(mode=Timer.ONE_SHOT, period=200, callback=buttonPressedHandle)

def setupUI():
    global buttonRight, buttonLeft, buttonUp, buttonDown, buttonStart

    buttonRight = Pin(5, Pin.IN, Pin.PULL_UP)
    buttonLeft = Pin(4, Pin.IN, Pin.PULL_UP)
    buttonDown = Pin(3, Pin.IN, Pin.PULL_UP)
    buttonUp = Pin(2, Pin.IN, Pin.PULL_UP)
    
    buttonStart = Pin(7, Pin.IN, Pin.PULL_UP)
    buttonStart.irq(trigger=Pin.IRQ_RISING, handler=debounce)
    

def changeDir(nuDx, nuDy):
    global snake, dx, dy
    
    if dx==nuDx and dy==nuDy:
        return
    
    headSeg = snake[0] #x,y,spriteCode
    headSpriteName = headSeg[2][0] # take first char of sprite code -> sprite name
    key = headSpriteName + fromOffset(dx,dy) + fromOffset(nuDx, nuDy)

    if key in turnTable:
        nuSpriteName = turnTable[key]
        nuCode = toCode(nuSpriteName, nuDx, nuDy)
        nuX, nuY = headSeg[0]+nuDx, headSeg[1]+nuDy
        snake.insert(0, (nuX,nuY,nuCode))
        drawSeg(nuX, nuY, nuCode) # new head is created due to turning, so draw this new head!
        
        ChopTail()
        dx,dy=nuDx,nuDy

def _map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def dirToDeltas(dir):
    results = (0,0)
    if dir==0: results = (0,+1)
    if dir==1: results = (+1,0)
    if dir==2: results = (0,-1)
    if dir==3: results = (-1,0)
    return results

def CheckButtons():
    global direction
    if buttonLeft.value()==False:
        changeDir(-1,0)
        if direction != "left" and direction != "right":
            functions.changeDirection()
        direction = "left"
    elif buttonRight.value()==False:
        changeDir(1,0)
        if direction != "left" and direction != "right":
            functions.changeDirection()
        direction = "right"
    elif buttonUp.value()==False:
        changeDir(0,1)
        if direction != "up" and direction != "down":
            functions.changeDirection()
        direction = "up"
    elif buttonDown.value()==False:
        changeDir(0,-1)
        if direction != "up" and direction != "down":
            functions.changeDirection()
        direction = "down"

def isInSnake(x,y):
    for seg in snake:
        if x==seg[0] and y==seg[1]:
            return True
    return False
            
def randomApple():
    global appleX, appleY
    hasCollision = True
    while hasCollision:
        appleX, appleY = randrange(1,gameWidth), randrange(1,gameHeight-2)
        hasCollision = isInSnake(appleX, appleY)

def drawApple(color):
    x,y=appleX, appleY
    p = [-1,+1] # position offset
    appleSize = 3*scale
#     oled.rect(border+x*3*scale+p[0]*scale,border+63-y*3*scale-p[1]*scale, appleSize,appleSize, color)
    oled.rect(border+x*3*scale+p[0]*scale,border+127-y*3*scale-p[1]*scale, appleSize,appleSize, oled.rgb(255,0,0) if color else 0)
#     circle(round(border+x*3*scale+p[0]*scale-(appleSize/2)),round(border+127-y*3*scale-p[1]*scale-(appleSize/2)), round(appleSize/2), oled.rgb(255,0,0) if color else 0)

def CenteredText(msg):   
    hOffset = int((WIDTH - 7*len(msg))/2)
    oled.fill(0)
    oled.text(msg, hOffset, int(HEIGHT/2), oled.rgb(255,255,255))
    oled.show()

def AreYouReady():
    global startWasPressed
    isBlank=False
    startWasPressed = False
    while not startWasPressed:
        oled.fill(0)
        if not isBlank:
            hOffset = int((WIDTH - 7*len("PRESS  "))/2) - 4
            oled.fill(0)
            oled.text("PRESS  ", hOffset, int((HEIGHT/2) - 6), oled.rgb(255,255,255))
            circle(85,61,5,oled.rgb(128,128,128))
            hOffset = int((WIDTH - 7*len("TO START"))/2) - 4
            oled.text("TO START", hOffset, int((HEIGHT/2) + 6), oled.rgb(255,255,255))
        oled.show()
        if isBlank: sleep(.5)
        else: sleep(1)
        isBlank = not isBlank

def GameOver():
    global score, gameOver
    global spd, direction
    global originalSpd
    gc.collect()
    spd = originalSpd
    first = True
    direction = "right"
    while gameOver:
        oled.fill(0)
        oled.text("GAME OVER", int((128 - 7*len("GAME OVER"))/2), int((128/2) - 18), oled.rgb(255,255,255))
        oled.text("SCORE: " + str(score), int((128 - 7*len("SCORE: " + str(score)))/2), int((128/2) - 6), oled.rgb(255,255,255))
        if high_score < score:
            db["highScores"]["snake"] = score
            with open('settings.json', 'w') as file:
                file.write(json.dumps(db))
            oled.text("NEW HIGH SCORE", 6, int((128/2) + 6), oled.rgb(255,255,255))
        else:
            oled.text("HIGH SCORE: " + str(high_score), int((128 - 7*len("HIGH SCORE: " + str(high_score)))/2)-5, int((128/2) + 6), oled.rgb(255,255,255))
        
        circle(34,103,5,oled.rgb(128,128,128))
        oled.text("CONTINUE", 42, 100, oled.rgb(255,255,255))
        circle(34,115,5,oled.rgb(255,0,0))
        oled.text("QUIT", 42, 112, oled.rgb(255,255,255))
        oled.show()
        if first:
            first = False
            functions.gameOver()
        while not buttonRight.value():
            if buttonRight.value():
                sys.exit()
#         else:
#             sleep(1)
#         
#         #-- draw end game --
#         oled.fill(0)
#         DrawWalls()
#         drawApple(1)
#         drawSnake()
#         sleep(.5)
    
    # wait for button release
    while buttonStart.value() == 0:
        sleep(0.5)
    
    global isDead, score
    isDead = False;
    score = 0

def SpeedUp():
    global spd
    spd -= 0.01
    if spd<0.07: spd=0.07

def main(): 
    setupUI()
    
    oled.fill(0)
    x=int(WIDTH/3/scale/2)
    y=int(HEIGHT/3/scale/2)
    global snakeX, snakeY, gameOver

    while True:
#         AreYouReady()
        
        snakeX, snakeY = int(WIDTH/3/scale/2), int(HEIGHT/3/scale/2)
          
        #initSnakeRL(x,y)
        initSnakeLR(x,y)
        #initSnakeUp(x,y)
#         initSnakeDown(x,y)
        
        oled.fill(0)
        randomApple()
        drawApple(1)
        gc.collect()
        while not isDead:
            DrawWalls() # redraw walls because screen is too short. Snake actually overlaps with bottom wall :-(
            CheckWalls()
            if not isDead:
                moveSnake(dx,dy)
                for i in range(buttonSpdScale):
                    sleep(spd/buttonSpdScale)
                    CheckButtons()
                    if pause:
                        speaker.duty_u16(0)
                        oled.fill(0)
                        hOffset = int((128 - 7*len("PAUSED"))/2)
                        oled.text("PAUSED", hOffset, 60, oled.rgb(255,255,255))
                        circle(34,103,5,oled.rgb(128,128,128))
                        oled.text("RESUME", 42, 100, oled.rgb(255,255,255))
                        circle(34,115,5,oled.rgb(255,0,0))
                        oled.text("QUIT", 42, 112, oled.rgb(255,255,255))
                        oled.show()
                        while pause:
                            if not buttonRight.value():
                                sys.exit()
                            sleep(.05)
                        oled.fill(0)
                        drawApple(1)
        gameOver = True
        GameOver()
main()