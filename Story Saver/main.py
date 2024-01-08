import pygame
from pygame import mixer
import constants
import csv
from weapon import Weapon
from items import Item
from world import World
from button import Button

mixer.init()
pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Story Saver")

# clock for maintaining frame rate
clock = pygame.time.Clock()

# define game variables
level = 0
start_game = False
pause_game = False
start_intro = False
screen_scroll = [0, 0]
gover = False

# define player movement
moving_left = False
moving_right = False
moving_up = False
moving_down = False

# define font
font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)


# helper for scaling
def scale_image(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h * scale))

# load audio
pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
shot_fx = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
shot_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
potion_fx = pygame.mixer.Sound("assets/audio/heal.wav")
potion_fx.set_volume(0.5)

# load button images
start_image = scale_image(pygame.image.load("assets/images/buttons/button_start.png").convert_alpha(),
                             constants.BUTTON_SCALE)
exit_image = scale_image(pygame.image.load("assets/images/buttons/button_exit.png").convert_alpha(),
                             constants.BUTTON_SCALE)
restart_image = scale_image(pygame.image.load("assets/images/buttons/button_restart.png").convert_alpha(),
                             constants.BUTTON_SCALE)
resume_image = scale_image(pygame.image.load("assets/images/buttons/button_resume.png").convert_alpha(),
                             constants.BUTTON_SCALE)

# load heart images
heart_empty = scale_image(pygame.image.load("assets/images/items/hearts/heart_empty.png").convert_alpha(),
                          constants.ITEM_SCALE)
heart_half = scale_image(pygame.image.load("assets/images/items/hearts/heart_half.png").convert_alpha(),
                         constants.ITEM_SCALE)
heart_full = scale_image(pygame.image.load("assets/images/items/hearts/heart_full.png").convert_alpha(),
                         constants.ITEM_SCALE)

# load coin images
coin_images = []
for x in range(4):
    img = scale_image(pygame.image.load(f"assets/images/items/collectibles/coin/f{x}.png").convert_alpha(),
                      constants.ITEM_SCALE)
    coin_images.append(img)

# load potion images
small_potion = scale_image(pygame.image.load("assets/images/items/collectibles/potion/small.png").convert_alpha(),
                           constants.POTION_SCALE)
big_potion = scale_image(pygame.image.load("assets/images/items/collectibles/potion/big.png").convert_alpha(),
                         constants.POTION_SCALE)

item_images = []
item_images.append(coin_images)
item_images.append(small_potion)
item_images.append(big_potion)

# load weapon images
bow_image = scale_image(pygame.image.load("assets/images/weapons/bow/bow0.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_image(pygame.image.load("assets/images/weapons/bow/arrow.png").convert_alpha(),
                          constants.WEAPON_SCALE)
fireball_image = scale_image(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(),
                             constants.FIREBALL_SCALE)

# load tilemap images
tile_list = []
for x in range(constants.TILE_TYPES):
    tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
    tile_list.append(tile_image)

# load character images
mob_animations = []
mob_types = ["knight", "imp", "masked_orc", "goblin", "lizard", "ogre", "big_demon", "princess"]

animation_types = ["idle", "run"]
for mob in mob_types:
    # load images
    animation_list = []
    for animation in animation_types:
        # reset temporary list of images
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/f{i}.png").convert_alpha()
            img = scale_image(img, constants.SCALE)
            temp_list.append(img)
        animation_list.append(temp_list)
    mob_animations.append(animation_list)


# function for putting text on the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# function for displaying game information
def draw_info():
    pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50))
    # draw lives
    half_heart_drawn = False
    for i in range(5):
        if player.health >= ((i + 1) * 20):
            screen.blit(heart_full, (10 + i * 50, 5))
        elif player.health % 20 > 0 and not half_heart_drawn:
            screen.blit(heart_half, (10 + i * 50, 5))
            half_heart_drawn = True
        else:
            screen.blit(heart_empty, (10 + i * 50, 5))

    # level
    draw_text("LEVEL: " + str(level), font, constants.WHITE, constants.SCREEN_WIDTH / 2, 15)

    # show coins
    draw_text(f"X{player.coins}", font, constants.WHITE, constants.SCREEN_WIDTH - 100, 15)


# level management
def reset_level():
    damage_text_group.empty()
    arrow_group.empty()
    item_group.empty()
    fireball_group.empty()

    # create empty tile list
    data = []
    for row in range(constants.ROWS):
        r = [-1] * constants.COLS
        data.append(r)

    return data


# create empty tile list
world_data = []
for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    world_data.append(r)
# load in level data to create world
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)


# damage text class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        # move damage text up
        self.rect.y -= 1
        # delete character after a few seconds
        self.counter += 1
        if self.counter > 30:
            self.kill()


