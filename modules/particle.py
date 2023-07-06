import pygame
from .config import *
from .engine import *
from random import choice, uniform, randint
from math import sqrt

class ParticleManager:

    def __init__(self, master):

        self.master = master
        master.particle_manager = self

        self.above_grp = CustomGroup()
        self.below_grp = CustomGroup()

        self.player_footstep_timer = CustomTimer(True)
        self.player_footstep_timer.start(80, 0)

    def change_pilot(self, which_pilot):

        self.player_footstep_timer.stop()
        self.player_footstep_timer.start(80, 0)

    def player_footsteps(self):

        if self.player_footstep_timer.check() and self.master.player.moving:
            if choice([1, 0]): self.master.sounds.play("SFX_Footstep", (1, 10))
            for _ in range(2):
                offset = (uniform(-5.0, 5.0), uniform(-5.0, 5.0)-3)
                pos = self.master.player.hitbox.centerx + offset[0], self.master.player.hitbox.bottom + offset[1]
                color = choice(("brown", "gold", "burlywood", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "#df821c", "#df821c", "#df821c"))
                Particle(self.master, [self.below_grp], pos, color, size=(2, 2))

    def spawn_blood(self, pos, intensity=100):

        for _ in range(intensity):
            
            speed = uniform(0.3, 1.2)
            velocity = pygame.Vector2()
            velocity.from_polar((speed, randint(0, 365)))
            duration = randint(16, 22)*100
            friction = 0.03
            # size = (2, 2)
            size = (randint(1, 2), randint(1, 2))
            color = choice(("red", "darkred", "firebrick1", "firebrick2", "firebrick3", "red1", "red2", "red3"))

            Particle(self.master, [self.below_grp], pos, color, size, velocity, friction=friction, duration=duration)

    def spawn_muzzle_flash(self, position, direction, intensity=150, dist=20.0, angle=30.0):

        for _ in range(intensity):
            
            radius = 14
            # distance = (sqrt(uniform(0.0, dist**2)))
            # distance = (dist-sqrt(uniform(0.0, dist**2)))
            distance = uniform(0.0, dist)
            pos = position + (direction*radius) + direction.rotate(uniform(-angle, angle)) * distance
            friction = 0.03
            size = (randint(1, 2), randint(1, 2))
            # colors = ("white", "lightyellow", "yellow", "red")
            colors = (0xFFFF22, 0xFFFF88, 0xFFFFCC, 0xFFFF88, 0xFFFF22)
            color = colors[int(distance/dist*len(colors))]
            Particle(self.master, [self.above_grp], pos, color, size, friction=friction, duration=100, fade=True)

    def add(self, type):

        pass

    def update(self):

        self.player_footsteps()
        self.below_grp.update()
        self.above_grp.update()


class Particle(pygame.sprite.Sprite):

    def __init__(self, master, grps, pos, color="red", size=(1, 1), velocity=(0, 0), force=(0, 0), friction=0, duration=500, fade=True, anchor=None, anchor_pull=0):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()

        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_frect(center=pos)

        self.velocity = pygame.Vector2(velocity)
        self.force = pygame.Vector2(force)
        self.friction = friction
        self.duration = duration
        self.anchor = anchor
        self.anchor_pull = anchor_pull
        self.fade = fade
        self.start_time = pygame.time.get_ticks()
        
        self.alive_timer = CustomTimer()

        self.alive_timer.start(duration)

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft+self.master.offset)

    def update(self):

        self.velocity += self.force *self.master.dt
        if self.friction != 0:
            self.velocity.move_towards_ip((0, 0), self.friction *self.master.dt)
        if self.anchor:
            anchor_force = pygame.Vector2(self.anchor[0] - self.rect.centerx, self.anchor[1] - self.rect.centery)
            anchor_force.scale_to_length(self.anchor_pull)
            self.velocity += anchor_force*self.master.dt

        self.rect.center += self.velocity *self.master.dt

        if self.fade:
            alpha = (pygame.time.get_ticks()-self.start_time) / self.duration * 255
            self.image.set_alpha(255-alpha)

        if self.alive_timer.check():
            self.kill()
            return