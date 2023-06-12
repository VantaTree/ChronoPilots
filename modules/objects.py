import pygame
from .config import *
from .engine import *
from .interactions import Check, Choice
from os import listdir

def do_interaction_check(obj, interactives, master):
        
        for name, rect in interactives:

            if not master.player.rect.colliderect(rect): continue
            master.interaction_manager.interactions.append((name, obj, rect))

def load_interaction_text(folder):
     
    interaction_text_dict = {}

    for file in listdir(F"data/interactive text/{folder}"):
        name = file[:-4]
        part_text_dict = {}
        marker = None
        extension = None
        with open(F"data/interactive text/{folder}/{file}") as text:
            for line in text.read().split("\n"):
                if line in ("", ")", "]"):
                    if extension is not None:
                        part_text_dict[marker].append(extension)
                        extension = None
                    marker = None
                elif line.startswith("$"):
                    marker = line[1:]
                    part_text_dict[marker] = []
                elif line == "(":
                    extension = Choice()
                elif line == "[":
                    extension = Check()
                elif extension is not None:
                    extension.append(line.strip())
                else:
                    part_text_dict[marker].append(line)

        interaction_text_dict[name] = part_text_dict

    return interaction_text_dict

objects_hitboxes = [
    None,
    (0, 0, 13, 7),
    (0, 0, 13, 7),
    (0, 0, 13, 7),
    (0, 0, 13, 7),
    (0, 0, 13, 7),
    (0, 0, 13, 7),
    None,
    None,
    None,
    (0, 0, 4, 2),
    (0, 0, 4, 3),
    (0, 0, 8, 7),
    (0, 0, 8, 7),
    (0, 0, 8, 7),
    (0, 0, 8, 7),
    (0, 0, 8, 7)
]

ORE_INTERACTIONS = [None]
EDIBLE_INTERACTIONS = [None]
for pilot in range(1, 5):
    ORE_INTERACTIONS.append(load_interaction_text(F"ore_deposits{pilot}"))
    EDIBLE_INTERACTIONS.append(load_interaction_text(F"tree_with_stuff{pilot}"))
    break


class Interactable(pygame.sprite.Sprite):

    def __init__(self, master, grps, type):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()
        self.type = type

    def change_pilot(self, which_pilot):

        pass

    def interacted(self, key):

        self.master.interaction_manager.activate_text(key, self)

    def interaction_logic_check(self, obj_key, key, checks):

        pass
            
    def select_choice(self, obj_key, key):

        pass

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)

    def update(self):

        if not self.rect.colliderect((
            -self.master.offset.x, -self.master.offset.y, W, H
        )): return
        do_interaction_check(self, self.interactives, self.master)


class SpaceShip1(Interactable):

    def __init__(self, master, grps, pos, object_hitboxes):

        super().__init__(master, grps, "spaceship1")

        self.image = pygame.image.load("graphics/objects/spaceship.png").convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)

        self.hitbox = pygame.Rect(0, 0, self.rect.width, 40)
        self.hitbox.midbottom = pos
        object_hitboxes.append(self.hitbox)

        self.interaction_text_dict = load_interaction_text("spaceship1")
        self.interactives = [
            ["spaceship", (16, 112, 218, 16)],
        ]

        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]


        self.first_interaction_p1 = True
        self.repaired = False

    def change_pilot(self, which_pilot):
        
        pass

    def interaction_logic_check(self, obj_key, key, checks):

        p = self.master.player

        if key == "init":
            if self.first_interaction_p1:
                self.first_interaction_p1 = False
                return checks[0]
            elif not self.repaired:
                if (p.inventory.get("titanium"), p.inventory.get("rubber")) == (4, 1):
                    p.inventory["titanium"] -= 4
                    p.inventory["rubber"] -= 1
                    self.repaired = True
                    return checks[2]
                else: return checks[1]
            elif (p.inventory.get("fruit"), p.inventory.get("vegetable")) != (1, 1):
                p.inventory["vegetable"] -= 1
                p.inventory["fruit"] -= 1
                return checks[3]
            else: return checks[4]
            
    def select_choice(self, obj_key, key):

        pass


class OreDeposit(Interactable):

    def __init__(self, master, grps, ore_type, ore_obj, ore_amount):

        super().__init__(master, grps, F"{ore_type} deposit")

        self.ore_type = ore_type
        self.ore_obj = ore_obj
        self.rect = pygame.Rect(ore_obj.x, ore_obj.y, ore_obj.width, ore_obj.height)
        self.ore_amount = ore_amount

        self.interaction_text_dict = ORE_INTERACTIONS[self.master.game.which_pilot]

        self.interactives = [
            [F"{ore_type} deposit", (0, 0, ore_obj.width, ore_obj.height)],
        ]
        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]

    def interaction_logic_check(self, obj_key, key, checks):

        if key == "init":
            if obj_key == "titanium deposit" and self.master.player.inventory.get(self.ore_type, 0) < 4:
                return checks[0]
            else: return checks[1]
            
    def select_choice(self, obj_key, key):

        if key == "mine" or key == "mine them anyway":
            self.ore_amount -= 1
            self.master.player.add_inventory(self.ore_type)
            if self.ore_amount == 0:
                self.interactives.clear()
                self.ore_obj.gid = self.master.level.data.map_gid(0+self.master.level.object_firstgid)[0][0]


class TreeWithStuff(Interactable):

    def __init__(self, master, grps, stuff_type, ore_obj, stuff_amount):

        super().__init__(master, grps, F"{stuff_type} tree")

        self.stuff_type = stuff_type
        self.ore_obj = ore_obj
        self.rect = pygame.Rect(ore_obj.x, ore_obj.y, ore_obj.width, ore_obj.height)
        self.stuff_amount = stuff_amount

        self.interaction_text_dict = EDIBLE_INTERACTIONS[self.master.game.which_pilot]

        self.interactives = [
            [F"{stuff_type} tree", (0, 0, ore_obj.width, ore_obj.height)],
        ]
        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]

    def interaction_logic_check(self, obj_key, key, checks):

        if key == "init":
            if self.master.player.inventory.get(self.stuff_type, 0) < 1:
                return checks[0]
            else: return checks[1]
            
    def select_choice(self, obj_key, key):

        if key == "pluck" or key == "get them anyway":
            self.stuff_amount -= 1
            self.master.player.add_inventory(self.stuff_type)
            if self.stuff_amount == 0:
                self.interactives.clear()
                self.ore_obj.gid = self.master.level.data.map_gid(11+self.master.level.object_firstgid)[0][0]



