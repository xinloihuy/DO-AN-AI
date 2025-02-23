import pygame
import sys
sys.path.append('GAME')
from map.MAP import*
from map.SETTINGS import*
import random, math
from map.Environment import*
from globals import*
from players.player import*
from map.Camera import*
from Enemies.Rocket import*
from GameOver.Button import*
from Upgrade.assets import*
from utils import*# upgrade_character,upgrade_logic,calculate_total_score

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('name_game')

x = tile_size*0
y = tile_size*9
i=3
player = Player(0*tile_size,7*tile_size)
map = Map()
camera = Camera(cols*tile_size,rows*tile_size)
rocket = Rocket()


play_button = Button(tile_size*10.5,tile_size*6,tile_size*11,tile_size*2,f"GameOver/assets/try_again_button.png",button_game_over)
home_button = Button(tile_size*10.5,tile_size*9,tile_size*11,tile_size*2,f"GameOver/assets/home_button.png",button_game_over)
upgrade_button = Button(tile_size*10.5,tile_size*12,tile_size*11,tile_size*2,f"GameOver/assets/upgrade_button.png",button_game_over)





level = 1
levels = [0,1]
score = 0
total_score = 60
game_over = False
def next_map():
    global level, player,all_sprite,map 
    all_sprite.empty() 
    gold_group.empty()
    map = Map()
    random_level = random.randint(0,1)
    while True:
        if random_level != level:
            level = random_level
            break
        random_level = random.randint(0,1)
    map.load_csv(level)
    map.load_data()
    player = Player(0,7*tile_size)
    
def new(): 
    map.load_csv(level%2)
    map.load_data()
                
def update():
   
    player.update(map.obobstacle_coord)
    camera.update(player)


      
def draw():
    global score,total_score, level
    #player.game_over = True
    if player.game_over == False:
        screen.blit(img_sunset,(0,0))   
        screen.blit(img_wave,(0,12*tile_size-img_wave.get_height()))  
        screen.blit(img_gold,(screen_width-img_gold.get_width()-tile_size*2,0))   
        
        

        for sprite in all_sprite:
            if not isinstance(sprite,Rocket):
                screen.blit(sprite.image, camera.apply(sprite))
        
        if pygame.sprite.spritecollide(player, gold_group,True):
            score += 1
        font = pygame.font.Font(None, 50)
        screen.blit(font.render(f"X {score}", True,"white"),(screen_width - tile_size*2,0))
        
          
        rocket.check_rocket(screen,player,300,camera)
        if player.rect.x >= 149.5*tile_size:
            next_map()
            
       
    else:
        screen.blit(img_game_over,(0,0))
        button_game_over.draw(screen)
        if upgrade_button.is_pressed():
            player.player_update = True
      
        if play_button.is_pressed():
            player.game_over = False
            rocket.rect.x = -tile_size
            player.rect.x = 0
            player.rect.y = tile_size*7
            new()
        elif home_button.is_pressed():
            pass
    
    if player.player_update == True:

        total_score += score
        total_score_xpox = round(math.log(total_score,10) + 28)*tile_size if score != 0 else 28*tile_size
        upgrade_character(screen,player, total_score,total_score_xpox )
        upgrade_logic(player,total_score)
        total_score = calculate_total_score()


    pygame.display.flip()
    





run = True
new() 
while run:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

     
    update()
    draw()
  

pygame.quit()
