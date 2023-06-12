import pygame
import random
from .engine import *
from .config import *
from .objects import objects_hitboxes
from .entity import *
from math import sin, cos, pi, radians, degrees

MATERIAL_SPRITE = {}

def load_materials():
    global MATERIAL_SPRITE

    MATERIAL_SPRITE = load_pngs_dict("graphics/materials")
    (MATERIAL_SPRITE)


class Player(pygame.sprite.Sprite):

    def __init__(self, master, grps):

        super().__init__(grps)
        self.master = master
        self.master.player = self
        self.screen = pygame.display.get_surface()

        pos = (196*16, 71*16)
        pos = (2000, 700)
        # pos = (300, 300)

        self.all_pilot_anims = [None]
        for i in range(1, 5):
            self.all_pilot_anims.append(import_sprite_sheets(F"graphics/player/pilot_{i}"))


        self.animations = self.all_pilot_anims[self.master.game.which_pilot]
        self.animation = self.animations["idle_side"]
        self.image = self.animation[0]
        self.rect = self.image.get_rect()

        self.anim_index = 0
        self.anim_speed = 0.15

        self.hitbox = pygame.FRect(0, 0, 13, 12)
        self.hitbox.midbottom = pos
        self.velocity = pygame.Vector2()
        self.input_direc = pygame.Vector2()
        self.max_speed = 1.8
        self.inventory_speed = 0.5
        # self.max_speed = 5
        self.acceleration = 0.3
        self.deceleration = 0.3
        self.facing_direc = pygame.Vector2(1, 0)

        self.moving = False
        self.in_control = True
        self.attacking = False
        self.can_attack = True

        self.health = 5
        self.max_health = 5

        # self.inventory = {"copper":1, "gold":2, "titanium":3, "diamond":4, "rubber":5, "uranium":6, "fruit":7, "vegetable":8, "wood":9}
        self.inventory = {}
        self.inventory_open = False

        self.heart_surf = pygame.image.load("graphics/ui/heart.png").convert_alpha()
        self.empty_heart_surf = pygame.image.load("graphics/ui/empty_heart.png").convert_alpha()
        self.heart_surf = pygame.transform.scale_by(self.heart_surf, 5)
        self.empty_heart_surf = pygame.transform.scale_by(self.empty_heart_surf, 5)

        self.attack_cooldown = CustomTimer()
        self.attack_for = CustomTimer()

    def add_inventory(self, item):

        amount = self.inventory.get(item, 0)
        self.inventory[item] = amount+1

    def update_image(self):

        state = []
        if self.attacking: state.append("shoot")
        elif self.moving: state.append("run")
        else: state.append("idle")

        if self.facing_direc.y != 0:
            if self.facing_direc.y >= 0:
                state.append("_down")
            else:
                state.append("_up")
        elif self.facing_direc.x != 0:
            state.append("_side")

        state = "".join(state)
        self.master.debug("state: ", state)

        try:
            image = self.animations[state][int(self.anim_index)]
        except IndexError:
            image = self.animations[state][0]
            self.anim_index = 0

        if self.inventory_open: self.anim_speed = 0.04
        elif self.moving: self.anim_speed = 0.15
        else: self.anim_speed = 0.08

        self.anim_index += self.anim_speed *self.master.dt

        if state.endswith("side"):
            self.image = pygame.transform.flip(image, self.facing_direc.x<0, False)
        else: self.image = image
        self.rect.midbottom = self.hitbox.midbottom

    def get_input(self):

        if not self.in_control:
            self.moving = False
            return

        self.input_direc.update(0, 0)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.input_direc.x += 1
        if keys[pygame.K_a]:
            self.input_direc.x -= 1
        if keys[pygame.K_s]:
            self.input_direc.y += 1
        if keys[pygame.K_w]:
            self.input_direc.y -= 1

        self.inventory_open = keys[pygame.K_TAB]
        
        self.moving = bool(self.input_direc)
        if self.moving:
            self.facing_direc.update(self.input_direc)

        if self.input_direc.x and self.input_direc.y:
            try:
                self.input_direc.normalize_ip()
            except ValueError:
                self.input_direc.update()

    def apply_force(self):

        if self.inventory_open: speed = self.inventory_speed
        else: speed = self.max_speed

        if self.moving:
            self.velocity.move_towards_ip( self.input_direc*speed, self.acceleration *self.master.dt)
        else:
            self.velocity.move_towards_ip( (0, 0), self.deceleration *self.master.dt)

    def move(self):

        obj_rects = get_obj_rects(self, self.master)
        self.hitbox.centerx += self.velocity.x * self.master.dt
        do_collision(self, 0, self.master, obj_rects)
        self.hitbox.centery += self.velocity.y * self.master.dt
        do_collision(self, 1, self.master, obj_rects)

    def process_events(self):

        if self.in_control and not self.inventory_open:
            for event in pygame.event.get((pygame.KEYUP, pygame.KEYDOWN)):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.master.game.pause_game()
                    if event.key in (pygame.K_e, pygame.K_SPACE):
                        self.master.interaction_manager.pressed_interact()
                    if event.key == pygame.K_SPACE and self.in_control and self.can_attack:
                        self.attacking = True
                        self.in_control = False
                        self.can_attack = False
                        self.attack_cooldown.start(500)
                        self.attack_for.start(200)
                        self.master.level.shoot_projectile("player_small", self)
        elif self.inventory_open:
            pygame.event.clear((pygame.KEYUP, pygame.KEYDOWN))

        if self.attack_cooldown.check():
            self.can_attack = True
        if self.attack_for.check():
            self.attacking = False
            self.in_control = True

    def change_pilot(self, which_pilot):

        self.animations = self.all_pilot_anims[which_pilot]
        self.health = self.max_health

        self.moving = False
        self.in_control = True
        self.attacking = False
        self.can_attack = True

        self.attack_cooldown.stop()
        self.attack_for.stop()

        #make dead body if neded
        self.inventory.clear()

    def draw_inventory(self):

        self.master.game.black_overlay.set_alpha(100)
        self.screen.blit(self.master.game.black_overlay, (0, 0))
        self.screen.blit(pygame.transform.gaussian_blur(self.screen, 5, False), (0, 0))

        widx, widy = 50, 50
        grid = 3
        mat_size = 16

        offx = (W-widx)/2
        offy = (H-widy)/2

        paddx = widx/grid+mat_size
        paddy = widy/grid+mat_size

        for i, (key, amount) in enumerate(self.inventory.items()):
            if amount == 0: continue
            y, x = divmod(i, grid)
            pos = x*paddx+offx-(mat_size/1), y*paddy+offy-(mat_size/1)
            self.screen.blit(pygame.transform.scale2x(MATERIAL_SPRITE[key]), (pos))
            text = self.master.font_d.render(F"x{amount}", True, (255, 255, 255))
            self.screen.blit(text, (pos[0]+mat_size/3*2, pos[1]+mat_size/2))

        radius = 115
        # pygame.draw.arc(self.screen, (100, 0, 20), (W/2-radius+15, H/2-radius+15, (radius-15)*2, (radius-15)*2), 0, pi*2/self.max_health*self.health, 5)
        for i in range(self.max_health):

            angle = pi*2/self.max_health*i - pi/2
            surf = self.heart_surf if i < self.health else self.empty_heart_surf
            rot_surf = pygame.transform.rotozoom(surf, -90 - degrees(angle), 1)
            pos = cos(angle)*radius + (W/2), sin(angle)*radius + (H/2)
            rect = rot_surf.get_rect(center=(pos))
            self.screen.blit(rot_surf, rect)

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)
        # pygame.draw.rect(self.screen, "blue", (self.hitbox.x+self.master.offset.x, self.hitbox.y+self.master.offset.y, self.hitbox.width, self.hitbox.height), 1)

    def update(self):

        self.process_events()
        self.get_input()
        self.apply_force()
        self.move()
        self.update_image()

        self.master.debug("pos: ", (round(self.hitbox.centerx, 2), round(self.hitbox.bottom, 2)))

