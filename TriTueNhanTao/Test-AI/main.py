import pygame
import sys
sys.path.append('GAME')
from map.MAP import*
from map.SETTINGS import*
import random, math
from map.Environment import*
from globals import*
from players.player import*
from players.pet import*
from map.Camera import*
from Enemies.Rocket import*
from Enemies.enemy_diep import*
from Enemies.enemy_boss import*
from GameOver.Button import*
from Upgrade.assets import*
from utils import*# upgrade_character,upgrade_logic,calculate_total_score
from Enemies.Explosion import*
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('name_game')

x_player = tile_size*0
y_player = tile_size*9
x_enemy = tile_size*30
y_enemy = tile_size*5
x_pet = tile_size*0
y_pet = tile_size*6
x_enemyboss = tile_size*50
y_enemyboss = tile_size*10
coordinate_enemy_level = [(tile_size*30,tile_size*5),(128*tile_size,7*tile_size)]
coordinate_enemyboss_level = [(70*tile_size,7*tile_size),(tile_size*40,tile_size*5)]
i=3
player = Player(x_player,y_player,scale=1.5)
enemy = Enemy(x_enemy,y_enemy,scale=1.5)
pet = Pet(x_pet,y_pet,scale=0.5,player=player)
boss = EnemyBoss(x_enemyboss, y_enemyboss, scale=5)
map = Map()
camera = Camera(cols*tile_size,rows*tile_size)
rocket = Rocket()
explosion = Explosion()

play_button = Button(tile_size*10.5,tile_size*6,tile_size*11,tile_size*2,f"GameOver/assets/try_again_button.png",button_game_over)
home_button = Button(tile_size*10.5,tile_size*9,tile_size*11,tile_size*2,f"GameOver/assets/home_button.png",button_game_over)
upgrade_button = Button(tile_size*10.5,tile_size*12,tile_size*11,tile_size*2,f"GameOver/assets/upgrade_button.png",button_game_over)



level = 1
levels = [0,1,2]
score = 0
total_score = 60
game_over = False
def next_map():
    global level, player,all_sprite,map, enemy,x_enemy,y_enemy, all_sprite_enemies, pet, x_pet, y_pet,boss, x_enemyboss, y_enemyboss
    all_sprite.empty() 
    all_sprite_enemies.empty()
    enemies_group.empty()
    gold_group.empty()
    map = Map()
    random_level = random.randint(0,2)
    while True:
        if random_level != level:
            level = random_level
            break
        random_level = random.randint(0,2)
    map.load_csv(level)
    map.load_data()
    player = Player(0,7*tile_size,scale=1.5)
    pet = Pet(0,6*tile_size,scale=0.5,player=player)
    pos_enemy = coordinate_enemy_level[level]
    x_enemy = pos_enemy[0]
    y_enemy = pos_enemy[1]
    
    enemy = Enemy(x_enemy,y_enemy,scale=1.5)

    pos_enemyboss = coordinate_enemyboss_level[level]
    x_enemyboss = pos_enemyboss[0]
    y_enemyboss = pos_enemyboss[1]

    boss = EnemyBoss(x_enemyboss, y_enemyboss, scale=5)

def new(): 
    global score 
    map.load_csv(level)
    map.load_data()
    score = 0
                
def reset_game():
    global score, level, player, enemy, rocket, map, all_sprite, enemies_group, gold_group, all_sprite_enemies, pet

    # Reset các đối tượng trong game
    all_sprite.empty()
    all_sprite_enemies.empty()
    enemies_group.empty()
    gold_group.empty()

    # Giải phóng tài nguyên
    for sprite in all_sprite:
        sprite.kill()
    for sprite in all_sprite_enemies:
        sprite.kill()
    for sprite in enemies_group:
        sprite.kill()
    for sprite in gold_group:
        sprite.kill()

    player.health = 10

    # Tạo lại map và các đối tượng
    map = Map()
    map.load_csv(level=0)
    map.load_data()

    # Thêm các đối tượng vào nhóm sprite
    all_sprite.add(player)
    all_sprite.add(pet)
    all_sprite_enemies.add(enemy)
    enemies_group.add(rocket)
    
    player.health = player.health_max
    player.mana = player.mana_max

def update():
   
    player.update(map.obobstacle_coord)
    pet.update(map.obobstacle_coord)
    enemy.update(map.obobstacle_coord,player)
    boss.update(map.obobstacle_coord, player)
    camera.update(player)
    


      
def draw():
    global score,total_score, level
    #player.game_over = True
    screen.fill((0,0,0))
    if player.game_over == False:
        if map.level != 1:
            screen.blit(img_sunset,(0,0))   
            screen.blit(img_wave,(0,12*tile_size-img_wave.get_height())) 
        else:
            for i in range(0,1):
                screen.blit(img_mountains1,(i*50*tile_size,0))
                screen.blit(img_mountains2,(i*50*tile_size,0))
            # screen.blit(img_mountains1,(camera.x,0))
            # screen.blit(img_mountains2,(camera.x,0))  
         
        screen.blit(img_gold,(screen_width-img_gold.get_width()-tile_size*2,0))  

        for sprite in all_sprite:
            screen.blit(sprite.image, camera.apply(sprite))
            #pygame.draw.rect(screen,'white',camera.apply(sprite),1)
        
        for sprite in all_sprite_enemies:
            screen.blit(sprite.image, camera.apply(sprite))
            pygame.draw.rect(screen, 'white', camera.apply(sprite), 1)
        
        enemy.draw_health_bar(screen, camera)
        boss.draw_health_bar2(screen, camera)  # Vẽ thanh máu của boss
        player.draw_bar(screen, camera)
        
        if pygame.sprite.spritecollide(player, gold_group,True):
            score += 1
        
        font = pygame.font.Font(None, 50)
        screen.blit(font.render(f"X {score}", True,"white"),(screen_width - tile_size*2,0))
          
        rocket.check_rocket(screen,player,100,camera,explosion)
        if player.rect.x >= 149.5*tile_size:
            next_map()
            
    else:
        screen.blit(img_game_over,(0,0))
        button_game_over.draw(screen)
        if upgrade_button.is_pressed():
            total_score += score
            player.player_update = True   
      
        if play_button.is_pressed():
            player.game_over = False
            player.health = 10
            rocket.rect.x = -tile_size
            player.rect.x = 0
            player.rect.y = tile_size*7

            new()
        elif home_button.is_pressed():
            pass
    
    if player.player_update == True and upgrade_button.is_pressed()== False:

        
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
