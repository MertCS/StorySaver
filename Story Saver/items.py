import pygame.sprite


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, animation_list, dummy_coin = False):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type  # 0 => coin, 1 => small potion, 2 => big potion
        self.animation_list = animation_list
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dummy_coin = dummy_coin

    def update(self, screen_scroll, player, coin_fx, potion_fx):
        # reposition based on screen scroll
        if not self.dummy_coin:
            self.rect.x += screen_scroll[0]
            self.rect.y += screen_scroll[1]

        # check to see if item has been collected by player
        if self.rect.colliderect(player.rect):
            # coin collected
            if self.item_type == 0:
                player.coins += 1
                coin_fx.play()
            # small potion collected
            elif self.item_type == 1:
                player.health += 10
                potion_fx.play()
                if player.health > 100:
                    player.health = 100
            # big potion collected
            elif self.item_type == 2:
                player.health += 20
                potion_fx.play()
                if player.health > 100:
                    player.health = 100

            self.kill()

        # handle animation
        animation_cooldown = 150
        # update image
        self.image = self.animation_list[self.frame_index]
        # check if enough time has passed to update frame
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # check if the animation has finished
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
