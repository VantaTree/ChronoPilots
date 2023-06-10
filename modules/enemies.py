import pygame
from .config import *
from .engine import *
from os import listdir
from random import randint

ENEMY_SPRITES = {}

def load_enemy_sprites():

    global ENEMY_SPRITES

    for folder in ("test",):
        ENEMY_SPRITES[folder] = import_sprite_sheets(F"graphics/enemies/{folder}")


IDLE = 0
AGRO = 1
FOLLOW = 2
ATTACK = 3


class Enemy(pygame.sprite.Sprite):

    def __init__(self, master, grps, pos, sprite_type):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()

        self.sprite_type = sprite_type
        self.animations = ENEMY_SPRITES[sprite_type]
        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect()
        self.anim_index = 0

        self.anim_index = 0
        self.anim_speed = 0.15

        self.hitbox = pygame.FRect(0, 0, 13, 12)
        self.hitbox.midbottom = pos
        self.velocity = pygame.Vector2()
        self.target_direc = pygame.Vector2()
        self.max_speed = 1.5
        self.acceleration = 0.2
        self.deceleration = 0.2
        self.facing_direc = pygame.Vector2(1, 0)

        self.moving = False

        self.state = IDLE

        self.follow_timer = CustomTimer()
        self.follow_for = CustomTimer()

        self.follow_timer.start(10_000, 0)

    def update_image(self):

        state = []
        if self.moving: state.append("run")
        elif self.state == AGRO: state.append("agro")
        elif self.state == ATTACK: state.append("attack")
        else: state.append("idle")

        state = "".join(state)

        try:
            image = self.animations[state][int(self.anim_index)]
        except IndexError:
            image = self.animations[state][0]
            self.anim_index = 0
            if self.state == ATTACK:
                self.state = AGRO

        if self.moving: self.anim_speed = 0.15
        elif self.state == ATTACK: self.anim_speed = 0.18
        else: self.anim_speed = 0.08

        self.anim_index += self.anim_speed *self.master.dt

        self.image = pygame.transform.flip(image, self.facing_direc.x<0, False)
        self.rect = self.image.get_rect(midbottom = self.hitbox.midbottom)


    def apply_force(self):

        if self.moving:
            self.velocity.move_towards_ip( self.target_direc*self.max_speed, self.acceleration *self.master.dt)
        else:
            self.velocity.move_towards_ip( (0, 0), self.deceleration *self.master.dt)

    def process_events(self):

        if dist_sq(self.master.player.rect.center, self.rect.center) < (8*16)**2:
            if self.state == IDLE:
                self.state = AGRO
        else:
            self.state = IDLE
            self.target_direc.update()
        if self.state == FOLLOW:
            self.target_direc = pygame.Vector2(self.master.player.rect.centerx - self.rect.centerx,
                self.master.player.rect.centery - self.rect.centery).normalize()

        if self.state in (AGRO, FOLLOW) and dist_sq(self.master.player.rect.center, self.rect.center) < 16**2:
            self.state = ATTACK
            self.anim_index = 0
            self.target_direc.update()
            self.facing_direc = pygame.Vector2(self.master.player.rect.centerx - self.rect.centerx,
                self.master.player.rect.centery - self.rect.centery).normalize()

    def control(self):

        self.moving = bool(self.target_direc)
        if self.moving:
            self.facing_direc.update(self.target_direc)

    def check_timers(self):

        if self.follow_timer.check() and self.state == AGRO:
            self.state = FOLLOW
            self.follow_for.start(randint(30, 60)*100)
        if self.follow_for.check() and self.state != IDLE:
            self.state = AGRO
            self.target_direc.update()
            self.moving = False

    def move(self):

        self.hitbox.centerx += self.velocity.x * self.master.dt
        do_collision(self, 0, self.master)
        self.hitbox.centery += self.velocity.y * self.master.dt
        do_collision(self, 1, self.master)

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)
        pygame.draw.rect(self.screen, "blue", (self.hitbox.x+self.master.offset.x, self.hitbox.y+self.master.offset.y, self.hitbox.width, self.hitbox.height), 1)

    def update(self):

        self.process_events()
        self.check_timers()
        self.control()
        self.apply_force()
        self.move()
        self.update_image()
        self.master.debug("state:", self.state)


def do_collision(entity, axis, master):

    px = int(entity.hitbox.centerx / TILESIZE)
    py = int(entity.hitbox.centery / TILESIZE)

    for y in range(py-1, py+2):
        for x in range(px-1, px+2):

            if x < 0 or y < 0: continue

            rect = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, TILESIZE)
            rectg = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, 8)
            if not entity.hitbox.colliderect(rect): continue

            cell = get_xy(master.game.collision, x, y)
            if cell <= 0: continue

            apply_collision(entity, axis, rect, cell)

    for rect in master.game.object_hitboxes:
        if not entity.hitbox.colliderect(rect): continue
        apply_collision(entity, axis, rect)


def apply_collision(entity, axis, rect, cell=1):

    if axis == 0: # x-axis

                if cell == 1:

                    if entity.velocity.x > 0:
                        entity.hitbox.right = rect.left
                    if entity.velocity.x < 0:
                        entity.hitbox.left = rect.right

    elif axis == 1: # y-axis

        if cell == 1:
            if entity.velocity.y < 0:
                entity.hitbox.top = rect.bottom
                # entity.velocity.y = 0
            if entity.velocity.y > 0:
                entity.hitbox.bottom = rect.top
                # entity.velocity.y = 0

                        
def get_xy(grid, x, y):

    if x < 0 or y < 0: return
    try:
        return grid[y][x]
    except IndexError: return