import pygame, os
from .config import *
# from PIL import Image, ImageFilter

class CustomGroup(pygame.sprite.Group):

    def draw(self):

        for sprite in self.sprites():
            sprite.draw()

    def draw_y_sort(self, key):

        for sprite in sorted(self.sprites(), key=key):
            sprite.draw()


def import_spritesheet(folder_path, sheet_name):
    "imports a given spritesheet and places it in a list"
    sprite_list = []
    name, size = sheet_name[:-4].split('-')
    w, h = [int(x) for x in size.split('x')]
    sheet = pygame.image.load(F"{folder_path}/{sheet_name}").convert_alpha()
    for j in range(sheet.get_height()//h):
        for i in range(sheet.get_width()//w):
            sprite = sheet.subsurface((w*i, h*j, w, h))
            sprite_list.append(sprite)
    return sprite_list


def import_sprite_sheets(folder_path):
    "imports all sprite sheets in a folder"
    animations = {}

    for file in os.listdir(folder_path):
        if file.endswith(".png"):
            animations[file.split('-')[0]] = import_spritesheet(folder_path, file)

    return animations

def load_pngs_dict(folder_path):

    sprites = {}
    for file in os.listdir(folder_path):
        sprites[file[:-4]] = pygame.image.load(F"{folder_path}/{file}").convert_alpha()
    return sprites

def load_pngs(folder_path):
    "loads all png from folder"

    return [pygame.image.load(F"{folder_path}/{file}").convert() for file in sorted(os.listdir(folder_path))]

def dist_sq(p1, p2):

    return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

def _get_mouse_pos(master) -> tuple[int, int]:

    mx, my = pygame.mouse.get_pos()
    wx, wy = master.window.size

    return int(mx/wx * W), int(my/wy * H)

class CustomTimer:

    def __init__(self, auto_clear=False):

        self.running = False

        self.duration = None
        self.start_time = None
        self.loops = 0
        self.auto_clear = auto_clear

    def start(self, duration, loops=1):

        self.running = True
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.loops = loops

    def stop(self):
        
        if self.running:
            self.running = False
            return True

    def check(self):

        if not self.running: return False
        
        if pygame.time.get_ticks() - self.duration >= self.start_time:
            self.loops -= 1
            if self.loops == 0:
                self.running = False
            else:
                if self.auto_clear:
                    self.start_time = pygame.time.get_ticks()
                else:
                    self.start_time += self.duration
            return True

# def blur_image(image, radius=6):
#     raw_str = pygame.image.tostring(image, 'RGBA')
#     pil_blured = Image.frombytes("RGBA", image.get_size(), raw_str).filter(ImageFilter.GaussianBlur(radius=radius))
#     return pygame.image.fromstring(pil_blured.tobytes("raw", 'RGBA'), image.get_size(), 'RGBA')