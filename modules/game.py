import pygame
from .engine import *
from .config import *
from .level import Level
from .menus import PauseMenu
from .player import Player, load_materials
from .interactions import InteractionManager
from .enemies import load_enemy_sprites, Enemy
from .projectile import load_projectile_sprites, Projectile
from .particle import ParticleManager
from .cutscene import FiFo

class Game:

    def __init__(self, master):

        self.master = master
        self.master.game = self
        self.screen = pygame.display.get_surface()

        load_enemy_sprites()
        load_projectile_sprites()
        load_materials()

        self.master.offset = pygame.Vector2(0, 0)

        self.which_pilot = 1 # 1234
        self.interaction_manager = InteractionManager(master)
        self.pause_menu = PauseMenu(master)
        self.particle_manager = ParticleManager(master)

        self.player = Player(master, [])
        self.camera = Camera(master)
        self.camera.set_target(self.player, lambda p: p.rect.center)
        self.camera.snap_offset()

        self.terrain_level = Level(master, self.player, "terrain")
        self.cave_level = Level(master, self.player, "cave")
        self.test_level = Level(master, self.player, "bug_test")

        self.test_level.camera_grp.add(self.player)
        self.terrain_level.camera_grp.add(self.player)
        self.cave_level.camera_grp.add(self.player)

        self.level = self.test_level
        self.player.hitbox.midbottom = (68, 100)
        self.player.rect.midbottom = (68, 100)
        # self.level = self.terrain_level
        self.master.level = self.level

        self.paused = False

        self.black_overlay = pygame.Surface(self.screen.get_size())

    def look_next_pilot(self, next_pilot):

        if next_pilot == 2:
            state = self.master.app.P1_TO_P2_CUTSCENE
            cutscene = "p1-2"
        elif next_pilot == 3:
            state = self.master.app.P2_TO_P3_CUTSCENE
            cutscene = "p2-3"
        elif next_pilot == 4:
            state = self.master.app.P3_TO_P4_CUTSCENE
            cutscene = "p3-4"
        elif next_pilot == 5:
            if self.player.dying:
                game_state = "lost"
                state = self.master.app.LOST_CUTSCENE
            else:
                game_state = "won"
                state = self.master.app.WON_CUTSCENE
            cutscene = F"end {game_state}"

        if cutscene.startswith("end"):
            self.master.app.cutscene = FiFo(self.master, cutscene)
            self.master.app.state = state
        else:
            self.master.app.cutscene = FiFo(self.master, "mission_completed" if not self.player.dying else "you_died",
                                            True, "darkred" if self.player.dying else "gold")
            self.master.app.state = self.master.app.PILOT_END_CUTSCENE
            self.master.app.next_state = state
            self.master.app.next_cutscene = cutscene
            if self.player.dying:
                self.master.sounds["SFX_DizzyEffect"].play()

        self.master.ambience.fadeout()
        self.master.music.change_track("main_menu")

    def change_pilot(self, which_pilot):

        self.which_pilot = which_pilot
        self.terrain_level.change_pilot(self.which_pilot)
        self.cave_level.change_pilot(self.which_pilot)
        self.player.change_pilot(which_pilot)
        self.particle_manager.change_pilot(which_pilot)

        self.level = self.terrain_level
        self.master.level = self.level

        for lvl in (self.terrain_level, self.cave_level, self.test_level):
            for enemy in lvl.enemy_grp.sprites():
                enemy.change_pilot(which_pilot)

    def transition_to(self, map, pos):

        if map == "terrain":
            self.level = self.terrain_level
        elif map == "cave":
            self.level = self.cave_level

        self.master.level = self.level
        self.player.hitbox.midbottom = pos
        self.player.rect.midbottom = pos
        self.camera.snap_offset()
        self.player.facing_direc.update(0, 1)

        self.master.app.state = self.master.app.TRANSITION
        self.master.app.cutscene = FiFo(self.master, "transition")

    def pause_game(self):
        if not self.paused:
            self.paused = True
            self.pause_menu.open()

    def run(self):

        if self.master.app.state == self.master.app.IN_GAME:
            target_music = None
            target_amb = None
            if self.level.map_type == "terrain":
                if self.level.spawn_rect.colliderect(self.player.rect):
                    target_music = "crash_site"
                    target_amb = "ambient_crash_site"
                else:
                    target_music = "plains"
                    target_amb = "ambient_plains"
            elif self.level.map_type == "terrain":
                target_music = "cave"
                target_amb = "ambient_cave"
            else:
                target_music = "crash_site"
                target_amb = "ambient_crash_site"

            if self.master.music.current_track != target_music:
                self.master.music.change_track(target_music)
            if self.master.ambience.current_track != target_amb:
                self.master.ambience.change_track(target_amb)

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

        self.master.offset = (self.get_target_pos() - pygame.Vector2(W/2, H/2)) * -1

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

        self.master.level.camera_grp.advanced_y_sort_draw(self.master)

    def update(self):

        self.update_offset()
        self.clamp_offset()
