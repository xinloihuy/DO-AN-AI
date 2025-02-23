import pygame
from map.SETTINGS import screen_width, screen_height, tile_size, rows, cols, vel, FPS
from globals import*
from map.Environment import*
from GameOver import*
#from main import*

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        global all_sprite
        super().__init__()
        self.image = pygame.image.load(f'assets/images/warrior.png')
        self.width = tile_size
        self.height = tile_size*2
        self.image = pygame.transform.scale(self.image,(self.width,self.height))
        self.rect = self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        # self.x=x
        # self.y=y
        self.jump = 0
        self.isJump = False
        self.vel = vel
        self.health = 10 
        self.defense = 0 
        self.attack = 5
        self.gold = 0
        self.score = 0
        self.game_over = False
        self.player_update = False
        all_sprite.add(self)
    def update(self,tiles):
        pygame.display.update()
        keys = pygame.key.get_pressed() 
        dx,dy = 0,0
        if (keys[pygame.K_LEFT] or keys[pygame.K_a])and self.rect.x > self.vel:
            dx = -self.vel  
            #self.checkcolisionx(tiles,dx)  
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d])and self.rect.x < 150*tile_size:       
            dx = self.vel
            #self.checkcolisionx(tiles,dx)
        if (keys[pygame.K_SPACE] or keys[pygame.K_w])and self.isJump == False :
            self.isJump = True  
            self.jump = -10
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) == False:
            self.isJump = False  
            
        self.jump += 1 
        if self.jump >= 15:
            self.jump = 15   
        dy += self.jump
        
        dx,dy = self.checkcollision(tiles,dx,dy)
         
        #print(f"player: {game_over}")
        self.rect.x += dx
        self.rect.y += dy
    
    
       
    def checkcollision(self,tiles,x,y):
        dx,dy = x,y
        vel = self.vel
        global game_over
        
        for tile in tiles:
                if tile.rect.colliderect(self.rect.x+dx, self.rect.y, self.width, self.height) and isinstance(tile,Ground):
                    dx = 0                
                if tile.rect.colliderect(self.rect.x+dx, self.rect.y, self.width, self.height) and (isinstance(tile,Grass) or isinstance(tile,Tree)): 
                    self.vel *= 2.5
                else:
                    self.vel = vel
                if tile.rect.colliderect(self.rect.x, self.rect.y+dy, self.width, self.height) and (isinstance(tile,Ground) or isinstance(tile,Water)):
                    if isinstance(tile,Water):
                        self.game_over = True
                
                    #check if jumping
                    else:
                        if self.jump < 0:
                            dy = tile.rect.bottom - self.rect.top
                        #check if falling    
                        else:
                            dy = self.rect.top - tile.rect.bottom  
                            dy = -(-self.rect.bottom + tile.rect.top)
                            self.jump = 0
                
        return dx,dy   
    
    
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
    
        
    
        



