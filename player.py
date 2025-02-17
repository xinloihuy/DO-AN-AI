from os import listdir
import pygame
from os.path import join, isfile, splitext
from PIL import Image
from map.World import*

def flip(sprites):
    """Lật danh sách các sprite theo chiều ngang"""
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets_quick(dir1, dir2, direction=False):
    """Tải sprite sheet từ thư mục, cắt thành từng frame, và lưu vào dictionary"""
    path = f'assets\Character\Hero'
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image))
        width, height = sprite_sheet.get_size()

        # Giả sử mỗi sprite có chiều rộng bằng chiều cao
        sprite_width = height  # Mỗi sprite là hình vuông

        # Tách các sprite từ sprite sheet
        sprites = []
        for i in range(0, width, sprite_width):
            sprite = sprite_sheet.subsurface((i, 0, sprite_width, height))
            sprite = pygame.transform.scale(sprite, (sprite_width * 1.5, height * 1.5))  # Phóng to 2x
            sprites.append(sprite)

        # Phân loại sprite dựa trên tên file
        base_name = image.split('.')[0]  # Bỏ phần mở rộng
        action = ''.join([i for i in base_name if not i.isdigit()])  # Tách phần chữ (vd: 'run', 'idle')

        if action not in all_sprites:
            all_sprites[action] = {}

        if direction:
            all_sprites[action + "_right"] = sprites
            all_sprites[action + "_left"] = flip(sprites)

    return all_sprites


class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets_quick("Character", "Hero", True)
    
    ANIMATION_DELAY = 2
    RUN_DELAY = 1
    def __init__(self, x, y, width, height, tiles):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.width = width
        self.height = height
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.tiles = tiles
        

        self.width = width
        self.height = height
    def move(self, dx, dy):
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
        self.y_vel = -self.GRAVITY*6
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count >= 2:
            self.y_vel = 0
            self.jump_count = 0

    def loop(self,fps):
        # self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.update_sprite()
        self.move(self.x_vel, self.y_vel)
        self.fall_count += 1
    
    def update_sprite(self):
        self.vel = 0
        delay = self.RUN_DELAY if self.x_vel != 0 else self.ANIMATION_DELAY
        sprite_sheet = "Idle"
        if self.x_vel != 0:
            sprite_sheet = "Run"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // delay) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        

    def check_collision(self,x,y):
        
        dx,dy = x,y
        for tile in self.tiles :
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) and isinstance(tile, Grass):
                dx = 0
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if y < 0:
                    self.jump_count = 0
                dy = 0
        return dx,dy


    def draw(self, screen):
        screen.blit(self.sprite, (self.rect.x, self.rect.y))
