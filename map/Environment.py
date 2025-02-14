from map.SETTINGS import*
import pygame
from globals import*
class EnvironmentTiles(pygame.sprite.Sprite):
    def __init__(self,x,y,image):
        super().__init__()
        global all_sprite,environment
        self.image=pygame.image.load(image)
        self.image=pygame.transform.scale(self.image,(tile_size,tile_size))
        self.rect=self.image.get_rect()
        self.x=x
        self.y=y
        self.rect.x=x*tile_size 
        self.rect.y=y*tile_size
        all_sprite.add(self)
        environment.add(self)
class Grass(EnvironmentTiles):
    def __init__(self,x,y,image):
        super().__init__(x,y,image)
class Ground(EnvironmentTiles):
    def __init__(self,x,y,image):
        super().__init__(x,y,image)
class Water(EnvironmentTiles):
    def __init__(self,x,y,image):
        super().__init__(x,y,image)
class Tree(EnvironmentTiles):
    def __init__(self,x,y,image):
        super().__init__(x,y,image)

       

          