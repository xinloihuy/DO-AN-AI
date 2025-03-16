from map.SETTINGS import*
import pygame
from globals import*
class Explosion(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = []
        for i in range(1,6):
            img = pygame.image.load(f"assets/Explosion/exp{i}.png")
            img = pygame.transform.scale(img,(tile_size,tile_size))
            self.images.append(img)
        self.index = 0 
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.counter = 0
        self.explosion_time = 0

        
    def update(self,rocket,screen,camera):
        explosion_speed = 7
        self.counter += 1 
        
        self.rect.x = rocket.rect.x
        self.rect.y = rocket.rect.y 

        if self.counter >= 2.5 and self.index < len(self.images) - 1:
            self.counter = 0  
            self.index += 1
            self.image = self.images[self.index]

        if self.index < len(self.images) - 1:
            screen.blit(self.image, camera.apply(self))
            
    def complete_exposion(self):
        if self.index >= len(self.images) - 1:
            self.index = 0
            #self.kill
            return True
        return False

        