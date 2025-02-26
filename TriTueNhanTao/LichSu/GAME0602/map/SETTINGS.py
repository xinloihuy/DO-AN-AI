import pygame
FPS = 100
screen_width = 512*2
screen_height = 272*2 # chi ve len 32 khung hinh
vel = 2
rows = 17 
cols = 150
tile_size = screen_height //rows
game_over = False
tiles_type = 31

img_sunset = pygame.image.load('assets/images/sunset.png')
img_sunset = pygame.transform.scale(img_sunset,(50*tile_size,10*tile_size))


img_wave = pygame.image.load('assets/images/wave.png')
img_wave = pygame.transform.scale(img_wave,(50*tile_size,2*tile_size))


img_game_over = pygame.image.load('GameOver/assets/screen_game_over.png')
img_game_over = pygame.transform.scale(img_game_over,(screen_width,screen_height))

img_upgrade_bg = pygame.image.load('Upgrade/assets/bg.png')
img_upgrade_bg = pygame.transform.scale(img_upgrade_bg,(screen_width,screen_height))


img_bar_upgrade = pygame.image.load(f"Upgrade/assets/bar_upgrade.png") 
img_bar_upgrade = pygame.transform.scale(img_bar_upgrade,(tile_size*18, tile_size*2))

img_gold = pygame.image.load('assets/images/gold.png')
img_gold = pygame.transform.scale(img_gold,(tile_size*2,tile_size*2))