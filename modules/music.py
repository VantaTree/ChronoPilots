import pygame
from .engine import *


class Music:
    def __init__(self, master):
        self.master = master
        master.music = self
        self.tracks = {
        }
        
        self.is_playing = False
        self.can_play = True
        self.started_playing = False

        self.is_loaded = False

        self.change_track_to = None
        self.current_track = None

        self.START_NEW_TRACK_TIMER = CustomTimer()

        self.START_NEW_TRACK_TIMER.start(500)
        self.change_track_to = "main_menu"


    def change_track(self, track_type):
        if track_type == self.current_track: return
        delay = 0
        if self.is_loaded:
            pygame.mixer.music.fadeout(2_000)
            delay = 2_100
        self.START_NEW_TRACK_TIMER.start(delay)
        self.change_track_to = track_type

    def process_events(self):

        if self.START_NEW_TRACK_TIMER.check():
            pygame.mixer.music.load(self.tracks[self.change_track_to])
            pygame.mixer.music.play(loops=-1, fade_ms=2_000)
            self.current_track = self.change_track_to
            self.change_track_to = None
            self.is_loaded = True
    
    def run(self):

        self.can_play = not self.master.game.paused

        self.process_events()

        if not self.is_loaded: return

        if self.can_play and not self.is_playing:
            if not self.started_playing:
                pygame.mixer.music.play(loops=-1, fade_ms= 2_000)
                self.started_playing = True
            else:
                pygame.mixer.music.unpause()

            self.is_playing = True

        elif not self.can_play and self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False