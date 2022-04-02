import functions
from color_setup import ssd as oled

from machine import Pin, PWM, SPI
from utime import sleep
import random # random direction for new ball
import framebuf

import time
                  
# Left and right push buttons connected to GP4 and GP5
left = Pin(4, Pin.IN, Pin.PULL_UP)
right = Pin(5, Pin.IN, Pin.PULL_UP)

# coordinates of the paddle on the screen in pixels
# the screen is 128 pixels wide by 64 pixel high
xp = 60 
yp = 124

# Simple Pong
x = 64 # ball coordinates on the screen in pixels
y = 0
vx = 2 # ball velocity along x and y in pixels per frame
vy = 2

while True:
    # Clear the screen
#     oled.fill(0)
    
    oled.fill_rect(xp, yp, 16, 4, 1)
    oled.show()
    
    if left.value() == 0:
        print("LEFT Button Pressed")
        xp = xp - 1 # Move the paddle to the left by 1 pixel
    elif right.value() == 0:
        print("RIGHT Button Pressed")
        xp = xp + 1 # Move the paddle to the right by 1 pixel
    oled.fill_rect(x, y, 4, 4, 1)
    oled.show()
    # Draw a 4x4 pixels ball at (x,y) in 
    
    # Move the ball by adding the velocity vector
    x += vx
    y += vy
    
    # Make the ball rebound on the edges of the screen
    if x < 0:
        x = 0
        vx = -vx
    if y < 0:
        y = 0
        vy = -vy
    if x + 4 > 128:
        x = 128 - 4
        vx = -vx
    if y + 4 > 128:
        y = 128 - 4
        vy = -vy