import pygame
from map.SETTINGS import tile_size, vel, FPS
from globals import*
from map.Environment import*
from GameOver import*
from os import listdir
from os.path import isfile, join, splitext

class Entity(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        super().__init__()
        
        self.JUMP_HEIGHT = 13
        self.ANIMATION_DELAY = 18
        self.RUN_DELAY = 17
        self.GRAVITY = 2
        self.SCALE_FACTOR = scale


        self.SPRITES = {'Idle': [None]}
        self.image = self.SPRITES['Idle'][0]
        self.x = x
        self.y = y
        self.width = tile_size*self.SCALE_FACTOR
        self.height = tile_size*self.SCALE_FACTOR
        self.vel = vel
        self.x_vel = 0
        self.y_vel = 0
        self.rect = pygame.Rect(self.x,self.y,self.width,self.height)
        


        self.animation_count = 0
        self.direction = "right"
        self.action = "Idle"

        
        self.jump_count = 0
        self.isJump = False
        self.fall_count = 20


        self.health = health
        self.defense = 0 
        self.attack = 5
        self.gold = 0
        self.score = 0
        self.game_over = False
        self.player_update = False


    
    def load_transparent_image(self, path):
        img = pygame.image.load(path).convert()
        colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey)
        return img

    

    def crop_sprite(self, sprite):
        """Cắt vùng chứa nhân vật trong sprite"""
        mask = pygame.mask.from_surface(sprite)  # Tạo mask (bỏ phần trong suốt)
        rect = mask.get_bounding_rects()  # Lấy vùng bao quanh nhân vật

        if rect:  # Nếu tìm thấy nhân vật
            return sprite.subsurface(rect[0])  # Cắt đúng vùng
        return sprite  # Nếu không có gì, giữ nguyên
    
    def flip(self, sprites):
        return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

    
    def move(self,dx,dy,tiles):
        dx,dy = self.checkcollision(tiles,dx,dy)
        self.rect.x += dx
        self.rect.y += dy
    
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def jump(self):
        self.y_vel = -self.JUMP_HEIGHT
        self.isJump = True
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count >= 2:
            self.y_vel = 0
            self.jump_count = 0

    def update_sprite(self):
        self.action = "Idle"
        DELAY = self.RUN_DELAY if self.x_vel != 0 else self.ANIMATION_DELAY
        
        if self.x_vel != 0:
            self.action = "Run"
        
        sprites = self.SPRITES[self.action]
        sprite_index = (self.animation_count // DELAY) % len(sprites)
        self.image = sprites[sprite_index]

        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)

        self.animation_count += 1
    

    def checkcollision(self, tiles, x, y):
        dx, dy = x, y
        global game_over

        for tile in tiles:
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) and isinstance(tile, Ground):
                dx = 0
                
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) and (isinstance(tile, Grass) or isinstance(tile, Tree)):
                self.vel = 1.5*vel
            else:
                self.vel = vel

            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height) and (isinstance(tile, Ground) or isinstance(tile, Water)):
                if isinstance(tile, Water):
                    self.game_over = "True0"
                else:
                    if self.y_vel < 0:  # Nhân vật đang nhảy lên
                        dy = tile.rect.bottom - self.rect.top
                        self.y_vel = 0  # Dừng lại khi chạm trần

                    elif self.y_vel >= 0:  # Nhân vật đang rơi xuống
                        dy = tile.rect.top - self.rect.bottom
                        self.y_vel = 0  # Dừng lại khi chạm đất
                        self.jump_count = 0  # Reset jump count khi chạm đất
                        self.isJump = False  # Đặt lại trạng thái nhảy
        
        return dx, dy

   
        
    