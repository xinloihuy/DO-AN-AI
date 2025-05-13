from map.SETTINGS import*
import pygame
from globals import*
class EnvironmentTiles(pygame.sprite.Sprite):
    def __init__(self,x,y,image):
        super().__init__()
        global all_sprite
        self.image=pygame.image.load(image)
        self.image=pygame.transform.scale(self.image,(tile_size,tile_size))
        self.rect=self.image.get_rect()
        self.x=x
        self.y=y
        self.rect.x=x*tile_size 
        self.rect.y=y*tile_size
        all_sprite.add(self)
\
class Grass(EnvironmentTiles):
    def __init__(self,x,y,image):
        super().__init__(x,y,image)
class Ground(EnvironmentTiles):
    def __init__(self,x,y,image):
        super().__init__(x,y,image)
class Water(EnvironmentTiles):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
class AnimatedWater(EnvironmentTiles):
    def __init__(self,x,y,image):
        super().__init__(x,y,image)
        self.frames = [
            pygame.image.load(f"assets/images/55.png"),
            pygame.image.load(f"assets/images/56.png"),
            pygame.image.load(f"assets/images/57.png"),
            pygame.image.load(f"assets/images/58.png")
        ]
        self.frames = [pygame.transform.scale(frame, (tile_size, tile_size)) for frame in self.frames]
        self.current_frame = 0
        self.frame_count = len(self.frames)
        self.animation_speed = 100
        self.time_since_last_frame = 0
        
        self.image = self.frames[self.current_frame]
    
    def update(self, dt):
        self.time_since_last_frame += dt 
        
        if self.time_since_last_frame >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.image = self.frames[self.current_frame]
            self.time_since_last_frame = 0 
class Tree(EnvironmentTiles):
    def __init__(self,x,y,image):
        super().__init__(x,y,image)
class Gold(EnvironmentTiles):
    def __init__(self,x,y,image):
        super().__init__(x,y,image)
        self.image=pygame.image.load(image)
        self.image=pygame.transform.scale(self.image,(tile_size*0.8,tile_size*0.8))
        global gold_group
        gold_group.add(self)


       

          