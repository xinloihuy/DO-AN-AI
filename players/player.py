import pygame
from map.SETTINGS import screen_width, screen_height, tile_size, rows, cols, vel, FPS
from globals import*
from map.Environment import*
from GameOver import*
from os import listdir
from os.path import isfile, join, splitext

def crop_sprite(sprite):
    mask = pygame.mask.from_surface(sprite)
    rect = mask.get_bounding_rects()

    if rect:
        return sprite.subsurface(rect[0])
    return sprite
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets_quick(dir1, dir2):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image))
        width, height = sprite_sheet.get_size()

        sprite_width = height

        sprites = []
        for i in range(0, width, sprite_width):
            
            sprite = sprite_sheet.subsurface((i, 0, sprite_width, height))
            sprite = crop_sprite(sprite)
            sprites.append(sprite)

        base_name = image.split('.')[0]
        action = ''.join([i for i in base_name if not i.isdigit()])
    
        if action not in all_sprites:
            all_sprites[action] = {}

        all_sprites[action + "_right"] = sprites
        all_sprites[action + "_left"] = flip(sprites)

    return all_sprites


class Player(pygame.sprite.Sprite):
    SPRITES = load_sprite_sheets_quick('Character', 'Hero')
    ANIMATION_DELAY = 8
    RUN_DELAY = 10
    GRAVITY = 2
    def __init__(self,x,y):
        global all_sprite
        super().__init__()
        self.image = self.SPRITES['Idle_right'][0]
        self.x = x
        self.y = y
        self.width = tile_size*2
        self.height = tile_size*2
        self.image = pygame.transform.scale(self.image,(self.width,self.height))
        self.vel = 4
        self.x_vel = 0
        self.y_vel = 0
        self.rect = pygame.Rect(self.x,self.y,tile_size*2,tile_size*2)
        # self.rect = self.image.get_rect()
        # self.rect.topleft = (self.x,self.y)
        


        self.animation_count = 0
        self.direction = "right"
        self.action = "Idle"

        
        self.jump_count = 0
        self.isJump = False
        self.fall_count = 0


        self.health = 10 
        self.defense = 0 
        self.attack = 5
        self.gold = 0
        self.score = 0
        self.game_over = False
        self.player_update = False
        all_sprite.add(self)
    
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
        self.y_vel = -15
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
        
        
        sprite_sheet_name = self.action + "_" + self.direction
        
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

    def update(self,tiles):
        pygame.display.update()
        self.x_vel = 0
        print(self.rect)


        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1



        keys = pygame.key.get_pressed() 
        dx,dy = 0,0
        if (keys[pygame.K_LEFT] or keys[pygame.K_a])and self.rect.x > vel:
            dx = -self.vel 
            self.move_left(vel)
            if self.direction != "left":
                self.direction = "left"
                self.animation_count = 0
            #self.checkcolisionx(tiles,dx)  
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d])and self.rect.x < 150*tile_size:       
            dx = self.vel
            self.move_right(vel)
            if self.direction != "right":
                self.direction = "right"
                self.animation_count = 0
            #self.checkcolisionx(tiles,dx)
        if (keys[pygame.K_SPACE] or keys[pygame.K_w])and self.isJump == False :
            self.jump()
            self.isJump = True  
            self.jump_count = -15
            self.animation_count = 0
            self.jump_count += 1

            # self.y_vel = -15
            # self.jump_count += 1
            # if self.jump_count >= 2:
            #     self.y_vel = 0
            #     self.jump_count = 0

        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) == False and self.jump_count > 2:
            self.isJump = False  
            self.jump_count = 0
        
    
        

        print(self.y_vel)
        
        
        


        # dx,dy = self.checkcollision(tiles,dx,dy)
        
        # print(f"player: {game_over}")
        # self.rect.x += dx
        # self.rect.y += dy

        self.move(self.x_vel,self.y_vel,tiles)
        
        self.update_sprite()
    

    def checkcollision(self, tiles, x, y):
        dx, dy = x, y
        global game_over

        for tile in tiles:
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) and isinstance(tile, Ground):
                dx = 0
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) and (isinstance(tile, Grass) or isinstance(tile, Tree)):
                self.x_vel *= 2.5
            else:
                self.vel = vel

            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height) and (isinstance(tile, Ground) or isinstance(tile, Water)):
                if isinstance(tile, Water):
                    self.game_over = True
                else:
                    # Check if jumping
                    if self.y_vel < 0:  # Nhân vật đang nhảy lên
                        dy = tile.rect.bottom - self.rect.top
                        self.y_vel = 0  # Dừng lại khi chạm trần
                    # Check if falling
                    elif self.y_vel >= 0:  # Nhân vật đang rơi xuống
                        dy = tile.rect.top - self.rect.bottom
                        self.y_vel = 0  # Dừng lại khi chạm đất
                        self.jump_count = 0  # Reset jump count khi chạm đất
                        self.isJump = False  # Đặt lại trạng thái nhảy

        

        return dx, dy

    
    
    def handle_upgrade(self,upgrade_attack_button, upgrade_heard_button, upgrade_shield_button):    
            if upgrade_attack_button.is_pressed():
                if self.gold-20 >= 0:
                    self.gold -= 20
                    self.attack += 1 
            elif upgrade_heard_button.is_pressed():
                if self.gold-20 >= 0:
                    self.gold -= 20
                    self.health += 1
            elif upgrade_shield_button.is_pressed():
                if self.gold-20 >= 0:
                    self.gold -= 20
                    self.defense += 1 
    
        
    
        



