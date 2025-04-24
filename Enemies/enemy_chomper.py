import pygame
import os
from os import listdir
from os.path import isfile, join
from map.SETTINGS import tile_size, FPS
from globals import *
from Enemies.enemy_thorn import Thorn

class Chomper(Thorn):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        
        # Load các trạng thái animation
        self.SPRITES_IDLE = self.load_sprite_sheets("chomper/idle", scale)
        self.SPRITES_ATTACK = self.load_sprite_sheets("chomper/attack", scale)
        
        self.SPRITES = self.SPRITES_IDLE  # Bắt đầu với trạng thái idle
        self.is_attacking = False  # Cờ trạng thái attack
        self.frame_delay = 10  # Tốc độ khung hình cho trạng thái idle
        self.attack_frame_delay = 3  # Tốc độ khung hình cho trạng thái attack
        self.time_to_attack = 0  # Thời gian chờ giữa các lần tấn công
        
    def load_sprite_sheets(self, subfolder, scale_factor=2):
        """Load sprite từ thư mục con, kế thừa từ Thorn"""
        base_path = rf"assets/Enemy/{subfolder}"
        all_sprites = []

        if os.path.exists(base_path):
            files = sorted([f for f in listdir(base_path) if isfile(join(base_path, f)) and f.endswith(".png")])
            for file in files:
                image = pygame.image.load(join(base_path, file)).convert_alpha()
                width = int(tile_size * scale_factor)
                height = int(tile_size * scale_factor)
                image = pygame.transform.scale(image, (width, height))
                all_sprites.append(image)

        return all_sprites if all_sprites else [pygame.Surface((tile_size, tile_size))]  # Tránh lỗi nếu thư mục rỗng

    def update(self, player):
        self.frame_counter += 1
        
        # Sử dụng tốc độ khung hình tương ứng với trạng thái hiện tại
        frame_delay = self.attack_frame_delay if self.is_attacking else self.frame_delay
        
        if self.frame_counter >= frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.SPRITES)
            self.frame_counter = 0

        self.image = self.SPRITES[self.current_frame]
        self.rect = self.image.get_rect(center=self.rect.center)

        # Xác định hướng quay mặt
        player_x = player.rect.centerx
        enemy_x = self.rect.centerx

        self.direction = "left" if player_x < enemy_x else "right"

        # Nếu va chạm với player, chuyển sang attack
        if self.rect.colliderect(player.rect):
            if not self.is_attacking:
                self.SPRITES = self.SPRITES_ATTACK
                self.current_frame = 0
                self.is_attacking = True

        # Gây sát thương tại frame giữa, nhưng chỉ khi vẫn còn va chạm
        middle_frame = len(self.SPRITES) // 2
        if self.is_attacking and self.current_frame == middle_frame and self.rect.colliderect(player.rect):
            if self.time_to_attack == 0:
                self.attack_player(player, attack_speed=2)
                self.time_to_attack = FPS // 2  # Đặt delay trước lần cắn tiếp theo

        # Khi attack xong, chuyển về idle
        elif self.is_attacking and self.current_frame == len(self.SPRITES) - 1:
            self.SPRITES = self.SPRITES_IDLE
            self.current_frame = 0
            self.is_attacking = False

        # Giảm thời gian chờ giữa các lần tấn công
        if self.time_to_attack > 0:
            self.time_to_attack -= 1

        # Lật ảnh theo hướng nhân vật
        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)
