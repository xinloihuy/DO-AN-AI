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
from Enemies.enemy_shark import*
from Enemies.enemy_thorn import *
from Enemies.enemy_chomper import *
from Enemies.Explosion import*
from GameOver.Button import*
from Upgrade.assets import*
from utils import*# upgrade_character,upgrade_logic,calculate_total_score

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('name_game')

x_player = tile_size*0#123
y_player = tile_size*5
x_enemy = tile_size*0
y_enemy = tile_size*5
x_pet = tile_size*0#123
y_pet = tile_size*5
x_enemyboss = tile_size*68
y_enemyboss = tile_size*5 
x_shark = tile_size*22
y_shark = tile_size*8
x_shark1 = tile_size*48
y_shark1 = tile_size*8
x_shark2 = tile_size*61
y_shark2 = tile_size*8
x_thorn = tile_size*3
y_thorn = tile_size*7.7
x_cayanthit = tile_size*80
y_cayanthit = tile_size*4

coordinate_enemy_level = [(tile_size*30,tile_size*5),(128*tile_size,7*tile_size),(tile_size*40,tile_size*5)]
coordinate_enemyboss_level = [(70*tile_size,7*tile_size),(tile_size*40,tile_size*5),(tile_size*40,tile_size*5)]
coordinate_shark_level = [
    [(tile_size*30, tile_size*5), (128*tile_size, 7*tile_size), (tile_size*40, tile_size*5)], 
    [(tile_size*22, tile_size*6), (tile_size*50, tile_size*7), (tile_size*60, tile_size*8)],
    [(tile_size*10, tile_size*4), (tile_size*35, tile_size*6), (tile_size*55, tile_size*9)]
]
coordinate_thorn_level = [(tile_size*30,tile_size*5),(128*tile_size,7*tile_size),(tile_size*40,tile_size*5)]

coordinate_cayanthit_level = [(tile_size*30,tile_size*5),(128*tile_size,7*tile_size),(tile_size*40,tile_size*5)]

i=3
map = Map()
player = Player(x_player,y_player,scale=1.5)
enemy = Enemy(x_enemy,y_enemy,scale=3)
pet = Pet(x_pet,y_pet,0.5,player,map=map)
boss = EnemyBoss(x_enemyboss, y_enemyboss, scale=5)
shark = Shark(x_shark, y_shark, scale=2)
shark1 = Shark(x_shark1, y_shark1, scale=2)
shark2 = Shark(x_shark2, y_shark2, scale=2)
thorn = Thorn(x_thorn, y_thorn, scale = 1.3)
cayanthit = Chomper(x_cayanthit, y_cayanthit, scale = 3)


camera = Camera(cols*tile_size,rows*tile_size)
rocket = Rocket()
explosion = Explosion()


play_button = Button(tile_size*10.5,tile_size*6,tile_size*11,tile_size*2,f"GameOver/assets/try_again_button.png",button_game_over)
home_button = Button(tile_size*10.5,tile_size*9,tile_size*11,tile_size*2,f"GameOver/assets/home_button.png",button_game_over)
upgrade_button = Button(tile_size*10.5,tile_size*12,tile_size*11,tile_size*2,f"GameOver/assets/upgrade_button.png",button_game_over)



level = 0
levels = [0,1,2]
score = 0
total_score = 60
game_over = False
def next_map():
    global level, player, map, enemy, pet, boss, thorn, cayanthit, all_sprite, all_sprite_enemies, enemies_group, gold_group
    global shark, shark1, shark2
    all_sprite.empty() 
    all_sprite_enemies.empty()
    enemies_group.empty()
    gold_group.empty()
    map = Map()
    random_level = random.randint(0,2)
    # while True:
    #     if random_level != level:
    #         level = random_level
    #         break
    #     random_level = random.randint(0,2)
    level = (level + 1) % len(levels)
    map.load_csv(level)
    map.load_data()
    player = Player(0,7*tile_size,scale=1.5)
    pet = Pet(0,6*tile_size,scale=0.5,player=player,map=map)
    pos_enemy = coordinate_enemy_level[level]
    pos_enemy = coordinate_enemy_level[0]
    x_enemy = pos_enemy[0]
    y_enemy = pos_enemy[1]
    
    x_enemyboss, y_enemyboss = coordinate_enemyboss_level[level]
    enemy = Enemy(x_enemy,y_enemy,scale=3)
    
    boss = EnemyBoss(x_enemyboss, y_enemyboss, scale=5)
    
    shark_positions = coordinate_shark_level[level]
    shark = Shark(shark_positions[0][0], shark_positions[0][1], scale=2)
    shark1 = Shark(shark_positions[1][0], shark_positions[1][1], scale=2)
    shark2 = Shark(shark_positions[2][0], shark_positions[2][1], scale=2)
    
    x_thorn, y_thorn = coordinate_thorn_level[level]
    thorn = Thorn(x_thorn, y_thorn, scale = 1.3)  
    
    all_sprite.add(player, pet)
    all_sprite_enemies.add(enemy, boss, shark, shark1, shark2, thorn, cayanthit)
    
