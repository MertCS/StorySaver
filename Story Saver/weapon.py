import random

import pygame

import constants
import math


class Weapon():
    def __init__(self, image, arrow_image):
        self.original_image = image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.arrow_image = arrow_image
        self.rect = self.image.get_rect()
        self.fired = False
        self.last_shot = pygame.time.get_ticks()

    def update(self, player):
        shot_cooldown = 300
        arrow = None
        self.rect.center = player.rect.center

        pos = pygame.mouse.get_pos()
        x_distance = pos[0] - self.rect.center[0]
        y_distance = -(pos[1] - self.rect.center[1])  # pygame y values increase DOWN the screen
        self.angle = math.degrees(math.atan2(y_distance, x_distance))

        # get mouse clicks
        if pygame.mouse.get_pressed()[0] and not self.fired and (
                pygame.time.get_ticks() - self.last_shot) >= shot_cooldown:
            arrow = Arrow(self.arrow_image, self.rect.centerx, self.rect.centery, self.angle)
            self.fired = True
            self.last_shot = pygame.time.get_ticks()

        # reset mouse click
        if not pygame.mouse.get_pressed()[0]:
            self.fired = False

        return arrow

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image, (
            (self.rect.centerx - int(self.image.get_width() / 2)),
            self.rect.centery - int(self.image.get_height() / 2)))


class Arrow(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # calculate horizontal and vertical speeds with the angle
        self.dx = math.cos(math.radians(self.angle)) * constants.WEAPON_SPEED
        self.dy = -(math.sin(
            math.radians(self.angle)) * constants.WEAPON_SPEED)  # negative because y increases as we go down

    def update(self, screen_scroll, obstacle_tiles, enemy_list):
        # reset variables
        damage = 0
        damage_pos = None

        # move the arrow
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        # check for collision with tile walls
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                self.kill()

        # check if arrow has gone off-screen
        if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
            self.kill()

        # check collision between arrow and enemies
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 + random.randint(-5, 5)
                damage_pos = enemy.rect
                enemy.health -= damage
                enemy.hit = True
                self.kill()
                break

        return damage, damage_pos

    def draw(self, surface):
        surface.blit(self.image, (
            (self.rect.centerx - int(self.image.get_width() / 2)),
            self.rect.centery - int(self.image.get_height() / 2)))


class Fireball(pygame.sprite.Sprite):
    def __init__(self, image, x, y, target_x, target_y):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        x_distance = target_x - x
        y_distance = -(target_y - y)
        self.angle = math.degrees(math.atan2(y_distance, x_distance))
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # calculate horizontal and vertical speeds with the angle
        self.dx = math.cos(math.radians(self.angle)) * constants.FIREBALL_SPEED
        self.dy = -(math.sin(
            math.radians(self.angle)) * constants.FIREBALL_SPEED)  # negative because y increases as we go down

    def update(self, screen_scroll, player):

        # move the arrow
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        # check if fireball has gone off-screen
        if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
            self.kill()

        # check collision with player
        if player.rect.colliderect(self.rect) and player.hit == False:
            player.hit = True
            player.last_hit = pygame.time.get_ticks()
            player.health -= 10
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, (
            (self.rect.centerx - int(self.image.get_width() / 2)),
            self.rect.centery - int(self.image.get_height() / 2)))
