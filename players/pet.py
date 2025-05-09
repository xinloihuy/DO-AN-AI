import pygame
from players.entity import Entity
from map.SETTINGS import tile_size, vel, FPS
from globals import*
from map.Environment import*
import os
from collections import deque

class Pet(Entity):
    def __init__(self, x, y, scale, player,map):
        super().__init__(x, y, scale)
        self.SPRITES = self.load_sprite_sheets(scale)
        self.ANIMATION_DELAY = 10
        self.game_map = map
        self.attack = 1
        self.is_attacking = False
        self.ATTACK_DELAY = 6
        self.attack_cooldown = 0

        global vel
        vel = 5.5
        self.is_running = False

        self.player = player
        self.target = None
        self.path = []
        self.move_up = False
        self.move_down = False

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

        # Update only every 3 frames to reduce CPU load
        if pygame.time.get_ticks() % 300 == 0:
            self.fall_count += 1
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if not self.path:
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
        """BFS pathfinding"""
        
        start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        goal = (target_pos[0] // tile_size, target_pos[1] // tile_size)
        
        # Thoát sớm nếu mục tiêu không thể tiếp cận
        if self.is_obstacle(goal):
            return self.avoid_obstacle()

        queue = deque([start])
        came_from = {start: None}
        
        # Limit iterations
        max_iterations = 4000
        iterations = 0

        while queue and iterations < max_iterations:
            iterations += 1
            current = queue.popleft()
            
            if current == goal:
                break
                
            for neighbor in self.get_neighbors(current):
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    queue.append(neighbor)
        
        # Reconstruct path if found
        if goal in came_from:
            path = []
            current = goal
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            # print(path)
            return [(pos[0] * tile_size, pos[1] * tile_size) for pos in path]
        
        return self.avoid_obstacle()

    def get_neighbors(self, pos):
        """
        Trả về danh sách các vị trí xung quanh nhưng chỉ nếu không bị vật cản.
        """
        x, y = pos
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [neighbor for neighbor in neighbors if not self.is_obstacle(neighbor)]

    def is_obstacle(self, pos):
        """
        Kiểm tra xem vị trí có phải là vật cản không.
        """
        x, y = pos
        for tile in self.game_map.obobstacle_coord:
            if tile.rect.colliderect(x * tile_size, y * tile_size, self.width, self.height):
                return True
        return False

    def avoid_obstacle(self):
        """
        Nếu Pet bị chặn, thử đi lên hoặc xuống để vượt qua.
        """
        if self.can_move(self.rect.x, self.rect.y - tile_size):  # Thử đi lên
            return [(self.rect.centerx, self.rect.centery - tile_size)]
        elif self.can_move(self.rect.x, self.rect.y + tile_size):  # Thử đi xuống
            return [(self.rect.centerx, self.rect.centery + tile_size)]
        return [(self.rect.centerx, self.rect.centery)]  # Nếu kẹt hoàn toàn, đứng im

    def can_move(self, x, y):
        """
        Kiểm tra xem vị trí mới có hợp lệ không (có bị chặn bởi vật cản không).
        """
        for tile in self.game_map.obobstacle_coord:
            if tile.rect.colliderect(x, y, self.width, self.height):
                return False
        return True

    def move_towards(self, target_pos):
        tx, ty = target_pos

        if len(self.path) < 9:
            if self.target == self.player:
                ty = self.player.rect.centery - 40  # Y offset cho player

        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery


        dist = max(1, (dx**2 + dy**2)**0.5)
        dx /= dist
        dy /= dist

        self.x_vel = dx * vel
        
        if len(self.path) < 7:
            self.y_vel = dy * vel
        else:
            future_x = self.rect.centerx + dx * tile_size
            future_y = self.rect.centery + dy * tile_size
            above_pos = (int(self.rect.centerx/tile_size), int(self.rect.centery/tile_size - 1))
            
            # Nếu có vật cản phía trước hoặc phía trên, thử các đường đi thay thế
            if self.is_obstacle((int(future_x/tile_size), int(future_y/tile_size))):
                if self.is_obstacle(above_pos):
                    # Nếu có vật cản cả phía trước và phía trên, thử đi xuống
                    self.y_vel = vel * 2.9
                    self.x_vel = 0
                else:
                    # Nếu không, quay ngược lại
                    self.x_vel = -dx * vel * 2
                    self.y_vel = -dy * vel * 2
                # Thử tìm 1 hướng mới
                self.find_target()
            else:
                self.x_vel = dx * vel
                self.y_vel = dy * vel

        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"

        # Kiểm tra xem Pet có gần đến vị trí đích không
        if dist < tile_size // 2:
            if self.path:
                self.path.pop(0)


    # def distance_to(self, entity):
    #     return abs(self.rect.centerx - entity.rect.centerx) + abs(self.rect.centery - entity.rect.centery)


    def distance_to(self, entity):
        dx = self.rect.centerx - entity.rect.centerx
        dy = self.rect.centery - entity.rect.centery
        return (dx*dx + dy*dy)**0.5  # Euclidean distance

    def attack_play(self):
        self.animation_count = 0
        self.action = "Attack"
        self.is_attacking = True
        self.attack_cooldown = FPS  # Khoảng thời gian chờ trước khi tấn công tiếp, có thể tùy chỉnh

        hits = pygame.sprite.spritecollide(self, all_sprite_enemies, False)
        for enemy in hits:
            enemy.health -= self.attack
