import pygame 
from map.SETTINGS import*
from GameOver.Button import*
back_button = Button(0,0,tile_size*3, tile_size*2,f"Upgrade/assets/back_button.png",button_upgrade)
upgrade_attack_button = Button(tile_size*5,tile_size*4,tile_size*20,tile_size*3,f"Upgrade/assets/upgrade_attack.png",button_upgrade)
upgrade_heard_button = Button(tile_size*5,tile_size*8,tile_size*20,tile_size*3,f"Upgrade/assets/upgrade_heart.png",button_upgrade)
upgrade_shield_button = Button(tile_size*5,tile_size*12,tile_size*20,tile_size*3,f"Upgrade/assets/upgrade_shield.png",button_upgrade)
points = 0 

def upgrade_character(screen,player, total_score,total_score_xpox):
        screen.blit(img_upgrade_bg,(0,0))
        screen.blit(img_bar_upgrade,(4*tile_size,0))
        screen.blit(img_gold,(27*tile_size,0))
        button_upgrade.draw(screen)
        
        font = pygame.font.Font(None, 52)
        screen.blit(font.render(f"{total_score}", True,"white"),(total_score_xpox,0))
        
        font_upgrade_index = pygame.font.Font(None,50)
        screen.blit(font_upgrade_index.render(f"{player.attack}", True,"Black"),(tile_size*15,5.1*tile_size))
        screen.blit(font_upgrade_index.render(f"{player.attack+1}", True,"Black"),(tile_size*18.5,5.1*tile_size))
        screen.blit(font_upgrade_index.render(f"{player.health}", True,"Black"),(tile_size*15,9.1*tile_size))
        screen.blit(font_upgrade_index.render(f"{player.health+1}", True,"Black"),(tile_size*18.5,9.1*tile_size))
        screen.blit(font_upgrade_index.render(f"{player.defense}", True,"Black"),(tile_size*15,13.1*tile_size))
        screen.blit(font_upgrade_index.render(f"{player.defense+1}", True,"Black"),(tile_size*18.5,13.1*tile_size))
def upgrade_logic(player, total_score):
    global points
    points =  total_score
    if upgrade_attack_button.is_pressed():
        if points-20 >= 0:
            points -= 20
            player.attack += 1                 
    elif upgrade_heard_button.is_pressed():
        if points-20 >= 0:
            points -= 20
            player.health += 1
    elif upgrade_shield_button.is_pressed():
        if points-20 >= 0:
            points -= 20
            player.defense += 1 
    if back_button.is_pressed():
        player.player_update = False

def calculate_total_score():
    return points