import pygame
from map.SETTINGS import tile_size, vel, FPS
from globals import*
from players.entity import Entity
import os
from os import listdir
from os.path import isfile, join

class Enemy(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        self.SPRITES = self.load_sprite_sheets(scale)
        self.vel1 = 2

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
        
        self.attack_frame_delay = 4  # Giảm tốc độ frame khi chém
        self.attack_frame_counter = 0  # Bộ đếm frame của animation chém

        
    def load_transparent_image(self, path):
        img = pygame.image.load(path).convert()
        colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey)
        return img

    def crop_sprite(self, sprite):
        """Cắt vùng chứa nhân vật trong sprite và giữ transparency"""
        mask = pygame.mask.from_surface(sprite)
        rect = mask.get_bounding_rects()

        if rect:
            cropped = sprite.subsurface(rect[0]).copy()
            return cropped.convert_alpha()

        return sprite.convert_alpha()

    def load_sprite_sheets(self, scale_factor=1):
        base_path = r"assets\Enemy\Saber"
        all_sprites = {}

        actions = {
            "Idle": "đứng yên",
            "Run": "chạy",
            "Attack": "tấn công"
        }

        for action, folder in actions.items():
            action_path = os.path.join(base_path, folder)
            
            if not os.path.exists(action_path):  
                continue

            files = sorted([f for f in listdir(action_path) if isfile(join(action_path, f)) and f.endswith(".png")])

            all_sprites[action] = []

            for file in files:
                image = self.load_transparent_image(join(action_path, file))
                image = self.crop_sprite(image)
                image = pygame.transform.scale(image, (int(tile_size * scale_factor), int(tile_size * scale_factor)))
                all_sprites[action].append(image)

        return all_sprites

    def move(self, x_vel, y_vel, tiles):
        dx, dy = self.checkcollision(tiles, x_vel, y_vel)
        self.rect.x += dx
        self.rect.y += dy
    
    def attack_player(self, player):
        """Gây sát thương cho nhân vật khi gặp"""
        if self.time_to_attack == 0:  # Chỉ cho phép tấn công khi hết thời gian chờ
            damage = max(0, self.attack - player.defense)
            player.health -= damage
            self.time_to_attack = FPS    # Đặt thời gian chờ (1 giây nếu FPS=60)

            if player.health <= 0:
                player.game_over = True


        
    def update(self, tiles, player):
        # Áp dụng trọng lực
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        # Kiểm tra va chạm với nhân vật
        if self.rect.colliderect(player.rect):
            self.x_vel = 0  # Dừng di chuyển khi chạm nhân vật

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

        # Cập nhật vị trí và sprite
        self.move(self.x_vel, self.y_vel, tiles)
        self.update_sprite()


    def update_sprite(self):
        if self.current_action in self.SPRITES:
            frames = self.SPRITES[self.current_action]
            max_frames = len(frames) - 1
            self.current_frame = min(self.current_frame, max_frames)  # Đảm bảo không bị lỗi out of range

            self.image = frames[self.current_frame]  # Cập nhật hình ảnh

            if self.direction == "left":
                self.image = pygame.transform.flip(self.image, True, False)

            # 🔥 **Tăng frame khi chạy**
            if self.current_action == "Run":
                self.frame_counter += 1
                if self.frame_counter >= self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(frames)
                    self.frame_counter = 0  # Reset bộ đếm

            # 🔥 **Chậm frame khi chém**
            elif self.current_action == "Attack":
                self.attack_frame_counter += 1
                if self.attack_frame_counter >= self.attack_frame_delay:
                    if self.current_frame < max_frames:
                        self.current_frame += 1  # Chuyển frame tiếp theo
                    else:
                        self.current_action = "Idle"  # Trở lại trạng thái ban đầu
                        self.current_frame = 0
                    self.attack_frame_counter = 0  # Reset bộ đếm


 

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
        

