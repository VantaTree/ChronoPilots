import pygame
import random
from .engine import *
from .config import *

class Player:

    def __init__(self, master):

        self.master = master
        self.master.player = self
        self.screen = pygame.display.get_surface()

        pos = (88, 96)

        self.animations = import_sprite_sheets("graphics/player/anims")
        self.animation = self.animations["idle_right"]
        self.image = self.animation[0]
        self.rect = self.image.get_rect()

        self.anim_index = 0
        self.anim_speed = 0.15

        self.hitbox = pygame.FRect(0, 0, 13, 12)
        self.hitbox.midbottom = pos
        self.base_rect = pygame.FRect(0, 0, 14, 3)
        self.velocity = pygame.Vector2()
        self.input_direc = pygame.Vector2()
        self.max_speed = 2
        self.acceleration = 0.5
        self.deceleration = 0.5
        self.facing_direc = pygame.Vector2(1, 0)

        self.moving = False
        self.in_control = True

    def update_image(self):

        state = []
        if self.moving: state.append("walk")
        else: state.append("idle")

        if self.facing_direc.y != 0:
            if self.facing_direc.y >= 0:
                state.append("_down")
            else:
                state.append("_up")
        elif self.facing_direc.x != 0:
            if self.facing_direc.x >= 0:
                state.append("_right")
            else:
                state.append("_left")

        state = "".join(state)
        self.master.debug("state: ", state)

        try:
            image = self.animations[state][int(self.anim_index)]
        except IndexError:
            image = self.animations[state][0]
            self.anim_index = 0

        if self.moving: self.anim_speed = 0.15
        else: self.anim_speed = 0.08

        self.anim_index += self.anim_speed *self.master.dt

        # self.image = pygame.transform.flip(image, self.facing_direc.x<0, False)
        self.image = image
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
        
        self.moving = bool(self.input_direc)
        if self.moving:
            self.facing_direc.update(self.input_direc)

        if self.input_direc.x and self.input_direc.y:
            self.input_direc.normalize_ip()

    def apply_force(self):

        if self.moving:
            self.velocity.move_towards_ip( self.input_direc*self.max_speed, self.acceleration *self.master.dt)
        else:
            self.velocity.move_towards_ip( (0, 0), self.deceleration *self.master.dt)

    def move(self):

        self.hitbox.centerx += self.velocity.x * self.master.dt
        do_collision(self, 0, self.master)
        self.hitbox.centery += self.velocity.y * self.master.dt
        do_collision(self, 1, self.master)

    def process_events(self):

        if self.in_control:
            for event in pygame.event.get((pygame.KEYUP, pygame.KEYDOWN)):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.master.game.pause_game()

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)
        pygame.draw.rect(self.screen, "blue", (self.hitbox.x+self.master.offset.x, self.hitbox.y+self.master.offset.y, self.hitbox.width, self.hitbox.height), 1)

    def update(self):

        self.process_events()
        self.get_input()
        self.apply_force()
        self.move()
        self.update_image()

        self.master.debug("pos: ", (round(self.hitbox.centerx, 2), round(self.hitbox.bottom, 2)))


def do_collision(player:Player, axis, master):

    px = int(player.hitbox.centerx / TILESIZE)
    py = int(player.hitbox.centery / TILESIZE)
    player.base_rect.midbottom = player.hitbox.midbottom
    player.base_rect.y += 1

    for y in range(py-1, py+2):
        for x in range(px-1, px+2):

            if x < 0 or y < 0: continue

            rect = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, TILESIZE)
            rectg = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, 8)
            if not player.hitbox.colliderect(rect): continue

            cell = get_xy(collision, x, y)

            if axis == 0: # x-axis

                if cell == 1:

                    if player.velocity.x > 0:
                        player.hitbox.right = rect.left
                    if player.velocity.x < 0:
                        player.hitbox.left = rect.right

            elif axis == 1: # y-axis

                if cell == 1:
                    if player.velocity.y < 0:
                        player.hitbox.top = rect.bottom
                        # player.velocity.y = 0
                    if player.velocity.y > 0:
                        player.hitbox.bottom = rect.top
                        # player.velocity.y = 0

                        
def get_xy(grid, x, y):

    if x < 0 or y < 0: return
    try:
        return grid[y][x]
    except IndexError: return


collision = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]