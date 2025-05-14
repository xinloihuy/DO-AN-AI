import pygame
from map.SETTINGS import*
from globals import*
class Button( pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image,button_group): #type_group):
        super().__init__()
        #global button_game_over, button_upgrade
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image,(width,height))
        self.rect = self.image.get_rect()
        self.rect.x = x 
        self.rect.y = y
        self.pressed = False
        # if type_group == 1:
        #     button_game_over.add(self)
        # elif type_group == 2:
        #     button_upgrade.add(self)
        button_group.add(self)    
     
    def is_pressed(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse_pos):
            if mouse_pressed[0] == 1 and self.pressed == False:
                self.pressed = True 
                return True 
        if not mouse_pressed[0]:
            self.pressed = False
            return False
