import pygame
from players.entity import Entity
from map.SETTINGS import tile_size, vel, FPS
from globals import*
from map.Environment import*
import os

class Pet(Entity):
    def __init__(self, x, y, scale, player):
        super().__init__(x, y, scale)
        self.SPRITES = self.load_sprite_sheets(scale)
        self.ANIMATION_DELAY = 10

        self.attack = 1
        self.is_attacking = False
        self.ATTACK_DELAY = 6
        self.attack_cooldown = 0

        global vel
        vel = 6
        self.is_running = False

        self.player = player
        self.target = None
        self.path = []

        all_sprite.add(self)

    def load_sprite_sheets(self, scale_factor=1):
        path = r"assets\Character\Pet"
        all_sprites = {}

        for file_name in sorted(os.listdir(path)):
            if file_name.endswith(".png"):
                action = ''.join([char for char in file_name if not char.isdigit()]).replace(".png", "")
                if action not in all_sprites:
                    all_sprites[action] = []
                
                img = pygame.image.load(os.path.join(path, file_name))
                img = self.crop_sprite(img)
                img = pygame.transform.scale(img, (int(tile_size * scale_factor), int(tile_size * scale_factor)))
                
                all_sprites[action].append(img)

        return all_sprites

    def update(self, tiles):
        self.x_vel = 0
        self.y_vel = 0

        # Update Gravity
        self.fall_count += 1

        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.find_target()
        if self.target != self.player and self.distance_to(self.target) < tile_size:
            if self.attack_cooldown == 0:
                self.attack_play()

        if self.path:
            next_pos = self.path.pop(0)
            self.move_towards(next_pos)

        if not self.is_attacking and not self.is_running:
            self.action = "Idle"

        self.move(self.x_vel, self.y_vel, tiles)
        self.update_sprite()

    def find_target(self):
        if self.distance_to(self.player) > 350 and self.player.action != "Idlee":
            self.target = self.player
            if self.distance_to(self.player) > tile_size:
                self.path = self.find_path_to(self.player.rect.center)
        else:
            self.target = None
            closest_enemy = None
            closest_distance = float('inf')
            for enemy in all_sprite_enemies:
                distance = self.distance_to(enemy)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_enemy = enemy

            if closest_enemy and closest_distance < tile_size*6:
                self.target = closest_enemy
                self.path = self.find_path_to(self.target.rect.center)
            else:
                self.target = self.player
                if self.distance_to(self.player) > tile_size*2:
                    self.path = self.find_path_to(self.player.rect.center)
                else:
                    self.path = []

    def find_path_to(self, target_pos):
        # Sử dụng thuật toán BFS để tìm đường đi
        start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        goal = (target_pos[0] // tile_size, target_pos[1] // tile_size)
        
        if not self.is_valid_pos(goal):
            return []  # Nếu đích không hợp lệ, trả về đường dẫn trống
        
        queue = [start]
        came_from = {start: None}

        while queue:
            current = queue.pop(0)
            if current == goal:
                break

            for neighbor in self.get_neighbors(current):
                if neighbor not in came_from:
                    queue.append(neighbor)
                    came_from[neighbor] = current

        if goal not in came_from:
            return []  # Nếu không tìm thấy đường, trả về đường dẫn trống

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]

        return [(pos[0] * tile_size, pos[1] * tile_size) for pos in path]

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [neighbor for neighbor in neighbors if self.is_valid_pos(neighbor)]

    def is_valid_pos(self, pos):
        x, y = pos
        return 0 <= x < cols and 0 <= y < rows #and not self.is_obstacle(pos)

    # def is_obstacle(self, pos):
    #     x, y = pos
    #     # Cần cập nhật điều kiện này phù hợp với map của bạn
    #     # Giả sử 1 là ô cản trở
    #     return self.map[y][x] == 1

    def move_towards(self, target_pos):
        tx, ty = target_pos
        
        # Đặt khoảng cách y cố định so với player
        target_y_offset = 40  # khoảng cách y cố định (có thể thay đổi)
        if self.target == self.player:
            ty = self.player.rect.centery - target_y_offset
        
        if self.rect.centerx < tx:
            self.move_right(vel)
        elif self.rect.centerx > tx:
            self.move_left(vel)
        if abs(self.rect.centery - ty) > 2:
            if self.rect.centery < ty:
                self.y_vel = vel
            elif self.rect.centery > ty:
                self.y_vel = -vel
        else:
            self.y_vel = 0

        # Dừng di chuyển nếu gần đến mục tiêu
        if abs(self.rect.centerx - tx) < tile_size*10 and abs(self.rect.centery - ty) < tile_size*8:
            self.path = []

    def distance_to(self, entity):
        return abs(self.rect.centerx - entity.rect.centerx) + abs(self.rect.centery - entity.rect.centery)

    def attack_play(self):
        self.animation_count = 0
        self.action = "Attack"
        self.is_attacking = True
        self.attack_cooldown = FPS  # Khoảng thời gian chờ trước khi tấn công tiếp, có thể tùy chỉnh

        hits = pygame.sprite.spritecollide(self, all_sprite_enemies, False)
        for enemy in hits:
            enemy.health -= self.attack
