import pygame
from .engine import *
from .config import *
from .objects import SpaceShip1
from .enemies import Enemy
from .projectile import Projectile
from pytmx.util_pygame import load_pygame


class Level:

    def __init__(self, master, player, map_type):

        self.master = master
        self.screen = pygame.display.get_surface()

        self.player = player
        self.map_type = map_type

        self.object_hitboxes = []
        self.obj_grp = CustomGroup()
        self.enemy_grp = CustomGroup()

        self.data = load_pygame(F"data/map/{map_type}.tmx")
        self.size = self.data.width, self.data.height

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

        self.collision = self.data.get_layer_by_name("collision").data
        
        for y, row in enumerate(self.collision):
            for x, gid in enumerate(row):

                self.collision[y][x] = self.data.tiledgidmap[gid] - collision_firstgid

    def get_tile_layers(self):

        self.tile_map_layers = [self.data.get_layer_by_name("main"), self.data.get_layer_by_name("over")]

    def init_object_layer(self):

        self.object_layer = self.data.get_layer_by_name("objects")
        self.object_chunk = {}
        for obj in self.object_layer:
            if obj.image is None:
                print(self.data.tiledgidmap[obj.gid]-2147483648, "is flipped")
                continue
            pos = int(obj.x//CHUNK), int(obj.y//CHUNK)
            chunk_list = self.object_chunk.get(pos)
            if chunk_list is None:
                self.object_chunk[(pos)] = [obj,]
                continue
            chunk_list.append(obj)

    def init_overworld(self):

        SpaceShip1(self.master, [self.master.camera.draw_sprite_grp, self.obj_grp], (480, 200), self.object_hitboxes)
        Enemy(self.master, [self.master.camera.draw_sprite_grp, self.enemy_grp], (688, 232), "test")

    def init_cave(self):
        
        pass

    def shoot_projectile(self, key, obj):

        if key == "player_small":
            Projectile(self.master, [self.master.camera.draw_sprite_grp, self.enemy_grp], "projectile_small", obj.rect.center, obj.facing_direc.copy())

    def draw_bg(self):

        self.screen.fill(0x4C0805)

        for layer in self.tile_map_layers:

            px1 = int(self.master.offset.x*-1//TILESIZE)
            px2 = px1 + W//TILESIZE
            py1 = int(self.master.offset.y*-1//TILESIZE)
            py2 = py1 + H//TILESIZE

            if px2 == self.size[0]: px2 = self.size[0]-1
            if py2 == self.size[1]: py2 = self.size[1]-1
            if px2 < 0: px2 = 0
            if py2 < 0: py2 = 0

            for y in range(py1, py2+1):
                for x in range(px1, px2+1):
                    gid = layer.data[y][x]
                    image = self.data.get_tile_image_by_gid(gid)
                    if image is None: continue
                    self.screen.blit(image, (x*TILESIZE + self.master.offset.x, y*TILESIZE + self.master.offset.y - image.get_height() + TILESIZE))


        for y in range(self.size[1]):
            for x in range(self.size[0]):

                if not self.collision[y][x]: continue

                pygame.draw.rect(self.screen, "green", (x*16+self.master.offset.x, y*16+self.master.offset.y, 16, 16), 1)

    def draw_fg(self):

        for rect in self.object_hitboxes:
            pygame.draw.rect(self.screen, "green", (rect.x+self.master.offset.x, rect.y+self.master.offset.y, rect.width, rect.height), 1)

    def update(self):

        self.obj_grp.update()
        self.enemy_grp.update()

