import pygame 
from SETTINGS import*
class Camera:
    def __init__(self,width,height):
        self.camera = pygame.Rect(0,0,width,height)
        self.width = width 
        self.height = height
    def apply(self, sprite):
        return sprite.rect.move(self.camera.topleft)
    
    def update(self, target):
        x=-target.rect.x + screen_width//2
        y=-target.rect.y + screen_height//2
        x=min(x,0)
        y=min(y,0)
        
        x=max(x,screen_width-self.width)
        y=max(y,screen_height-self.height)

        self.camera = pygame.Rect(x,y,self.width,self.height)