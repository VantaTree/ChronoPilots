import pygame
from .config import *
from .engine import *
from random import choice, uniform

class ParticleManager:

    def __init__(self, master):

        self.master = master
        master.particle_manager = self

        self.above_grp = CustomGroup()
        self.below_grp = CustomGroup()

        self.player_footstep_timer = CustomTimer()
        self.player_footstep_timer.start(80, 0)

    def change_pilot(self, which_pilot):

        self.player_footstep_timer.stop()
        self.player_footstep_timer.start(80, 0)

    def player_footsteps(self):

        if self.player_footstep_timer.check() and self.master.player.moving:
            for _ in range(2):
                offset = (uniform(-5.0, 5.0), uniform(-5.0, 5.0)-3)
                pos = self.master.player.hitbox.centerx + offset[0], self.master.player.hitbox.bottom + offset[1]
                color = choice(("brown", "gold", "burlywood", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "#df821c", "#df821c", "#df821c"))
                Particle(self.master, [self.below_grp], pos, color, size=(2, 2))


    def add(self, type):

        pass

    def update(self):

        self.player_footsteps()
        self.below_grp.update()
        self.above_grp.update()


class Particle(pygame.sprite.Sprite):

    def __init__(self, master, grps, pos, color="red", size=(1, 1), direction=(0, 0), duration=500, speed=0, fade=True):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()

        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_frect(center=pos)

        self.direction = pygame.Vector2(direction)
        self.speed = speed
        self.duration = duration
        self.fade = fade
        self.start_time = pygame.time.get_ticks()
        
        self.alive_timer = CustomTimer()

        self.alive_timer.start(duration)

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft+self.master.offset)

    def update(self):

        self.rect.center += self.direction*self.speed*self.master.dt

        alpha = (pygame.time.get_ticks()-self.start_time) / self.duration * 255
        self.image.set_alpha(255-alpha)

        if self.alive_timer.check():
            self.kill()
            return