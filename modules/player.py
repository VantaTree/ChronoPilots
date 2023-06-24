import pygame
import random
from .engine import *
from .config import *
from .objects import objects_hitboxes
from .entity import *
from .objects import DeadBody
from math import sin, cos, pi, radians, degrees

MATERIAL_SPRITE = {}

def load_materials():
    global MATERIAL_SPRITE

    MATERIAL_SPRITE = load_pngs_dict("graphics/materials")
    for key, value in MATERIAL_SPRITE.items():
        MATERIAL_SPRITE[key] = pygame.transform.scale_by(value, 2)
    MATERIAL_SPRITE.update(load_pngs_dict("graphics/ui/gun_ui"))

PILOT_POSITION = [ None,
    (3024, 1169+36),
    (2624, 1360+36),
    (1136,  320+36),
    (342,  1300+36),
]

class Player(pygame.sprite.Sprite):

    def __init__(self, master, grps):

        super().__init__(grps)
        self.master = master
        self.master.player = self
        self.screen = pygame.display.get_surface()

        # pos = (196*16, 71*16)
        # pos = (2000, 700)
        # pos = (300, 300)
        pos = PILOT_POSITION[self.master.game.which_pilot]
        # pos = (3*16, 5*16-8)
        # pos = (8*16, 173*16)

        self.all_pilot_anims = [None]
        for i in range(1, 5):
            self.all_pilot_anims.append(import_sprite_sheets(F"graphics/player/pilot_{i}"))


        self.animations = self.all_pilot_anims[self.master.game.which_pilot]
        self.animation = self.animations["idle_side"]
        self.image = self.animation[0]
        self.rect = self.image.get_rect()

        self.anim_index = 0
        self.anim_speed = 0.15

        self.hitbox = pygame.FRect(0, 0, 10, 10)
        self.hitbox.midbottom = pos
        self.rect.midbottom = pos
        self.velocity = pygame.Vector2()
        self.input_direc = pygame.Vector2()
        self.max_speed = 1.8
        self.inventory_speed = 0.5
        self.acceleration = 0.3
        self.deceleration = 0.3
        self.facing_direc = pygame.Vector2(0, 1)

        self.moving = False
        self.in_control = True
        self.attacking = False
        self.can_attack = True
        self.has_gun = False

        self.health = 5
        self.max_health = 5
        self.invinsible = False
        self.hurting = False
        self.dying = False

        self.inventory = {}
        self.inventory = {"uranium":1, "titanium":2, "copper":3, "gold":4, "diamond":5, "wood":6, "rubber":7, "fruit":8, "vegetable":9}
        self.inventory_open = False
        self.has_final_resource = False
        self.weapon_upgraded = False

        self.heart_surf = pygame.image.load("graphics/ui/heart.png").convert_alpha()
        self.empty_heart_surf = pygame.image.load("graphics/ui/empty_heart.png").convert_alpha()
        self.heart_surf = pygame.transform.scale_by(self.heart_surf, 5)
        self.empty_heart_surf = pygame.transform.scale_by(self.empty_heart_surf, 5)

        self.attack_cooldown = CustomTimer()
        self.attack_for = CustomTimer()

        self.invinsibility_timer = CustomTimer()
        self.hurt_for = CustomTimer()

    def add_inventory(self, item, amount=1):

        old_amount = self.inventory.get(item, 0)
        self.inventory[item] = old_amount+amount

    def update_image(self):

        if self.dying: return

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
        # self.master.debug("state: ", state)

        try:
            image = self.animations[state][int(self.anim_index)]
        except IndexError:
            image = self.animations[state][0]
            self.anim_index = 0

        if self.inventory_open: self.anim_speed = 0.04
        elif self.moving: self.anim_speed = 0.15
        else: self.anim_speed = 0.08

        self.anim_index += self.anim_speed *self.master.dt

        self.image = image.copy()
        if state.endswith("side"):
            self.image = pygame.transform.flip(self.image, self.facing_direc.x<0, False)
        self.rect.midbottom = self.hitbox.midbottom

        if self.invinsible:
            self.image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
            if self.hurting:
                self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MIN)
            self.image.set_alpha(int((sin(pygame.time.get_ticks()/30)+1)/2 *255))

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
        do_collision(self, 2, self.master, obj_rects)

    def process_events(self):

        if self.in_control and not self.inventory_open:
            for event in pygame.event.get((pygame.KEYUP, pygame.KEYDOWN)):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_k:
                        self.get_hurt(1)
                    if event.key == pygame.K_ESCAPE:
                        self.master.game.pause_game()
                    if event.key == pygame.K_e:
                        self.master.interaction_manager.pressed_interact()
                    if event.key == pygame.K_SPACE and self.in_control and self.can_attack and self.has_gun:
                        self.attacking = True
                        self.in_control = False
                        self.can_attack = False
                        self.attack_cooldown.start(500)
                        self.attack_for.start(200)
                        self.master.sounds.play("SFX_Weapon", (1, 4))
                        if self.weapon_upgraded:
                            proj = "player_small"
                        else: proj = "player_mini"
                        self.master.level.shoot_projectile(proj, self)
        elif self.inventory_open or self.hurting:
            pygame.event.clear((pygame.KEYUP, pygame.KEYDOWN))

        if self.attack_cooldown.check():
            self.can_attack = True
        if self.attack_for.check():
            self.attacking = False
            self.in_control = True
        if self.invinsibility_timer.check():
            self.invinsible = False
        if self.hurt_for.check():
            self.hurting = False
            self.in_control = True

    def change_pilot(self, which_pilot):

        self.animations = self.all_pilot_anims[which_pilot]
        self.health = self.max_health

        self.moving = False
        self.in_control = True
        self.attacking = False
        self.can_attack = True
        self.has_gun = True
        self.dying = False
        self.hurting = False
        self.invinsible = False
        self.has_final_resource = False
        self.weapon_upgraded = False
        self.facing_direc.update(0, 1)
        self.hitbox.midbottom = PILOT_POSITION[self.master.game.which_pilot]

        self.attack_cooldown.stop()
        self.attack_for.stop()
        self.invinsibility_timer.stop()
        self.hurt_for.stop()

        #make dead body if neded
        self.inventory.clear()

    def die(self):

        self.dying = True
        self.anim_index = 0
        DeadBody(self.master, [self.master.level.obj_grp, self.master.level.camera_grp],
                 self.animations["dead"][0], self.hitbox.midbottom, self.facing_direc.x>0, True, self.inventory, self.has_final_resource, self.weapon_upgraded)
        self.master.game.look_next_pilot(self.master.game.which_pilot+1)
        self.master.sounds["SFX_Death"].play()

    def get_hurt(self, damage):

        if self.invinsible or self.dying: return
        self.health -= damage
        self.moving = False
        self.hurting = True
        self.invinsible = True
        self.in_control = False
        self.velocity.update()
        self.hurt_for.start(200)
        self.invinsibility_timer.start(1_000)

        if self.health <= 0:
            self.die()
        else:
            self.master.sounds["SFX_DamageReceived"].play()

    def draw_inventory(self):

        self.master.game.black_overlay.set_alpha(100)
        self.screen.blit(self.master.game.black_overlay, (0, 0))
        self.screen.blit(pygame.transform.gaussian_blur(self.screen, 5, False), (0, 0))

        mat_size = 16
        padd = 12
        gridx, gridy = 4, 3

        widx = mat_size*gridx + padd*(gridx-1)
        widy = mat_size*gridy + padd*(gridy-1)

        offx = (W-widx)/2
        offy = (H-widy)/2

        inventory = []
        if self.has_gun:
            key = F"gun{'_upgraded' if self.weapon_upgraded else ''}{self.master.game.which_pilot}"
            inventory.append((key, None))
        if self.has_final_resource:
            inventory.append(("final_resource", None))
        for key, amount in self.inventory.items():
            if amount != 0:
                inventory.append((key, amount))

        for i, (key, amount) in enumerate(inventory):
            if amount == 0: continue
            y, x = divmod(i, gridx)
            pos = x*(mat_size+padd)+offx, y*(mat_size+padd)+offy
            self.screen.blit(MATERIAL_SPRITE[key], (pos))
            if amount is not None:
                text = self.master.font_d.render(F"x{amount}", False, (255, 255, 255))
                self.screen.blit(text, (pos[0]+mat_size/3*2, pos[1]+mat_size/2))

            mouse_pos = pygame.mouse.get_pos()
            if pos[0] <= mouse_pos[0] <= pos[0]+mat_size and pos[1] <= mouse_pos[1] <= pos[1]+mat_size:
                if key.startswith("gun"):
                    name = "gun"
                elif key == "final_resource":
                    name = "final resource"
                else: name = key
                text = self.master.font_d.render(name, False, (255, 255, 255))
                self.screen.blit(text, (pos[0]-(text.get_width()-mat_size)/2, pos[1]-text.get_height()+2))

        radius = min((W, H))/5*2
        # pygame.draw.arc(self.screen, (100, 0, 20), (W/2-radius+15, H/2-radius+15, (radius-15)*2, (radius-15)*2), 0, pi*2/self.max_health*self.health, 5)
        for i in range(self.max_health):

            angle = pi*2/self.max_health*i - pi/2
            surf = self.heart_surf if i < self.health else self.empty_heart_surf
            rot_surf = pygame.transform.rotate(surf, -90 - degrees(angle))
            pos = cos(angle)*radius + (W/2), sin(angle)*radius + (H/2)
            rect = rot_surf.get_rect(center=(pos))
            self.screen.blit(rot_surf, rect)

    def draw(self):

        if self.dying: return
        self.screen.blit(self.image, self.rect.topleft + self.master.offset)
        pygame.draw.rect(self.screen, "blue", (self.hitbox.x+self.master.offset.x, self.hitbox.y+self.master.offset.y, self.hitbox.width, self.hitbox.height), 1)

    def update(self):

        self.process_events()
        self.get_input()
        self.apply_force()
        self.move()
        self.update_image()

        self.master.debug("pos: ", (round(self.hitbox.centerx, 2), round(self.hitbox.bottom, 2)))

