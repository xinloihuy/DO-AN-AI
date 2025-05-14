import pygame
import sys
import csv
from math import*
from map.Environment import*
import random 
sys.path.append('map')
from SETTINGS import *
class Map:
    def __init__(self):
        self.data = []
        self.tiles = []
        self.obobstacle_coord = []
        self.level = 0
    # def reset(self,screen):
    #     #screen.fill((0,0,0))
    #     self.data = []
        
        
    def load_csv(self,level):
        self.data = []
        self.level = level
        with open(f"map/map{level}.csv","r") as file:
            
            reader = csv.reader(file,delimiter=',')
            for line in reader:
                self.data.append(line)



    
    def load_data(self):
        self.tiles = []
        for row, tile_row in enumerate(self.data):   
            for col, tile in enumerate(tile_row):
                num_tile = int(tile)
                if self.level != 1:
                    if num_tile != -1:
                        if num_tile in [0, 21, 25, 26, 27,33]:
                            if num_tile == 33:
                                self.obobstacle_coord.append(Water(col, row, f'assets/images/{num_tile}.png'))
                            self.tiles.append(Water(col, row, f'assets/images/{num_tile}.png'))       
                        if num_tile in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,32]:
                            if num_tile not in [6,13]:
                                self.obobstacle_coord.append(Ground(col, row, 'assets/images/13.png'))
                            self.tiles.append(Ground(col, row, f'assets/images/{num_tile}.png'))
                        if num_tile in [22, 23, 24]:
                            self.tiles.append(Grass(col, row, f'assets/images/{num_tile}.png'))
                        if num_tile in [1, 11, 15, 16, 17, 18, 19, 20, 28, 29, 30]:
                            self.tiles.append(Tree(col, row, f'assets/images/{num_tile}.png'))
                        if num_tile in [31]:
                            self.tiles.append(Gold(col, row, f'assets/images/{num_tile}.png'))
                else:
                    if num_tile != -1:
                        if num_tile in [51,55,56,57,58]:
                            self.tiles.append(Water(col, row, f'assets/images/{num_tile}.png'))       
                        if num_tile in [34,35,36,37,38,39,40,41,42,43,47,48,49,50,52,53,54]:
                            if num_tile in [35,37,38,39,40,41,54]:
                                self.obobstacle_coord.append(Ground(col, row, 'assets/images/13.png'))
                            self.tiles.append(Ground(col, row, f'assets/images/{num_tile}.png'))
                        if num_tile in [44,45,46]:
                            self.tiles.append(Grass(col, row, f'assets/images/{num_tile}.png'))
                        if num_tile in [31]:
                            self.tiles.append(Gold(col, row, f'assets/images/{num_tile}.png'))

    