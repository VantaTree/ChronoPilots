import pygame
from .engine import *
from .config import *
from .objects import SpaceShip1, OreDeposit, TreeWithStuff, SpaceShip2, SpaceShip3, SpaceShip4, Door
from .enemies import Dog, Squid
from .projectile import Projectile
from pytmx.util_pygame import load_pygame
from math import sin, pi


class Level:

    def __init__(self, master, player, map_type):

        self.master = master
        self.screen = pygame.display.get_surface()

        self.player = player
        self.map_type = map_type

        self.object_hitboxes = []
        self.camera_grp = AdvancedCustomGroup()
        self.obj_grp = CustomGroup()
        self.enemy_grp = CustomGroup()
        self.projectile_grp = CustomGroup()

        self.data = load_pygame(F"data/map/{map_type}.tmx")
        self.size = self.data.width, self.data.height

        self.spawn_rect = pygame.Rect(-10000, -100000, 4*CHUNK, 4*CHUNK)

        if map_type == "terrain":
            self.init_overworld()
        elif map_type == "cave":
            self.init_cave()
        
        self.get_collision_data()
        self.get_tile_layers()
        self.init_object_layer()

    def get_collision_data(self):
        
        for tileset in self.data.tilesets:
            if tileset.name == "collision":
                collision_firstgid = tileset.firstgid
            if tileset.name == "objects":
                self.object_firstgid = tileset.firstgid

        self.collision = self.data.get_layer_by_name("collision").data
        
        for y, row in enumerate(self.collision):
            for x, gid in enumerate(row):

                self.collision[y][x] = self.data.tiledgidmap[gid] - collision_firstgid

    def create_lvl_object(self, id, ore_obj):

        if (1 < id <= 6) or id == 17:
            l = [None, None, "copper", "diamond", "gold", "titanium", "uranium"]
            c = l[id] if id != 17 else "final"
            OreDeposit(self.master, [self.obj_grp], c, ore_obj, 3)
        elif id in (14, 15, 16):
            if id == 14:
                stuff = "fruit"
            elif id == 15:
                stuff = "vegetable"
            elif id == 16:
                stuff = "rubber"

            TreeWithStuff(self.master, [self.obj_grp], stuff, ore_obj, 1)
        elif id in (18, 19):
            dog = ["dog1", "dog2"][id-18]
            Dog(self.master, [self.camera_grp, self.enemy_grp], self, (ore_obj.x, ore_obj.y), dog)
        elif id == 20:
            Squid(self.master, [self.camera_grp, self.enemy_grp], self, (ore_obj.x, ore_obj.y))

    def get_tile_layers(self):

        self.tile_map_layers = [self.data.get_layer_by_name("main"), self.data.get_layer_by_name("over")]

    def init_object_layer(self):

        self.object_layer = self.data.get_layer_by_name("objects")
        self.object_chunk = {}
        for obj in self.object_layer:
            if obj.image is None:
                print(self.data.tiledgidmap[obj.gid]-2147483648, "is flipped")
                continue
            id = self.data.tiledgidmap[obj.gid]-self.object_firstgid+1
            if id in (18, 19, 20):
                self.create_lvl_object(id, obj)
                continue

            self.create_lvl_object(id, obj)
            pos = int(obj.x//CHUNK), int(obj.y//CHUNK)
            chunk_list = self.object_chunk.get(pos)

            if chunk_list is None:
                self.object_chunk[(pos)] = [obj,]
                continue
            chunk_list.append(obj)

    def init_overworld(self):

        SpaceShip1(self.master, [self.camera_grp, self.obj_grp], (3024, 1169), self.object_hitboxes)
        self.spawn_rect.center = (3024, 1169)
        Door(self.master, [self.obj_grp], "cave")

        self.maroon_overlay = pygame.Surface(self.screen.get_size())
        self.maroon_overlay.fill(0x4C4A93)
        self.maroon_overlay.set_alpha(0)
        self.night_alpha = 128
        self.current_time_alpha = 0
        self.time_alpha_direction = 1
        self.day_progress_timer = CustomTimer()
        self.day_progress_timer.start(3_500, 0)

    def init_cave(self):
        
        Door(self.master, [self.obj_grp], "terrain")

    def shoot_projectile(self, key, obj):

        if key == "player_small":
            Projectile(self.master, [self.camera_grp, self.projectile_grp], "projectile_small", obj.rect.center, obj.facing_direc.copy(), damage=2)
        if key == "player_mini":
            Projectile(self.master, [self.camera_grp, self.projectile_grp], "projectile_mini", obj.rect.center, obj.facing_direc.copy(), damage=1)

    def change_pilot(self, which_pilot):

        if self.map_type == "terrain":
            if which_pilot == 2:
                SpaceShip2(self.master, [self.camera_grp, self.obj_grp], (2624, 1360), self.object_hitboxes)
                self.spawn_rect.center = (2624, 1360)
            if which_pilot == 3:
                SpaceShip3(self.master, [self.camera_grp, self.obj_grp], (1136, 320), self.object_hitboxes)
                self.spawn_rect.center = (1136, 320)
            if which_pilot == 4:
                SpaceShip4(self.master, [self.camera_grp, self.obj_grp], (342, 1300), self.object_hitboxes)
                self.spawn_rect.center = (342, 1300)

        for obj in self.obj_grp.sprites():
            obj.change_pilot(which_pilot)

    def draw_bg(self):

        self.screen.fill(0x4C0805)

        for layer in self.tile_map_layers:

            px1 = int(self.master.offset.x*-1//TILESIZE)
            px2 = px1 + W//TILESIZE +1
            py1 = int(self.master.offset.y*-1//TILESIZE)
            py2 = py1 + H//TILESIZE

            if px2 >= self.size[0]: px2 = self.size[0]-1
            if py2 >= self.size[1]: py2 = self.size[1]-1
            if px2 < 0: px2 = 0
            if py2 < 0: py2 = 0

            for y in range(py1, py2+1):
                for x in range(px1, px2+1):
                    gid = layer.data[y][x]
                    image = self.data.get_tile_image_by_gid(gid)
                    if image is None: continue
                    self.screen.blit(image, (x*TILESIZE + self.master.offset.x, y*TILESIZE + self.master.offset.y - image.get_height() + TILESIZE))

        if self.master.debug.on:
            for y in range(self.size[1]):
                for x in range(self.size[0]):

                    cell =  self.collision[y][x]
                    if not cell: continue
                    if cell == 1:
                        pygame.draw.rect(self.screen, "green", (x*16+self.master.offset.x, y*16+self.master.offset.y, 16, 16), 1)
                    elif cell == 2:
                        pygame.draw.rect(self.screen, "blue", (x*16+self.master.offset.x, y*16+self.master.offset.y, 16, 16), 1)
                    elif cell == 4:
                        pygame.draw.polygon(self.screen, 'blue', ( ((x*TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy,
                        ((x*TILESIZE+TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy, ((x*TILESIZE+TILESIZE, y*TILESIZE)+self.master.offset).xy ), 1)
                    elif cell == 5:
                        pygame.draw.polygon(self.screen, 'blue', ( ((x*TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy,
                        ((x*TILESIZE+TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy, ((x*TILESIZE, y*TILESIZE)+self.master.offset).xy ), 1)
                    elif cell == 6:
                        pygame.draw.polygon(self.screen, 'blue', ( ((x*TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy,
                        ((x*TILESIZE, y*TILESIZE)+self.master.offset).xy, ((x*TILESIZE+TILESIZE, y*TILESIZE)+self.master.offset).xy ), 1)
                    elif cell == 7:
                        pygame.draw.polygon(self.screen, 'blue', ( ((x*TILESIZE, y*TILESIZE)+self.master.offset).xy,
                        ((x*TILESIZE+TILESIZE, y*TILESIZE)+self.master.offset).xy, ((x*TILESIZE+TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy ), 1)

    def draw_fg(self):

        # if self.master.debug.on:
        #     for rect in self.object_hitboxes:
        #         pygame.draw.rect(self.screen, "green", (rect.x+self.master.offset.x, rect.y+self.master.offset.y, rect.width, rect.height), 1)

        if self.map_type == "terrain":

            if self.day_progress_timer.check():
                self.current_time_alpha += self.time_alpha_direction
                if self.current_time_alpha == 0:
                    self.time_alpha_direction = 1
                elif self.current_time_alpha == self.night_alpha:
                    self.time_alpha_direction = -1

            if self.current_time_alpha < 40:
                self.day_progress_timer.duration = 3_500
            else:
                self.day_progress_timer.duration = 1_000

            self.maroon_overlay.set_alpha(self.current_time_alpha)
            self.screen.blit(self.maroon_overlay, (0, 0))
            self.master.debug("day:", self.current_time_alpha)

        if self.player.inventory_open:
            self.player.draw_inventory()            

    def update(self):

        self.obj_grp.update()
        self.enemy_grp.update()
        self.projectile_grp.update()