# class for handling screen fade
class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # go out
            pygame.draw.rect(screen, self.colour,
                             (0 - self.fade_counter, 0, constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (
            constants.SCREEN_WIDTH // 2 + self.fade_counter, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour,
                             (0, 0 - self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (
            0, constants.SCREEN_HEIGHT // 2 + self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        elif self.direction == 2:  # come in
            pygame.draw.rect(screen, self.colour, (0, 0, constants.SCREEN_WIDTH, 0 + self.fade_counter))

        if self.fade_counter >= constants.SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


# create player
player = world.player

# create players weapon
bow = Weapon(bow_image, arrow_image)

# load enemies from world data
enemy_list = world.character_list

# create sprite groups
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
item_group.add(score_coin)
# add the items from level data
for item in world.item_list:
    item_group.add(item)

# create screen fade
intro_fade = ScreenFade(1, constants.BLACK, 4)
death_fade = ScreenFade(2, constants.DARK_RED, 4)
game_over_fade = ScreenFade(2, constants.GREEN, 4)

# create buttons
start_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 - 150, start_image)
exit_button = Button(constants.SCREEN_WIDTH // 2 - 110, constants.SCREEN_HEIGHT // 2 + 50, exit_image)
restart_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 150, restart_image)
resume_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 150, resume_image)

# main game loop
run = True
while run:

    # frame rate control
    clock.tick(constants.FPS)

    # game menu
    if not start_game:
        screen.fill(constants.MENU_COLOR)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        if pause_game:
            screen.fill(constants.MENU_COLOR)
            if resume_button.draw(screen):
                pause_game = False
            if exit_button.draw(screen):
                run = False
        else:

            # fill background
            screen.fill(constants.BG)

            if player.alive and not gover:
                # calculate player movement
                dx = 0
                dy = 0

                if moving_right:
                    dx = constants.PLAYER_SPEED
                if moving_left:
                    dx = -constants.PLAYER_SPEED
                if moving_up:
                    dy = -constants.PLAYER_SPEED
                if moving_down:
                    dy = constants.PLAYER_SPEED

                # movement of player
                screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tiles, world.exit_tile)

                # update all objects
                world.update(screen_scroll)
                for enemy in enemy_list:
                    game_over, fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
                    if fireball:
                        fireball_group.add(fireball)
                    if enemy.alive:
                        enemy.update()
                    if game_over:
                        gover = True
                arrow = bow.update(player)
                player.update()

                if arrow:
                    arrow_group.add(arrow)
                    shot_fx.play()

                for arrow in arrow_group:
                    damage, damage_pos = arrow.update(screen_scroll, world.obstacle_tiles, enemy_list)
                    if damage:
                        damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
                        damage_text_group.add(damage_text)
                        hit_fx.play()
                damage_text_group.update()
                fireball_group.update(screen_scroll, player)
                item_group.update(screen_scroll, player, coin_fx, potion_fx)

            # draw the player and the weapon and the level on the screen
            world.draw(screen)
            for enemy in enemy_list:
                enemy.draw(screen)
            player.draw(screen)
            bow.draw(screen)

            for arrow in arrow_group:
                arrow.draw(screen)
            for fireball in fireball_group:
                fireball.draw(screen)
            damage_text_group.draw(screen)
            item_group.draw(screen)
            draw_info()
            score_coin.draw(screen)

            # check game over
            # check if princess is reached
            if gover:
                if game_over_fade.fade():
                    if restart_button.draw(screen):
                        death_fade.fade_counter = 0
                        start_intro = True
                        gover = False
                        world_data = reset_level()
                        level = 0
                        # load in level data to create world
                        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                            reader = csv.reader(csvfile, delimiter=",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        world.process_data(world_data, tile_list, item_images, mob_animations)
                        player = world.player
                        enemy_list = world.character_list
                        score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
                        item_group.add(score_coin)
                        for item in world.item_list:
                            item_group.add(item)
                    elif exit_button.draw(screen):
                        run = False

            # check level complete
            if level_complete:
                start_intro = True
                level += 1
                world_data = reset_level()
                # load in level data to create world
                with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                world.process_data(world_data, tile_list, item_images, mob_animations)
                temp_hp = player.health
                temp_score = player.coins
                player = world.player
                player.health = temp_hp
                player.coins = temp_score
                enemy_list = world.character_list
                score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
                item_group.add(score_coin)
                for item in world.item_list:
                    item_group.add(item)

            # show intro
            if start_intro:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0

            # show death screen
            if not player.alive:
                if death_fade.fade():
                    if restart_button.draw(screen):
                        death_fade.fade_counter = 0
                        start_intro = True
                        world_data = reset_level()
                        level = 0
                        # load in level data to create world
                        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                            reader = csv.reader(csvfile, delimiter=",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        world.process_data(world_data, tile_list, item_images, mob_animations)
                        player = world.player
                        enemy_list = world.character_list
                        score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
                        item_group.add(score_coin)
                        for item in world.item_list:
                            item_group.add(item)
                    elif exit_button.draw(screen):
                        run = False


    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_s:
                moving_down = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_ESCAPE:
                pause_game = True

        # keyboard releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_s:
                moving_down = False
            if event.key == pygame.K_d:
                moving_right = False

    pygame.display.update()

pygame.quit()
