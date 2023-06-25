import pygame
from .config import *
from .engine import *
from os import listdir
from random import randint, choice
from math import sin
from .entity import *
from .objects import DeadBody

ENEMY_SPRITES = {}

def load_enemy_sprites():

    global ENEMY_SPRITES

    for folder in ("dog1", "dog2", "squid"):
        ENEMY_SPRITES[folder] = import_sprite_sheets(F"graphics/enemies/{folder}")


IDLE = 0
AGRO = 1
FOLLOW = 2
ATTACK = 3
DYING = 4

class Enemy(pygame.sprite.Sprite):

    def __init__(self, master, grps, level, sprite_type, pos, hitbox, attack_rect, max_health, max_speed, acc, dcc):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()
        self.level = level

        self.sprite_type = sprite_type
        self.animations = ENEMY_SPRITES[sprite_type]
        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect()

        self.anim_index = 0
        self.anim_speed = 0.15

        self.attack_rect_dimen = attack_rect
        self.attack_rect = pygame.FRect(*attack_rect)

        self.pos = pos
        self.hitbox = pygame.FRect(*hitbox)
        self.hitbox.midbottom = pos
        self.velocity = pygame.Vector2()
        self.target_direc = pygame.Vector2()
        self.max_speed = max_speed
        self.acceleration = acc
        self.deceleration = dcc
        self.facing_direc = pygame.Vector2(choice((1, -1)), 0)

        self.state = IDLE
        self.moving = False
        self.max_health = max_health
        self.health = self.max_health
        self.invinsible = False
        self.hurting = False

        self.invinsibility_timer = CustomTimer()
        self.hurt_for = CustomTimer()

    def update_image(self):

        if self.state == DYING: state = "dead"
        elif self.moving: state = "run"
        elif self.state == ATTACK: state = "attack"
        else: state = "idle"

        try:
            image = self.animations[state][int(self.anim_index)]
        except IndexError:
            image = self.animations[state][0]
            self.anim_index = 0
            if self.state == ATTACK:
                self.state = AGRO
            elif self.state == DYING:
                self.die()
                return

        if self.moving: self.anim_speed = 0.15
        elif self.state == ATTACK: self.anim_speed = 0.18
        else: self.anim_speed = 0.08

        self.anim_index += self.anim_speed *self.master.dt

        flip = self.facing_direc.x<0
        self.image = pygame.transform.flip(image, flip, False)
        self.rect = self.image.get_rect(midbottom = self.hitbox.midbottom)

        if self.invinsible:
            if self.hurting:
                self.image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
                self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MIN)
            self.image.set_alpha(int((sin(pygame.time.get_ticks()/30)+1)/2 *255))

    def die(self):

        DeadBody(self.master, [self.level.camera_grp], self.animations["dead"][-1], self.rect.midbottom, self.facing_direc.x<0)
        self.kill()

    def apply_force(self):

        if self.moving:
            self.velocity.move_towards_ip( self.target_direc*self.max_speed, self.acceleration *self.master.dt)
        else:
            self.velocity.move_towards_ip( (0, 0), self.deceleration *self.master.dt)

        if self.moving:
            for enemy in self.level.enemy_grp.sprites():
                if enemy is self: continue
                if self.rect.colliderect(enemy.rect):
                    try:
                        space_vec = pygame.Vector2(self.rect.centerx-enemy.rect.centerx, self.rect.centery-enemy.rect.centery)
                        self.velocity += space_vec.normalize() * 0.008
                    except ValueError: pass

    def control(self):

        self.moving = bool(self.target_direc) and not self.hurting
        if self.moving:
            self.facing_direc.update(self.target_direc)

    def check_timers(self):

        if self.invinsibility_timer.check():
            self.invinsible = False
        if self.hurt_for.check():
            self.hurting = False

    def move(self):

        obj_rects = get_obj_rects(self, self.master)
        self.hitbox.centerx += self.velocity.x * self.master.dt
        do_collision(self, 0, self.master, obj_rects)
        self.hitbox.centery += self.velocity.y * self.master.dt
        do_collision(self, 1, self.master, obj_rects)
        do_collision(self, 2, self.master)

    def process_events(self):

        pass

    def check_player_collision(self):

        if self.hitbox.colliderect(self.master.player.hitbox):
            self.master.player.get_hurt(1)

    def get_hurt(self, damage):

        if self.invinsible or self.state == DYING: return
        self.health -= damage
        self.velocity.update()
        self.moving = False
        self.hurting = True
        self.invinsible = True
        self.hurt_for.start(200)
        self.invinsibility_timer.start(1_000)
        self.master.particle_manager.spawn_blood(self.hitbox.midbottom)

        if self.health <= 0:
            self.state = DYING
            self.anim_index = 0
            self.master.sounds["SFX_Death"].play()
        else:
            self.master.sounds.play("SFX_CreatureDamage", (1, 2))

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)
        # pygame.draw.rect(self.screen, "blue", (self.hitbox.x+self.master.offset.x, self.hitbox.y+self.master.offset.y, self.hitbox.width, self.hitbox.height), 1)
        # pygame.draw.rect(self.screen, "red", (self.attack_rect.x+self.master.offset.x, self.attack_rect.y+self.master.offset.y, self.attack_rect.width, self.attack_rect.height), 1)

    def update(self):

        self.process_events()
        self.check_timers()
        self.control()
        self.apply_force()
        self.move()
        self.check_player_collision()
        self.update_image()


