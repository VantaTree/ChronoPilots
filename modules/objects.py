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

ORE_INTERACTION = load_interaction_text("ore_deposits")
EDIBLE_INTERACTION = load_interaction_text("tree_with_stuff")
DEAD_BODY_INTERACTION_TEXT = load_interaction_text("dead_body")

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

        self.image = pygame.image.load("graphics/objects/spaceship1.png").convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)

        self.hitbox = pygame.Rect(0, 0, 82, 13)
        self.hitbox.midbottom = pos
        object_hitboxes.append(self.hitbox)

        self.interaction_text_dict = load_interaction_text("spaceship1")
        self.interactives = [
            ["spaceship", (24, 51, 82, 13)],
        ]

        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]


        self.first_interaction_p1 = True
        self.repaired = False
        self.salvaged = False
    
    def change_pilot(self, which_pilot):

        if which_pilot == 2:
            self.interactives[0][0] = "very old spaceship"

    def interaction_logic_check(self, obj_key, key, checks):

        p = self.master.player

        if obj_key != "spaceship":
            if key == "init":
                if self.salvaged:
                    return checks[1]
                else:
                    return checks[0]
            return

        if key == "init":
            if self.first_interaction_p1:
                self.first_interaction_p1 = False
                return checks[0]
            elif not self.repaired:
                if p.inventory.get("titanium", 0)>=4 and p.inventory.get("rubber", 0)>=1:
                    p.inventory["titanium"] -= 4
                    p.inventory["rubber"] -= 1
                    self.repaired = True
                    return checks[2]
                else: return checks[1]
            elif p.inventory.get("fruit", 0)>=1 and p.inventory.get("vegetable", 0)>=1:
                p.inventory["vegetable"] -= 1
                p.inventory["fruit"] -= 1
                return checks[3]
            else: return checks[4]
            
    def select_choice(self, obj_key, key):

        if obj_key != "spaceship":
            if key == "salvage":
                self.salvaged = True
                self.master.player.add_inventory("copper", 2)
                self.master.player.add_inventory("uranium", 1)
            return

        if key == "get me out of here":
            self.kill()
            self.master.level.object_hitboxes.remove(self.hitbox)
            self.master.game.look_next_pilot(2)


class SpaceShip2(Interactable):

    def __init__(self, master, grps, pos, object_hitboxes):

        super().__init__(master, grps, "spaceship2")

        self.image = pygame.image.load("graphics/objects/spaceship2.png").convert_alpha()
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(midbottom=pos)

        self.hitbox = pygame.Rect(0, 0, 82, 13)
        self.hitbox.midbottom = pos
        object_hitboxes.append(self.hitbox)

        self.interaction_text_dict = load_interaction_text("spaceship2")
        self.interactives = [
            ["spaceship", (24, 51, 82, 13)],
        ]

        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]

        # self.first_interaction_p2 = True
        self.edibles_deposited = False
        self.salvaged = False

    def change_pilot(self, which_pilot):

        if which_pilot == 3:
            self.interactives[0][0] = "old spaceship"

    def interaction_logic_check(self, obj_key, key, checks):

        p = self.master.player

        if obj_key != "spaceship":
            if key == "init":
                if self.salvaged:
                    return checks[1]
                else:
                    return checks[0]
            return

        if not self.edibles_deposited:
            if p.inventory.get("diamond", 0)>=1 and p.inventory.get("gold", 0)>=1 and p.inventory.get("uranium", 0)\
                >=1 and p.inventory.get("fruit", 0)>=1 and p.inventory.get("vegetable", 0)>=1:
                p.inventory["diamond"] -= 1
                p.inventory["gold"] -= 1
                p.inventory["uranium"] -= 1
                p.inventory["fruit"] -= 1
                p.inventory["vegetable"] -= 1
                self.edibles_deposited = True
                return checks[1]
            else: return checks[0]
        else: return checks[2]

            
    def select_choice(self, obj_key, key):

        if obj_key != "spaceship":
            if key == "salvage":
                self.salvaged = True
                self.master.player.add_inventory("fruit", 1)
                self.master.player.add_inventory("vegetable", 1)
                self.master.player.add_inventory("uranium", 1)
            return

        if key == "leave":
            self.kill()
            self.master.level.object_hitboxes.remove(self.hitbox)
            self.master.game.look_next_pilot(3)


class SpaceShip3(Interactable):

    def __init__(self, master, grps, pos, object_hitboxes):

        super().__init__(master, grps, "spaceship3")

        self.image = pygame.image.load("graphics/objects/spaceship3.png").convert_alpha()
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(midbottom=pos)

        self.hitbox = pygame.Rect(0, 0, 82, 13)
        self.hitbox.midbottom = pos
        object_hitboxes.append(self.hitbox)

        self.interaction_text_dict = load_interaction_text("spaceship3_4")
        self.interactives = [
            ["spaceship", (24, 51, 82, 13)],
        ]

        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]

        # self.first_interaction_p3 = True
        self.salvaged = False

    def change_pilot(self, which_pilot):

        if which_pilot == 4:
            self.interactives[0][0] = "another spaceship"

    def interaction_logic_check(self, obj_key, key, checks):

        p = self.master.player

        if obj_key != "spaceship":
            if key == "init":
                if self.salvaged:
                    return checks[1]
                else:
                    return checks[0]
            return

        if key == "init":
            if p.has_final_resource:
                return checks[0]
            else: return checks[1]
        elif key == "heal":
            if p.health == p.max_health:
                return checks[0]
            elif p.inventory.get("vegetable", 0)>=1 and p.inventory.get("fruit", 0)>=1:
                p.inventory["vegetable"] -= 1
                p.inventory["fruit"] -= 1
                p.health += 1
                return checks[1]
            else: return checks[2]
        elif key == "upgrade weapon":
            if p.weapon_upgraded:
                return checks[0]
            elif p.inventory.get("titanium", 0)>=5 and p.inventory.get("copper", 0)>=6 and p.inventory.get("diamond", 0)\
                  >=2 and p.inventory.get("uranium", 0)>=3 and p.inventory.get("gold", 0)>=1:# == (5, 6, 2, 3, 1):
                p.inventory["titanium"] -= 5
                p.inventory["copper"] -= 6
                p.inventory["diamond"] -= 2
                p.inventory["uranium"] -= 3
                p.inventory["gold"] -= 1
                p.weapon_upgraded = True
                return checks[1]
            else: return checks[2]

            
    def select_choice(self, obj_key, key):

        if obj_key != "spaceship":
            if key == "salvage":
                self.salvaged = True
                self.master.player.add_inventory("titanium", 2)
                self.master.player.add_inventory("gold", 1)
                self.master.player.add_inventory("uranium", 1)
            return

        if key == "leave":
            self.kill()
            self.master.level.object_hitboxes.remove(self.hitbox)
            self.master.game.look_next_pilot(4)


