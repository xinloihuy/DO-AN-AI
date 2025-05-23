import pygame
from map.SETTINGS import tile_size, vel, FPS, cols, rows
from globals import*
from players.entity import Entity
import os
from map.Environment import*
from os import listdir
from os.path import isfile, join
from enum import Enum
import heapq
import random

class EnemyPathAlgo(Enum):
    ASTAR = 1
    SAHC = 2
    Q_LEARNING = 3


class Enemy(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        self.SPRITES = self.load_sprite_sheets(scale)
        self.vel1 = 2
        self.vel = self.vel1
        self.health_max = 10

        # Phạm vi di chuyển của kẻ địch
        self.move_range = tile_size * 4
        self.patrol_left = self.x - self.move_range
        self.patrol_right = self.x + self.move_range
        self.patrolling = True
        self.direction = "right"

        # Attack
        self.attack = 0.3
        self.time_to_attack = 0
        
        self.current_frame = 0  # Bắt đầu từ frame 0
        self.current_action = "Idle"  # Trạng thái ban đầu

        self.frame_delay = 5  # Chỉ thay đổi frame mỗi 5 lần update
        self.frame_counter = 0  # Đếm số lần update
        
        self.attack_frame_delay = 5  # Giảm tốc độ frame khi chém
        self.attack_frame_counter = 0  # Bộ đếm frame của animation chém
        
        self.selected_algo = EnemyPathAlgo.ASTAR
        Enemy.current_algorithm = EnemyPathAlgo.ASTAR
        self.font = pygame.font.SysFont("Courier New", 20)
        self.buttons = {
            EnemyPathAlgo.ASTAR: pygame.Rect(tile_size*10, tile_size*2, 120, 30),
            EnemyPathAlgo.SAHC: pygame.Rect(tile_size*15, tile_size*2, 120, 30),
            EnemyPathAlgo.Q_LEARNING: pygame.Rect(tile_size*20, tile_size*2, 120, 30),
        }
        self.path = []

        all_sprite_enemies.add(self)
    
    def draw_3_button(self, screen):
        for algo, rect in self.buttons.items():
            color = (0, 200, 0) if algo == self.selected_algo else (100, 100, 100)
            pygame.draw.rect(screen, color, rect)
            text = self.font.render(algo.name, True, (255, 255, 255))
            screen.blit(text, (rect.x + 5, rect.y + 5))

    def handle_click(self, pos):
        for algo, rect in self.buttons.items():
            if rect.collidepoint(pos):
                Enemy.current_algorithm = algo
                self.selected_algo = algo

    def find_path_astar(self, target_pos, tiles):
        start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        goal = (target_pos[0] // tile_size, target_pos[1] // tile_size)
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                break
            for neighbor in self.get_neighbors(current, tiles):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        if goal in came_from:
            path = []
            current = goal
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return [(pos[0] * tile_size, pos[1] * tile_size) for pos in path]
        return []

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # def find_path_sahc(self, target_pos, tiles):
    #     start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
    #     goal = (target_pos[0] // tile_size, target_pos[1] // tile_size)
    #     current = start
    #     path = [current]
    #     visited = set()
    #     max_steps = 100
    #     for _ in range(max_steps):
    #         if current == goal:
    #             break
    #         neighbors = [n for n in self.get_neighbors(current, tiles) if n not in visited]
    #         if not neighbors:
    #             break
    #         next_node = min(neighbors, key=lambda n: self.heuristic(n, goal))
    #         if self.heuristic(next_node, goal) >= self.heuristic(current, goal):
    #             break
    #         current = next_node
    #         path.append(current)
    #         visited.add(current)
    #     if current == goal:
    #         return [(pos[0] * tile_size, pos[1] * tile_size) for pos in path]
    #     return []

    # def find_path_q_learning(self, target_pos, tiles):
    #     start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
    #     goal = (target_pos[0] // tile_size, target_pos[1] // tile_size)
    #     current = start
    #     path = [current]
    #     visited = set()
    #     max_steps = 100
    #     for _ in range(max_steps):
    #         if current == goal:
    #             break
    #         neighbors = [n for n in self.get_neighbors(current, tiles) if n not in visited]
    #         if not neighbors:
    #             break
    #         current = random.choice(neighbors)
    #         path.append(current)
    #         visited.add(current)
    #     if current == goal:
    #         return [(pos[0] * tile_size, pos[1] * tile_size) for pos in path]
    #     return []
    
    def find_path_sahc(self, target_pos, tiles):
        start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        goal = (target_pos[0] // tile_size, target_pos[1] // tile_size)
        current = start
        path = [current]
        
        while current != goal:
            # Lấy các node lân cận
            neighbors = self.get_neighbors(current, tiles)
            if not neighbors:
                break
                
            # Tìm node lân cận tốt nhất
            current_score = self.heuristic(current, goal)
            best_neighbor = None
            best_score = float('inf')
            
            for neighbor in neighbors:
                score = self.heuristic(neighbor, goal)
                if score < best_score:
                    best_score = score
                    best_neighbor = neighbor
                    
            # Nếu không tìm được node tốt hơn, ta đã ở cực đại địa phương
            if best_score >= current_score:
                break
                
            current = best_neighbor
            path.append(current)
            
        return [(pos[0] * tile_size, pos[1] * tile_size) for pos in path]
    
    def find_path_q_learning(self, target_pos, tiles):
        start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        goal = (target_pos[0] // tile_size, target_pos[1] // tile_size)
        
        # Khởi tạo Q-table nếu chưa có
        if not hasattr(self, 'q_table'):
            self.q_table = {}
        
        # Các tham số
        alpha = 0.1  # Tỷ lệ học
        gamma = 0.9  # Hệ số giảm
        epsilon = 0.2  # Tăng tỷ lệ khám phá lên để đa dạng hơn
        
        current = start
        path = [current]
        visited = set([current])
        max_steps = 50  # Giảm số bước để tránh đường đi quá dài
        
        for _ in range(max_steps):
            if current == goal:
                break
                
            # Lấy các node lân cận chưa thăm
            neighbors = [n for n in self.get_neighbors(current, tiles) if n not in visited]
            if not neighbors:
                break
                
            # Khởi tạo Q-values cho trạng thái hiện tại
            if current not in self.q_table:
                self.q_table[current] = {n: 0 for n in neighbors}
                
            # Chọn hành động theo epsilon-greedy
            if random.random() < epsilon:
                next_state = random.choice(neighbors)
            else:
                # Ưu tiên di chuyển về phía goal
                next_state = min(neighbors, key=lambda n: self.heuristic(n, goal))
                    
            # Cập nhật path và các trạng thái đã thăm
            current = next_state
            path.append(current)
            visited.add(current)
            
            # Thoát sớm nếu đủ gần goal
            if self.heuristic(current, goal) <= 2:
                break
                
        return [(pos[0] * tile_size, pos[1] * tile_size) for pos in path]

    def find_path(self, target_pos, tiles):
        if Enemy.current_algorithm == EnemyPathAlgo.ASTAR:
            self.path = self.find_path_astar(target_pos, tiles)
        elif Enemy.current_algorithm == EnemyPathAlgo.SAHC:
            self.path = self.find_path_sahc(target_pos, tiles)
        elif Enemy.current_algorithm == EnemyPathAlgo.Q_LEARNING:
            self.path = self.find_path_q_learning(target_pos, tiles)
        else:
            self.path = []

    def get_neighbors(self, pos, tiles):
        x, y = pos
        neighbors = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < cols and 0 <= ny < rows:  # Sửa lại theo kích thước map của bạn
                if not self.is_obstacle((nx, ny), tiles):
                    neighbors.append((nx, ny))
        return neighbors

    def is_obstacle(self, pos, tiles):
        for tile in tiles:
            if (tile.rect.x // tile_size, tile.rect.y // tile_size) == pos:
                return True
        return False

    def load_sprite_sheets(self, scale_factor=1):
        base_path = r"assets\Enemy\Saber"
        all_sprites = {}

        actions = {
            "Idle": "đứng yên1",
            "Run": "chạy1",
            "Attack": "tấn công1",
            "death1": "chết1",
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
        if self.current_action == "death1":
            self.update_sprite()
            return

        # Apply gravity
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        # Reset velocity
        self.x_vel = 0

        # Check distance to player
        distance_x = abs(self.rect.centerx - player.rect.centerx)
        distance_y = abs(self.rect.centery - player.rect.centery)
        attack_range = 90

        # Handle death
        if self.health <= 0 and self.current_action != "death1":
            self.current_action = "death1"
            self.current_frame = 0
            self.x_vel = self.y_vel = 0
            self.move(self.x_vel, self.y_vel, tiles)
            self.update_sprite()
            return

        # Handle player game over
        if player.game_over:
            self.reset_state()
            return

        # Attack mode
        if distance_x <= attack_range and distance_y <= attack_range:
            self.handle_attack_mode(player)
        # Movement mode
        else:
            self.handle_movement_mode(player, tiles)

        # Apply movement and update sprite
        self.move(self.x_vel, self.y_vel, tiles)
        self.update_sprite()

    def handle_attack_mode(self, player):
        self.direction = "left" if player.rect.centerx < self.rect.centerx else "right"
        
        if self.current_action != "Attack":
            self.current_action = "Attack"
            self.current_frame = 0
            self.attack_frame_counter = 0

        if self.current_frame >= len(self.SPRITES["Attack"]) - 1:
            if self.time_to_attack == 0:
                self.attack_player(player)
                self.time_to_attack = FPS // 2

        if self.time_to_attack > 0:
            self.time_to_attack -= 1

    def handle_movement_mode(self, player, tiles):
        if self.selected_algo in [EnemyPathAlgo.ASTAR, EnemyPathAlgo.SAHC, EnemyPathAlgo.Q_LEARNING]:
            # Update path if needed
            if not self.path or self.should_update_path(player):
                self.find_path(player.rect.center, tiles)

            if self.path:
                self.follow_path(tiles)
            else:
                self.current_action = "Idle"
        else:
            self.patrol(tiles)

    def should_update_path(self, player):
        if not self.path:
            return True
        target_pos = self.path[-1]
        return (abs(target_pos[0] - player.rect.centerx) > tile_size or 
                abs(target_pos[1] - player.rect.centery) > tile_size)

    def follow_path(self, tiles):
        next_pos = self.path[0]
        
        # Check if reached current waypoint
        if abs(self.rect.centerx - next_pos[0]) < 100 and abs(self.rect.centery - next_pos[1]) < 100:
            self.path.pop(0)
            if not self.path:
                self.current_action = "Idle"
                return
            next_pos = self.path[0]

        # Calculate movement
        dx = next_pos[0] - self.rect.centerx
        self.direction = "right" if dx > 0 else "left"
        self.x_vel = self.vel1 if dx > 0 else -self.vel1

        # Handle obstacles
        if self.check_wall_collision(tiles, self.x_vel) or self.check_edge(tiles, 1 if dx > 0 else -1):
            if self.on_ground(tiles):
                self.y_vel = -12

        self.current_action = "Run"

    def reset_state(self):
        self.rect.topleft = (self.x, self.y)
        self.x_vel = self.y_vel = 0
        self.current_action = "Idle"
        self.current_frame = 0
        self.health = self.health_max
        
    def on_ground(self, tiles):
        self.rect.y += 1
        on_ground = any(self.rect.colliderect(tile.rect) for tile in tiles)
        self.rect.y -= 1
        return on_ground


    def update_sprite(self):
        if self.current_action in self.SPRITES:
            frames = self.SPRITES[self.current_action]
            max_frames = len(frames) - 1
            self.current_frame = min(self.current_frame, max_frames)
            self.image = frames[self.current_frame]
            
            self.rect = self.image.get_rect(center=self.rect.center) # thêm lúc nãy

            if self.direction == "left":
                self.image = pygame.transform.flip(self.image, True, False)
            else:
                self.image = pygame.transform.flip(self.image, False, False)
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
            elif self.current_action == "death1":
                self.attack_frame_counter += 1
                if self.attack_frame_counter >= self.attack_frame_delay:
                    if self.current_frame < max_frames:
                        self.current_frame += 1
                    else:
                        self.kill()
                        self.rect.topleft = (-1000, -1000)
                    self.attack_frame_counter = 0

    def check_wall_collision(self, tiles, x_offset):
        """Kiểm tra xem kẻ địch có bị kẹt vào tường không"""
        future_rect = self.rect.move(x_offset*1.2, tile_size)
        for tile in tiles:
            if future_rect.colliderect(tile.rect):
                return True
        return False

    def check_edge(self, tiles, direction):
        """Kiểm tra nếu kẻ địch sắp bước vào hố"""
        # Check point in front of enemy
        check_distance = tile_size * 1.5
        x_check = self.rect.centerx + (direction * check_distance)
        y_check = self.rect.bottom + 5

        # Kiểm tra có đất phía dưới điểm check không
        found_ground = False
        for tile in tiles:
            if tile.rect.collidepoint(x_check, y_check):
                found_ground = True
                break

        # Trả về True nếu không có đất (tức là có hố)
        return not found_ground

    def patrol(self, tiles):
        """Kẻ địch di chuyển tuần tra khi không thấy nhân vật"""
        self.current_action = "Run"  # Chạy khi tuần tra

        if self.direction == "left":
            self.x_vel = -self.vel1
            if self.rect.x <= self.patrol_left or self.check_wall_collision(tiles, -self.vel1) or self.check_edge(tiles, -1):
                self.direction = "right"
                self.x_vel = +self.vel1
 
        elif self.direction == "right":
            self.x_vel = +self.vel1
            if self.rect.x >= self.patrol_right or self.check_wall_collision(tiles, self.vel1) or self.check_edge(tiles, 1):
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
