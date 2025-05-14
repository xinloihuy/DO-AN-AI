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
        self.SPRITES,self.Heart_Icon,self.Mana_Icon,self.Skill_Icon = self.load_sprite_sheets(scale)
        
        self.mana_max = mana + 20
        self.mana = self.mana_max
        self.mana_consumption = self.mana_max/10
        self.out_of_mana = False
        self.out_of_mana_time = 0

        self.health_max = health
        self.health = self.health_max
        self.last_health = self.health_max

        self.attack = damage
        self.attack_count = 0
        self.ATTACK_DELAY = 6
        self.is_attacking = False

        self.is_running = False

        self.is_life_steal = False
        self.resistance = 0
        self.double_gold = False

        self.skill_durations_run = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
        }

        self.skill_durations = {
            0: 5000,
            1: 5000,
            2: 5000,
            3: 5000,
            4: 8000,
        }

        self.COOL_DOWN = 1000*10 # 10 giây

        self.skill_cooldowns = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
        }

        self.skill_cooldown_durations = {
            0: self.COOL_DOWN,
            1: self.COOL_DOWN,
            2: self.COOL_DOWN,
            3: self.COOL_DOWN,
            4: self.COOL_DOWN,
        }

        self.sfx = {
                        "attack1": pygame.mixer.Sound("assets/Sound_Effect/attack_knight.wav"),
                        "attack2": pygame.mixer.Sound("assets/Sound_Effect/attack_knight2.wav"),
                        "coin": pygame.mixer.Sound("assets/Sound_Effect/coin.wav"),
                        "die": pygame.mixer.Sound("assets/Sound_Effect/die_knight.wav"),
                        "hurt": pygame.mixer.Sound("assets/Sound_Effect/hurt_knight.wav"),
                        "jump": pygame.mixer.Sound("assets/Sound_Effect/jump_knight.wav"),
                        "walk": pygame.mixer.Sound("assets/Sound_Effect/walk_knight.wav"),
                    }
        
        self.is_hurt = False

        
        all_sprite.add(self)
    
    def load_sprite_sheets(self, scale_factor=1):
        path = r"assets\Character\Armor"
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

        heart_path = r"assets/Attribute_Player/Heart"
        Heart_Icon = [pygame.transform.scale(self.crop_sprite(pygame.image.load(os.path.join(heart_path, f"Heart{i}.png"))),
                                            (tile_size * 1.2, tile_size * 1.2)) for i in range(2)]

        mana_path = r"assets/Attribute_Player/Mana"
        Mana_Icon = [pygame.transform.scale(self.crop_sprite(pygame.image.load(os.path.join(mana_path, f"Mana{i}.png"))),
                                            (tile_size * 1.2, tile_size * 1.2)) for i in range(4)]
        
        skill_path = r"assets/Attribute_Player/Skill"
        Skill_Icon = [pygame.transform.scale(self.crop_sprite(pygame.image.load(os.path.join(skill_path, f"Skill{i}.png"))),
                                            (tile_size * 1.5, tile_size * 1.5)) for i in range(5)]

        return all_sprites, Heart_Icon, Mana_Icon, Skill_Icon

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
            self.sfx["attack1"].play()

        elif self.attack_count == 2:
            self.action = "Attackk"
            self.sfx["attack1"].play()
            self.attack_count = 0


        # elif self.attack_count == 3:
        #     self.action = "Attackkk"
        #     self.attack_count = 0
        
        self.is_attacking = True

        hits = pygame.sprite.spritecollide(self, all_sprite_enemies, False)
        for enemy in hits:
            enemy.health -= self.attack
            if self.is_life_steal:
                self.health += self.attack*0.1
                self.health = min(self.health, self.health_max)

        if not self.action.startswith("Attack"):
            self.action = "Attack"
    
    def update_sprite(self):
        DELAY = self.RUN_DELAY if self.x_vel != 0 else self.ANIMATION_DELAY
        HURT_DELAY = 18
        if self.action.startswith("Attack"):
            DELAY = self.ATTACK_DELAY
        
        if self.action == "Attack" and self.is_hurt:
            self.action = "Attack"
        if self.action == "Attackk" and self.is_hurt:
            self.action = "Attackk"

        if self.action == "Jump" and self.is_hurt:
            self.animation_count = 0
            self.action = "Jump"
            self.is_hurt = False

        sprites = self.SPRITES[self.action]
        sprite_index = (self.animation_count // DELAY) % len(sprites)
        
        if self.action == "Hurt":
            sprite_index = (self.animation_count // HURT_DELAY) % len(sprites)
            if self.animation_count >= len(sprites)*HURT_DELAY:
                self.animation_count = 0
                self.is_hurt = False
                self.action = "Idle"
        
        self.image = sprites[sprite_index]

        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)

        self.animation_count += 1

        if self.action == "Jump":
            DELAY = self.ANIMATION_DELAY  # Đặt độ trễ cho animation Jump

        if self.is_attacking:
            if self.animation_count >= len(sprites)*DELAY:
                self.animation_count = 0
                self.is_attacking = False

    def update(self, tiles):
        if self.game_over == "True0":
            self.sfx["die"].play()
            self.game_over = True
        
        if self.game_over == True:
            return
        
        self.x_vel = 0

        # Update Gravity
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and not self.isJump:
            self.jump()
            self.action = "Jump"
            self.sfx["jump"].play()

            if self.is_attacking:
                self.action = "Attack"
            else:
                self.action = "Jump"

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.x > vel:
            self.move_left(vel)
            self.action = "Run"
            self.is_running = True

            if self.is_attacking:
                self.action = "Attack"
            
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.x < 150 * tile_size:
            self.move_right(vel)
            self.action = "Run"
            self.is_running = True

            if self.is_attacking:
                self.action = "Attack"
            
        current_time = pygame.time.get_ticks()

        if self.mana - self.mana_consumption >= 0:
            if keys[pygame.K_0] and current_time > self.skill_cooldowns[0]:
                self.skill_cooldowns[0] = current_time + self.skill_cooldown_durations[0]
                self.skill_durations_run[0] = current_time + self.skill_durations[0]
                self.attack = 1.3 * damage
                self.mana -= self.mana_consumption

            if self.skill_durations_run[0] < current_time:
                self.attack = damage

            if keys[pygame.K_1] and current_time > self.skill_cooldowns[1]:
                self.skill_cooldowns[1] = current_time + self.skill_cooldown_durations[1]
                self.skill_durations_run[1] = current_time + self.skill_durations[1]
                self.health += self.health_max * 0.3
                self.health = min(self.health, self.health_max)
                self.mana -= self.mana_consumption

            if keys[pygame.K_2] and current_time > self.skill_cooldowns[2]:
                self.skill_cooldowns[2] = current_time + self.skill_cooldown_durations[2]
                self.skill_durations_run[2] = current_time + self.skill_durations[2]
                self.is_life_steal = True
                self.mana -= self.mana_consumption
            
            if self.skill_durations_run[2] < current_time:
                self.is_life_steal = False

            if keys[pygame.K_3] and current_time > self.skill_cooldowns[3]:
                self.skill_cooldowns[3] = current_time + self.skill_cooldown_durations[3]
                self.skill_durations_run[3] = current_time + self.skill_durations[3]
                self.resistance = 0.1
                self.mana -= self.mana_consumption
            
            if self.skill_durations_run[3] < current_time:
                self.resistance = 0

            if keys[pygame.K_4] and current_time > self.skill_cooldowns[4]:
                self.skill_cooldowns[4] = current_time + self.skill_cooldown_durations[4]
                self.skill_durations_run[4] = current_time + self.skill_durations[4]
                self.double_gold = True
                self.mana -= self.mana_consumption

            if self.skill_durations_run[4] < current_time:
                self.double_gold = False
        else:
            if keys[pygame.K_0] or keys[pygame.K_1] or keys[pygame.K_2] or keys[pygame.K_3] or keys[pygame.K_4]:
                self.out_of_mana_time = pygame.time.get_ticks()
                self.out_of_mana = True

        if self.out_of_mana:
            current_time = pygame.time.get_ticks()
            if current_time - self.out_of_mana_time > 2000:
                self.out_of_mana = False
            
        
        if keys[pygame.K_f] and not self.is_attacking:
            self.attack_play()
                
        if not self.is_attacking and not self.is_running and not self.isJump and not self.is_hurt:
            self.action = "Idle"

        if self.isJump:
            self.action = "Jump"

        if self.last_health > self.health:
            self.action = "Hurt"
            self.sfx["hurt"].play()
            self.last_health = self.health
            self.is_hurt = True
        
        if self.health <= 1:
            self.game_over = "True0"
            self.animation_count = 0
            self.action = "Idle"
            self.is_hurt = False
        

        if self.rect.y >= 17*tile_size:
            self.game_over = "True0"
            

        self.move(self.x_vel, self.y_vel, tiles)
        self.update_sprite()

    
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

        index = int((1 - self.mana / self.mana_max) * 4)
        index = min(index, 3)  # Đảm bảo không vượt quá 3

        screen.blit(self.Mana_Icon[index],(0,tile_size*1.5))

    def draw_skill(self, screen):
        start = tile_size * 7
        skill_icon_spacing = tile_size * 4
        skill_icon_y = screen.get_height() - tile_size * 3

        for i in range(5):
            screen.blit(self.Skill_Icon[i], (start + i * skill_icon_spacing, skill_icon_y))
            font = pygame.font.SysFont("Courier New", 36)
            text = font.render(str(i), True, (255, 255, 255))
            text_rect = text.get_rect(center=(start + i * skill_icon_spacing + tile_size // 2 + 6, skill_icon_y - tile_size // 2))
            screen.blit(text, text_rect)
    
    def draw_skill_cooldowns(self, screen):
        font = pygame.font.SysFont("Courier New", 24)
        start = tile_size * 7
        skill_icon_spacing = tile_size * 4
        skill_icon_y = screen.get_height() - tile_size * 3

        current_time = pygame.time.get_ticks()

        for i in range(5):
            cooldown_remaining = max(0, (self.skill_cooldowns[i] - current_time)) // 1000  # Chuyển đổi sang giây
            if cooldown_remaining > 0:
                text = font.render(str(cooldown_remaining), True, (255, 0, 0))
                text_rect = text.get_rect(center=(start + i * skill_icon_spacing + tile_size // 2, skill_icon_y + tile_size // 2))
                screen.blit(text, text_rect)
    
    def draw_out_of_mana(self, screen, camera):
        font = pygame.font.SysFont("Arial", 16)
        text = font.render("Out of Mana!", True, "white")
        screen.blit(text, (self.rect.x + camera.camera.x - 10, self.rect.y - tile_size + camera.camera.y))