class SpaceShip4(SpaceShip3):

    def __init__(self, master, grps, pos, object_hitboxes):
        super().__init__(master, grps, pos, object_hitboxes)
        self.image = pygame.image.load("graphics/objects/spaceship4.png").convert_alpha()

    def change_pilot(self, which_pilot): pass

    def select_choice(self, obj_key, key): pass


class OreDeposit(Interactable):

    def __init__(self, master, grps, ore_type, ore_obj, ore_amount):

        super().__init__(master, grps, F"{ore_type} deposit")

        self.ore_type = ore_type
        self.ore_obj = ore_obj
        self.rect = pygame.Rect(ore_obj.x, ore_obj.y, ore_obj.width, ore_obj.height)
        self.ore_amount = ore_amount

        self.interaction_text_dict = ORE_INTERACTION
        self.interactives = [
            [F"{ore_type} deposit", (0, 0, ore_obj.width, ore_obj.height)],
        ]
        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]

    def interaction_logic_check(self, obj_key, key, checks):

        if key == "init":
            if self.master.game.which_pilot == 1:
                if obj_key == "titanium deposit" and self.master.player.inventory.get(self.ore_type, 0) < 4:
                    return checks[0]
                else: return checks[1]
            elif self.master.game.which_pilot == 2:
                if obj_key in ("gold deposit", "diamond deposit", "uranium deposit") and self.master.player.inventory.get(self.ore_type, 0) < 1:
                    return checks[0]
                else: return checks[1]
            elif self.master.game.which_pilot in (3, 4):
                return checks[0]
            
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

        self.interaction_text_dict = EDIBLE_INTERACTION

        self.interactives = [
            [F"{stuff_type} tree", (0, 0, ore_obj.width, ore_obj.height)],
        ]
        for i, (_, rect) in enumerate(self.interactives):
            self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]

    def interaction_logic_check(self, obj_key, key, checks):

        if key == "init":
            if self.master.game.which_pilot == 1:
                if self.master.player.inventory.get(self.stuff_type, 0) < 1:
                    return checks[0]
                else: return checks[1]
            elif self.master.game.which_pilot == 2:
                if obj_key in ("fruit tree", "vegetable tree") and self.master.player.inventory.get(self.stuff_type, 0) < 1:
                    return checks[0]
                else: return checks[1]
            elif self.master.game.which_pilot in (3, 4):
                return checks[0]
            
    def select_choice(self, obj_key, key):

        if key == "pluck" or key == "get them anyway":
            self.stuff_amount -= 1
            self.master.player.add_inventory(self.stuff_type)
            if self.stuff_amount == 0:
                self.interactives.clear()
                self.ore_obj.gid = self.master.level.data.map_gid(11+self.master.level.object_firstgid)[0][0]


class DeadBody(Interactable):

    def __init__(self, master, grps, image, pos, flipped=False, interactable=False, inventory=None, has_final_resource=False, weapon_upgraded=False):

        super().__init__(master, grps, "dead body")
        self.master = master
        self.screen = pygame.display.get_surface()
        self.image = image
        self.rect = self.image.get_rect(midbottom=pos)
        self.hitbox = self.rect
        if flipped:
            self.image = pygame.transform.flip(self.image, True, False)

        self.interactable = interactable
        if self.interactable:

            self.interaction_text_dict = DEAD_BODY_INTERACTION_TEXT
            self.interactives = [
                ["dead body", (0, 0, self.rect.width, self.rect.height)],
            ]

            for i, (_, rect) in enumerate(self.interactives):
                self.interactives[i][1] = rect[0]+self.rect.x, rect[1]+self.rect.y, rect[2], rect[3]

            self.inventory = inventory.copy()
            self.has_final_resource = has_final_resource
            self.weapon_upgraded = weapon_upgraded
            self.looted = False

    def interaction_logic_check(self, obj_key, key, checks):

        if key == "init":
            if not self.inventory:
                self.looted = True
                return checks[2]
            elif self.looted:
                return checks[0]
            else: return checks[1]
            
    def select_choice(self, obj_key, key):

        if key == "loot it":
            self.looted = True
            for key, amount in self.inventory.items():
                old_amount = self.master.player.inventory.get(key, 0)
                self.master.player.inventory[key] = old_amount+amount

            self.master.player.has_final_resource = self.has_final_resource
            self.master.player.weapon_upgraded = self.weapon_upgraded

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft+self.master.offset)
