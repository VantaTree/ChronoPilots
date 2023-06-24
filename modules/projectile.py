from typing import Any
import pygame
from .config import *
from .engine import *

PROJECTILE_SPRITES = {}

def load_projectile_sprites():

    global PROJECTILE_SPRITES

    PROJECTILE_SPRITES = import_sprite_sheets("graphics/projectile")


class Projectile(pygame.sprite.Sprite):

    def __init__(self, master, grps, sprite_type, pos, direction, anim_speed=0.15, speed=5, damage=1):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()

        self.animation = PROJECTILE_SPRITES[sprite_type]
        self.image = self.animation[0]
        self.rect = self.image.get_frect(center=pos)
        
        self.hitbox = self.rect
        self.direction = direction.normalize()

        self.anim_speed = anim_speed
        self.anim_index = 0
        self.speed = speed
        self.damage = damage

    def update_image(self):

        try:
            image = self.animation[int(self.anim_index)]
        except IndexError:
            image = self.animation[0]
            self.anim_index = 0

        self.anim_index += self.anim_speed *self.master.dt

        self.image = pygame.transform.rotozoom(image, self.direction.angle_to((1, 0)), 1)

    def move(self):

        self.hitbox.center += self.direction*self.speed*self.master.dt

    def check_hit(self):

        for enemy in self.master.level.enemy_grp.sprites():
            if enemy.rect.colliderect(self.rect):
                enemy.get_hurt(self.damage)
                self.kill()

    def check_collisoin(self):

        if not self.rect.colliderect((
            -self.master.offset.x-100, -self.master.offset.y-100, W+200, H+200
        )):
            self.kill()
            return

        x = int(self.hitbox.centerx / TILESIZE)
        y = int(self.hitbox.centery / TILESIZE)

        if x < 0 or y < 0: return
        cell = get_xy(self.master.level.collision, x, y)
        if cell == 1:
            self.kill()

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft+self.master.offset)

    def update(self):

        self.move()
        self.check_collisoin()
        self.check_hit()
        self.update_image()


def get_xy(grid, x, y):

    if x < 0 or y < 0: return
    try:
        return grid[y][x]
    except IndexError: return
