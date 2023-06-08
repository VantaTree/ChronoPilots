import pygame
from os import listdir

class SoundSet:

    def __init__(self, master):

        self.dict:dict[str, pygame.mixer.Sound] = {}
        
        self.master = master
        self.master.sounds = self

        for sound_file in listdir("sounds"):
            self.dict[sound_file[:-4]] = pygame.mixer.Sound(F"sounds/{sound_file}")

    def __getitem__(self, key):

        return self.dict[key]