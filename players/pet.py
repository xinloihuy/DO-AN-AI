import pygame
from players.entity import Entity
from map.SETTINGS import tile_size, vel, FPS
from globals import*
from map.Environment import*
import os
from collections import deque
from enum import Enum
import sys
import random
sys.setrecursionlimit(1000000)

class PathAlgo(Enum):
    BFS = 1
    AND_OR = 2
    BACKTRACK = 3


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
        vel = 3.5
        self.is_running = False

        self.player = player
        self.target = None
        self.path = []
        self.move_up = False
        self.move_down = False

        self.pathfinding_strategy = self.find_path_bfs  # Mặc định dùng BFS

        self.selected_algo = PathAlgo.BFS
        self.font = pygame.font.SysFont("Courier New", 20)
        
        # Định nghĩa vùng nút
        self.buttons = {
            PathAlgo.BFS: pygame.Rect(tile_size*10, tile_size/2, 120, 30),
            PathAlgo.AND_OR: pygame.Rect(tile_size*15, tile_size/2, 120, 30),
            PathAlgo.BACKTRACK: pygame.Rect(tile_size*20, tile_size/2, 120, 30),
        }
        self.search_radius = 1000  # Bán kính tìm kiếm cho thuật toán AND-OR và BACKTRACK

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
        current_time = pygame.time.get_ticks()
        # if not hasattr(self, 'last_pathfind_time'):
        #     self.last_pathfind_time = 0

        # # Only execute pathfinding if enough time has passed (1000ms)
        # if current_time - self.last_pathfind_time < 1000:
        #     return

        if self.distance_to(self.player) > 350 and self.player.action != "Idlee":
            self.target = self.player
            if self.distance_to(self.player) > tile_size:
                self.path = self.pathfinding_strategy(self.player.rect.center)
                self.last_pathfind_time = current_time
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
                self.path = self.pathfinding_strategy(self.target.rect.center)
                self.last_pathfind_time = current_time
            else:
                self.target = self.player
                if self.distance_to(self.player) > tile_size*2:
                    self.path = self.pathfinding_strategy(self.player.rect.center)
                    self.last_pathfind_time = current_time
                else:
                    self.path = []

    def find_path_bfs(self, target_pos):
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

    def find_path_and_or_search(self, target_pos):
        start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        goal = (target_pos[0] // tile_size, target_pos[1] // tile_size)
        
        # Define search boundaries
        min_x = min(start[0], goal[0])
        max_x = max(start[0], goal[0])
        min_y = min(start[1], goal[1])
        max_y = max(start[1], goal[1])

        visited = []
        plan = []

        def or_search(current, depth):
            nonlocal plan
            if depth > self.search_radius or current in visited:
                return False
            if current == goal:
                return True
                
            visited.append(current)
            neighbors = [(x,y) for x,y in self.get_neighbors(current) 
                        if min_x <= x <= max_x and min_y <= y <= max_y]
            
            for nbr in neighbors:
                plan.append(nbr)
                if and_search([nbr], depth + 1):
                    return True
                plan.pop()
            visited.remove(current)
            return False

        def and_search(states, depth):
            nonlocal plan
            print(depth)
            if depth > self.search_radius:
                return False
            if all(s == goal for s in states):
                return True
                
            common_actions = []
            for s in states:
                neighbors = [(x,y) for x,y in self.get_neighbors(s)
                            if min_x <= x <= max_x and min_y <= y <= max_y]
                common_actions.extend(neighbors)
            
            for action in set(common_actions):
                next_states = []
                for s in states:
                    if action not in self.get_neighbors(s):
                        break
                    next_states.append(action)
                else:
                    plan.append(action)
                    if or_search(action, depth + 1):
                        return True
                    plan.pop()
            return False

        if not self.is_obstacle(goal) and or_search(start, 0):
            return [(x * tile_size, y * tile_size) for x, y in plan]
        return self.avoid_obstacle()

    def find_path_backtracking(self, target_pos):
        start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        goal = (target_pos[0] // tile_size, target_pos[1] // tile_size)

        # Define search boundaries
        min_x = min(start[0], goal[0])
        max_x = max(start[0], goal[0])
        min_y = min(start[1], goal[1])
        max_y = max(start[1], goal[1])

        visited = set()
        path = []
        
        def backtrack(current, depth=0):
            nonlocal path
            if current == goal:
                return True
            if depth >= self.search_radius or current in visited:
                return False
                
            visited.add(current)
            neighbors = [(x,y) for x,y in self.get_neighbors(current)
                        if min_x <= x <= max_x and min_y <= y <= max_y]
            
            for nbr in neighbors:
                path.append(nbr)
                if backtrack(nbr, depth + 1):
                    return True
                path.pop()
            visited.remove(current)
            return False

        if not self.is_obstacle(goal) and backtrack(start):
            return [(x * tile_size, y * tile_size) for x, y in path]
        return self.avoid_obstacle()



    def get_neighbors(self, pos):
        """
        Trả về danh sách các vị trí xung quanh nhưng chỉ nếu không bị vật cản.
        """
        x, y = pos
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        # random.shuffle(neighbors)
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
                ty = self.player.rect.centery  # Y offset cho player

        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery

        dist = max(1, (dx**2 + dy**2)**0.5)
        dx /= dist
        dy /= dist

        # Ensure equal velocity in both directions
        self.x_vel = dx * vel
        self.is_running = abs(dx) > 0.1  # Set running state based on horizontal movement
        
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
        self.attack_cooldown = FPS  # Khoảng thời gian chờ trước khi tấn công tiếp

        hits = pygame.sprite.spritecollide(self, all_sprite_enemies, False)
        for enemy in hits:
            enemy.health -= self.attack

    def set_pathfinding_algo(self, algo: PathAlgo):
        self.selected_algo = algo
        if algo == PathAlgo.BFS:
            self.pathfinding_strategy = self.find_path_bfs
        elif algo == PathAlgo.AND_OR:
            self.pathfinding_strategy = self.find_path_and_or_search
        elif algo == PathAlgo.BACKTRACK:
            self.pathfinding_strategy = self.find_path_backtracking

    def handle_click(self, pos):
        for algo, rect in self.buttons.items():
            if rect.collidepoint(pos):
                self.set_pathfinding_algo(algo)
                print(f"Switched to: {algo.name}")

    def draw_3_button(self, screen):
        # Vẽ các nút chọn thuật toán
        for algo, rect in self.buttons.items():
            color = (0, 200, 0) if algo == self.selected_algo else (100, 100, 100)
            pygame.draw.rect(screen, color, rect)
            text = self.font.render(algo.name, True, (255, 255, 255))
            screen.blit(text, (rect.x + 5, rect.y + 5))
