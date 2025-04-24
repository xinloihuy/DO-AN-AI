import pygame
from map.SETTINGS import tile_size, vel, FPS
from globals import*
from players.entity import Entity
import os
from map.Environment import*
from os import listdir
from os.path import isfile, join

class Enemy(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        self.SPRITES = self.load_sprite_sheets(scale)
        self.vel1 = 2
        self.health_max = 10

        # Phạm vi di chuyển của kẻ địch
        self.move_range = tile_size * 4
        self.patrol_left = self.x - self.move_range
        self.patrol_right = self.x + self.move_range
        self.patrolling = True
        self.direction = "left"

        # Attack
        self.attack = 0.3
        self.time_to_attack = 0
        
        self.current_frame = 0  # Bắt đầu từ frame 0
        self.current_action = "Idle"  # Trạng thái ban đầu

        self.frame_delay = 5  # Chỉ thay đổi frame mỗi 5 lần update
        self.frame_counter = 0  # Đếm số lần update
        
        self.attack_frame_delay = 5  # Giảm tốc độ frame khi chém
        self.attack_frame_counter = 0  # Bộ đếm frame của animation chém

        all_sprite_enemies.add(self)
    

    def load_sprite_sheets(self, scale_factor=1):
        base_path = r"assets\Enemy\Saber"
        all_sprites = {}

        actions = {
            "Idle": "đứng yên1",
            "Run": "chạy1",
            "Attack": "tấn công1"
        }

        for action, folder in actions.items():
            action_path = os.path.join(base_path, folder)
            
            if not os.path.exists(action_path):  
                continue

            files = sorted([f for f in listdir(action_path) if isfile(join(action_path, f)) and f.endswith(".png")])

            all_sprites[action] = []

            for file in files:
                image = self.load_transparent_image(join(action_path, file))
                # image = self.crop_sprite(image)
                image = pygame.transform.scale(image, (int(tile_size * scale_factor * 1.5), int(tile_size * scale_factor)))
                all_sprites[action].append(image)

        return all_sprites

    
    def attack_player(self, player, attack_speed=1):
        """Gây sát thương cho nhân vật khi gặp"""
        if self.time_to_attack == 0:
            damage = max(0, self.attack - player.defense - player.resistance)   
            player.health -= damage
            self.time_to_attack = FPS // attack_speed

            if player.health <= 0:
                player.game_over = True

    def update(self, tiles, player):
        # Áp dụng trọng lực
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        # Kiểm tra va chạm với nhân vật
        if self.rect.colliderect(player.rect):
            self.x_vel = 0  # Dừng di chuyển khi chạm nhân vật

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


        if self.health < 0:
            self.rect.x = -1000
            self.rect.y = -1000

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

    def update_sprite(self):
        if self.current_action in self.SPRITES:
            frames = self.SPRITES[self.current_action]
            max_frames = len(frames) - 1
            self.current_frame = min(self.current_frame, max_frames)
            self.image = frames[self.current_frame]
            
            self.rect = self.image.get_rect(center=self.rect.center) # thêm lúc nãy

            if self.direction == "left":
                self.image = pygame.transform.flip(self.image, True, False)

            if self.current_action == "Run":
                self.frame_counter += 1
                if self.frame_counter >= self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(frames)
                    self.frame_counter = 0
            elif self.current_action == "Attack":
                self.attack_frame_counter += 1
                if self.attack_frame_counter >= self.attack_frame_delay:
                    if self.current_frame < max_frames:
                        self.current_frame += 1
                    else:
                        self.current_action = "Idle"
                        self.current_frame = 0
                    self.attack_frame_counter = 0

    def check_wall_collision(self, tiles, x_offset):
        """Kiểm tra xem kẻ địch có bị kẹt vào tường không"""
        future_rect = self.rect.move(x_offset, 0)
        for tile in tiles:
            if future_rect.colliderect(tile.rect):
                return True
        return False

    def check_edge(self, tiles, direction):
        """Kiểm tra nếu kẻ địch sắp bước vào hố"""
        x_check = self.rect.centerx + (direction * tile_size // 2)
        y_check = self.rect.bottom + 5  # Kiểm tra phía trước chân

        for tile in tiles:
            if tile.rect.collidepoint(x_check, y_check):  # Có nền đất phía trước
                return False  
        return True  # Nếu không có nền đất, tức là hố, cần quay đầu

    def patrol(self, tiles):
        """Kẻ địch di chuyển tuần tra khi không thấy nhân vật"""
        self.current_action = "Run"  # Chạy khi tuần tra

        if self.direction == "left":
            self.x_vel = -self.vel1
            if self.rect.x <= self.patrol_left or self.check_wall_collision(tiles, -self.vel) or self.check_edge(tiles, -1):
                self.direction = "right"
                self.x_vel = self.vel1

        elif self.direction == "right":
            self.x_vel = self.vel1
            if self.rect.x >= self.patrol_right or self.check_wall_collision(tiles, self.vel) or self.check_edge(tiles, 1):
                self.direction = "left"
                self.x_vel = -self.vel1
        
    def draw_health_bar(self, screen, camera):
        """Vẽ thanh máu của Enemy"""
        bar_width = 50  # Chiều rộng thanh máu
        bar_height = 5  # Chiều cao thanh máu
        fill = (self.health / 10) * bar_width  # Tính phần máu còn lại (giả sử máu tối đa là 10)

        # Vị trí thanh máu (tính toán dựa trên vị trí của Entity và camera)
        bar_x = self.rect.x + (self.width // 2) - (bar_width // 2) + camera.camera.x + 20
        bar_y = self.rect.y + 15 + camera.camera.y

        # Vẽ viền thanh máu (màu đỏ)
        pygame.draw.rect(screen, "gray", (bar_x, bar_y, bar_width, bar_height))
        # Vẽ thanh máu bên trong (màu xanh)
        pygame.draw.rect(screen, "red", (bar_x, bar_y, fill, bar_height))
