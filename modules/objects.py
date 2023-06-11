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
    (0, 0, 8, 7)
]

ORE_INTERACTIONS = load_interaction_text("ore_deposits")


class SpaceShip1(pygame.sprite.Sprite):

    def __init__(self, master, grps, pos, object_hitboxes):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()

        self.image = pygame.image.load("graphics/objects/spaceship.png").convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)

        self.hitbox = pygame.FRect(0, 0, self.rect.width, 40)
        self.hitbox.midbottom = pos
        object_hitboxes.append(self.hitbox)

        self.interactives = [
            ["fabricator", (151, 110, 21, 15)],
            ["engine", (28, 86, 70, 38)],
        ]

        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]

        self.engine_core_fixed = False

        self.interaction_text_dict = load_interaction_text("spaceship1")
        # print(self.interaction_text_dict)

    def interacted(self, key):

        self.master.interaction_manager.activate_text(key, self)

    def interaction_logic_check(self, obj_key, key, checks):

        if obj_key == "engine":
            if key == "init":
                return checks[0] if self.engine_core_fixed else checks[1]
            
    def select_choice(self, obj_key, key):

        if obj_key == "fabricator":
            if key == "engine core":
                pass
                # self.engine_core_fixed = True

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)

    def update(self):

        do_interaction_check(self, self.interactives, self.master)


class OreDeposit(pygame.sprite.Sprite):

    def __init__(self, master, grps, ore_type, ore_obj, ore_amount):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()

        self.ore_type = ore_type
        self.ore_obj = ore_obj
        self.rect = pygame.Rect(ore_obj.x, ore_obj.y, ore_obj.width, ore_obj.height)
        self.ore_amount = ore_amount

        self.interactives = [
            [F"{ore_type} deposit", (0, 0, ore_obj.width, ore_obj.height)],
        ]
        self.interaction_text_dict = ORE_INTERACTIONS

        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]

    def interacted(self, key):

        self.master.interaction_manager.activate_text(key, self)

    def interaction_logic_check(self, obj_key, key, checks):

        pass
            
    def select_choice(self, obj_key, key):

        if key == "mine":
            self.ore_amount -= 1
            if self.ore_amount == 0:
                self.interactives.clear()
                # self.ore_obj.image = 

    def update(self):

        if not self.rect.colliderect((
            -self.master.offset.x, -self.master.offset.y, W, H
        )): return
        do_interaction_check(self, self.interactives, self.master)




