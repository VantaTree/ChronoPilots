import pygame
from .engine import *
from .config import *
from .level import Level
from .menus import PauseMenu
from .player import Player
from .objects import SpaceShip1
from .interactions import InteractionManager
from .enemies import load_enemy_sprites, Enemy
from .projectile import load_projectile_sprites, Projectile
from .particle import ParticleManager

class Game:

    def __init__(self, master):

        self.master = master
        self.master.game = self
        self.screen = pygame.display.get_surface()

        load_enemy_sprites()
        load_projectile_sprites()

        self.master.offset = pygame.Vector2(0, 0)

        self.interaction_manager = InteractionManager(master)
        self.pause_menu = PauseMenu(master)
        self.particle_manager = ParticleManager(master)

        self.player = Player(master, [])
        self.camera = Camera(master)
        self.camera.set_target(self.player, lambda p: p.rect.center)
        self.camera.draw_sprite_grp.add(self.player)
        self.level = Level(master, self.player, "terrain")
        self.master.level = self.level

        self.paused = False

    def pause_game(self):
        return
        if not self.paused:
            self.paused = True
            self.pause_menu.open()

    def run(self):

        self.master.music.run()
        self.master.ambience.run()

        if self.paused:
            self.pause_menu.draw()
            self.pause_menu.update()
            return

        self.player.update()
        self.camera.update()
        self.level.update()
        self.particle_manager.update()

        self.level.draw_bg()
        self.particle_manager.below_grp.draw()
        self.camera.draw()
        self.particle_manager.above_grp.draw()

        self.interaction_manager.update()

        self.level.draw_fg()        


class Camera:

    def __init__(self, master, target = None, key = None):

        self.master = master
        master.camera = self

        self.draw_sprite_grp = AdvancedCustomGroup()

        self.camera_rigidness = 0.05

        self.target = target
        self.key = key

    def key(self): pass

    def set_target(self, target, key):

        self.target = target
        self.key = key

    def get_target_pos(self):

        return self.key(self.target)

    def snap_offset(self):

        self.master.offset =  (self.get_target_pos() - pygame.Vector2(W/2, H/2)) * -1

    def update_offset(self):

        if self.target == self.master.player:
            self.camera_rigidness = 0.18 if self.master.player.moving else 0.05
        else: self.camera_rigidness = 0.05
        
        self.master.offset -= (self.master.offset + (self.get_target_pos() - pygame.Vector2(W/2, H/2)))\
            * self.camera_rigidness * self.master.dt

    def clamp_offset(self):

        size = self.master.level.size

        if size[0]*TILESIZE <= W: self.master.offset.x = 0
        elif self.master.offset.x > 0: self.master.offset.x = 0
        elif self.master.offset.x < -size[0]*TILESIZE + W:
            self.master.offset.x = -size[0]*TILESIZE + W
        
        if size[1]*TILESIZE <= H:
            self.master.offset.y = 0
        elif self.master.offset.y > 0: self.master.offset.y = 0
        elif self.master.offset.y < -size[1]*TILESIZE + H:
            self.master.offset.y = -size[1]*TILESIZE + H

    def draw(self):

        self.draw_sprite_grp.advanced_y_sort_draw(self.master)
        # self.draw_sprite_grp.advanced_y_sort_draw(self.master)

    def update(self):

        self.update_offset()
        self.clamp_offset()


class AdvancedCustomGroup(CustomGroup):

    def advanced_y_sort_draw(self, master):

        draw_list = []
        px1 = int(master.offset.x*-1//CHUNK) -1
        px2 = px1 + W//CHUNK +2
        py1 = int(master.offset.y*-1//CHUNK) -1
        py2 = py1 + H//CHUNK +2

        for y in range(py1, py2+1):
            for x in range(px1, px2+1):
                obj_list = master.level.object_chunk.get((x, y))
                if obj_list is None: continue
                draw_list.extend(obj_list)

        draw_list.extend(self.sprites())

        master.debug("obj count:", len(draw_list))
        master.debug("", (px1, px2, "", py1, py2))

        for sprite in sorted(draw_list, key=self.key):
            try:
                sprite.draw()
            except Exception:
                if sprite.image is not None: # BIG PROBLEM
                    master.game.screen.blit(sprite.image, (int(sprite.x), int(sprite.y))+master.offset)
                else:
                    master.level.data.tiledgidmap[sprite.gid]

    @staticmethod
    def key(p):

        try:
            return p.rect.bottom
        except Exception:
            return p.y+p.height