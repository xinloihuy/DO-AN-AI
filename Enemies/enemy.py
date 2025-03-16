
import pygame
from map.SETTINGS import tile_size, vel, FPS
from globals import*
from players.entity import Entity
from os import listdir
from os.path import isfile, join, splitext

class Enemy(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        self.SPRITES = self.load_sprite_sheets(scale)
        self.vel = 3

        # Phạm vi di chuyển của kẻ địch
        self.move_range = tile_size*2 
        self.patrol_left = self.x - self.move_range
        self.patrol_right = self.x + self.move_range
        self.patrolling = True


        #attack dame
        self.attack = 2.5
        self.time_to_attack = 0

    

    def load_sprite_sheets(self, scale_factor=1):
        path = r"assets\Enemy\Saber"
        all_sprites = {}

        actions = {
            "Idle": 9,
            "Run": 6,
            "Attack": 12
        }

        for action, frames in actions.items():
            all_sprites[action] = []
            for i in range(frames):
                image = self.load_transparent_image(f"{path}/{action}{i}.png")
                image = self.crop_sprite(image)
                image = pygame.transform.scale(image, (int(tile_size * scale_factor), int(tile_size * scale_factor)))
                all_sprites[action].append(image)

        return all_sprites

    def move(self, x_vel, y_vel, tiles):
        dx,dy = self.checkcollision(tiles,x_vel,y_vel)
        # self.x += dx
        self.rect.x += dx
        self.rect.y += dy
        
    def update(self, tiles, player):
        # Update Gravity
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        # Di chuyển tự động trong phạm vi nhất định
        if self.patrolling:
            if self.direction == "left":
                self.x_vel = -self.vel
                if self.rect.x <= self.patrol_left:
                    self.direction = "right"
                    self.x_vel = self.vel

            elif self.direction == "right":
                self.x_vel = self.vel
                if self.rect.x >= self.patrol_right:
                    self.direction = "left"
                    self.x_vel = -self.vel

        # Cập nhật vị trí và sprite
        self.move(self.x_vel, self.y_vel, tiles)
        self.check_collision_with_player(player)
        self.update_sprite()



    def check_collision_with_player(self, player):
        """Kiểm tra va chạm với nhân vật và gây sát thương nếu có"""
        if self.rect.colliderect(player.rect) and self.time_to_attack >= player.invincible_time:
            player.health -= max(0, self.attack - player.defense)  # Giảm máu của nhân vật
            self.time_to_attack = 0
            if player.health <= 0:
                player.game_over = True
        if self.time_to_attack < player.invincible_time:
            self.time_to_attack += 1
        #print(self.time_to_attack)