class Dog(Enemy):

    def __init__(self, master, grps, level, pos, sprite_type, ranget=(8, 12)):
        super().__init__(master, grps, level, sprite_type, pos, (0, 0, 12, 6), (4, 21, 11, 11), 6, 1.1, 0.08, 0.04)

        self.follow_timer = CustomTimer()
        self.follow_for = CustomTimer()

        self.start_this_timer = CustomTimer()
        self.start_this_timer.start(randint(10, 20) *1000)
        self.ranget = ranget

    def process_events(self):

        if self.state == DYING: return

        dist = dist_sq(self.master.player.rect.center, self.rect.center)
        if dist < (8*16)**2:
            if self.state == IDLE:
                self.state = AGRO
        else:
            self.state = IDLE
            self.target_direc.update()
        if dist < (12*16)**2:
            if randint(0, 3_000) == randint(693, 713):
                self.master.sounds["SFX_CreatureIdle"].play()
        if self.state == FOLLOW:
            self.target_direc.update(self.master.player.rect.centerx - self.rect.centerx,
                self.master.player.rect.centery - self.rect.centery)
            try:
                self.target_direc.normalize_ip()
            except ValueError:
                self.target_direc.update()

        if self.state in (AGRO, FOLLOW):
            self.facing_direc.update(self.master.player.rect.centerx - self.rect.centerx,
                self.master.player.rect.centery - self.rect.centery)
            try:
                self.facing_direc.normalize_ip()
            except ValueError:
                self.facing_direc.update()
            if dist_sq(self.master.player.rect.center, self.rect.center) < (16*2)**2:
                self.state = ATTACK
                self.anim_index = 0
                self.target_direc.update()
                self.master.sounds["SFX_CreatureAttack"].play()

        if self.state == ATTACK:
            self.attack_rect.x = self.attack_rect_dimen[0] + self.rect.x
            self.attack_rect.y = self.attack_rect_dimen[1] + self.rect.y
            if self.facing_direc.x>=0:
                self.attack_rect.right = self.rect.width - self.attack_rect_dimen[0] + self.rect.x

    def check_timers(self):

        super().check_timers()

        if self.follow_timer.check() and self.state == AGRO:
            self.state = FOLLOW
            self.follow_for.start(randint(30, 60)*100)
        if self.follow_for.check() and self.state != IDLE:
            self.state = AGRO
            self.target_direc.update()
            self.moving = False
        if self.start_this_timer.check():
            self.follow_timer.start(randint(*self.ranget)*1000, 0)


class Squid(Enemy):

    def __init__(self, master, grps, level, pos):

        super().__init__(master, grps, level, "squid", pos, (0, 0, 22, 14), (0, 0, 22, 14), 4, 1.0, 0.04, 0.02)
        self.hitbox.center = pos

    def update_image(self):

        state = []
        if self.state == DYING: state.append("dead")
        else: state.append("idle")

        state = "".join(state)

        try:
            image = self.animations[state][int(self.anim_index)]
        except IndexError:
            image = self.animations[state][0]
            self.anim_index = 0
            if self.state == DYING:
                DeadBody(self.master, [self.master.level.camera_grp], self.animations["dead"][0], self.rect.midbottom, self.facing_direc.x<0)
                self.kill()
                return

        if self.moving: self.anim_speed = 0.15
        else: self.anim_speed = 0.08

        self.anim_index += self.anim_speed *self.master.dt

        flip = self.facing_direc.x<0
        self.image = pygame.transform.flip(image, flip, False)
        self.rect = self.image.get_rect(center = self.hitbox.center)

        if self.invinsible:
            if self.hurting:
                self.image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
                self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MIN)
            self.image.set_alpha(int((sin(pygame.time.get_ticks()/30)+1)/2 *255))

    def process_events(self):

        if self.state == DYING: return
        dist = dist_sq(self.master.player.rect.center, self.rect.center)
        if dist < (8*16)**2:
            if self.state == IDLE:
                self.state = FOLLOW
        else:
            self.state = IDLE
            self.target_direc.update()

        if dist < (12*16)**2:
            if randint(0, 1_020) == randint(10, 20):
                self.master.sounds["SFX_CreatureIdle"].play()

        if self.state == FOLLOW:
            self.target_direc.update(self.master.player.rect.centerx - self.rect.centerx,
                self.master.player.rect.centery - self.rect.centery)
            try:
                self.target_direc.normalize_ip()
            except ValueError:
                self.target_direc.update()

            self.facing_direc.update(self.master.player.rect.centerx - self.rect.centerx,
                self.master.player.rect.centery - self.rect.centery)
            try:
                self.facing_direc.normalize_ip()
            except ValueError:
                self.facing_direc.update()

