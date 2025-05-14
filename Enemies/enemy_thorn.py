import pygame
from map.SETTINGS import tile_size, FPS
from globals import *
from players.entity import Entity
from Enemies.enemy_diep import Enemy
import os
from os import listdir
from os.path import isfile, join

class Thorn(Enemy):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        self.SPRITES = self.load_sprite_sheets(scale)
        self.attack = 0.5

    def load_sprite_sheets(self, scale_factor=2):
        base_path = r"assets/Enemy/thorn"
        all_sprites = []

        if os.path.exists(base_path):
            files = sorted([f for f in listdir(base_path) if isfile(join(base_path, f)) and f.endswith(".png")])
            for file in files:
                image = pygame.image.load(join(base_path, file)).convert_alpha()
                width = int(tile_size * scale_factor)
                height = int(tile_size * scale_factor)
                image = pygame.transform.scale(image, (width, height))
                all_sprites.append(image)

        return all_sprites

    def update(self, player):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.SPRITES)
            self.frame_counter = 0
        
        self.image = self.SPRITES[self.current_frame]
        self.rect = self.image.get_rect(center=self.rect.center)

        # Kiểm tra va chạm với nhân vật
        if self.rect.colliderect(player.rect):
            self.attack_player(player, attack_speed=2)

        if self.time_to_attack > 0:
            self.time_to_attack -= 1
