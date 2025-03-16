import pygame
from map.SETTINGS import tile_size, vel, FPS
from globals import*
from map.Environment import*
from GameOver import*
from players.entity import Entity
import os

class Player(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        self.rect = pygame.Rect(self.x, self.y, self.width - 13, self.height)
        self.SPRITES,self.Heart_Icon,self.Mana_Icon = self.load_sprite_sheets(scale)
        self.invincible_time = FPS # thời gian bất tử
        self.mana_max = mana + 20
        self.mana = self.mana_max
        self.mana_consumption = 0.1/FPS
        self.mana_increase = 1.8/FPS

        self.health_max = health
        self.health = self.health_max


        self.attack_count = 0
        self.ATTACK_DELAY = 6
        self.is_attacking = False

        self.is_running = False
        self.is_sliding = False
        self.SLIDE_DELAY = 3
        self.slide_timer_start = 0
        self.slide_duration = FPS*2
        self.slide_cooldown = FPS*30
        
        all_sprite.add(self)
    
    def load_sprite_sheets(self, scale_factor=1):
        path = r"assets\Character\Adventurer"
        all_sprites = {}

        for file_name in sorted(os.listdir(path)):
            if file_name.endswith(".png"):
                action = ''.join([char for char in file_name if not char.isdigit()]).replace(".png", "")
                if action not in all_sprites:
                    all_sprites[action] = []
                
                img = pygame.image.load(os.path.join(path, file_name))
                img = self.crop_sprite(img)
                if action == "SlideX":
                    img = pygame.transform.scale(img, (int(tile_size * scale_factor), int(tile_size * 1)))
                else:
                    img = pygame.transform.scale(img, (int(tile_size * scale_factor), int(tile_size * scale_factor)))
                

                all_sprites[action].append(img)

        # Load icon của Heart và Mana
        heart_path = r"assets/Attribute_Player/Heart"
        Heart_Icon = [pygame.transform.scale(self.crop_sprite(pygame.image.load(os.path.join(heart_path, f"Heart{i}.png"))),
                                            (tile_size * 1.2, tile_size * 1.2)) for i in range(2)]

        mana_path = r"assets/Attribute_Player/Mana"
        Mana_Icon = [pygame.transform.scale(self.crop_sprite(pygame.image.load(os.path.join(mana_path, f"Mana{i}.png"))),
                                            (tile_size * 1.2, tile_size * 1.2)) for i in range(4)]

        return all_sprites, Heart_Icon, Mana_Icon

    def move(self,dx,dy,tiles):
        dx,dy = self.checkcollision(tiles,dx,dy)
        
        self.rect.x += dx
        self.rect.y += dy
        
        self.is_running = False
    

    def attack_play(self):
        self.animation_count = 0
        self.attack_count += 1

        if self.attack_count == 1:
            self.action = "Attack"

        elif self.attack_count == 2:
            self.action = "Attackk"

        elif self.attack_count == 3:
            self.action = "Attackkk"
            self.attack_count = 0
        
        self.is_attacking = True

        hits = pygame.sprite.spritecollide(self, all_sprite_enemies, False)
        for enemy in hits:
            enemy.health -= 3

        
        self.mana -= self.mana_consumption
        if not self.action.startswith("Attack"):
            self.action = "Attack"
    
    def update_sprite(self):
        DELAY = self.RUN_DELAY if self.x_vel != 0 else self.ANIMATION_DELAY

        if self.action.startswith("Attack"):
            DELAY = self.ATTACK_DELAY

        if self.action == "Slide":
            DELAY = self.SLIDE_DELAY

        sprites = self.SPRITES[self.action]
        sprite_index = (self.animation_count // DELAY) % len(sprites)
        self.image = sprites[sprite_index]

        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)

        self.animation_count += 1

        if self.action == "Idlee" and self.mana < self.mana_max:
            self.mana += self.mana_increase

        
        if self.is_attacking:
            if self.animation_count >= len(sprites)*DELAY:
                self.animation_count = 0
                self.is_attacking = False

        if self.is_sliding:
            if pygame.time.get_ticks() - self.slide_timer_start > self.slide_duration:
                self.animation_count = 0
                self.is_sliding = False
                # self.rect.height = self.SCALE_FACTOR*tile_size
                

    
    def slide(self):
        self.animation_count = 0
        self.mana -= self.mana_consumption
        self.action = "Slide"
        self.is_sliding = True
        self.slide_timer_start = pygame.time.get_ticks()

        # self.rect.height = tile_size
        


    def update(self, tiles):
        self.x_vel = 0

        # Update Gravity
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.x > vel:
            self.move_left(vel)
            self.mana -= self.mana_consumption
            self.action = "Run"
            self.is_running = True

            if self.is_attacking:
                self.action = "Attack"

            if self.is_sliding == True:
                self.action = "Slide"
            
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.x < 150 * tile_size:
            self.move_right(vel)
            self.mana -= self.mana_consumption
            self.action = "Run"
            self.is_running = True

            if self.is_attacking:
                self.action = "Attack"

            if self.is_sliding == True:
                self.action = "Slide"
            

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and not self.isJump and not self.is_sliding:
            self.jump()
            self.mana -= self.mana_consumption
            self.action = "Jump"

            if self.is_attacking:
                self.action = "Attack"
        
        if keys[pygame.K_f] and not self.is_attacking:
            self.attack_play()

        if pygame.time.get_ticks() > self.slide_timer_start + self.slide_cooldown:
            if keys[pygame.K_LSHIFT] and not self.isJump:
                self.slide()
                
        
        if self.is_sliding:
            if self.direction == "right":
                self.move_right(2*vel)
            else:
                self.move_left(2*vel)
                
        if not self.is_attacking and not self.is_running and not self.is_sliding:
            self.action = "Idlee"

        if self.mana < 0:
            self.action = "Idlee"
            self.x_vel = 0
            self.mana = max(-2,self.mana)

        self.move(self.x_vel, self.y_vel, tiles)
        self.update_sprite()

    
    def checkcollision(self, tiles, x, y):
        dx, dy = x, y

        for tile in tiles:
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) and isinstance(tile, Ground):
                dx = 0
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) and (isinstance(tile, Grass) or isinstance(tile, Tree)):
                self.vel = 1.5*vel
            else:
                self.vel = vel

            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height) and (isinstance(tile, Ground) or isinstance(tile, Water)):
                if isinstance(tile, Water):
                    self.game_over = True
                else:
                    if self.y_vel < 0:  # Nhân vật đang nhảy lên
                        dy = tile.rect.bottom - self.rect.top
                        self.y_vel = 0  # Dừng lại khi chạm trần

                    elif self.y_vel >= 0:  # Nhân vật đang rơi xuống
                        
                        dy = tile.rect.top - self.rect.bottom
                        self.y_vel = 0  # Dừng lại khi chạm đất
                        self.jump_count = 0  # Reset jump count khi chạm đất
                        self.isJump = False  # Đặt lại trạng thái nhảy
        
        return dx, dy

    def draw_bar(self, screen, camera):

        bar_width = tile_size*6 + (self.health_max/health)*tile_size
        bar_height = tile_size/2
        fill = (self.health / health) * bar_width

        # Vị trí thanh máu
        bar_x_health = (self.width // 2) - (bar_width // 2) + tile_size*3.5
        bar_y_health = tile_size*1.2/2

        # Vẽ viền thanh máu (red)
        pygame.draw.rect(screen, ("grey"), (bar_x_health, bar_y_health, bar_width, bar_height))
        # Vẽ thanh máu bên trong (green)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x_health, bar_y_health, fill, bar_height))
        # Vẽ viền ngoài thanh máu (black)
        pygame.draw.rect(screen, (0, 0, 0), (bar_x_health, bar_y_health, bar_width, bar_height),1)

        
        bar_width = tile_size*6 + (self.mana_max / mana)*tile_size
        bar_x_mana = (self.width // 2) - (bar_width // 2) + tile_size*3.5
        bar_y_mana = tile_size*2
        fill = (self.mana / self.mana_max) * bar_width

        # Vẽ viền thanh mana (white)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x_mana, bar_y_mana, bar_width, bar_height))
        # Vẽ thanh mana bên trong (blue)
        pygame.draw.rect(screen, (0, 0, 255), (bar_x_mana, bar_y_mana, fill, bar_height))
        # Vẽ viền ngoài thanh mana (black)
        pygame.draw.rect(screen, (0, 0, 0), (bar_x_mana, bar_y_mana, bar_width, bar_height),1)


        if self.health >= health/2:
            screen.blit(self.Heart_Icon[0],(0,0))
        else:
            screen.blit(self.Heart_Icon[1],(0,0))
        if self.rect.y >= 17*tile_size:
            self.game_over = True

        index = int((1 - self.mana / self.mana_max) * 4)
        index = min(index, 3)  # Đảm bảo không vượt quá 3

        screen.blit(self.Mana_Icon[index],(0,tile_size*1.5))