def new(): 
    global score 
    map.load_csv(level)
    map.load_data()
    score = 0
                
def reset_game():
    global score, level, player, enemy, rocket, map, all_sprite, enemies_group, gold_group, all_sprite_enemies, pet, shark,shark1,shark2, boss, thorn, cayanthit

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


    player.game_over = False
    rocket.rect.x = 0
    rocket.rect.y = 0
    player.rect.x = 0
    player.rect.y = tile_size*7
    player.health = player.health_max
    player.mana = player.mana_max
    pet.rect.x = 0
    pet.rect.y = tile_size*6

    # Tạo lại map và các đối tượng
    map = Map()
    map.load_csv(level) 
    map.load_data()
    
    # Thêm các đối tượng vào nhóm sprite
    all_sprite.add(player)
    all_sprite.add(pet)
    all_sprite_enemies.add(enemy, boss, shark, shark1, shark2, thorn)
    enemies_group.add(rocket)

    

def update():
   
    player.update(map.obobstacle_coord)
    pet.update(map.obobstacle_coord)
    enemy.update(map.obobstacle_coord,player)
    boss.update(map.obobstacle_coord, player)
    shark.update(player)
    shark1.update(player)
    shark2.update(player)
    thorn.update(player)
    cayanthit.update(player)
    camera.update(player)
    
    if level == 1:
        for tile in map.animated_tiles:
            tile.update(dt)


      
def draw():
    global score,total_score, level
    #player.game_over = True
    screen.fill((0,0,0))
    if player.game_over == False:
        if map.level != 1:
            screen.blit(img_sunset,(0,0))   
            screen.blit(img_wave,(0,12*tile_size-img_wave.get_height())) 
        else:
            mountains_width = img_mountains1.get_width()
            num_repeat = int(round(150*tile_size // mountains_width)) + 1 
            for i in range(num_repeat):
                x_pos = i*mountains_width
                screen_pos = camera.apply_position((x_pos,0))
                screen.blit(img_mountains1, screen_pos)  
                screen.blit(img_mountains2, screen_pos)   
            
            # for i in range(0,1):
            #     screen.blit(img_mountains1,(i*50*tile_size,0))
            #     screen.blit(img_mountains2,(i*50*tile_size,0))
                
            # screen.blit(img_mountains1,(camera.x,0))
            # screen.blit(img_mountains2,(camera.x,0))  


        screen.blit(img_gold,(screen_width-img_gold.get_width()-tile_size*2,0))           

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pet.handle_click(event.pos)  # Gọi xử lý click
                enemy.handle_click(event.pos) 

        for sprite in all_sprite:
            screen.blit(sprite.image, camera.apply(sprite))
            # pygame.draw.rect(screen,'white',camera.apply(sprite),1)
        
        for x, y in pet.path:
            rect = pygame.Rect(x, y, tile_size, tile_size)
            screen_rect = rect.move(camera.camera.topleft)
            pygame.draw.rect(screen, 'lightblue', screen_rect)
            
        for x, y in enemy.path:
            rect = pygame.Rect(x, y, tile_size, tile_size)
            screen_rect = rect.move(camera.camera.topleft)
            # pygame.draw.rect(screen, 'lightyellow', screen_rect)

        for sprite in all_sprite_enemies: 
            screen.blit(sprite.image, camera.apply(sprite))
            # pygame.draw.rect(screen, 'white', camera.apply(sprite), 1)
        
        pet.draw_3_button(screen)
        enemy.draw_3_button(screen)

        enemy.draw_health_bar(screen, camera)
        boss.draw_health_bar2(screen, camera)  # Vẽ thanh máu của boss
        player.draw_bar(screen, camera)
        player.draw_skill(screen)
        player.draw_skill_cooldowns(screen)
        if player.out_of_mana:
            player.draw_out_of_mana(screen,camera)
        
        if pygame.sprite.spritecollide(player, gold_group,True):
            player.sfx["coin"].play()
            if player.double_gold == True:
                score += 2
            else:
                score += 1
        
        font = pygame.font.Font(None, 50)
        screen.blit(font.render(f"X {score}", True,"white"),(screen_width - tile_size*2,0))
          
       # rocket.check_rocket(screen,player,100,camera,explosion)
        if player.rect.x >= 149.5*tile_size:
            next_map()
            
    else:
        screen.blit(img_game_over,(0,0))
        button_game_over.draw(screen)
        if upgrade_button.is_pressed():
            total_score += score
            player.player_update = True   
      
        if play_button.is_pressed():
            reset_game()
        elif home_button.is_pressed():
            pass
    
    if player.player_update == True and upgrade_button.is_pressed()== False:
        
        total_score_xpox = round(math.log(total_score,10) + 26)*tile_size if score != 0 else 28*tile_size
        upgrade_character(screen,player, total_score,total_score_xpox )
        upgrade_logic(player,total_score)
        total_score = calculate_total_score()


    pygame.display.flip()
    
run = True
new() 
while run:
    dt = clock.tick(FPS)
    #all_sprite.update(dt)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

     
    update()
    draw()
  

pygame.quit()
