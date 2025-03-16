import pygame.font
import pygame
from map.SETTINGS import*
from globals import*
class Rocket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        global enemies_group
        self.image = pygame.image.load(f'assets/images/rocket.png')
        self.width = tile_size*1.5 
        self.height = tile_size
        self.image = pygame.transform.scale(self.image,(self.width,self.height))
        self.rect = self.image.get_rect()
        self.rect.x = screen_width
        self.rect.y = screen_height//2 #- tile_size
        self.active = False 
        self.delay = 0 
        self.counter = 0  
        self.explosion_time = 0
        self.index = 0
        self.vel = vel
        self.is_collide = False
    def check_rocket(self,screen,player,time_counter,camera,explosion):
        if player.game_over == False:
            self.counter += 1 
            if self.counter > time_counter:
                self.counter = 0
                self.active = True
            if self.active :
                if self.delay < 90:
                    if player.rect.x + screen_width//2 < screen_width:
                        self.rect.x = screen_width - tile_size
                    else:
                        self.rect.x = player.rect.x + 15*tile_size if player.rect.x + 15*tile_size <= 149*tile_size else 149 *tile_size
                    self.delay +=1
                    self.draw_rocket(screen,player,0,camera,explosion) 
                else:
                    self.draw_rocket(screen,player,1,camera,explosion) 
                    
                if self.rect.x < 0:
                    self.delay = 0
                    self.active = False
                    self.rect.x = screen_width
                    self.rect.y = screen_height//2 - tile_size
    def draw_rocket(self,screen,player,mode,camera,explosion):
        if mode == 0:
            if player.rect.y > self.rect.y:
                self.rect.y += self.vel
            elif player.rect.y < self.rect.y:
                self.rect.y -= self.vel
            self.width = tile_size
            pygame.draw.rect(screen,'dark red',camera.apply(self))
            font = pygame.font.Font(None, 36)
            screen.blit(font.render("  !  ", True, 'Orange'),camera.apply(self))

            
        elif mode == 1:
            self.width = tile_size*2
            if self.is_collide == False:
                screen.blit(self.image, camera.apply(self))
                self.rect.x -= self.vel
            
            if self.rect.colliderect(player.rect)  and self.is_collide == False:
                player.health -= 5/2
                self.counter = 0
                self.deplay = 0
                self.is_collide = True

            if self.is_collide == True:
                explosion.update(player,screen,camera)
                if explosion.complete_exposion():
                    self.is_collide = False
                    
                    self.rect.x = -tile_size
                if player.health <= 0 :
                    player.game_over = True

            
            
                
    
            
            
                        
        
               
        

      
    
    