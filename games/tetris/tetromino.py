class Tetromino_1:
    def __init__(self, oled, x: int, y:int, block_size: int, rotation: int = 0):
        self.oled = oled
        self.x = x
        self.y = y
        self.block_size = block_size
        self.rotation = rotation
        self.draw_tetromino()
        self.height = None
        self.width = None
        self.update_size()
        self.oled.show()

    def draw_tetromino(self, erase=False):
        block_size = self.block_size
        oled = self.oled
        x = self.x
        y = self.y
        rotation = self.rotation
        if erase:
            inner_color = 0
            outer_color = 0
        else:
            inner_color = oled.rgb(0, 221, 255)
            outer_color = oled.rgb(0, 85, 255)
        if rotation == 0 or rotation == 2:
            oled.fill_rect(x+1, y+1, block_size-2, block_size-2, inner_color)
            oled.rect(x, y, block_size, block_size, outer_color)
            oled.fill_rect(x+block_size+1, y+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+block_size, y, block_size, block_size, outer_color)
            oled.fill_rect(x+2*block_size+1, y+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+(block_size*2), y, block_size, block_size, outer_color)
            oled.fill_rect(x+3*block_size+1, y+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+(block_size*3), y, block_size, block_size, outer_color)
        elif rotation == 1 or rotation == 3:
            oled.fill_rect(x+1, y+1, block_size-2, block_size-2, inner_color)
            oled.rect(x, y, block_size, block_size, outer_color)
            oled.fill_rect(x+1, y+block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x, y+block_size, block_size, block_size, outer_color)
            oled.fill_rect(x+1, y+2*block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x, y+(block_size*2), block_size, block_size, outer_color)
            oled.fill_rect(x+1, y+3*block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x, y+(block_size*3), block_size, block_size, outer_color)
    
    def move(self, x:int = None, y:int = None, show:bool = False):
        self.draw_tetromino(erase = True)
        if x != None:
            self.x = x
        if y != None:
            self.y = y
        self.draw_tetromino()
        if show:
            self.oled.show()
    
    def rotate(self, rotation: int, show:bool = False):
        self.draw_tetromino(erase = True)
        self.rotation = rotation
        self.update_size()
        self.draw_tetromino()
        if show:
            self.oled.show()
    
    def update_size(self):
        self.height = self.block_size if self.rotation == 0 or self.rotation == 2 else self.block_size * 4
        self.width = self.block_size * 4 if self.rotation == 0 or self.rotation == 2 else self.block_size



class Tetromino_2:
    def __init__(self, oled, x: int, y:int, block_size: int, rotation: int = 0):
        self.oled = oled
        self.x = x
        self.y = y
        self.block_size = block_size
        self.rotation = rotation
        self.draw_tetromino()
        self.height = None
        self.width = None
        self.update_size()
        self.oled.show()

    def draw_tetromino(self, erase=False):
        block_size = self.block_size
        oled = self.oled
        x = self.x
        y = self.y
        rotation = self.rotation
        if erase:
            inner_color = 0
            outer_color = 0
        else:
            inner_color = oled.rgb(0, 0, 240)
            outer_color = oled.rgb(0, 0, 75)
            
        if rotation == 0:
            oled.fill_rect(x+1, y+1, block_size-2, block_size-2, inner_color)
            oled.rect(x, y, block_size, block_size, outer_color)
            oled.fill_rect(x+1, y+block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x, y+block_size, block_size, block_size, outer_color)
            oled.fill_rect(x+block_size+1, y+block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+block_size, y+block_size, block_size, block_size, outer_color)
            oled.fill_rect(x+2*block_size+1, y+block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+block_size*2, y+block_size, block_size, block_size, outer_color)
        elif rotation == 1:
            oled.fill_rect(x+1, y+1, block_size-2, block_size-2, inner_color)
            oled.rect(x, y, block_size, block_size, outer_color)
            oled.fill_rect(x+block_size+1, y+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+block_size, y, block_size, block_size, outer_color)
            oled.fill_rect(x+1, y+block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x, y+block_size, block_size, block_size, outer_color)
            oled.fill_rect(x+1, y+block_size*2+1, block_size-1, block_size-1, inner_color)
            oled.rect(x, y+block_size*2, block_size, block_size, outer_color)
        elif rotation == 2:
            oled.fill_rect(x+2*block_size+1, y+1, block_size-2, block_size-2, inner_color)
            oled.rect(x+2*block_size, y, block_size, block_size, outer_color)
            oled.fill_rect(x+1, y+block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x, y+block_size, block_size, block_size, outer_color)
            oled.fill_rect(x+block_size+1, y+block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+block_size, y+block_size, block_size, block_size, outer_color)
            oled.fill_rect(x+block_size*2+1, y+block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+block_size*2, y+block_size, block_size, block_size, outer_color)
        elif rotation == 3:
            oled.fill_rect(x+1, y+1, block_size-2, block_size-2, inner_color)
            oled.rect(x, y, block_size, block_size, outer_color)
            oled.fill_rect(x+block_size+1, y+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+block_size, y, block_size, block_size, outer_color)
            oled.fill_rect(x+block_size+1, y+block_size+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+block_size, y+block_size, block_size, block_size, outer_color)
            oled.fill_rect(x+block_size+1, y+block_size*2+1, block_size-1, block_size-1, inner_color)
            oled.rect(x+block_size, y+block_size*2, block_size, block_size, outer_color)
    
    def move(self, x:int = None, y:int = None, show:bool = False):
        self.draw_tetromino(erase = True)
        if x != None:
            self.x = x
        if y != None:
            self.y = y
        self.draw_tetromino()
        if show:
            self.oled.show()
    
    def rotate(self, rotation: int, show:bool = False):
        self.draw_tetromino(erase = True)
        self.rotation = rotation
        self.update_size()
        self.draw_tetromino()
        if show:
            self.oled.show()
    
    def update_size(self):
        self.height = self.block_size * 2 if self.rotation == 0 or self.rotation == 2 else self.block_size * 4
        self.width = self.block_size * 3 if self.rotation == 0 or self.rotation == 2 else self.block_size
