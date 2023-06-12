import pygame
from os import listdir
from random import randint

class SoundSet:

    def __init__(self, master):

        self.dict:dict[str, pygame.mixer.Sound] = {}
        
        self.master = master
        self.master.sounds = self

        for sound_file in listdir("sounds"):
            self.dict[sound_file[:-4]] = pygame.mixer.Sound(F"sounds/{sound_file}")

        self.dict["UI_Select"].set_volume(0.1)
        self.dict["UI_Hover"].set_volume(0.1)
        self.dict["UI_Pause"].set_volume(0.1)
        self.dict["UI_Return"].set_volume(0.1)
        self.dict["SFX_Spawn"].set_volume(0.5)

    def __getitem__(self, key, range=None):

        return self.dict[key]
    
    def play(self, key, range=None):

        if range is not None:
            key += str(randint(range[0], range[1]))
        self.dict[key].play()