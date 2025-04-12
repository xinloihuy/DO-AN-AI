import pygame
from map.SETTINGS import tile_size, vel, FPS
from globals import*
from map.Environment import*
from GameOver import*
from players.entity import Entity

class Player(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, scale)
        self.SPRITES,self.Heart_Icon,self.Mana_Icon = self.load_sprite_sheets(scale)
        self.invincible_time = FPS # thời gian bất tử
        self.mana = mana
        self.mana_consumption = 7/FPS
        self.mana_increase = 1.2/FPS
        
    def load_sprite_sheets(self, scale_factor=1):
        path = f"assets\Character\Adventurer"
        all_sprites = {
            "Idle": [pygame.transform.scale(self.crop_sprite(pygame.image.load(f"{path}/Idlee{i}.png")),(int(tile_size * scale_factor), int(tile_size * scale_factor))) \
                    for i in range(0, 4)],
            "Run": [pygame.transform.scale(self.crop_sprite(pygame.image.load(f"{path}/Run{i}.png")), (int(tile_size * scale_factor), int(tile_size * scale_factor))) \
                    for i in range(0, 6)],
            "Jump": [pygame.transform.scale(self.crop_sprite(pygame.image.load(f"{path}/Jump{i}.png")), (int(tile_size * scale_factor), int(tile_size * scale_factor))) \
                    for i in range(0, 4)]
        }
        path = r"assets/Attribute_Player/Heart"
        Heart_Icon = [pygame.transform.scale(self.crop_sprite(pygame.image.load(f"{path}/Heart{i}.png")),(tile_size*1.2, tile_size*1.2)) \
                    for i in range(0, 2)]

        path = r"assets/Attribute_Player/Mana"
        Mana_Icon = [pygame.transform.scale(self.crop_sprite(pygame.image.load(f"{path}/Mana{i}.png")),(tile_size*1.2, tile_size*1.2)) \
                    for i in range(0, 4)]
        return all_sprites,Heart_Icon,Mana_Icon

    def update_sprite(self):
        super().update_sprite()
        self.action = "Idle"

        if self.action == "Idle" and self.mana < mana:
            self.mana += self.mana_increase

    def update(self, tiles):
        self.x_vel = 0

        # Update Gravity
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        # Handle player input
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.x > vel:
            self.move_left(vel)
            self.mana -= self.mana_consumption

        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.x < 150 * tile_size:
            self.move_right(vel)
            self.mana -= self.mana_consumption
            
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and not self.isJump:
            self.jump()
            self.isJump = True
            self.animation_count = 0
            self.mana -= self.mana_consumption

        if not (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.jump_count > 1:
            self.isJump = False

        # Move and update sprite
        if self.mana < 0:
            self.x_vel = 0
            self.mana = max(-2,self.mana)
        
        self.move(self.x_vel, self.y_vel, tiles)
        self.update_sprite()

    def draw_bar(self, screen, camera):
        """Vẽ thanh máu của Player"""

        bar_width = tile_size*6  # Chiều rộng thanh máu
        bar_height = tile_size/2  # Chiều cao thanh máu
        fill = (self.health / health) * bar_width  # Tính phần máu còn lại (giả sử máu tối đa là 10)

        # Vị trí thanh máu
        bar_x_health = (self.width // 2) - (bar_width // 2) + tile_size*3.5
        bar_y_health = tile_size*1.2/2

        # Vẽ viền thanh máu (red)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x_health, bar_y_health, bar_width, bar_height))
        # Vẽ thanh máu bên trong (green)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x_health, bar_y_health, fill, bar_height))
        # Vẽ viền ngoài thanh máu (black)
        pygame.draw.rect(screen, (0, 0, 0), (bar_x_health, bar_y_health, bar_width, bar_height),1)

        bar_x_mana = (self.width // 2) - (bar_width // 2) + tile_size*3.5
        bar_y_mana = tile_size*2
        fill = (self.mana / mana) * bar_width
        # Vẽ viền thanh mana (white)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x_mana, bar_y_mana, bar_width, bar_height))
        # Vẽ thanh mana bên trong (blue)
        pygame.draw.rect(screen, (0, 0, 255), (bar_x_mana, bar_y_mana, fill, bar_height))
        # Vẽ viền ngoài thanh mana (black)
        pygame.draw.rect(screen, (0, 0, 0), (bar_x_mana, bar_y_mana, bar_width, bar_height),1)


        if self.health >= health/2:
            screen.blit(self.Heart_Icon[0])
        else:
            screen.blit(self.Heart_Icon[1])

        index = int((1 - self.mana / mana) * 4)
        index = min(index, 3)  # Đảm bảo không vượt quá 3

        screen.blit(self.Mana_Icon[index],(0,tile_size*1.5))

