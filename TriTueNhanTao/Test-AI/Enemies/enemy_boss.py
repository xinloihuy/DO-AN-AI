import pygame
from map.SETTINGS import tile_size, vel, FPS
from globals import *
from players.entity import Entity
import os
from os import listdir
from os.path import isfile, join

class EnemyBoss(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        self.SPRITES = self.load_sprite_sheets(scale)
        self.health = 50
        self.vel1 = 2

        # Phạm vi di chuyển của kẻ địch
        self.move_range = tile_size * 7
        self.patrol_left = self.x - self.move_range
        self.patrol_right = self.x + self.move_range
        self.patrolling = True
        self.direction = "left"

        # Attack
        self.attack = 0.5
        self.time_to_attack = 0
        
        self.current_frame = 0  # Bắt đầu từ frame 0
        self.current_action = "idle"  # Trạng thái ban đầu

        self.frame_delay = 5  # Chỉ thay đổi frame mỗi 5 lần update
        self.frame_counter = 0  # Đếm số lần update
        
        self.attack_frame_delay = 3  # Giảm tốc độ frame khi chém
        self.attack_frame_counter = 0  # Bộ đếm frame của animation chém

        self.fill_max = 0
        all_sprite_enemies.add(self)

    def load_transparent_image(self, path):
        img = pygame.image.load(path).convert()
        colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey)
        return img

    def load_sprite_sheets(self, scale_factor=2):
        base_path = r"assets/Enemy/Boss"
        all_sprites = {}

        actions = ["idle1", "walk1", "cleave1", "death1", "take_hit1"]
        
        for action in actions:
            action_path = os.path.join(base_path, action)
            
            if not os.path.exists(action_path):  
                continue

            files = sorted([f for f in listdir(action_path) if isfile(join(action_path, f)) and f.endswith(".png")])
            all_sprites[action] = []

            for file in files:
                image = self.load_transparent_image(join(action_path, file))
                # image = self.crop_sprite(image)
                # image = pygame.transform.scale(image, (int(tile_size * scale_factor), int(tile_size * scale_factor)))
                width = int(tile_size * scale_factor * 1.5)  # Tăng chiều rộng lên 1.5 lần
                height = int(tile_size * scale_factor)  # Giữ nguyên chiều cao
                image = pygame.transform.scale(image, (width, height))
                
                all_sprites[action].append(image)

        return all_sprites

    def move(self, x_vel, y_vel, tiles):
        dx, dy = self.checkcollision(tiles, x_vel, y_vel)
        self.rect.x += dx
        self.rect.y += dy
    
    def attack_player(self, player):
        """Gây sát thương cho nhân vật khi gặp"""
        if self.time_to_attack == 0:
            damage = max(0, self.attack - player.defense)
            player.health -= damage
            self.time_to_attack = FPS

            if player.health <= 0:
                player.game_over = True

    def update(self, tiles, player):
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        if self.rect.colliderect(player.rect):
            self.x_vel = 0
            
            player_x = player.rect.centerx
            boss_x = self.rect.centerx

            if player_x < boss_x:
                self.direction = "right"
            else:
                self.direction = "left"
                
            if self.current_action != "cleave1":
                self.current_action = "cleave1"
                self.current_frame = 0
                self.attack_frame_counter = 0

            if self.current_frame >= len(self.SPRITES["cleave1"]) - 1:
                if self.time_to_attack == 0:
                    self.attack_player(player)
                    self.time_to_attack = FPS // 2

            if self.time_to_attack > 0: 
                self.time_to_attack -= 1  
        else:
            self.current_action = "walk1"
            self.patrol(tiles)

        self.move(self.x_vel, self.y_vel, tiles)

        if self.health < 0:
            self.rect.x = -1000
            self.rect.y = -1000
            
        self.update_sprite()

    def update_sprite(self):
        if self.current_action in self.SPRITES:
            frames = self.SPRITES[self.current_action]
            max_frames = len(frames) - 1
            self.current_frame = min(self.current_frame, max_frames)
            self.image = frames[self.current_frame]
            
            self.rect = self.image.get_rect(center=self.rect.center) # thêm lúc nãy

            if self.direction == "left":
                self.image = pygame.transform.flip(self.image, True, False)

            if self.current_action == "walk1":
                self.frame_counter += 1
                if self.frame_counter >= self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(frames)
                    self.frame_counter = 0
            elif self.current_action == "cleave1":
                self.attack_frame_counter += 1
                if self.attack_frame_counter >= self.attack_frame_delay:
                    if self.current_frame < max_frames:
                        self.current_frame += 1
                    else:
                        self.current_action = "idle1"
                        self.current_frame = 0
                    self.attack_frame_counter = 0

    def check_wall_collision(self, tiles, x_offset):
        future_rect = pygame.Rect(self.rect.x + x_offset, self.rect.y, 60, 60)  # Kích thước 60x80
        for tile in tiles:
            if future_rect.colliderect(tile.rect):
                return True
        return False

    def check_edge(self, tiles, direction):
        x_check = self.rect.centerx + (direction * tile_size // 2)
        y_check = self.rect.bottom + 5
        for tile in tiles:
            if tile.rect.collidepoint(x_check, y_check):
                return False  
        return True

    def patrol(self, tiles):
        self.current_action = "walk1"

        if self.direction == "right":
            self.x_vel = -self.vel1
            if self.rect.x <= self.patrol_left or self.check_wall_collision(tiles, -self.vel) or self.check_edge(tiles, -1):
                self.direction = "left"
                self.x_vel = self.vel1

        elif self.direction == "left":
            self.x_vel = self.vel1
            if self.rect.x >= self.patrol_right or self.check_wall_collision(tiles, self.vel) or self.check_edge(tiles, 1):
                self.direction = "right"
                self.x_vel = -self.vel1

    def draw_health_bar2(self, screen, camera):
        """Vẽ thanh máu của Entity"""
        bar_width = 50  # Chiều rộng thanh máu
        bar_height = 10  # Chiều cao thanh máu
        fill = (self.health / 10) * bar_width  # Tính phần máu còn lại (giả sử máu tối đa là 10)
        self.fill_max = max(self.fill_max,fill)
        # Vị trí thanh máu (tính toán dựa trên vị trí của Entity và camera)
        bar_x = self.rect.x + (self.width // 2) - (bar_width // 2) + camera.camera.x - 60
        bar_y = self.rect.y + 40 + camera.camera.y  # Đặt thanh máu phía trên Entity

        # Vẽ viền thanh máu (màu đỏ)
        pygame.draw.rect(screen, "grey", (bar_x, bar_y, self.fill_max, bar_height))
        # Vẽ thanh máu bên trong (màu xanh)
        pygame.draw.rect(screen, "red", (bar_x, bar_y, fill, bar_height))