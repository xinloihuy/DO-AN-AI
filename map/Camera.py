import pygame 
from SETTINGS import*
class Camera:
    def __init__(self,width,height):
        self.camera = pygame.Rect(0,0,width,height)
        self.width = width 
        self.height = height
        self.x = 0 
        self.y = 0
    def apply(self, sprite):
        return sprite.rect.move(self.camera.topleft)
    def apply_position(self, pos):
        x, y = pos
        return (x + self.camera.topleft[0], y + self.camera.topleft[1])
    
    def update(self, target):
        self.x = -target.rect.x + screen_width//2
        self.y = -target.rect.y + screen_height//2
        self.x = min(self.x,0)
        self.y = min(self.y,0)
        
        self.x = max(self.x,screen_width-self.width)
        self.y = max(self.y,screen_height-self.height)

        self.camera = pygame.Rect(self.x,self.y,self.width,self.height)