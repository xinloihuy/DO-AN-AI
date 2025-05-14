import pygame
from map.SETTINGS import tile_size, vel, FPS
from globals import *
from Enemies.enemy_diep import Enemy
import os
from os import listdir
from os.path import isfile, join

class EnemyBoss(Enemy):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        self.SPRITES = self.load_sprite_sheets(scale)
        self.health = 50
        self.health_max = 50
        self.fill_max_health = 0
        self.vel1 = 2

        # Phạm vi di chuyển của kẻ địch
        self.move_range = tile_size * 7

        self.attack = 0.5
        
        self.attack_frame_delay = 3  # Giảm tốc độ frame khi chém

    def update(self, tiles, player):
        # Áp dụng trọng lực
        if self.current_action == "death1":
            self.update_sprite()
            return
        
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        distance_x = abs(self.rect.centerx - player.rect.centerx)
        distance_y = abs(self.rect.centery - player.rect.centery)
        attack_range = 150  # Phạm vi tấn công (50 pixel)
        attack_rangey = 90

        # Kiểm tra nếu nhân vật trong phạm vi tấn công
        if distance_x <= attack_range and distance_y <= attack_rangey:
            self.x_vel = 0

            player_x = player.rect.centerx
            boss_x = self.rect.centerx

            if player_x < boss_x:
                self.direction = "left"
            else:
                self.direction = "right"
            
            # Nếu chưa ở trạng thái Attack, bắt đầu chém
            if self.current_action != "Attack":
                self.current_action = "Attack"
                self.current_frame = 0  # Reset frame về 0 khi bắt đầu chém
                self.attack_frame_counter = 0  # Reset bộ đếm frame attack

            # Khi hoàn thành animation chém, gây sát thương rồi chờ tiếp
            if self.current_frame >= len(self.SPRITES["Attack"]) - 1:
                if self.time_to_attack == 0:
                    self.attack_player(player)
                    self.time_to_attack = FPS // 2  # Delay trước khi chém tiếp

            # Đếm thời gian giữa các đòn chém
            if self.time_to_attack > 0:
                self.time_to_attack -= 1  

        else:
            # Khi không va chạm, quay lại tuần tra
            self.current_action = "Run"
            self.patrol(tiles)
            
        if self.health <= 0 and self.current_action != "death1":
            self.current_action = "death1"
            self.current_frame = 0
            self.x_vel = 0
            self.y_vel = 0

        # if self.health < 0:
        #     self.rect.x = -1000
        #     self.rect.y = -1000

        if player.game_over:
            self.rect.topleft = (self.x, self.y)
            self.x_vel = 0
            self.y_vel = 0
            self.current_action = "Idle"
            self.current_frame = 0
            self.health = self.health_max
        

        # Cập nhật vị trí và sprite
        self.move(self.x_vel, self.y_vel, tiles)
        self.update_sprite()

    def load_sprite_sheets(self, scale_factor=2):
        base_path = r"assets/Enemy/Boss"
        all_sprites = {}

        actions = ["Idle", "Run", "Attack", "death1", "take_hit1"]
        
        for action in actions:
            action_path = os.path.join(base_path, action)
            
            if not os.path.exists(action_path):  
                continue

            files = sorted([f for f in listdir(action_path) if isfile(join(action_path, f)) and f.endswith(".png")])
            all_sprites[action] = []

            for file in files:
                image = self.load_transparent_image(join(action_path, file))
                width = int(tile_size * scale_factor * 2)
                height = int(tile_size * scale_factor)
                image = pygame.transform.scale(image, (width, height))
                
                all_sprites[action].append(image)

        return all_sprites

    def check_wall_collision(self, tiles, x_offset):
        future_rect = pygame.Rect(self.rect.x + x_offset, self.rect.y, 60, 80)  # Kích thước 60x80
        for tile in tiles:
            if future_rect.colliderect(tile.rect):
                return True
        return False


    def draw_health_bar2(self, screen, camera):
        """Vẽ thanh máu của Boss"""
        bar_width = 50  # Chiều rộng thanh máu
        bar_height = 10  # Chiều cao thanh máu
        fill = (self.health / 10) * bar_width  # Tính phần máu còn lại (giả sử máu tối đa là 10)
        self.fill_max_health = max(self.fill_max_health,fill)
        # Vị trí thanh máu (tính toán dựa trên vị trí của Entity và camera)
        bar_x = self.rect.x + (self.width // 2) - (bar_width // 2) + camera.camera.x - 20
        bar_y = self.rect.y + camera.camera.y  # Đặt thanh máu phía trên Entity

        # Vẽ viền thanh máu (màu đỏ)
        pygame.draw.rect(screen, "grey", (bar_x, bar_y, self.fill_max_health, bar_height))
        # Vẽ thanh máu bên trong (màu xanh)
        pygame.draw.rect(screen, "red", (bar_x, bar_y, fill, bar_height))